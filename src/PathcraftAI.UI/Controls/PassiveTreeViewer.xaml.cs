using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using PathcraftAI.UI.Services.PassiveTree;

namespace PathcraftAI.UI.Controls
{
    /// <summary>
    /// POB 스타일 스프라이트 기반 오프라인 패시브 트리 뷰어
    /// 프레임, 아이콘, 그룹 배경을 POB와 동일하게 렌더링
    /// </summary>
    public partial class PassiveTreeViewer : UserControl
    {
        private PassiveTreeData? _treeData;
        private SpriteAtlasManager? _spriteManager;
        private TreeTransform _transform = new();

        private bool _isLoaded = false;
        private bool _isDragging = false;
        private Point _lastMousePos;
        private TreeNode? _hoveredNode;
        private string _selectedClass = "Marauder";
        private HashSet<string> _allocatedNodes = new();

        // POB 스타일 렌더링 상수
        // Scale은 TreeTransform.Scale = min(viewport) / treeSize * zoom
        // 800px viewport, 15000 tree size, zoom=1.73 (zoomLevel=3) → Scale=0.092
        private const double MinScaleForIcons = 0.02;     // Scale 0.02 이상에서 아이콘 표시
        private const double MinScaleForFrames = 0.015;   // Scale 0.015 이상에서 프레임 표시
        private const double MinScaleForLabels = 0.08;    // Scale 0.08 이상에서 라벨 표시

        public PassiveTreeViewer()
        {
            InitializeComponent();
        }

        #region Initialization

        private async void UserControl_Loaded(object sender, RoutedEventArgs e)
        {
            if (_isLoaded) return;

            await LoadTreeDataAsync();
        }

        private async Task LoadTreeDataAsync()
        {
            try
            {
                StatusText.Text = "Loading passive tree data...";

                await Task.Run(() =>
                {
                    // JSON 데이터 로드
                    _treeData = PassiveTreeData.LoadFromResources();
                });

                StatusText.Text = "Initializing sprites...";

                // 스프라이트 매니저 초기화
                _spriteManager = new SpriteAtlasManager();
                if (_treeData != null)
                {
                    _spriteManager.Initialize(_treeData.Sprites);
                }

                // 뷰 초기화
                _transform.ViewportWidth = ActualWidth > 0 ? ActualWidth : 800;
                _transform.ViewportHeight = ActualHeight > 0 ? ActualHeight : 600;

                if (_treeData != null)
                {
                    // 트리 크기 설정 (POB Scale 계산에 사용)
                    _transform.TreeSize = Math.Max(_treeData.Bounds.Width, _treeData.Bounds.Height);

                    // 전체 트리가 보이도록 초기 뷰 설정
                    _transform.FitBounds(_treeData.Bounds);

                    // 선택된 클래스로 이동
                    CenterOnClass(_selectedClass);
                }

                _isLoaded = true;
                LoadingPanel.Visibility = Visibility.Collapsed;

                // 통계 표시
                UpdateStatsText();

                // 초기 렌더링
                RenderTree();

                InfoText.Text = "Offline Passive Tree (POB Style). Drag to pan, scroll to zoom.";
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[PassiveTreeViewer] Load error: {ex.Message}");
                StatusText.Text = $"Error: {ex.Message}";
                LoadingProgress.Visibility = Visibility.Collapsed;
            }
        }

        private void UpdateStatsText()
        {
            if (_treeData == null) return;

            var stats = _treeData.Stats;
            StatsText.Text = $"Nodes: {stats.TotalNodes} | Keystones: {stats.Keystones} | " +
                            $"Notables: {stats.Notables} | Allocated: {_allocatedNodes.Count}";
        }

        #endregion

        #region Rendering

        private void RenderTree()
        {
            if (_treeData == null || !_isLoaded) return;

            var width = (int)ActualWidth;
            var height = (int)ActualHeight;
            if (width <= 0 || height <= 0) return;

            // DrawingVisual로 렌더링
            var drawingVisual = new DrawingVisual();
            // 고품질 스케일링 설정
            RenderOptions.SetBitmapScalingMode(drawingVisual, BitmapScalingMode.HighQuality);
            using (var dc = drawingVisual.RenderOpen())
            {
                // 보이는 영역 계산
                var visibleBounds = _transform.GetVisibleTreeBounds();
                visibleBounds.Inflate(500, 500); // 여유 마진

                // 1. 메인 배경 렌더링 (POB 스타일)
                RenderMainBackground(dc, width, height);

                // 2. 그룹 배경 렌더링
                RenderGroupBackgrounds(dc, visibleBounds);

                // 3. 연결선 렌더링
                RenderConnections(dc, visibleBounds);

                // 4. 노드 렌더링 (프레임 + 아이콘)
                RenderNodes(dc, visibleBounds);
            }

            // RenderTargetBitmap으로 변환
            var rtb = new RenderTargetBitmap(width, height, 96, 96, PixelFormats.Pbgra32);
            rtb.Render(drawingVisual);
            rtb.Freeze();

            TreeImage.Source = rtb;
            TreeImage.Width = width;
            TreeImage.Height = height;

            // 줌 레벨 표시 업데이트 (Scale * 1000으로 표시, 사용자가 이해하기 쉬운 값)
            ZoomLevelText.Text = $"Scale: {_transform.Scale * 100:F1}";
        }

        /// <summary>
        /// 메인 배경 렌더링 (POB 스타일 배경 이미지 타일링)
        /// </summary>
        private void RenderMainBackground(DrawingContext dc, int width, int height)
        {
            // 기본 어두운 배경
            var baseBrush = new SolidColorBrush(Color.FromRgb(18, 18, 18));
            baseBrush.Freeze();
            dc.DrawRectangle(baseBrush, null, new Rect(0, 0, width, height));

            // 배경 이미지 가져오기
            var bgImage = _spriteManager?.GetBackground();
            if (bgImage == null) return;

            // POB 스타일: Scale 기반 타일 크기 계산
            var scale = _transform.Scale;
            var bgWidth = bgImage.Width * scale * 4;  // 적절한 타일 크기
            var bgHeight = bgImage.Height * scale * 4;

            // 너무 작으면 타일링 스킵 (성능)
            if (bgWidth < 100 || bgHeight < 100) return;

            // 화면 중심 기준 오프셋 계산 (TreeToScreen으로 정확한 위치)
            var origin = _transform.TreeToScreen(0, 0);
            var offsetX = origin.X % bgWidth;
            var offsetY = origin.Y % bgHeight;

            // 뷰포트 시작 전부터 타일링
            if (offsetX > 0) offsetX -= bgWidth;
            if (offsetY > 0) offsetY -= bgHeight;

            // 투명도 적용 (0.4 → 0.5로 밝게)
            dc.PushOpacity(0.5);

            // 타일 렌더링
            for (double y = offsetY; y < height + bgHeight; y += bgHeight)
            {
                for (double x = offsetX; x < width + bgWidth; x += bgWidth)
                {
                    dc.DrawImage(bgImage, new Rect(x, y, bgWidth, bgHeight));
                }
            }

            dc.Pop();
        }

        /// <summary>
        /// 그룹 배경 렌더링 (POB PSGroupBackground1/2/3 - sprites.json 좌표 사용)
        /// </summary>
        private void RenderGroupBackgrounds(DrawingContext dc, Rect visibleBounds)
        {
            if (_treeData == null || _spriteManager == null) return;

            var scale = _transform.Scale;
            if (scale < 0.01) return; // 너무 축소되면 배경 스킵

            // POB 스타일 크기 배율
            const double sizeMultiplier = 15.0;

            foreach (var group in _treeData.Groups.Values)
            {
                if (group.IsProxy) continue;
                if (group.Orbits == null || group.Orbits.Count == 0) continue;

                // 보이는 영역 체크
                if (!visibleBounds.Contains(new Point(group.X, group.Y))) continue;

                var screenPos = _transform.TreeToScreen(group.X, group.Y);

                // 궤도 수에 따른 배경 선택
                var maxOrbit = group.Orbits.Max();

                // sprites.json에서 정확한 배경 스프라이트 가져오기
                var bgImage = _spriteManager.GetGroupBackground(maxOrbit);
                if (bgImage != null)
                {
                    // sprites.json의 실제 크기 사용
                    var bgSize = _spriteManager.GetGroupBackgroundSize(maxOrbit);
                    var scaledWidth = bgSize.Width * scale * sizeMultiplier;
                    var scaledHeight = bgSize.Height * scale * sizeMultiplier;

                    if (scaledWidth < 20) continue;

                    var rect = new Rect(
                        screenPos.X - scaledWidth / 2,
                        screenPos.Y - scaledHeight / 2,
                        scaledWidth,
                        scaledHeight);

                    dc.PushOpacity(0.6);
                    dc.DrawImage(bgImage, rect);
                    dc.Pop();
                }
                else
                {
                    // 폴백: 반투명 원
                    var orbitRadii = _treeData.Constants?.OrbitRadii;
                    double radius = 100;
                    if (orbitRadii != null && maxOrbit < orbitRadii.Count)
                    {
                        radius = orbitRadii[maxOrbit] * 1.2;
                    }
                    var size = radius * scale * 2 * sizeMultiplier;
                    if (size < 20) continue;

                    var bgBrush = new SolidColorBrush(Color.FromArgb(40, 60, 50, 40));
                    bgBrush.Freeze();
                    dc.DrawEllipse(bgBrush, null, screenPos, size / 2, size / 2);
                }
            }
        }

        /// <summary>
        /// POB 스타일 연결선 렌더링
        /// </summary>
        private void RenderConnections(DrawingContext dc, Rect visibleBounds)
        {
            if (_treeData == null) return;

            var scale = _transform.Scale;

            // POB 스타일 연결선 색상
            var inactiveColor = SpriteAtlasManager.GetConnectionColor(false, false);
            var activeColor = SpriteAtlasManager.GetConnectionColor(true, false);
            var pathColor = SpriteAtlasManager.GetConnectionColor(false, true);

            // 연결선 두께 (노드 크기에 맞춤: 1.33 배율 적용)
            var baseThickness = Math.Max(1.0, 30 * scale);

            var inactivePen = new Pen(new SolidColorBrush(inactiveColor), baseThickness);
            var activePen = new Pen(new SolidColorBrush(activeColor), baseThickness * 1.3);
            var pathPen = new Pen(new SolidColorBrush(pathColor), baseThickness * 1.1);

            inactivePen.Freeze();
            activePen.Freeze();
            pathPen.Freeze();

            // 렌더링된 연결 추적 (중복 방지)
            var renderedConnections = new HashSet<string>();

            foreach (var node in _treeData.Nodes.Values)
            {
                // 어센던시 노드는 별도 처리
                if (!string.IsNullOrEmpty(node.AscendancyName)) continue;
                if (node.Type == NodeType.Proxy) continue;

                // 보이는 영역 체크 (시작점)
                if (!visibleBounds.Contains(new Point(node.X, node.Y))) continue;

                var nodeIdStr = node.Id?.ToString() ?? "";
                var isNodeAllocated = !string.IsNullOrEmpty(nodeIdStr) && _allocatedNodes.Contains(nodeIdStr);

                foreach (var outNodeId in node.OutConnections)
                {
                    // 중복 체크
                    var connKey = nodeIdStr.CompareTo(outNodeId) < 0
                        ? $"{nodeIdStr}_{outNodeId}"
                        : $"{outNodeId}_{nodeIdStr}";
                    if (renderedConnections.Contains(connKey)) continue;
                    renderedConnections.Add(connKey);

                    if (!_treeData.Nodes.TryGetValue(outNodeId, out var outNode)) continue;
                    if (!string.IsNullOrEmpty(outNode.AscendancyName)) continue;

                    var startScreen = _transform.TreeToScreen(node.X, node.Y);
                    var endScreen = _transform.TreeToScreen(outNode.X, outNode.Y);

                    // 연결 상태 결정
                    var isOutAllocated = _allocatedNodes.Contains(outNodeId);
                    var isConnAllocated = isNodeAllocated && isOutAllocated;

                    var pen = isConnAllocated ? activePen : inactivePen;
                    dc.DrawLine(pen, startScreen, endScreen);
                }
            }
        }

        /// <summary>
        /// POB 스타일 노드 렌더링 (프레임 + 아이콘)
        /// POB는 Scale = min(viewport) / treeSize * zoom 사용
        /// 프레임 크기는 Scale 기반으로 계산하여 화면에 적절한 크기로 표시
        /// </summary>
        private void RenderNodes(DrawingContext dc, Rect visibleBounds)
        {
            if (_treeData == null || _spriteManager == null) return;

            var scale = _transform.Scale;
            var showFrames = scale >= MinScaleForFrames;
            var showIcons = scale >= MinScaleForIcons;

            // POB 기준: 노드 크기는 artWidth * scale * 1.33
            // PathcraftAI Scale이 POB보다 작아서 15.0 사용 (더 큰 노드)
            const double sizeMultiplier = 15.0;

            foreach (var node in _treeData.Nodes.Values)
            {
                // 어센던시 노드는 별도 처리 (현재는 스킵)
                if (!string.IsNullOrEmpty(node.AscendancyName)) continue;
                if (node.Type == NodeType.Proxy) continue;

                // 보이는 영역 체크
                if (!visibleBounds.Contains(new Point(node.X, node.Y))) continue;

                var screenPos = _transform.TreeToScreen(node.X, node.Y);
                var nodeIdStr = node.Id?.ToString() ?? "";
                var isAllocated = !string.IsNullOrEmpty(nodeIdStr) && _allocatedNodes.Contains(nodeIdStr);
                var isHovered = _hoveredNode?.Id?.ToString() == nodeIdStr;

                // 마스터리 노드 특별 처리
                if (node.Type == NodeType.Mastery)
                {
                    RenderMasteryNode(dc, node, screenPos, isAllocated, isHovered, scale);
                    continue;
                }

                // 프레임 크기 계산 (POB 스타일: Scale 기반)
                var frameSize = SpriteAtlasManager.GetFrameSize(node.Type);
                var scaledSize = new Size(
                    frameSize.Width * scale * sizeMultiplier,
                    frameSize.Height * scale * sizeMultiplier);

                // 최소 크기 제한 (2px 이하에서만 점으로 폴백)
                if (scaledSize.Width < 2 || scaledSize.Height < 2)
                {
                    // 너무 작으면 점으로 표시
                    var dotBrush = GetNodeDotBrush(node.Type, isAllocated);
                    dc.DrawEllipse(dotBrush, null, screenPos, 2, 2);
                    continue;
                }

                // 프레임 렌더링
                if (showFrames && scaledSize.Width >= 8)
                {
                    var frame = _spriteManager.GetNodeFrame(node.Type, isAllocated, isHovered);
                    if (frame != null)
                    {
                        var frameRect = new Rect(
                            screenPos.X - scaledSize.Width / 2,
                            screenPos.Y - scaledSize.Height / 2,
                            scaledSize.Width,
                            scaledSize.Height);
                        dc.DrawImage(frame, frameRect);
                    }
                    else
                    {
                        // 프레임이 없으면 폴백: 원으로 표시
                        RenderFallbackNode(dc, node, screenPos, scaledSize, isAllocated, isHovered);
                    }
                }
                else
                {
                    // 줌이 낮으면 간소화된 렌더링
                    RenderFallbackNode(dc, node, screenPos, scaledSize, isAllocated, isHovered);
                }

                // 아이콘 렌더링 (프레임 위에)
                if (showIcons && !string.IsNullOrEmpty(node.Icon) && scaledSize.Width >= 12)
                {
                    var iconSize = SpriteAtlasManager.GetIconSize(node.Type);
                    var scaledIconSize = new Size(
                        iconSize.Width * scale * sizeMultiplier,
                        iconSize.Height * scale * sizeMultiplier);

                    // 최소 아이콘 크기
                    if (scaledIconSize.Width >= 6)
                    {
                        var icon = _spriteManager.GetNodeIcon(node.Icon, isAllocated, node.Type);
                        if (icon != null)
                        {
                            var iconRect = new Rect(
                                screenPos.X - scaledIconSize.Width / 2,
                                screenPos.Y - scaledIconSize.Height / 2,
                                scaledIconSize.Width,
                                scaledIconSize.Height);
                            dc.DrawImage(icon, iconRect);
                        }
                    }
                }
            }
        }

        /// <summary>
        /// 마스터리 노드 렌더링 (sprites.json 좌표 사용)
        /// </summary>
        private void RenderMasteryNode(DrawingContext dc, TreeNode node, Point screenPos,
            bool isAllocated, bool isHovered, double scale)
        {
            if (_spriteManager == null) return;

            // 마스터리 크기도 Scale 기반
            const double sizeMultiplier = 15.0;
            var baseSize = 65.0;
            var size = baseSize * scale * sizeMultiplier;
            if (size < 5) return;

            // sprites.json에서 마스터리 아이콘 가져오기
            var masteryIcon = _spriteManager.GetMasteryIcon(node.Icon, isAllocated, isConnected: false);
            if (masteryIcon != null)
            {
                var rect = new Rect(
                    screenPos.X - size / 2,
                    screenPos.Y - size / 2,
                    size,
                    size);
                dc.DrawImage(masteryIcon, rect);

                // 호버 시 하이라이트
                if (isHovered)
                {
                    var hoverPen = new Pen(new SolidColorBrush(Color.FromRgb(255, 200, 100)), 2);
                    hoverPen.Freeze();
                    dc.DrawEllipse(null, hoverPen, screenPos, size / 2 + 2, size / 2 + 2);
                }
            }
            else
            {
                // 폴백: 원으로 표시
                var brush = new SolidColorBrush(isAllocated
                    ? Color.FromRgb(180, 140, 200)
                    : Color.FromRgb(100, 80, 110));
                brush.Freeze();
                dc.DrawEllipse(brush, null, screenPos, size / 2, size / 2);

                // 호버 시 하이라이트
                if (isHovered)
                {
                    var hoverPen = new Pen(new SolidColorBrush(Color.FromRgb(255, 200, 100)), 2);
                    hoverPen.Freeze();
                    dc.DrawEllipse(null, hoverPen, screenPos, size / 2 + 2, size / 2 + 2);
                }
            }
        }

        /// <summary>
        /// 폴백 노드 렌더링 (프레임 없을 때)
        /// </summary>
        private void RenderFallbackNode(DrawingContext dc, TreeNode node, Point screenPos,
            Size scaledSize, bool isAllocated, bool isHovered)
        {
            var brush = GetNodeDotBrush(node.Type, isAllocated);
            var radius = Math.Max(scaledSize.Width, scaledSize.Height) / 2;

            // 원 그리기
            dc.DrawEllipse(brush, null, screenPos, radius, radius);

            // 키스톤/노터블은 외곽선
            if (node.Type == NodeType.Keystone || node.Type == NodeType.Notable)
            {
                var outlineColor = isAllocated
                    ? Color.FromRgb(255, 215, 0)
                    : Color.FromRgb(120, 100, 70);
                var outlinePen = new Pen(new SolidColorBrush(outlineColor), 1);
                outlinePen.Freeze();
                dc.DrawEllipse(null, outlinePen, screenPos, radius + 1, radius + 1);
            }

            // 호버 시 하이라이트
            if (isHovered)
            {
                var hoverPen = new Pen(new SolidColorBrush(Color.FromRgb(255, 200, 100)), 2);
                hoverPen.Freeze();
                dc.DrawEllipse(null, hoverPen, screenPos, radius + 2, radius + 2);
            }
        }

        /// <summary>
        /// 노드 타입별 기본 브러시
        /// </summary>
        private static Brush GetNodeDotBrush(NodeType type, bool isAllocated)
        {
            Color color;
            if (isAllocated)
            {
                color = type switch
                {
                    NodeType.Keystone => Color.FromRgb(255, 215, 0),    // Gold
                    NodeType.Notable => Color.FromRgb(200, 180, 140),   // Tan
                    NodeType.Mastery => Color.FromRgb(180, 140, 200),   // Purple
                    NodeType.Socket => Color.FromRgb(100, 180, 220),    // Blue
                    NodeType.ClassStart => Color.FromRgb(220, 150, 150), // Red
                    _ => Color.FromRgb(175, 96, 37)                      // POB Active 색상
                };
            }
            else
            {
                color = type switch
                {
                    NodeType.Keystone => Color.FromRgb(100, 85, 55),
                    NodeType.Notable => Color.FromRgb(80, 70, 55),
                    NodeType.Mastery => Color.FromRgb(70, 55, 80),
                    NodeType.Socket => Color.FromRgb(50, 80, 100),
                    NodeType.ClassStart => Color.FromRgb(100, 60, 60),
                    _ => Color.FromRgb(60, 53, 46)                       // POB Inactive 색상
                };
            }

            var brush = new SolidColorBrush(color);
            brush.Freeze();
            return brush;
        }

        #endregion

        #region Mouse Events

        private void TreeCanvas_MouseWheel(object sender, MouseWheelEventArgs e)
        {
            var mousePos = e.GetPosition(TreeCanvas);
            _transform.ZoomAtPoint(e.Delta > 0 ? 1 : -1, mousePos);
            RenderTree();
        }

        private void TreeCanvas_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            _isDragging = true;
            _lastMousePos = e.GetPosition(TreeCanvas);
            TreeCanvas.CaptureMouse();
        }

        private void TreeCanvas_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            _isDragging = false;
            TreeCanvas.ReleaseMouseCapture();

            // 클릭으로 노드 토글 (드래그 아닌 경우만)
            var currentPos = e.GetPosition(TreeCanvas);
            if (Math.Abs(currentPos.X - _lastMousePos.X) < 3 &&
                Math.Abs(currentPos.Y - _lastMousePos.Y) < 3)
            {
                HandleNodeClick(currentPos);
            }
        }

        private void TreeCanvas_MouseMove(object sender, MouseEventArgs e)
        {
            var currentPos = e.GetPosition(TreeCanvas);

            if (_isDragging)
            {
                var delta = currentPos - _lastMousePos;
                _transform.Pan(delta.X, delta.Y);
                _lastMousePos = currentPos;
                RenderTree();
            }
            else
            {
                // 노드 호버 감지
                UpdateHoveredNode(currentPos);
            }
        }

        private void TreeCanvas_MouseLeave(object sender, MouseEventArgs e)
        {
            _hoveredNode = null;
            NodeTooltip.IsOpen = false;
        }

        private void UpdateHoveredNode(Point screenPos)
        {
            if (_treeData == null) return;

            var treePos = _transform.ScreenToTree(screenPos);
            TreeNode? closestNode = null;
            double closestDistSq = double.MaxValue;

            foreach (var node in _treeData.Nodes.Values)
            {
                // 어센던시/프록시 스킵
                if (!string.IsNullOrEmpty(node.AscendancyName)) continue;
                if (node.Type == NodeType.Proxy) continue;

                var dx = treePos.X - node.X;
                var dy = treePos.Y - node.Y;
                var distSq = dx * dx + dy * dy;

                // 히트박스 크기 (트리 좌표 기준)
                // POB 스타일: 화면에서 클릭하면 트리 좌표로 변환 후 거리 계산
                var hitRadius = NodeSizes.GetHitRadius(node.Type) / _transform.Scale;
                var hitRadiusSq = hitRadius * hitRadius;

                if (distSq <= hitRadiusSq && distSq < closestDistSq)
                {
                    closestDistSq = distSq;
                    closestNode = node;
                }
            }

            if (closestNode != _hoveredNode)
            {
                _hoveredNode = closestNode;

                if (_hoveredNode != null)
                {
                    ShowNodeTooltip(_hoveredNode);
                }
                else
                {
                    NodeTooltip.IsOpen = false;
                }

                RenderTree();
            }
        }

        private void HandleNodeClick(Point screenPos)
        {
            if (_hoveredNode == null) return;

            var nodeId = _hoveredNode.Id?.ToString() ?? "";
            if (string.IsNullOrEmpty(nodeId)) return;

            if (_allocatedNodes.Contains(nodeId))
            {
                _allocatedNodes.Remove(nodeId);
            }
            else
            {
                _allocatedNodes.Add(nodeId);
            }

            UpdateStatsText();
            RenderTree();
        }

        private void ShowNodeTooltip(TreeNode node)
        {
            TooltipTitle.Text = node.Name;

            // 스탯 텍스트 조합
            var stats = string.Join("\n", node.Stats.Select(s => s.Replace("\\n", "\n")));
            TooltipStats.Text = stats;

            // 플레이버 텍스트 (키스톤만)
            if (node.Type == NodeType.Keystone && node.FlavourText?.Count > 0)
            {
                TooltipFlavour.Text = string.Join("\n", node.FlavourText);
                TooltipFlavour.Visibility = Visibility.Visible;
            }
            else
            {
                TooltipFlavour.Visibility = Visibility.Collapsed;
            }

            NodeTooltip.IsOpen = true;
        }

        #endregion

        #region Controls

        private void ClassComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ClassComboBox.SelectedItem is ComboBoxItem selected)
            {
                var className = selected.Content?.ToString() ?? "Marauder";
                _selectedClass = className;

                if (_isLoaded)
                {
                    CenterOnClass(className);
                    RenderTree();
                }
            }
        }

        private void CenterOnClass(string className)
        {
            if (_treeData == null) return;

            if (_treeData.ClassStarts.TryGetValue(className, out var nodeId))
            {
                if (_treeData.Nodes.TryGetValue(nodeId, out var node))
                {
                    _transform.CenterOn(node.X, node.Y);
                    _transform.ZoomLevel = 5; // 적당한 줌 레벨로 설정
                }
            }
        }

        private void ZoomInButton_Click(object sender, RoutedEventArgs e)
        {
            _transform.ZoomAtCenter(1);
            RenderTree();
        }

        private void ZoomOutButton_Click(object sender, RoutedEventArgs e)
        {
            _transform.ZoomAtCenter(-1);
            RenderTree();
        }

        private void ResetViewButton_Click(object sender, RoutedEventArgs e)
        {
            if (_treeData != null)
            {
                _transform.FitBounds(_treeData.Bounds);
                RenderTree();
            }
        }

        private void UserControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            _transform.ViewportWidth = e.NewSize.Width;
            _transform.ViewportHeight = e.NewSize.Height;

            if (_isLoaded)
            {
                RenderTree();
            }
        }

        #endregion

        #region Public API

        private PassiveTreeUrlCodec? _urlCodec;
        private PathOptimizer? _pathOptimizer;
        private int _currentClassId = 1;  // Marauder
        private int _currentAscendancyId = 0;

        /// <summary>
        /// 외부에서 할당된 노드 설정
        /// </summary>
        public void SetAllocatedNodes(IEnumerable<string> nodeIds)
        {
            _allocatedNodes = new HashSet<string>(nodeIds);
            UpdateStatsText();

            if (_isLoaded)
            {
                RenderTree();
            }
        }

        /// <summary>
        /// 현재 트리 상태를 URL로 인코딩
        /// </summary>
        public string ExportToUrl(string? prefix = null)
        {
            _urlCodec ??= new PassiveTreeUrlCodec();

            // 문자열 노드 ID를 정수로 변환
            var nodeIds = _allocatedNodes
                .Select(id => int.TryParse(id, out int num) ? num : 0)
                .Where(id => id > 0)
                .ToList();

            return _urlCodec.Encode(_currentClassId, _currentAscendancyId, nodeIds, prefix);
        }

        /// <summary>
        /// URL에서 트리 상태 불러오기
        /// </summary>
        public bool ImportFromUrl(string url)
        {
            _urlCodec ??= new PassiveTreeUrlCodec();

            var result = _urlCodec.Decode(url);
            if (!result.Success)
            {
                Debug.WriteLine($"[PassiveTreeViewer] URL decode failed: {result.ErrorMessage}");
                return false;
            }

            // 클래스 업데이트
            _currentClassId = result.ClassId;
            _currentAscendancyId = result.AscendancyId;

            // 클래스 이름으로 변환하고 콤보박스 업데이트
            var className = PassiveTreeUrlCodec.GetClassName(_currentClassId);
            _selectedClass = className;
            foreach (ComboBoxItem item in ClassComboBox.Items)
            {
                if (item.Content?.ToString() == className)
                {
                    ClassComboBox.SelectedItem = item;
                    break;
                }
            }

            // 노드 할당
            _allocatedNodes = new HashSet<string>(
                result.NodeIds.Select(id => id.ToString())
            );

            UpdateStatsText();

            if (_isLoaded)
            {
                CenterOnClass(_selectedClass);
                RenderTree();
            }

            return true;
        }

        /// <summary>
        /// 목표 노드들까지 최적 경로 계산
        /// </summary>
        public List<string> CalculateOptimalPath(IEnumerable<string> targetNodeIds)
        {
            if (_treeData == null) return new List<string>();

            _pathOptimizer ??= new PathOptimizer(_treeData);

            // 시작 노드 찾기
            var startNodeId = _pathOptimizer.GetClassStartNode(_currentClassId);
            if (startNodeId == null) return new List<string>();

            // 최적 경로 계산
            var optimalNodes = _pathOptimizer.FindOptimalPathToTargets(
                startNodeId,
                targetNodeIds,
                _allocatedNodes
            );

            return optimalNodes.ToList();
        }

        /// <summary>
        /// 목표 노드들까지 최적 경로로 자동 할당
        /// </summary>
        public int AllocateOptimalPath(IEnumerable<string> targetNodeIds)
        {
            var optimalNodes = CalculateOptimalPath(targetNodeIds);
            if (optimalNodes.Count == 0) return 0;

            int newlyAllocated = 0;
            foreach (var nodeId in optimalNodes)
            {
                if (!_allocatedNodes.Contains(nodeId))
                {
                    _allocatedNodes.Add(nodeId);
                    newlyAllocated++;
                }
            }

            UpdateStatsText();
            if (_isLoaded)
            {
                RenderTree();
            }

            return newlyAllocated;
        }

        /// <summary>
        /// 현재 할당된 노드 ID 목록 반환
        /// </summary>
        public IReadOnlyCollection<string> GetAllocatedNodes()
        {
            return _allocatedNodes;
        }

        /// <summary>
        /// 할당된 포인트 수 반환
        /// </summary>
        public int GetAllocatedPointCount()
        {
            if (_treeData == null) return 0;

            _pathOptimizer ??= new PathOptimizer(_treeData);
            var startNodeId = _pathOptimizer.GetClassStartNode(_currentClassId);
            if (startNodeId == null) return _allocatedNodes.Count;

            return _pathOptimizer.CalculatePointsUsed(_allocatedNodes, startNodeId);
        }

        /// <summary>
        /// 모든 할당 초기화
        /// </summary>
        public void ClearAllAllocations()
        {
            _allocatedNodes.Clear();
            UpdateStatsText();

            if (_isLoaded)
            {
                RenderTree();
            }
        }

        /// <summary>
        /// 현재 클래스 ID 설정
        /// </summary>
        public void SetClass(int classId, int ascendancyId = 0)
        {
            _currentClassId = classId;
            _currentAscendancyId = ascendancyId;

            var className = PassiveTreeUrlCodec.GetClassName(classId);
            _selectedClass = className;

            foreach (ComboBoxItem item in ClassComboBox.Items)
            {
                if (item.Content?.ToString() == className)
                {
                    ClassComboBox.SelectedItem = item;
                    break;
                }
            }

            if (_isLoaded)
            {
                CenterOnClass(_selectedClass);
                RenderTree();
            }
        }

        /// <summary>
        /// 특정 노드 목록 하이라이트
        /// </summary>
        public void HighlightNodes(IEnumerable<string> nodeIds)
        {
            // TODO: 하이라이트 구현
        }

        /// <summary>
        /// 특정 노드로 뷰 이동
        /// </summary>
        public void FocusOnNode(string nodeId)
        {
            if (_treeData == null) return;

            if (_treeData.Nodes.TryGetValue(nodeId, out var node))
            {
                _transform.CenterOn(node.X, node.Y);
                _transform.ZoomLevel = 7;
                RenderTree();
            }
        }

        /// <summary>
        /// 아키타입에 맞는 트리 로드
        /// </summary>
        public void LoadTreeForArchetype(string archetype, string className,
            List<string>? allocatedNodes = null)
        {
            _selectedClass = className;

            // 클래스 콤보박스 업데이트
            foreach (ComboBoxItem item in ClassComboBox.Items)
            {
                if (item.Content?.ToString() == className)
                {
                    ClassComboBox.SelectedItem = item;
                    break;
                }
            }

            if (allocatedNodes != null)
            {
                SetAllocatedNodes(allocatedNodes);
            }

            if (_isLoaded)
            {
                CenterOnClass(className);
                RenderTree();
            }
        }

        #endregion
    }
}
