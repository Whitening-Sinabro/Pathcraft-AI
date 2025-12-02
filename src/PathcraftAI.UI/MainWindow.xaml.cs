using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Newtonsoft.Json.Linq;
using PathcraftAI.Overlay;

namespace PathcraftAI.UI
{
    public partial class MainWindow : Window
    {
        // Win32 API for sending keys to POE
        [DllImport("user32.dll")]
        private static extern IntPtr FindWindow(string? lpClassName, string lpWindowName);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

        private const byte VK_RETURN = 0x0D;
        private const byte VK_CONTROL = 0x11;
        private const byte VK_C = 0x43;
        private const byte VK_V = 0x56;
        private const uint KEYEVENTF_KEYUP = 0x0002;

        private readonly string _pythonPath;
        private readonly string _recommendationScriptPath;
        private readonly string _oauthScriptPath;
        private readonly string _compareBuildScriptPath;
        private readonly string _upgradePathScriptPath;
        private readonly string _upgradePathTradeScriptPath;
        private readonly string _passiveTreeScriptPath;
        private readonly string _filterGeneratorScriptPath;
        private readonly string _tokenFilePath;
        private string? _currentPOBXmlPath = null;  // 필터 생성용 POB XML 경로
        private bool _isLoading = false;
        private string _currentLeague = "Keepers";
        private string _currentPhase = "Mid-Season";
        private JObject? _poeAccountData = null;
        private JObject? _currentUserBuild = null;  // 현재 로드된 사용자 빌드 데이터
        private bool _isPOEConnected = false;
        private string? _currentPOBUrl = null;
        private int _currentBudget = 100; // Default budget in chaos orbs
        private GlobalHotkey? _hideoutHotkey;
        private GlobalHotkey? _priceCheckHotkey;
        private GlobalHotkey? _thankYouHotkey;
        private PathcraftAI.Overlay.PriceOverlayWindow? _priceOverlay;
        private string? _currentCharacterName = null;
        private bool _isHardcoreMode = false;
        private string _currentClassFilter = "All";
        private string _currentSortOrder = "views";
        private int? _currentBudgetFilter = 100;
        private readonly string _debugLogPath;

        /// <summary>
        /// 디버그 로그를 파일에 기록
        /// </summary>
        private void LogDebug(string message)
        {
            try
            {
                var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                var logLine = $"[{timestamp}] {message}\n";
                Debug.WriteLine(message);
                File.AppendAllText(_debugLogPath, logLine);
            }
            catch { }
        }

        public MainWindow()
        {
            InitializeComponent();

            // F5 단축키 등록 (하이드아웃 이동)
            Loaded += (s, e) => RegisterHotkeys();
            Closed += (s, e) => UnregisterHotkeys();
            Closing += MainWindow_Closing;

            // Python 경로 설정 (AppSettings에서 자동 감지)
            var baseDir = AppDomain.CurrentDomain.BaseDirectory;
            var projectRoot = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", ".."));
            var parserDir = Path.Combine(projectRoot, "src", "PathcraftAI.Parser");

            // AppSettings에서 Python 경로 가져오기 (자동 감지 포함)
            var settings = AppSettings.Load();
            _pythonPath = settings.GetResolvedPythonPath(parserDir);

            _recommendationScriptPath = Path.Combine(parserDir, "auto_recommendation_engine.py");
            _oauthScriptPath = Path.Combine(parserDir, "test_oauth.py");
            _compareBuildScriptPath = Path.Combine(parserDir, "compare_build.py");
            _upgradePathScriptPath = Path.Combine(parserDir, "upgrade_path.py");
            _upgradePathTradeScriptPath = Path.Combine(parserDir, "upgrade_path_trade.py");
            _passiveTreeScriptPath = Path.Combine(parserDir, "passive_tree_analyzer.py");
            _filterGeneratorScriptPath = Path.Combine(parserDir, "filter_generator_cli.py");
            _tokenFilePath = Path.Combine(parserDir, "poe_token.json");

            // 디버그 로그 경로 설정
            _debugLogPath = Path.Combine(baseDir, "pathcraft_price_debug.log");

            // 경로 확인 및 디버깅
            var logPath = Path.Combine(baseDir, "pathcraft_debug.log");
            try
            {
                File.WriteAllText(logPath, $"[PATH DEBUG] BaseDirectory: {baseDir}\n" +
                    $"[PATH DEBUG] ProjectRoot: {projectRoot}\n" +
                    $"[PATH DEBUG] ParserDir: {parserDir}\n" +
                    $"[PATH DEBUG] PythonPath: {_pythonPath}\n" +
                    $"[PATH DEBUG] Python exists: {File.Exists(_pythonPath)}\n" +
                    $"[PATH DEBUG] RecommendationScript exists: {File.Exists(_recommendationScriptPath)}\n");
            }
            catch { }

            Debug.WriteLine($"[PATH DEBUG] BaseDirectory: {baseDir}");
            Debug.WriteLine($"[PATH DEBUG] ProjectRoot: {projectRoot}");
            Debug.WriteLine($"[PATH DEBUG] ParserDir: {parserDir}");
            Debug.WriteLine($"[PATH DEBUG] PythonPath: {_pythonPath}");
            Debug.WriteLine($"[PATH DEBUG] Python exists: {File.Exists(_pythonPath)}");

            if (!File.Exists(_pythonPath))
            {
                PlaceholderPanel.Visibility = Visibility.Visible;
                PlaceholderText.Text = $"⚠️ Python not found\n\n{_pythonPath}\n\nPlease check virtual environment setup.\n\nSee pathcraft_debug.log for details.";
            }

            if (!File.Exists(_recommendationScriptPath))
            {
                PlaceholderPanel.Visibility = Visibility.Visible;
                PlaceholderText.Text = $"⚠️ Script not found\n\n{_recommendationScriptPath}\n\nSee pathcraft_debug.log for details.";
            }

            // 저장된 토큰 확인
            CheckPOEConnection();

            // 앱 시작 시 자동으로 추천 로드
            _ = LoadRecommendations();
        }

        private async void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            await LoadRecommendations();
        }

        private async Task LoadRecommendations()
        {
            if (_isLoading) return;

            try
            {
                _isLoading = true;
                RefreshButton.IsEnabled = false;
                RefreshButton.Content = "Loading...";
                PlaceholderPanel.Visibility = Visibility.Collapsed;
                ResultsPanel.Children.Clear();

                // Loading indicator
                var loadingText = new TextBlock
                {
                    Text = "Loading build recommendations...",
                    FontSize = 14,
                    Foreground = new SolidColorBrush(Color.FromRgb(175, 96, 37)),
                    HorizontalAlignment = HorizontalAlignment.Center,
                    Margin = new Thickness(0, 100, 0, 0)
                };
                ResultsPanel.Children.Add(loadingText);

                // Python 프로세스 실행
                var result = await System.Threading.Tasks.Task.Run(() => ExecuteRecommendationEngine());

                // 결과 표시
                ResultsPanel.Children.Clear();
                DisplayRecommendations(result);
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "추천 빌드를 불러오는 중 오류가 발생했습니다.");
                PlaceholderPanel.Visibility = Visibility.Visible;
            }
            finally
            {
                _isLoading = false;
                RefreshButton.IsEnabled = true;
                RefreshButton.Content = "Refresh Recommendations";
            }
        }

        private string ExecuteRecommendationEngine()
        {
            var parserDir = Path.GetDirectoryName(_recommendationScriptPath)!;

            // 필터 파라미터 구성
            var filterArgs = new List<string>
            {
                $"\"{_recommendationScriptPath}\"",
                "--json-output",
                "--include-user-build-analysis"
            };

            // 클래스 필터
            if (_currentClassFilter != "All")
            {
                filterArgs.Add($"--class \"{_currentClassFilter}\"");
            }

            // 정렬 필터
            filterArgs.Add($"--sort {_currentSortOrder}");

            // 예산 필터
            if (_currentBudgetFilter.HasValue)
            {
                filterArgs.Add($"--budget {_currentBudgetFilter.Value}");
            }

            // 하드코어 모드
            if (_isHardcoreMode)
            {
                filterArgs.Add("--hardcore");
            }

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = string.Join(" ", filterArgs),
                WorkingDirectory = parserDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                StandardErrorEncoding = System.Text.Encoding.UTF8
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";
            psi.Environment["PYTHONIOENCODING"] = "utf-8";

            // API 키 환경 변수로 전달 (설정에서 가져오기)
            var settings = AppSettings.Load();
            var youtubeApiKey = settings.GetApiKey("youtube") ?? "";
            if (!string.IsNullOrEmpty(youtubeApiKey))
            {
                psi.Environment["YOUTUBE_API_KEY"] = youtubeApiKey;
            }

            Debug.WriteLine($"[EXEC] Running: {_pythonPath}");
            Debug.WriteLine($"[EXEC] Args: {psi.Arguments}");
            Debug.WriteLine($"[EXEC] WorkingDir: {parserDir}");

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start Python process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            Debug.WriteLine($"[EXEC] Exit code: {process.ExitCode}");
            Debug.WriteLine($"[EXEC] Output length: {output.Length}");
            if (!string.IsNullOrWhiteSpace(error))
            {
                Debug.WriteLine($"[EXEC] Stderr: {error}");
            }

            if (process.ExitCode != 0)
            {
                throw new Exception($"Recommendation engine error (exit code {process.ExitCode}):\n{error}");
            }

            return output;
        }

        private void DisplayRecommendations(string jsonOutput)
        {
            try
            {
                // JSON이 비어있는지 확인
                if (string.IsNullOrWhiteSpace(jsonOutput))
                {
                    ShowNoRecommendations();
                    return;
                }

                // JSON 부분만 추출 (첫 번째 { 부터 마지막 } 까지)
                var jsonStart = jsonOutput.IndexOf('{');
                var jsonEnd = jsonOutput.LastIndexOf('}');

                if (jsonStart == -1 || jsonEnd == -1 || jsonEnd <= jsonStart)
                {
                    ShowNoRecommendations();
                    return;
                }

                var jsonString = jsonOutput.Substring(jsonStart, jsonEnd - jsonStart + 1);

                JObject data;
                try
                {
                    data = JObject.Parse(jsonString);
                }
                catch (Newtonsoft.Json.JsonReaderException ex)
                {
                    // JSON 파싱 실패 - Python 로그가 섞였을 가능성
                    Debug.WriteLine($"JSON Parse Error: {ex.Message}");
                    Debug.WriteLine($"Python Output (first 500 chars):\n{jsonOutput.Substring(0, Math.Min(500, jsonOutput.Length))}");

                    var errorMsg = $"JSON 파싱에 실패했습니다.\n\n" +
                                  $"원인: Python 스크립트가 로그를 stdout으로 출력했을 가능성이 있습니다.\n\n" +
                                  $"해결: PYTHON_LOGGING_RULES.md 참고\n\n" +
                                  $"에러: {ex.Message}\n\n" +
                                  $"Python 출력 (처음 200자):\n{jsonOutput.Substring(0, Math.Min(200, jsonOutput.Length))}";

                    MessageBox.Show(errorMsg, "추천 데이터 파싱 오류", MessageBoxButton.OK, MessageBoxImage.Error);
                    ShowNoRecommendations();
                    return;
                }

                // 리그 정보 업데이트
                _currentLeague = data["league"]?.ToString() ?? "Keepers";
                _currentPhase = FormatLeaguePhase(data["league_phase"]?.ToString() ?? "mid");

                LeagueNameText.Text = $"Current League: {_currentLeague} ({_currentPhase})";

                // Divine 환율 및 예산 필터 동적 업데이트
                var currencyData = data["currency"] as JObject;
                UpdateDivineRateDisplay(currencyData);
                UpdateBudgetFilterOptions(currencyData);

                // 사용자 빌드 정보 표시 (personalized 모드가 아닐 때만)
                var leaguePhase = data["league_phase"]?.ToString();
                if (leaguePhase != "personalized")
                {
                    DisplayUserBuild(data["user_build"] as JObject);
                }
                // personalized 모드일 때는 기존 사용자 빌드 정보 유지

                var recommendations = data["recommendations"] as JArray;

                if (recommendations == null || recommendations.Count == 0)
                {
                    ShowNoRecommendations();
                    return;
                }

                // 각 추천 카테고리 표시
                foreach (var rec in recommendations)
                {
                    var category = rec["category"]?.ToString();
                    var title = rec["title"]?.ToString();
                    var subtitle = rec["subtitle"]?.ToString();
                    var builds = rec["builds"] as JArray;

                    if (builds == null || builds.Count == 0)
                        continue;

                    // 카테고리 헤더
                    var categoryHeader = new TextBlock
                    {
                        Text = title,
                        FontSize = 16,
                        FontWeight = FontWeights.SemiBold,
                        Margin = new Thickness(0, 16, 0, 4)
                    };
                    ResultsPanel.Children.Add(categoryHeader);

                    var categorySubtitle = new TextBlock
                    {
                        Text = subtitle,
                        FontSize = 12,
                        Foreground = new SolidColorBrush(Color.FromRgb(180, 180, 180)),
                        Margin = new Thickness(0, 0, 0, 12)
                    };
                    ResultsPanel.Children.Add(categorySubtitle);

                    // 빌드 카드들
                    foreach (var build in builds)
                    {
                        var buildCard = CreateRecommendationCard(build as JObject, category);
                        ResultsPanel.Children.Add(buildCard);
                    }
                }

                // Popular Builds 섹션 추가 (YouTube 빌드 가이드)
                DisplayPopularBuilds();
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "추천 데이터를 파싱하는 중 오류가 발생했습니다.");
                ShowNoRecommendations();
            }
        }

        private void DisplayUserBuild(JObject? userBuild)
        {
            if (userBuild == null)
            {
                // 빌드 데이터가 없으면 섹션 숨김
                BuildOverviewExpander.Visibility = Visibility.Collapsed;
                BuildComparisonExpander.Visibility = Visibility.Collapsed;
                return;
            }

            // 현재 빌드 데이터 저장 (레벨링 가이드 fallback에서 사용)
            _currentUserBuild = userBuild;

            // 빌드 데이터가 있으면 섹션 표시
            BuildOverviewExpander.Visibility = Visibility.Visible;

            // 캐릭터 정보
            var characterName = userBuild["character_name"]?.ToString() ?? "-";
            var characterClass = userBuild["class"]?.ToString() ?? "-";
            var level = userBuild["level"]?.ToString() ?? "-";
            BuildCharacterName.Text = $"Character: {characterName} (Lv{level} {characterClass})";

            // 빌드 타입
            var buildType = userBuild["build_type"]?.ToString() ?? "-";
            BuildType.Text = $"Build Type: {buildType}";

            // 메인 스킬
            var mainSkill = userBuild["main_skill"]?.ToString();
            BuildMainSkill.Text = $"Main Skill: {mainSkill ?? "Unknown"}";

            // 유니크 아이템 개수
            var uniqueItems = userBuild["unique_items"] as JArray;
            int uniqueCount = uniqueItems?.Count ?? 0;
            BuildUniqueCount.Text = $"Unique Items: {uniqueCount}";

            // 총 가치
            var totalValue = userBuild["total_unique_value"]?.ToObject<double>() ?? 0.0;
            BuildTotalValue.Text = $"Estimated Value: ~{totalValue:F0}c";

            // 업그레이드 제안
            var upgradeSuggestions = userBuild["upgrade_suggestions"] as JArray;
            if (upgradeSuggestions != null && upgradeSuggestions.Count > 0)
            {
                UpgradePathExpander.IsExpanded = true;

                var upgradeList = new List<UpgradeSuggestion>();
                foreach (var suggestion in upgradeSuggestions)
                {
                    upgradeList.Add(new UpgradeSuggestion
                    {
                        ItemName = suggestion["item_name"]?.ToString() ?? "",
                        ChaosValue = suggestion["chaos_value"]?.ToObject<double>() ?? 0.0,
                        Reason = suggestion["reason"]?.ToString() ?? "",
                        TradeUrl = suggestion["trade_url"]?.ToString() ?? ""
                    });
                }

                UpgradesList.ItemsSource = upgradeList;
            }
            else
            {
                UpgradePathExpander.IsExpanded = false;
            }

            // POB 링크가 있으면 빌드 비교 로드
            var pobUrl = userBuild["pob_url"]?.ToString();
            if (!string.IsNullOrEmpty(pobUrl) && characterName != "-" && _isPOEConnected)
            {
                _ = LoadBuildComparison(pobUrl, characterName);
            }
            else
            {
                BuildComparisonExpander.Visibility = Visibility.Collapsed;
            }
        }

        private string FormatLeaguePhase(string phase)
        {
            return phase switch
            {
                "pre_season" => "Pre-Season (Starting Soon)",
                "early" => "Early League (Week 1)",
                "mid" => "Mid-Season",
                "late" => "Late League (1+ Month)",
                _ => "Active"
            };
        }

        private Border CreateRecommendationCard(JObject? build, string? category)
        {
            if (build == null)
                return new Border();

            var card = new Border
            {
                Width = 320,
                Background = new SolidColorBrush(Color.FromRgb(38, 38, 56)),  // #262638
                BorderBrush = new SolidColorBrush(Color.FromRgb(69, 71, 90)),  // #45475A
                BorderThickness = new Thickness(2),
                CornerRadius = new CornerRadius(8),
                Padding = new Thickness(0),
                Margin = new Thickness(0, 0, 8, 12),
                Cursor = Cursors.Hand,
                VerticalAlignment = VerticalAlignment.Top
            };

            // Mouse hover effects
            card.MouseEnter += (s, e) =>
            {
                card.Background = new SolidColorBrush(Color.FromRgb(49, 50, 68));  // #313244
                card.BorderBrush = new SolidColorBrush(Color.FromRgb(137, 180, 250));  // #89B4FA
            };

            card.MouseLeave += (s, e) =>
            {
                card.Background = new SolidColorBrush(Color.FromRgb(38, 38, 56));  // #262638
                card.BorderBrush = new SolidColorBrush(Color.FromRgb(69, 71, 90));  // #45475A
            };

            var mainGrid = new Grid();
            mainGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(160) }); // Thumbnail
            mainGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) }); // Content

            // YouTube 썸네일 영역
            var thumbnail = build["thumbnail"]?.ToString();
            if (!string.IsNullOrEmpty(thumbnail) || build["url"] != null)
            {
                var thumbnailBorder = new Border
                {
                    Width = 160,
                    Height = 90,
                    Background = new SolidColorBrush(Color.FromRgb(24, 24, 37)),  // #181825
                    CornerRadius = new CornerRadius(8, 0, 0, 8),
                    ClipToBounds = true
                };

                if (!string.IsNullOrEmpty(thumbnail))
                {
                    // 실제 YouTube 썸네일 이미지 표시
                    var image = new System.Windows.Controls.Image
                    {
                        Stretch = Stretch.UniformToFill,
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center
                    };

                    var bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(thumbnail, UriKind.Absolute);
                    bitmap.CacheOption = BitmapCacheOption.OnLoad;
                    bitmap.EndInit();
                    image.Source = bitmap;

                    thumbnailBorder.Child = image;
                }
                else
                {
                    // 썸네일 URL이 없으면 이모지 표시
                    var thumbnailText = new TextBlock
                    {
                        Text = "🎬",
                        FontSize = 32,
                        Foreground = new SolidColorBrush(Color.FromRgb(137, 180, 250)),  // #89B4FA
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center
                    };
                    thumbnailBorder.Child = thumbnailText;
                }

                Grid.SetColumn(thumbnailBorder, 0);
                mainGrid.Children.Add(thumbnailBorder);
            }

            // Content area
            var contentStack = new StackPanel
            {
                Margin = new Thickness(12)
            };

            Grid.SetColumn(contentStack, thumbnail != null || build["url"] != null ? 1 : 0);
            if (thumbnail == null && build["url"] == null)
            {
                Grid.SetColumnSpan(contentStack, 2);
            }

            // 빌드 이름
            string buildName = ExtractBuildName(build, category);
            var title = new TextBlock
            {
                Text = buildName,
                FontSize = 15,
                FontWeight = FontWeights.Bold,
                TextWrapping = TextWrapping.Wrap,
                Margin = new Thickness(0, 0, 0, 6),
                Foreground = Brushes.White
            };
            contentStack.Children.Add(title);

            // Build keyword/category tag
            var buildKeyword = build["build_keyword"]?.ToString();
            if (!string.IsNullOrEmpty(buildKeyword))
            {
                var keywordBorder = new Border
                {
                    Background = new SolidColorBrush(Color.FromArgb(100, 175, 96, 37)),
                    CornerRadius = new CornerRadius(4),
                    Padding = new Thickness(6, 2, 6, 2),
                    Margin = new Thickness(0, 0, 0, 6),
                    HorizontalAlignment = HorizontalAlignment.Left
                };

                var keywordText = new TextBlock
                {
                    Text = buildKeyword,
                    FontSize = 10,
                    FontWeight = FontWeights.SemiBold,
                    Foreground = new SolidColorBrush(Color.FromRgb(249, 226, 175))  // #F9E2AF
                };

                keywordBorder.Child = keywordText;
                contentStack.Children.Add(keywordBorder);
            }

            // Build metadata
            var metadata = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 0, 8) };

            // Channel name
            var channel = build["channel_title"]?.ToString() ?? build["channel"]?.ToString();
            if (!string.IsNullOrEmpty(channel))
            {
                metadata.Children.Add(new TextBlock
                {
                    Text = $"📺 {channel}",
                    FontSize = 11,
                    Foreground = new SolidColorBrush(Color.FromRgb(186, 194, 222)),  // #BAC2DE
                    Margin = new Thickness(0, 0, 12, 0)
                });
            }

            // View count
            var views = build["view_count"]?.ToObject<int>() ?? build["views"]?.ToObject<int>() ?? 0;
            if (views > 0)
            {
                metadata.Children.Add(new TextBlock
                {
                    Text = $"👁 {views:N0}",
                    FontSize = 11,
                    Foreground = new SolidColorBrush(Color.FromRgb(186, 194, 222)),  // #BAC2DE
                    Margin = new Thickness(0, 0, 12, 0)
                });
            }

            // Build Info
            var infoText = BuildInfoText(build, category);
            if (!string.IsNullOrEmpty(infoText))
            {
                metadata.Children.Add(new TextBlock
                {
                    Text = infoText,
                    FontSize = 11,
                    Foreground = new SolidColorBrush(Color.FromRgb(186, 194, 222))  // #BAC2DE
                });
            }

            if (metadata.Children.Count > 0)
            {
                contentStack.Children.Add(metadata);
            }

            // Action buttons
            var buttonStack = new StackPanel { Orientation = Orientation.Horizontal };

            // POB links
            var pobLinks = build["pob_links"] as JArray;
            if (pobLinks != null && pobLinks.Count > 0)
            {
                var pobButton = new Button
                {
                    Content = "Open POB",
                    FontSize = 11,
                    Padding = new Thickness(10, 4, 10, 4),
                    Margin = new Thickness(0, 0, 8, 0),
                    Background = new SolidColorBrush(Color.FromRgb(166, 227, 161)),  // #A6E3A1
                    Foreground = new SolidColorBrush(Color.FromRgb(30, 30, 46)),  // Dark text
                    BorderThickness = new Thickness(0),
                    Cursor = Cursors.Hand,
                    Tag = pobLinks[0].ToString()
                };

                pobButton.Click += (s, e) =>
                {
                    var url = (s as Button)?.Tag?.ToString();
                    if (!string.IsNullOrEmpty(url))
                    {
                        try
                        {
                            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                            {
                                FileName = url,
                                UseShellExecute = true
                            });
                        }
                        catch (Exception ex)
                        {
                            ShowNotification($"Failed to open POB link: {ex.Message}", isError: true);
                        }
                    }
                };

                buttonStack.Children.Add(pobButton);

                // AI Analyze button (only if POB link exists)
                var aiAnalyzeButton = new Button
                {
                    Content = "🤖 Analyze",
                    FontSize = 11,
                    Padding = new Thickness(10, 4, 10, 4),
                    Margin = new Thickness(0, 0, 8, 0),
                    Background = new SolidColorBrush(Color.FromRgb(203, 166, 247)),  // #CBA6F7
                    Foreground = new SolidColorBrush(Color.FromRgb(30, 30, 46)),  // Dark text
                    BorderThickness = new Thickness(0),
                    Cursor = Cursors.Hand,
                    Tag = pobLinks[0].ToString()
                };

                aiAnalyzeButton.Click += (s, e) =>
                {
                    var pobUrl = (s as Button)?.Tag?.ToString();
                    if (!string.IsNullOrEmpty(pobUrl))
                    {
                        // Set the POB URL and trigger AI analysis
                        _currentPOBUrl = pobUrl;
                        AIAnalysis_Click(s, e);
                    }
                };

                buttonStack.Children.Add(aiAnalyzeButton);
            }

            // YouTube video link
            var videoUrl = build["url"]?.ToString();
            if (!string.IsNullOrEmpty(videoUrl))
            {
                var videoButton = new Button
                {
                    Content = "Watch Video",
                    FontSize = 11,
                    Padding = new Thickness(10, 4, 10, 4),
                    Margin = new Thickness(0, 0, 8, 0),
                    Background = new SolidColorBrush(Color.FromRgb(243, 139, 168)),  // #F38BA8
                    Foreground = new SolidColorBrush(Color.FromRgb(30, 30, 46)),  // Dark text
                    BorderThickness = new Thickness(0),
                    Cursor = Cursors.Hand,
                    Tag = videoUrl
                };

                videoButton.Click += (s, e) =>
                {
                    var url = (s as Button)?.Tag?.ToString();
                    if (!string.IsNullOrEmpty(url))
                    {
                        try
                        {
                            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                            {
                                FileName = url,
                                UseShellExecute = true
                            });
                        }
                        catch (Exception ex)
                        {
                            ShowNotification($"Failed to open video: {ex.Message}", isError: true);
                        }
                    }
                };

                buttonStack.Children.Add(videoButton);
            }

            if (buttonStack.Children.Count > 0)
            {
                contentStack.Children.Add(buttonStack);
            }

            mainGrid.Children.Add(contentStack);
            card.Child = mainGrid;

            return card;
        }

        private string ExtractBuildName(JObject build, string? category)
        {
            // YouTube 빌드
            if (build["title"] != null)
                return build["title"]?.ToString() ?? "Unknown Build";

            // Ladder/Streamer 빌드
            var charName = build["character_name"]?.ToString();
            var className = build["class"]?.ToString();
            var ascendancy = build["ascendancy_class"]?.ToString();

            if (!string.IsNullOrEmpty(charName))
            {
                if (!string.IsNullOrEmpty(ascendancy))
                    return $"{charName} ({ascendancy})";
                else if (!string.IsNullOrEmpty(className))
                    return $"{charName} ({className})";
                else
                    return charName;
            }

            // poe.ninja 빌드
            if (!string.IsNullOrEmpty(className) && !string.IsNullOrEmpty(ascendancy))
                return $"{ascendancy} {className}";

            return "Unknown Build";
        }

        private string BuildInfoText(JObject build, string? category)
        {
            var infoParts = new List<string>();

            // Streamer 빌드
            if (build["streamer_name"] != null)
            {
                infoParts.Add($"Streamer: {build["streamer_name"]}");
            }

            // Ladder rank
            if (build["rank"] != null)
            {
                infoParts.Add($"Rank #{build["rank"]}");
            }

            // Level
            if (build["level"] != null)
            {
                infoParts.Add($"Lvl {build["level"]}");
            }

            // Popularity (poe.ninja)
            if (build["count"] != null)
            {
                infoParts.Add($"{build["count"]} players");
            }

            // YouTube stats
            if (build["channel"] != null)
            {
                infoParts.Add($"Channel: {build["channel"]}");
            }

            if (build["views"] != null)
            {
                var views = build["views"]?.Value<int>() ?? 0;
                infoParts.Add($"{views:N0} views");
            }

            return string.Join(" | ", infoParts);
        }

        private void DisplayPopularBuilds()
        {
            try
            {
                // popular_builds JSON 파일 로드
                var parserDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "PathcraftAI.Parser");
                var buildDataPath = Path.Combine(parserDir, "build_data", $"popular_builds_{_currentLeague}.json");

                // Standard 리그로 폴백
                if (!File.Exists(buildDataPath))
                {
                    buildDataPath = Path.Combine(parserDir, "build_data", "popular_builds_Standard.json");
                }

                if (!File.Exists(buildDataPath))
                {
                    return; // 파일이 없으면 섹션 표시 안 함
                }

                var jsonContent = File.ReadAllText(buildDataPath, System.Text.Encoding.UTF8);
                var popularData = JObject.Parse(jsonContent);

                var youtubeBuilds = popularData["youtube_builds"] as JArray;

                if (youtubeBuilds == null || youtubeBuilds.Count == 0)
                {
                    return; // 빌드가 없으면 섹션 표시 안 함
                }

                // 섹션 헤더
                var sectionHeader = new TextBlock
                {
                    Text = "🎬 Popular Build Guides from YouTube",
                    FontSize = 18,
                    FontWeight = FontWeights.Bold,
                    Foreground = new SolidColorBrush(Color.FromRgb(200, 120, 50)),
                    Margin = new Thickness(0, 24, 0, 4)
                };
                ResultsPanel.Children.Add(sectionHeader);

                var sectionSubtitle = new TextBlock
                {
                    Text = $"Based on POE.Ninja data and YouTube community guides (League: {popularData["league_version"]})",
                    FontSize = 12,
                    Foreground = new SolidColorBrush(Color.FromRgb(180, 180, 180)),
                    Margin = new Thickness(0, 0, 0, 12)
                };
                ResultsPanel.Children.Add(sectionSubtitle);

                // 빌드 키워드별로 그룹화
                var buildGroups = youtubeBuilds
                    .Cast<JObject>()
                    .GroupBy(b => b["build_keyword"]?.ToString() ?? "Other")
                    .Take(5); // 상위 5개 키워드만

                foreach (var group in buildGroups)
                {
                    var keyword = group.Key;

                    // 키워드 헤더
                    var keywordHeader = new TextBlock
                    {
                        Text = $"🔸 {keyword} Builds",
                        FontSize = 14,
                        FontWeight = FontWeights.SemiBold,
                        Foreground = new SolidColorBrush(Color.FromRgb(255, 200, 100)),
                        Margin = new Thickness(0, 12, 0, 8)
                    };
                    ResultsPanel.Children.Add(keywordHeader);

                    // 각 키워드의 빌드 카드 (최대 3개)
                    foreach (var build in group.Take(3))
                    {
                        // channel_title 또는 channel 필드를 channel_title로 통일
                        if (build["channel"] != null && build["channel_title"] == null)
                        {
                            build["channel_title"] = build["channel"];
                        }

                        var buildCard = CreateRecommendationCard(build, "youtube");
                        ResultsPanel.Children.Add(buildCard);
                    }
                }
            }
            catch (Exception ex)
            {
                // 에러가 발생해도 전체 UI를 망가뜨리지 않음
                Debug.WriteLine($"Failed to load popular builds: {ex.Message}");
            }
        }

        private void ShowNoRecommendations()
        {
            var noResults = new TextBlock
            {
                Text = "No recommendations available.\nPlease check your internet connection or try refreshing.",
                FontSize = 14,
                Foreground = new SolidColorBrush(Color.FromRgb(180, 180, 180)),
                TextWrapping = TextWrapping.Wrap,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 100, 0, 0)
            };
            ResultsPanel.Children.Add(noResults);
        }

        private void OpenTrade_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var tradeWindow = new TradeWindow(_currentLeague);
                tradeWindow.Show();
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "POE Trade 창을 여는 중 오류가 발생했습니다.");
            }
        }

        private void Bookmarks_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var bookmarksWindow = new BookmarksWindow();
                bookmarksWindow.Owner = this;

                if (bookmarksWindow.ShowDialog() == true && bookmarksWindow.SelectedBookmark != null)
                {
                    var bookmark = bookmarksWindow.SelectedBookmark;

                    // Load POB from bookmark
                    if (!string.IsNullOrEmpty(bookmark.PobUrl))
                    {
                        POBInputBox.Text = bookmark.PobUrl;
                    }
                    else if (!string.IsNullOrEmpty(bookmark.PobCode))
                    {
                        POBInputBox.Text = bookmark.PobCode;
                    }

                    POBInputBox.Foreground = new SolidColorBrush(Color.FromRgb(205, 214, 244));
                    ShowNotification($"Loaded bookmark: {bookmark.BuildName}");
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "북마크 창을 여는 중 오류가 발생했습니다.");
            }
        }

        private void SaveBookmark_Click(object sender, RoutedEventArgs e)
        {
            // This will be called from build cards to save a build
            if (sender is Button button && button.Tag is string pobUrl)
            {
                try
                {
                    // Simple bookmark creation - in real app would show dialog for notes/tags
                    var bookmark = new BuildBookmark
                    {
                        BuildName = "Saved Build",
                        PobUrl = pobUrl,
                        CreatedAt = DateTime.Now
                    };

                    var service = new BookmarkService();
                    service.AddBookmark(bookmark);
                    ShowNotification("Build bookmarked!");
                }
                catch (Exception ex)
                {
                    ShowFriendlyError(ex, "북마크 저장 중 오류가 발생했습니다.");
                }
            }
        }

        private void Settings_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var settingsWindow = new SettingsWindow();
                settingsWindow.Owner = this;
                if (settingsWindow.ShowDialog() == true)
                {
                    // Settings saved - reload any necessary settings
                    var settings = AppSettings.Load();
                    // Update UI with new settings if needed
                    LeagueNameText.Text = $"Current League: {settings.DefaultLeague}";
                    ShowNotification("Settings saved successfully!");
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "Settings 창을 여는 중 오류가 발생했습니다.");
            }
        }

        private void LeagueMode_Changed(object sender, RoutedEventArgs e)
        {
            // 초기화 중에는 무시
            if (HCModeButton == null) return;

            _isHardcoreMode = HCModeButton.IsChecked == true;
            var modeText = _isHardcoreMode ? "Hardcore" : "Softcore";
            ShowNotification($"Mode changed to {modeText}");

            // 추천 빌드 새로고침 (HC/SC에 따라 다른 빌드 추천)
            // TODO: LoadRecommendations()에 HC 모드 전달
        }

        private void ShowFriendlyError(Exception ex, string context = "")
        {
            string title = "알림";
            string message = ex.Message;
            MessageBoxImage icon = MessageBoxImage.Warning;

            // Rate Limit 에러 (HTTP 429)
            if (ex is System.Net.Http.HttpRequestException && (message.Contains("429") || message.Contains("Too Many Requests")))
            {
                title = "요청 제한 도달";
                message = "POE API 요청 제한에 도달했습니다.\n\n30초 후 다시 시도해주세요.";
                icon = MessageBoxImage.Information;
            }
            // Privacy 설정 에러
            else if (message.Contains("privacy", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("private", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("character tab", StringComparison.OrdinalIgnoreCase))
            {
                title = "캐릭터 비공개 설정";
                message = "캐릭터 아이템이 비공개 상태입니다.\n\n" +
                          "POE 웹사이트에서 설정 변경:\n" +
                          "1. My Account → Privacy Settings\n" +
                          "2. 'Hide characters' 옵션 체크 해제\n" +
                          "3. 저장 후 다시 시도해주세요";
                icon = MessageBoxImage.Information;
            }
            // 네트워크 에러
            else if (ex is System.Net.Http.HttpRequestException ||
                     ex is System.Net.WebException ||
                     message.Contains("network", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("connection", StringComparison.OrdinalIgnoreCase))
            {
                title = "네트워크 오류";
                message = "인터넷 연결을 확인해주세요.\n\n" +
                          "다음을 확인하세요:\n" +
                          "1. 인터넷 연결 상태\n" +
                          "2. 방화벽 설정\n" +
                          "3. POE 서버 상태 (pathofexile.com)";
                icon = MessageBoxImage.Error;
            }
            // YouTube API 키 에러
            else if (message.Contains("API key", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("YOUTUBE_API_KEY", StringComparison.OrdinalIgnoreCase))
            {
                title = "YouTube API 키 없음";
                message = "YouTube API 키가 설정되지 않았습니다.\n\n" +
                          "설정 방법:\n" +
                          "1. Google Cloud Console에서 API 키 발급\n" +
                          "2. YouTube Data API v3 활성화\n" +
                          "3. 환경 변수에 API 키 추가\n\n" +
                          "현재는 Mock 데이터로 표시됩니다.";
                icon = MessageBoxImage.Information;
            }
            // Python 프로세스 에러
            else if (message.Contains("Python", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("process", StringComparison.OrdinalIgnoreCase))
            {
                title = "Python 실행 오류";
                message = "Python 스크립트 실행에 실패했습니다.\n\n" +
                          "해결 방법:\n" +
                          "1. Virtual environment 활성화 확인\n" +
                          "2. 필요한 패키지 설치 확인\n" +
                          "3. Python 경로 확인\n\n" +
                          $"오류 내용: {ex.Message}";
                icon = MessageBoxImage.Error;
            }
            // POB 파싱 에러
            else if (message.Contains("POB", StringComparison.OrdinalIgnoreCase) ||
                     message.Contains("pastebin", StringComparison.OrdinalIgnoreCase))
            {
                title = "POB 링크 오류";
                message = "POB 링크를 불러올 수 없습니다.\n\n" +
                          "확인사항:\n" +
                          "1. 올바른 POB 링크인지 확인\n" +
                          "2. Pastebin이 접근 가능한지 확인\n" +
                          "3. POB 데이터가 유효한지 확인";
                icon = MessageBoxImage.Warning;
            }
            // 일반 에러 (컨텍스트 추가)
            else if (!string.IsNullOrEmpty(context))
            {
                title = "오류 발생";
                message = $"{context}\n\n오류 내용:\n{ex.Message}";
                icon = MessageBoxImage.Error;
            }

            MessageBox.Show(message, title, MessageBoxButton.OK, icon);
        }

        private void Donate_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Support PathcraftAI!\n\nThank you for your support!",
                "Donate", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void AIProviderCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            // API 키 상태 업데이트
            if (APIKeyStatusText == null) return;

            int selectedIndex = AIProviderCombo.SelectedIndex;

            // 각 모드에 필요한 API 키 확인
            string statusText = "";
            string statusColor = "#7F849C"; // 기본 회색

            switch (selectedIndex)
            {
                case 0: // Rule-Based
                case 1: // Upgrade Guide
                    statusText = "✅ API 키 불필요";
                    statusColor = "#A6E3A1"; // 녹색
                    break;
                case 2: // Claude
                    var claudeKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY");
                    if (!string.IsNullOrEmpty(claudeKey))
                    {
                        statusText = "✅ Claude API 연결됨";
                        statusColor = "#A6E3A1";
                    }
                    else
                    {
                        statusText = "⚠️ ANTHROPIC_API_KEY 필요";
                        statusColor = "#F9E2AF"; // 노란색
                    }
                    break;
                case 3: // OpenAI
                    var openaiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
                    if (!string.IsNullOrEmpty(openaiKey))
                    {
                        statusText = "✅ OpenAI API 연결됨";
                        statusColor = "#A6E3A1";
                    }
                    else
                    {
                        statusText = "⚠️ OPENAI_API_KEY 필요";
                        statusColor = "#F9E2AF";
                    }
                    break;
                case 4: // Gemini
                    var geminiKey = Environment.GetEnvironmentVariable("GOOGLE_API_KEY");
                    if (!string.IsNullOrEmpty(geminiKey))
                    {
                        statusText = "✅ Gemini API 연결됨";
                        statusColor = "#A6E3A1";
                    }
                    else
                    {
                        statusText = "⚠️ GOOGLE_API_KEY 필요 (무료 제공)";
                        statusColor = "#F9E2AF";
                    }
                    break;
                case 5: // Both
                    var bothClaude = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY");
                    var bothOpenai = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
                    if (!string.IsNullOrEmpty(bothClaude) && !string.IsNullOrEmpty(bothOpenai))
                    {
                        statusText = "✅ 두 API 모두 연결됨";
                        statusColor = "#A6E3A1";
                    }
                    else if (!string.IsNullOrEmpty(bothClaude) || !string.IsNullOrEmpty(bothOpenai))
                    {
                        statusText = "⚠️ 일부 API 키 누락";
                        statusColor = "#F9E2AF";
                    }
                    else
                    {
                        statusText = "❌ 두 API 키 모두 필요";
                        statusColor = "#F38BA8"; // 빨간색
                    }
                    break;
            }

            APIKeyStatusText.Text = statusText;
            APIKeyStatusText.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString(statusColor));
        }

        private async void AIAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_currentPOBUrl))
            {
                MessageBox.Show("POB 링크를 먼저 입력해주세요.\n\n'Refresh Recommendations'를 먼저 실행하거나, POB 링크가 있는 빌드를 선택해주세요.",
                    "POB 링크 필요", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                AIAnalysisButton.IsEnabled = false;
                AIAnalysisButton.Content = "Analyzing...";
                AIAnalysisExpander.Visibility = Visibility.Visible;
                AIAnalysisText.Text = "🔄 AI가 빌드를 분석 중입니다. 잠시만 기다려주세요...";

                // Get selected AI provider (순서: Auto, Rule-Based, Guide, Claude, OpenAI, Gemini, Grok, Both)
                int selectedProvider = AIProviderCombo.SelectedIndex;
                string provider = selectedProvider switch
                {
                    0 => "auto",        // Auto (Best Available) - 기본값
                    1 => "rule-based",
                    2 => "guide",
                    3 => "claude",
                    4 => "openai",
                    5 => "gemini",
                    6 => "grok",
                    7 => "both",
                    _ => "auto"
                };

                System.Diagnostics.Debug.WriteLine($"[AI] Selected provider index: {selectedProvider}, mapped to: {provider}");

                // Run AI analysis via Python
                var result = await System.Threading.Tasks.Task.Run(() => ExecuteAIAnalysis(_currentPOBUrl, provider));

                System.Diagnostics.Debug.WriteLine($"[AI] Result to parse: {result?.Substring(0, Math.Min(500, result?.Length ?? 0))}");

                // Parse and display result
                JObject analysisData;
                try
                {
                    analysisData = JObject.Parse(result ?? "{}");
                }
                catch (Newtonsoft.Json.JsonReaderException jsonEx)
                {
                    // JSON 파싱 실패 시 상세 정보 표시
                    System.Diagnostics.Debug.WriteLine($"[AI] JSON Parse Error: {jsonEx.Message}");
                    System.Diagnostics.Debug.WriteLine($"[AI] Raw result: {result}");
                    AIAnalysisText.Text = $"❌ JSON 파싱 실패\n\n원본 출력:\n{result?.Substring(0, Math.Min(1000, result?.Length ?? 0))}";
                    return;
                }

                if (analysisData["error"] != null)
                {
                    AIAnalysisText.Text = $"❌ 오류: {analysisData["error"]}";
                }
                else
                {
                    DisplayAIAnalysis(analysisData);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[AI] Exception: {ex}");
                ShowFriendlyError(ex, "AI 분석 중 오류가 발생했습니다.");
                AIAnalysisText.Text = $"❌ 분석 실패: {ex.Message}";
            }
            finally
            {
                AIAnalysisButton.IsEnabled = true;
                AIAnalysisButton.Content = "🤖 AI Analysis";
            }
        }

        private string ExecuteAIAnalysis(string pobInput, string provider)
        {
            var parserDir = Path.GetDirectoryName(_recommendationScriptPath)!;
            var aiAnalyzerScript = Path.Combine(parserDir, "ai_build_analyzer.py");

            // POB URL인지 POB 코드인지 판단
            bool isUrl = pobInput.StartsWith("http://") || pobInput.StartsWith("https://");
            string arguments;

            // 설정 로드 (API 키, 예산 등에 사용)
            var settings = AppSettings.Load();

            // guide 모드일 때 예산 추가
            string budgetArg = "";
            if (provider == "guide")
            {
                var budget = settings.DefaultBudget > 0 ? settings.DefaultBudget : 1000;
                var league = !string.IsNullOrEmpty(settings.DefaultLeague) ? settings.DefaultLeague : "Keepers";
                budgetArg = $" --budget {budget} --league {league}";
            }

            if (isUrl)
            {
                arguments = $"\"{aiAnalyzerScript}\" --pob \"{pobInput}\" --provider {provider}{budgetArg} --json";
            }
            else
            {
                // POB 코드 직접 사용 (base64 인코딩됨)
                arguments = $"\"{aiAnalyzerScript}\" --pob-code \"{pobInput}\" --provider {provider}{budgetArg} --json";
            }

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = arguments,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = parserDir,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                StandardErrorEncoding = System.Text.Encoding.UTF8
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";
            psi.Environment["PYTHONIOENCODING"] = "utf-8";

            // API 키 전달 (Settings 우선, 없으면 환경 변수)
            var anthropicKey = settings.GetApiKey("claude");
            var openaiKey = settings.GetApiKey("openai");
            var geminiKey = settings.GetApiKey("gemini");
            var grokKey = settings.GetApiKey("grok");

            // 자동 감지된 API 키 정보 (디버그)
            var (bestApiKey, detectedProvider) = settings.GetBestAvailableApiKey();

            // 디버그: API 키 상태 로깅
            System.Diagnostics.Debug.WriteLine($"[AI] Provider requested: {provider}");
            System.Diagnostics.Debug.WriteLine($"[AI] Best available: {detectedProvider ?? "NONE"} (key: {(string.IsNullOrEmpty(bestApiKey) ? "MISSING" : bestApiKey.Substring(0, Math.Min(10, bestApiKey.Length)) + "...")})");
            System.Diagnostics.Debug.WriteLine($"[AI] Claude API Key: {(string.IsNullOrEmpty(anthropicKey) ? "MISSING" : "SET")}");
            System.Diagnostics.Debug.WriteLine($"[AI] OpenAI API Key: {(string.IsNullOrEmpty(openaiKey) ? "MISSING" : "SET")}");
            System.Diagnostics.Debug.WriteLine($"[AI] Gemini API Key: {(string.IsNullOrEmpty(geminiKey) ? "MISSING" : "SET")}");
            System.Diagnostics.Debug.WriteLine($"[AI] Grok API Key: {(string.IsNullOrEmpty(grokKey) ? "MISSING" : "SET")}");

            if (!string.IsNullOrEmpty(anthropicKey))
                psi.Environment["ANTHROPIC_API_KEY"] = anthropicKey;
            if (!string.IsNullOrEmpty(openaiKey))
                psi.Environment["OPENAI_API_KEY"] = openaiKey;
            if (!string.IsNullOrEmpty(geminiKey))
                psi.Environment["GOOGLE_API_KEY"] = geminiKey;
            if (!string.IsNullOrEmpty(grokKey))
                psi.Environment["XAI_API_KEY"] = grokKey;

            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start AI analysis process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                // POB URL 에러인 경우 더 자세한 메시지
                if (error.Contains("Could not fetch POB") || error.Contains("500 Server Error"))
                {
                    throw new Exception($"POB URL을 가져올 수 없습니다.\n\n가능한 원인:\n" +
                        $"1. pobb.in 서버가 일시적으로 다운됨 (Cloudflare 장애)\n" +
                        $"2. POB URL이 만료되었거나 삭제됨\n\n" +
                        $"해결 방법:\n" +
                        $"- pastebin.com POB URL 사용 (예: pastebin.com/xxxxxxxx)\n" +
                        $"- 나중에 다시 시도\n\n" +
                        $"상세 에러:\n{error}");
                }
                throw new Exception($"AI analysis failed:\n{error}");
            }

            // stdout에서 JSON 부분만 추출 (로그 메시지 무시)
            System.Diagnostics.Debug.WriteLine($"[AI] Raw output length: {output?.Length ?? 0}");
            System.Diagnostics.Debug.WriteLine($"[AI] Raw stderr: {error}");

            if (!string.IsNullOrEmpty(output))
            {
                // JSON 객체의 시작과 끝 찾기
                var jsonStart = output.IndexOf('{');
                var jsonEnd = output.LastIndexOf('}');

                if (jsonStart >= 0 && jsonEnd > jsonStart)
                {
                    var jsonStr = output.Substring(jsonStart, jsonEnd - jsonStart + 1);
                    System.Diagnostics.Debug.WriteLine($"[AI] Extracted JSON: {jsonStr.Substring(0, Math.Min(200, jsonStr.Length))}...");
                    return jsonStr;
                }

                // JSON을 찾지 못한 경우 에러 반환
                System.Diagnostics.Debug.WriteLine($"[AI] No valid JSON found in output: {output.Substring(0, Math.Min(500, output.Length))}");
                return "{\"error\": \"No valid JSON in output: " + output.Replace("\"", "'").Replace("\n", " ").Substring(0, Math.Min(200, output.Length)) + "\"}";
            }

            return "{\"error\": \"Empty output from Python script\"}";
        }

        private void DisplayAIAnalysis(JObject analysisData)
        {
            // Guide 모드인지 확인 (tiers 배열이 있으면 guide)
            if (analysisData["tiers"] != null)
            {
                DisplayGuideAnalysis(analysisData);
                return;
            }

            var provider = analysisData["provider"]?.ToString() ?? "unknown";
            var model = analysisData["model"]?.ToString() ?? "unknown";
            var analysis = analysisData["analysis"]?.ToString() ?? "";
            var elapsed = analysisData["elapsed_seconds"]?.ToObject<double>() ?? 0;
            var inputTokens = analysisData["input_tokens"]?.ToObject<int>() ?? 0;
            var outputTokens = analysisData["output_tokens"]?.ToObject<int>() ?? 0;

            // Update header
            AIProviderText.Text = $" - {model}";
            AITokensText.Text = $"Tokens: {inputTokens:N0} / {outputTokens:N0} ({elapsed:F1}s)";

            // Update analysis text
            AIAnalysisText.Text = analysis;
        }

        private void DisplayGuideAnalysis(JObject guideData)
        {
            var buildName = guideData["build_name"]?.ToString() ?? "Unknown";
            var divineRate = guideData["divine_rate"]?.ToObject<double>() ?? 150;
            var tiers = guideData["tiers"] as JArray;
            var currentGear = guideData["current_gear"] as JObject;

            // Update header for guide mode
            AIProviderText.Text = " - Upgrade Guide";
            AITokensText.Text = $"Tiers: {tiers?.Count ?? 0} | Divine: {divineRate:F0}c";

            // Build guide text
            var sb = new System.Text.StringBuilder();
            sb.AppendLine($"🎯 {buildName} - 업그레이드 로드맵\n");

            // 현재 장비 요약 표시
            if (currentGear != null)
            {
                var uniqueCount = currentGear["unique_count"]?.ToObject<int>() ?? 0;
                var rareCount = currentGear["rare_count"]?.ToObject<int>() ?? 0;
                var estimatedValue = currentGear["estimated_value"]?.ToObject<int>() ?? 0;
                var keyItems = currentGear["key_items"] as JArray;

                sb.AppendLine("📦 현재 장비 분석");
                sb.AppendLine($"   유니크: {uniqueCount}개 | 레어: {rareCount}개");
                sb.AppendLine($"   추정 가치: {FormatChaosValue(estimatedValue, divineRate)}");

                if (keyItems != null && keyItems.Count > 0)
                {
                    sb.AppendLine("   핵심 아이템:");
                    foreach (var item in keyItems)
                    {
                        var itemName = item["name"]?.ToString();
                        var itemPrice = item["estimated_price"]?.ToObject<int>() ?? 0;
                        sb.AppendLine($"     • {itemName} ({FormatChaosValue(itemPrice, divineRate)})");
                    }
                }
                sb.AppendLine();
            }

            if (tiers != null)
            {
                foreach (var tier in tiers)
                {
                    var tierName = tier["tier_name"]?.ToString();
                    var budgetRange = tier["budget_range"]?.ToString();
                    var totalCost = tier["total_cost_formatted"]?.ToString();
                    var upgrades = tier["upgrades"] as JArray;

                    sb.AppendLine($"━━━ [{tierName}] {budgetRange} ━━━");
                    sb.AppendLine($"총 비용: {totalCost}\n");

                    if (upgrades != null)
                    {
                        int idx = 1;
                        foreach (var upgrade in upgrades)
                        {
                            var slot = upgrade["slot"]?.ToString();
                            var priority = upgrade["priority"]?.ToString();
                            var current = upgrade["current_item"]?.ToString();
                            var target = upgrade["target_item"]?.ToString();
                            var price = upgrade["price_formatted"]?.ToString();
                            var reason = upgrade["reason"]?.ToString();
                            var dpsGain = upgrade["dps_gain_percent"]?.ToObject<double>() ?? 0;
                            var ehpGain = upgrade["ehp_gain"]?.ToObject<double>() ?? 0;

                            string priorityIcon = priority switch
                            {
                                "CRITICAL" => "🔴",
                                "HIGH" => "🟠",
                                "MEDIUM" => "🟡",
                                _ => "🟢"
                            };

                            sb.AppendLine($"{idx}. {priorityIcon} [{priority}] {slot}");
                            sb.AppendLine($"   현재: {current}");
                            sb.AppendLine($"   목표: {target}");
                            sb.AppendLine($"   가격: {price}");
                            sb.AppendLine($"   이유: {reason}");

                            if (dpsGain > 0)
                                sb.AppendLine($"   📈 예상 DPS 증가: +{dpsGain}%");
                            if (ehpGain > 0)
                                sb.AppendLine($"   🛡️ 예상 EHP 증가: +{ehpGain}");

                            sb.AppendLine();
                            idx++;
                        }
                    }
                }
            }

            AIAnalysisText.Text = sb.ToString();
        }

        /// <summary>
        /// Format chaos value as "Xc" or "Yd" based on divine rate
        /// </summary>
        private string FormatChaosValue(int chaosValue, double divineRate)
        {
            if (divineRate > 0 && chaosValue >= divineRate)
            {
                double divine = chaosValue / divineRate;
                return divine >= 10 ? $"{(int)divine}d" : $"{divine:F1}d";
            }
            return $"{chaosValue}c";
        }

        private void CopyAIAnalysis_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var analysisText = AIAnalysisText.Text;
                if (string.IsNullOrEmpty(analysisText) || analysisText.StartsWith("Click"))
                {
                    MessageBox.Show("분석 결과가 없습니다.\n먼저 'AI Analysis' 버튼을 클릭해주세요.",
                        "알림", MessageBoxButton.OK, MessageBoxImage.Information);
                    return;
                }

                Clipboard.SetText(analysisText);
                ShowNotification("AI 분석 결과가 클립보드에 복사되었습니다!");
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "분석 결과 복사 중 오류가 발생했습니다.");
            }
        }

        private void CopyWhisper_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string whisperMessage)
            {
                try
                {
                    Clipboard.SetText(whisperMessage);
                    ShowNotification("Whisper message copied to clipboard!");
                }
                catch (Exception ex)
                {
                    ShowFriendlyError(ex, "Whisper 메시지 복사 중 오류가 발생했습니다.");
                }
            }
        }

        private void OpenTradeForItem_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string itemName)
            {
                try
                {
                    var tradeWindow = new TradeWindow(_currentLeague);
                    tradeWindow.NavigateToSearch(itemName);
                    tradeWindow.Show();
                }
                catch (Exception ex)
                {
                    ShowFriendlyError(ex, "POE Trade 창을 여는 중 오류가 발생했습니다.");
                }
            }
        }

        private void OpenTradeUrl_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string tradeUrl)
            {
                try
                {
                    if (!string.IsNullOrEmpty(tradeUrl) && tradeUrl.StartsWith("http"))
                    {
                        // WebView2 TradeWindow에서 Trade URL 열기
                        var tradeWindow = new TradeWindow(_currentLeague);
                        tradeWindow.NavigateToUrl(tradeUrl);
                        tradeWindow.Show();
                        ShowNotification("Opening Trade URL...");
                    }
                }
                catch (Exception ex)
                {
                    ShowFriendlyError(ex, "Trade URL을 여는 중 오류가 발생했습니다.");
                }
            }
        }

        private void BrowsePOBFile_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new Microsoft.Win32.OpenFileDialog
                {
                    Title = "Select POB XML File",
                    Filter = "POB XML Files|*.xml|All Files|*.*",
                    InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
                };

                if (dialog.ShowDialog() == true)
                {
                    var filePath = dialog.FileName;

                    // 파일 크기 체크 (10MB 제한)
                    var fileInfo = new System.IO.FileInfo(filePath);
                    if (fileInfo.Length > 10 * 1024 * 1024)
                    {
                        MessageBox.Show("파일 크기가 너무 큽니다. (최대 10MB)",
                            "파일 크기 초과", MessageBoxButton.OK, MessageBoxImage.Warning);
                        return;
                    }

                    // XML 파일 유효성 검사
                    try
                    {
                        var content = System.IO.File.ReadAllText(filePath);
                        if (!content.Contains("<PathOfBuilding") && !content.Contains("<Build"))
                        {
                            MessageBox.Show("유효한 POB XML 파일이 아닙니다.\nPath of Building에서 내보낸 파일인지 확인해주세요.",
                                "잘못된 파일", MessageBoxButton.OK, MessageBoxImage.Warning);
                            return;
                        }
                    }
                    catch (Exception)
                    {
                        MessageBox.Show("파일을 읽을 수 없습니다.",
                            "파일 읽기 오류", MessageBoxButton.OK, MessageBoxImage.Error);
                        return;
                    }

                    // 파일 경로를 POBInputBox에 설정 (file:// 프로토콜 사용)
                    POBInputBox.Text = $"file://{filePath}";
                    POBInputBox.Foreground = new SolidColorBrush(Color.FromRgb(205, 214, 244));

                    ShowNotification($"POB 파일 로드됨: {System.IO.Path.GetFileName(filePath)}");
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "POB 파일을 여는 중 오류가 발생했습니다.");
            }
        }

        private void POBInputBox_GotFocus(object sender, RoutedEventArgs e)
        {
            if (sender is TextBox textBox &&
                (textBox.Text == "https://pobb.in/..." ||
                 textBox.Text == "URL 또는 POB 코드 붙여넣기" ||
                 textBox.Text == "pobb.in URL 또는 POB 코드 붙여넣기"))
            {
                textBox.Text = "";
            }
        }

        private void StreamerInputBox_GotFocus(object sender, RoutedEventArgs e)
        {
            if (sender is TextBox textBox && (textBox.Text.StartsWith("예:") || string.IsNullOrWhiteSpace(textBox.Text)))
            {
                textBox.Text = "";
            }
        }

        private void ClassFilter_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender is ComboBox combo && combo.SelectedItem is ComboBoxItem item)
            {
                var content = item.Content?.ToString() ?? "All Classes";
                _currentClassFilter = content == "All Classes" ? "All" : content;
                Debug.WriteLine($"[FILTER] Class filter changed to: {_currentClassFilter}");
            }
        }

        private void SortFilter_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender is ComboBox combo && combo.SelectedItem is ComboBoxItem item)
            {
                var content = item.Content?.ToString() ?? "";
                _currentSortOrder = content switch
                {
                    "조회수 높은순" => "views",
                    "최신순" => "date",
                    "좋아요순" => "likes",
                    "가격 낮은순" => "price",
                    _ => "views"
                };
                Debug.WriteLine($"[FILTER] Sort order changed to: {_currentSortOrder}");
            }
        }

        private void BudgetFilter_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender is ComboBox combo && combo.SelectedItem is ComboBoxItem item)
            {
                // Tag에 저장된 chaos 값 사용 (동적으로 설정됨)
                if (item.Tag is int chaosValue)
                {
                    _currentBudgetFilter = chaosValue == 0 ? null : chaosValue;
                }
                else
                {
                    // 폴백: 레이블에서 파싱
                    var content = item.Content?.ToString() ?? "";
                    _currentBudgetFilter = content switch
                    {
                        "전체" => null,
                        "~50c" => 50,
                        "~100c" => 100,
                        "~500c" => 500,
                        "~1000c" => 1000,
                        "1000c+" => 10000,
                        _ => 100
                    };
                }
                Debug.WriteLine($"[FILTER] Budget filter changed to: {_currentBudgetFilter}");
            }
        }

        private double _currentDivineRate = 150.0;

        private void UpdateDivineRateDisplay(JObject? currencyData)
        {
            if (currencyData == null) return;

            _currentDivineRate = currencyData["divine_chaos_rate"]?.Value<double>() ?? 150.0;
            DivineRateText.Text = $"1 div = {(int)_currentDivineRate}c";

            // 소수점 단위 환산표 생성
            var conversionText = $"0.1 div = {(int)(_currentDivineRate * 0.1)}c\n" +
                                $"0.3 div = {(int)(_currentDivineRate * 0.3)}c\n" +
                                $"0.5 div = {(int)(_currentDivineRate * 0.5)}c\n" +
                                $"1 div = {(int)_currentDivineRate}c\n" +
                                $"3 div = {(int)(_currentDivineRate * 3)}c\n" +
                                $"5 div = {(int)(_currentDivineRate * 5)}c\n" +
                                $"10 div = {(int)(_currentDivineRate * 10)}c";

            DivineConversionText.Text = conversionText;
        }

        private void DivineRateText_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // 툴팁은 XAML에서 자동으로 표시됨
            // 추가 동작이 필요하면 여기에 구현
        }

        private void UpdateBudgetFilterOptions(JObject? currencyData)
        {
            if (currencyData == null) return;

            var budgetTiers = currencyData["budget_tiers"] as JArray;
            if (budgetTiers == null || budgetTiers.Count == 0) return;

            var divineRate = currencyData["divine_chaos_rate"]?.Value<double>() ?? 150.0;
            Debug.WriteLine($"[INFO] Divine rate: {divineRate}c, updating budget filter options");

            // 현재 선택된 값 저장
            var currentSelection = _currentBudgetFilter;

            // ComboBox 아이템 업데이트
            BudgetFilterCombo.Items.Clear();

            int closestIndex = 0;
            int closestDiff = int.MaxValue;

            for (int i = 0; i < budgetTiers.Count; i++)
            {
                var tier = budgetTiers[i];
                var label = tier["label"]?.ToString() ?? "";
                var tooltip = tier["tooltip"]?.ToString() ?? "";
                var chaosToken = tier["chaos_value"];
                var chaosValue = chaosToken != null && chaosToken.Type != JTokenType.Null
                    ? chaosToken.Value<int>()
                    : 0;

                var comboItem = new ComboBoxItem
                {
                    Content = label,
                    Tag = chaosValue
                };

                // Divine 환산표 툴팁 (호버 시 표시)
                if (!string.IsNullOrEmpty(tooltip))
                {
                    comboItem.ToolTip = tooltip;
                }

                BudgetFilterCombo.Items.Add(comboItem);

                // 현재 선택에 가장 가까운 값 찾기
                if (currentSelection.HasValue)
                {
                    int diff = Math.Abs(chaosValue - currentSelection.Value);
                    if (diff < closestDiff)
                    {
                        closestDiff = diff;
                        closestIndex = i;
                    }
                }
                else if (chaosValue == 0)
                {
                    closestIndex = i;
                }
            }

            // 가장 가까운 값 선택
            if (BudgetFilterCombo.Items.Count > 0)
            {
                BudgetFilterCombo.SelectedIndex = closestIndex;
            }
        }

        private async void SearchBuilds_Click(object sender, RoutedEventArgs e)
        {
            var streamerName = StreamerInputBox.Text?.Trim();

            // 플레이스홀더 텍스트 제거
            if (streamerName?.StartsWith("예:") == true) streamerName = null;

            if (string.IsNullOrWhiteSpace(streamerName))
            {
                // 스트리머 없으면 일반 추천
                await LoadRecommendations();
                return;
            }

            // 스트리머 기반 검색
            await LoadPersonalizedRecommendations(null, streamerName);
        }

        private async void AnalyzeMyBuild_Click(object sender, RoutedEventArgs e)
        {
            var pobUrl = POBInputBox.Text?.Trim();

            // 플레이스홀더 텍스트 제거
            if (pobUrl == "https://pobb.in/..." || pobUrl == "URL 또는 POB 코드 붙여넣기" || pobUrl == "pobb.in URL 또는 POB 코드 붙여넣기") pobUrl = null;

            if (string.IsNullOrWhiteSpace(pobUrl))
            {
                MessageBox.Show("POB URL 또는 코드를 입력해주세요.", "입력 필요", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            // 빌드 분석 실행
            _currentPOBUrl = pobUrl;

            // 로딩 UI 표시
            ShowLoadingOverlay("빌드 분석 중...", "POB 데이터를 가져오는 중입니다");

            // [핵심] POB URL에서 빌드 데이터를 먼저 파싱하여 _currentUserBuild 설정
            // 이렇게 하면 후속 함수들(LoadLevelingGuide, LoadFarmingStrategy 등)에서
            // _currentUserBuild를 직접 사용할 수 있고, 중복 파싱을 피할 수 있음
            try
            {
                UpdateLoadingText("POB 데이터 파싱 중...");
                var pobData = await Task.Run(() => ParsePobUrlForBuildInfo(pobUrl));
                if (pobData != null)
                {
                    _currentUserBuild = new JObject
                    {
                        ["main_skill"] = pobData.MainSkill,
                        ["class"] = pobData.ClassName,
                        ["ascendancy"] = pobData.Ascendancy,
                        ["dps"] = pobData.Dps,
                        ["ehp"] = pobData.Ehp
                    };
                    Debug.WriteLine($"[INFO] _currentUserBuild initialized: skill={pobData.MainSkill}, class={pobData.ClassName}");
                }
                else
                {
                    Debug.WriteLine("[WARNING] ParsePobUrlForBuildInfo returned null, _currentUserBuild not set");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] Failed to parse POB URL for _currentUserBuild: {ex.Message}");
            }
            AnalyzeButton.IsEnabled = false;
            AIAnalysisButton.IsEnabled = false;

            // 실패 추적용 리스트
            var failedSections = new List<string>();
            int successCount = 0;

            try
            {
                // Empty State 숨기고 결과 패널 표시
                EmptyStatePanel.Visibility = Visibility.Collapsed;
                AnalysisResultsPanel.Visibility = Visibility.Visible;
                LeagueInfoBar.Visibility = Visibility.Visible;

                // 빌드 비교 로드
                UpdateLoadingText("빌드 비교 분석 중...");
                try
                {
                    if (!string.IsNullOrEmpty(_currentCharacterName))
                    {
                        await LoadBuildComparison(pobUrl, _currentCharacterName);
                        successCount++;
                    }
                    else
                    {
                        successCount++; // 캐릭터 없으면 스킵 (실패 아님)
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[ERROR] LoadBuildComparison failed: {ex.Message}");
                    failedSections.Add("빌드 비교");
                }

                // 업그레이드 경로 로드
                UpdateLoadingText("업그레이드 경로 계산 중...");
                try
                {
                    await LoadUpgradePath(pobUrl, _currentCharacterName ?? "Unknown", _currentBudget);
                    successCount++;
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[ERROR] LoadUpgradePath failed: {ex.Message}");
                    failedSections.Add("업그레이드 경로");
                }

                // 레벨링 가이드 생성
                UpdateLoadingText("레벨링 가이드 생성 중...");
                try
                {
                    await LoadLevelingGuide(pobUrl);
                    successCount++;
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[ERROR] LoadLevelingGuide failed: {ex.Message}");
                    failedSections.Add("레벨링 가이드");
                }

                // 파밍 전략 생성
                UpdateLoadingText("파밍 전략 분석 중...");
                try
                {
                    await LoadFarmingStrategy(pobUrl);
                    successCount++;
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[ERROR] LoadFarmingStrategy failed: {ex.Message}");
                    failedSections.Add("파밍 전략");
                }

                // POE 계정이 연결되어 있으면 계정 이름 자동 설정
                if (_poeAccountData != null && string.IsNullOrEmpty(FilterAccountNameBox.Text))
                {
                    var accountName = _poeAccountData["name"]?.ToString();
                    if (!string.IsNullOrEmpty(accountName))
                    {
                        FilterAccountNameBox.Text = accountName;
                    }
                }

                // 첫 번째 Expander (빌드 개요) 열기
                BuildOverviewExpander.IsExpanded = true;

                // 결과 알림 (부분 성공/실패 구분)
                if (failedSections.Count == 0)
                {
                    ShowNotification("빌드 분석 완료!");
                }
                else if (successCount > 0)
                {
                    ShowNotification($"빌드 분석 완료 (일부 실패: {string.Join(", ", failedSections)})", isWarning: true);
                }
                else
                {
                    ShowNotification("빌드 분석 실패. POB URL을 확인해주세요.", isError: true);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[CRITICAL ERROR] AnalyzeMyBuild_Click: {ex.Message}\n{ex.StackTrace}");
                ShowFriendlyError(ex, "빌드 분석 중 오류가 발생했습니다.");
            }
            finally
            {
                // 로딩 UI 숨기기
                HideLoadingOverlay();
                AnalyzeButton.IsEnabled = true;
                AIAnalysisButton.IsEnabled = true;
            }
        }

        private void ShowLoadingOverlay(string text, string subText = "")
        {
            LoadingText.Text = text;
            LoadingSubText.Text = subText;
            LoadingOverlay.Visibility = Visibility.Visible;
        }

        private void UpdateLoadingText(string text, string subText = "")
        {
            LoadingText.Text = text;
            if (!string.IsNullOrEmpty(subText))
                LoadingSubText.Text = subText;
        }

        private void HideLoadingOverlay()
        {
            LoadingOverlay.Visibility = Visibility.Collapsed;
        }

        private string _selectedFilterTheme = "chaos_dot";

        private void FilterTheme_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (FilterThemeCombo?.SelectedItem is ComboBoxItem selected)
            {
                _selectedFilterTheme = selected.Tag?.ToString() ?? "default";
                Debug.WriteLine($"[Filter] Theme changed to: {_selectedFilterTheme}");
            }
        }

        private void AskAIAboutTheme_Click(object sender, RoutedEventArgs e)
        {
            // TODO: AI 대화 기능 연동
            MessageBox.Show("AI 테마 추천 기능은 준비 중입니다.\n빌드 분석 결과를 기반으로 자동 감지된 테마를 사용해주세요.",
                "AI 테마 추천", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private async void ApplyThemeAndGenerate_Click(object sender, RoutedEventArgs e)
        {
            // 선택된 테마로 필터 생성
            await GenerateFilterWithTheme(_selectedFilterTheme);
        }

        private async Task GenerateFilterWithTheme(string theme)
        {
            var pobUrl = POBInputBox.Text?.Trim();
            if (pobUrl == "https://pobb.in/..." || pobUrl == "URL 또는 POB 코드 붙여넣기") pobUrl = null;

            string pobInput;
            if (!string.IsNullOrWhiteSpace(pobUrl))
            {
                pobInput = pobUrl;
            }
            else if (!string.IsNullOrEmpty(_currentPOBXmlPath) && File.Exists(_currentPOBXmlPath))
            {
                pobInput = _currentPOBXmlPath;
            }
            else
            {
                MessageBox.Show("POB URL을 입력하거나 빌드를 먼저 분석해주세요.", "POB 필요", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                var filterFolder = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "My Games", "Path of Exile");

                if (!Directory.Exists(filterFolder))
                {
                    Directory.CreateDirectory(filterFolder);
                }

                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath)!;
                // New CLI: filter_generator_cli.py (Clean Architecture)
                // Default: SSF mode, EarlyMap phase, area-level 1, progressive hiding enabled
                var args = $"\"{_filterGeneratorScriptPath}\" \"{pobInput}\" --output \"{filterFolder}\" --mode ssf --phase EarlyMap --area-level 68";

                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = args,
                    WorkingDirectory = parserDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8,
                };

                var result = await Task.Run(() =>
                {
                    using var process = Process.Start(psi);
                    if (process == null) return "Process failed to start";

                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit(60000);

                    if (!string.IsNullOrWhiteSpace(error))
                        Debug.WriteLine($"[Filter] stderr: {error}");

                    return output;
                });

                Debug.WriteLine($"[Filter] Result: {result}");
                MessageBox.Show($"필터가 생성되었습니다!\n테마: {theme}\n경로: {filterFolder}",
                    "필터 생성 완료", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[Filter] Error: {ex.Message}");
                ShowFriendlyError(ex, "필터 생성 중 오류가 발생했습니다.");
            }
        }

        private async void GenerateFilter_Click(object sender, RoutedEventArgs e)
        {
            var pobUrl = POBInputBox.Text?.Trim();
            if (pobUrl == "https://pobb.in/..." || pobUrl == "URL 또는 POB 코드 붙여넣기") pobUrl = null;

            // POB URL 또는 저장된 XML 필요
            string pobInput;
            if (!string.IsNullOrWhiteSpace(pobUrl))
            {
                pobInput = pobUrl;
            }
            else if (!string.IsNullOrEmpty(_currentPOBXmlPath) && File.Exists(_currentPOBXmlPath))
            {
                pobInput = _currentPOBXmlPath;
            }
            else
            {
                MessageBox.Show("POB URL을 입력하거나 빌드를 먼저 분석해주세요.", "POB 필요", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                // POE 필터 폴더 경로
                var filterFolder = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "My Games", "Path of Exile");

                if (!Directory.Exists(filterFolder))
                {
                    Directory.CreateDirectory(filterFolder);
                }

                // Python 스크립트 실행
                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath)!;

                // filter_generator_cli.py (Clean Architecture)
                // Default: SSF mode, EarlyMap phase, area-level 68, progressive hiding enabled
                var args = $"\"{_filterGeneratorScriptPath}\" \"{pobInput}\" --output \"{filterFolder}\" --mode ssf --phase EarlyMap --area-level 68";

                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = args,
                    WorkingDirectory = parserDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                psi.Environment["PYTHONUTF8"] = "1";

                var result = await Task.Run(() =>
                {
                    using var process = Process.Start(psi);
                    if (process == null) return "Process failed to start";

                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit();

                    return $"{output}\n{error}";
                });

                // 결과 표시
                if (result.Contains("Generated") || result.Contains("filter files"))
                {
                    // 생성된 파일 이름 추출
                    var generatedFiles = new System.Collections.Generic.List<string>();
                    foreach (var line in result.Split('\n'))
                    {
                        if (line.Contains("Generated:") && line.Contains(".filter"))
                        {
                            var fileName = Path.GetFileName(line.Split("Generated:")[1].Trim());
                            generatedFiles.Add(fileName);
                        }
                    }

                    var fileList = generatedFiles.Count > 0
                        ? string.Join("\n• ", generatedFiles)
                        : "Leveling / EarlyMap / Endgame";

                    var message = $"필터 파일이 생성되었습니다!\n\n위치: {filterFolder}\n\n생성된 파일:\n• {fileList}\n\n게임에서 /itemfilter 명령어로 적용하세요.";

                    MessageBox.Show(message, "필터 생성 완료", MessageBoxButton.OK, MessageBoxImage.Information);

                    // 폴더 열기
                    Process.Start("explorer.exe", filterFolder);
                }
                else
                {
                    MessageBox.Show($"필터 생성 중 오류가 발생했습니다.\n\n{result}", "오류", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "필터 생성 중 오류가 발생했습니다.");
            }
        }

        private async void GetPersonalizedRecommendations_Click(object sender, RoutedEventArgs e)
        {
            var pobUrl = POBInputBox.Text?.Trim();
            var streamerName = StreamerInputBox.Text?.Trim();

            // 플레이스홀더 텍스트 제거
            if (pobUrl == "https://pobb.in/..." || pobUrl == "URL 또는 POB 코드 붙여넣기") pobUrl = null;
            if (streamerName?.StartsWith("예:") == true) streamerName = null;

            if (string.IsNullOrWhiteSpace(pobUrl) && string.IsNullOrWhiteSpace(streamerName))
            {
                // 둘 다 비어있으면 일반 추천
                await LoadRecommendations();
                return;
            }

            // POB URL이 있으면 My Build 탭으로 전환
            if (!string.IsNullOrWhiteSpace(pobUrl))
            {
                MainTabControl.SelectedIndex = 1; // My Build 탭
            }

            // 맞춤 추천 실행
            await LoadPersonalizedRecommendations(pobUrl, streamerName);
        }

        private async Task LoadPersonalizedRecommendations(string? pobUrl, string? streamerName)
        {
            if (_isLoading) return;

            try
            {
                _isLoading = true;
                PlaceholderPanel.Visibility = Visibility.Collapsed;
                ResultsPanel.Children.Clear();

                // Loading indicator
                var loadingText = new TextBlock
                {
                    Text = "🔍 맞춤 추천을 찾고 있습니다...",
                    FontSize = 14,
                    Foreground = new SolidColorBrush(Color.FromRgb(203, 166, 247)),
                    HorizontalAlignment = HorizontalAlignment.Center,
                    Margin = new Thickness(0, 100, 0, 0)
                };
                ResultsPanel.Children.Add(loadingText);

                // Python 스크립트 실행 (POB URL과 스트리머 이름 전달)
                var result = await System.Threading.Tasks.Task.Run(() => ExecutePersonalizedRecommendation(pobUrl, streamerName));

                // 결과 표시
                ResultsPanel.Children.Clear();
                DisplayRecommendations(result);

                // POB URL이 있으면 자동으로 AI 분석 실행
                if (!string.IsNullOrEmpty(pobUrl))
                {
                    _currentPOBUrl = pobUrl;
                    // AI 분석 자동 실행 (비동기)
                    _ = Task.Run(async () =>
                    {
                        await Task.Delay(500); // 추천 결과 표시 후 약간의 딜레이
                        Dispatcher.Invoke(() => AIAnalysis_Click(this, new RoutedEventArgs()));
                    });
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "맞춤 추천을 불러오는 중 오류가 발생했습니다.");
                PlaceholderPanel.Visibility = Visibility.Visible;
            }
            finally
            {
                _isLoading = false;
            }
        }

        private string ExecutePersonalizedRecommendation(string? pobUrl, string? streamerName)
        {
            var parserDir = Path.GetDirectoryName(_recommendationScriptPath)!;

            // Arguments 구성
            var args = $"\"{_recommendationScriptPath}\" --json-output";
            if (!string.IsNullOrEmpty(pobUrl))
                args += $" --reference-pob \"{pobUrl}\"";
            if (!string.IsNullOrEmpty(streamerName))
                args += $" --streamer \"{streamerName}\"";

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = args,
                WorkingDirectory = parserDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";

            // API 키 환경 변수로 전달 (설정에서 가져오기)
            var settings = AppSettings.Load();
            var youtubeApiKey = settings.GetApiKey("youtube") ?? "";
            if (!string.IsNullOrEmpty(youtubeApiKey))
            {
                psi.Environment["YOUTUBE_API_KEY"] = youtubeApiKey;
            }

            Debug.WriteLine($"[EXEC] Running personalized recommendation: {_pythonPath}");
            Debug.WriteLine($"[EXEC] Args: {psi.Arguments}");

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start Python process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            Debug.WriteLine($"[EXEC] Exit code: {process.ExitCode}");
            if (!string.IsNullOrWhiteSpace(error))
            {
                Debug.WriteLine($"[EXEC] Stderr: {error}");
            }

            if (process.ExitCode != 0)
            {
                throw new Exception($"Personalized recommendation error (exit code {process.ExitCode}):\n{error}");
            }

            return output;
        }

        private async void AnalyzePOB_Click(object sender, RoutedEventArgs e)
        {
            var pobUrl = POBInputBox.Text?.Trim();

            if (string.IsNullOrWhiteSpace(pobUrl) || pobUrl == "https://pobb.in/...")
            {
                // POB 링크 없으면 Refresh Recommendations 실행
                await LoadRecommendations();
                return;
            }

            // POB 링크가 있으면 AI 분석 실행
            _currentPOBUrl = pobUrl;
            await AnalyzePOBBuild(pobUrl);
        }

        private async Task AnalyzePOBBuild(string pobUrl)
        {
            try
            {
                PlaceholderPanel.Visibility = Visibility.Collapsed;
                ResultsPanel.Children.Clear();

                var loadingText = new TextBlock
                {
                    Text = "🤖 AI 분석 중... 잠시만 기다려주세요",
                    FontSize = 14,
                    Foreground = new SolidColorBrush(Color.FromRgb(175, 96, 37)),
                    HorizontalAlignment = HorizontalAlignment.Center,
                    Margin = new Thickness(0, 100, 0, 0)
                };
                ResultsPanel.Children.Add(loadingText);

                // Rule-Based 분석 먼저 실행 (빠름)
                await System.Threading.Tasks.Task.Run(() => AnalyzePOBWithRules(pobUrl));

                // 추천 빌드도 함께 로드
                await LoadRecommendations();
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "POB 분석 중 오류가 발생했습니다.");
                PlaceholderPanel.Visibility = Visibility.Visible;
            }
        }

        private void AnalyzePOBWithRules(string pobUrl)
        {
            var parserDir = Path.GetDirectoryName(_recommendationScriptPath)!;
            var ruleAnalyzerScript = Path.Combine(parserDir, "rule_based_analyzer.py");

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{ruleAnalyzerScript}\" --pob \"{pobUrl}\" --json",
                WorkingDirectory = parserDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8
            };

            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start Python process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                throw new Exception($"Rule-based analyzer error (exit code {process.ExitCode}):\n{error}");
            }

            // JSON 파싱 및 AI Analysis 섹션 표시
            Dispatcher.Invoke(() =>
            {
                DisplayRuleBasedAnalysis(output);
            });
        }

        private void DisplayRuleBasedAnalysis(string jsonOutput)
        {
            try
            {
                var jsonStart = jsonOutput.IndexOf('{');
                var jsonEnd = jsonOutput.LastIndexOf('}');

                if (jsonStart == -1 || jsonEnd == -1)
                    return;

                var jsonString = jsonOutput.Substring(jsonStart, jsonEnd - jsonStart + 1);
                var data = JObject.Parse(jsonString);

                // AI Analysis 섹션 표시
                AIAnalysisExpander.Visibility = Visibility.Visible;
                AIProviderText.Text = "Provider: Rule-Based (Free)";

                var analysis = data["analysis"]?.ToString() ?? "분석 결과가 없습니다.";
                AIAnalysisText.Text = analysis;

                // 토큰 정보는 Rule-Based에서는 N/A
                var execTime = data["execution_time"]?.ToObject<double>() ?? 0.0;
                AITokensText.Text = $"Tokens: N/A (Free) | {execTime:F1}s";
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] DisplayRuleBasedAnalysis: {ex.Message}");
            }
        }

        private async void ConnectPOE_Click(object sender, RoutedEventArgs e)
        {
            if (_isPOEConnected)
            {
                // 이미 연결된 경우 - 연결 해제 옵션
                var result = MessageBox.Show(
                    $"Currently connected as: {_poeAccountData?["username"]}\n\nDo you want to disconnect?",
                    "POE Account",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Question);

                if (result == MessageBoxResult.Yes)
                {
                    DisconnectPOE();
                }
                return;
            }

            // OAuth 인증 시작
            try
            {
                ConnectPOEButton.IsEnabled = false;
                ConnectPOEButton.Content = "Connecting...";

                await System.Threading.Tasks.Task.Run(() => ExecuteOAuthFlow());

                // 토큰 확인
                CheckPOEConnection();

                if (_isPOEConnected)
                {
                    MessageBox.Show($"Successfully connected to POE!\n\nUsername: {_poeAccountData?["username"]}",
                        "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "POE 계정 연결 중 오류가 발생했습니다.");
            }
            finally
            {
                ConnectPOEButton.IsEnabled = true;
                UpdatePOEButtonState();

                // 추천 새로고침 (사용자 캐릭터 기반) - UI 블로킹 방지를 위해 비동기로 실행
                if (_isPOEConnected)
                {
                    _ = LoadRecommendations();
                }
            }
        }

        private void CheckPOEConnection()
        {
            try
            {
                if (File.Exists(_tokenFilePath))
                {
                    var tokenJson = File.ReadAllText(_tokenFilePath);
                    _poeAccountData = JObject.Parse(tokenJson);

                    var username = _poeAccountData["username"]?.ToString();
                    if (!string.IsNullOrEmpty(username))
                    {
                        _isPOEConnected = true;
                        POEAccountText.Text = $"Connected: {username}";
                        POEAccountText.Foreground = new SolidColorBrush(Color.FromRgb(166, 227, 161));  // #A6E3A1

                        // 캐릭터 정보 로드
                        LoadCharacterInfo();
                    }
                }
                else
                {
                    _isPOEConnected = false;
                    POEAccountText.Text = "Not connected";
                    POEAccountText.Foreground = new SolidColorBrush(Color.FromRgb(127, 132, 156));  // #7F849C
                }

                UpdatePOEButtonState();
            }
            catch
            {
                _isPOEConnected = false;
                POEAccountText.Text = "Not connected";
            }
        }

        private void LoadCharacterInfo()
        {
            try
            {
                // Python 스크립트로 캐릭터 정보 가져오기
                var baseDir = AppDomain.CurrentDomain.BaseDirectory;
                var projectRoot = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", ".."));
                var parserDir = Path.Combine(projectRoot, "src", "PathcraftAI.Parser");

                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = $"-c \"from poe_oauth import load_token, get_user_characters; token = load_token(); result = get_user_characters(token['access_token']) if token else None; chars = result.get('characters', []) if isinstance(result, dict) else []; print(len(chars))\"",
                    WorkingDirectory = parserDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using var process = Process.Start(psi);
                if (process != null)
                {
                    var output = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();

                    if (int.TryParse(output.Trim(), out int charCount) && charCount > 0)
                    {
                        // 메인 캐릭터 찾기 (current: true인 캐릭터)
                        FindMainCharacter();
                    }
                }
            }
            catch (Exception ex)
            {
                // 캐릭터 정보 로드 실패 로깅
                Debug.WriteLine($"[ERROR] LoadCharacterInfo failed: {ex.Message}\n{ex.StackTrace}");
            }
        }

        private void FindMainCharacter()
        {
            try
            {
                var baseDir = AppDomain.CurrentDomain.BaseDirectory;
                var projectRoot = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", ".."));
                var parserDir = Path.Combine(projectRoot, "src", "PathcraftAI.Parser");

                var pythonCode = @"
from poe_oauth import load_token, get_user_characters
token = load_token()
if token:
    result = get_user_characters(token['access_token'])
    chars = result.get('characters', []) if isinstance(result, dict) else []
    if chars:
        current = next((c for c in chars if c.get('current')), chars[0])
        if current:
            print(f""{current['name']} Lv{current['level']} {current['class']}"")
";
                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = $"-c \"{pythonCode}\"",
                    WorkingDirectory = parserDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using var process = Process.Start(psi);
                if (process != null)
                {
                    var output = process.StandardOutput.ReadToEnd().Trim();
                    process.WaitForExit();

                    if (!string.IsNullOrEmpty(output) && output != "-")
                    {
                        MainCharacterText.Text = $"Main: {output}";
                    }
                }
            }
            catch (Exception ex)
            {
                // 실패 시 로깅
                Debug.WriteLine($"[ERROR] FindMainCharacter failed: {ex.Message}\n{ex.StackTrace}");
            }
        }

        private void UpdatePOEButtonState()
        {
            if (_isPOEConnected)
            {
                ConnectPOEButton.Content = "Disconnect POE";
            }
            else
            {
                ConnectPOEButton.Content = "Connect POE Account";
            }
        }

        private void DisconnectPOE()
        {
            try
            {
                if (File.Exists(_tokenFilePath))
                {
                    File.Delete(_tokenFilePath);
                }

                _isPOEConnected = false;
                _poeAccountData = null;
                POEAccountText.Text = "Not connected";
                POEAccountText.Foreground = new SolidColorBrush(Color.FromRgb(128, 128, 128));
                CharacterInfoPanel.Visibility = Visibility.Collapsed;
                UpdatePOEButtonState();

                MessageBox.Show("Disconnected from POE account.", "Info", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "POE 계정 연결 해제 중 오류가 발생했습니다.");
            }
        }

        private void ExecuteOAuthFlow()
        {
            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{_oauthScriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = false,  // 브라우저 열기 위해 window 표시
                WorkingDirectory = Path.GetDirectoryName(_oauthScriptPath)
            };

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start OAuth process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                throw new Exception($"OAuth authentication failed:\n{error}");
            }
        }

        private async Task LoadBuildComparison(string pobUrl, string characterName)
        {
            try
            {
                _currentPOBUrl = pobUrl;

                // Python 스크립트로 비교 데이터 가져오기
                var result = await System.Threading.Tasks.Task.Run(() =>
                    ExecuteBuildComparison(pobUrl, characterName));

                if (string.IsNullOrWhiteSpace(result))
                {
                    BuildComparisonExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // JSON 파싱
                var data = JObject.Parse(result);

                // 에러 체크
                if (data["error"] != null)
                {
                    BuildComparisonExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // 비교 데이터 표시
                DisplayBuildComparison(data);
                BuildComparisonExpander.Visibility = Visibility.Visible;

                // 빌드 비교 로드 후 업그레이드 경로 로드
                _ = LoadUpgradePath(pobUrl, characterName, _currentBudget);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Build comparison failed: {ex.Message}");
                BuildComparisonExpander.Visibility = Visibility.Collapsed;
            }
        }

        private string ExecuteBuildComparison(string pobUrl, string characterName)
        {
            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{_compareBuildScriptPath}\" --pob \"{pobUrl}\" --character \"{characterName}\" --json",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(_compareBuildScriptPath)
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start comparison process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                Debug.WriteLine($"Comparison script error: {error}");
                return string.Empty;
            }

            return output;
        }

        private void DisplayBuildComparison(JObject data)
        {
            // 비교 데이터 바인딩
            var comparison = data["comparison"] as JArray;
            if (comparison != null && comparison.Count > 0)
            {
                var comparisonList = new List<ComparisonRow>();

                foreach (var item in comparison)
                {
                    var stat = item["stat"]?.ToString() ?? "";
                    var current = item["current"]?.ToObject<double>() ?? 0;
                    var target = item["target"]?.ToObject<double>() ?? 0;
                    var gap = item["gap"]?.ToObject<double>() ?? 0;
                    var status = item["status"]?.ToString() ?? "";
                    var unit = item["unit"]?.ToString() ?? "";

                    comparisonList.Add(new ComparisonRow
                    {
                        Stat = stat,
                        CurrentDisplay = FormatStatValue(current, unit),
                        TargetDisplay = FormatStatValue(target, unit),
                        GapDisplay = FormatGapValue(gap, unit),
                        Status = status
                    });
                }

                ComparisonGrid.ItemsSource = comparisonList;
            }

            // Priority Upgrades 표시
            var priorityUpgrades = data["priority_upgrades"] as JArray;
            if (priorityUpgrades != null && priorityUpgrades.Count > 0)
            {
                var upgradeList = new List<PriorityUpgrade>();

                foreach (var upgrade in priorityUpgrades)
                {
                    upgradeList.Add(new PriorityUpgrade
                    {
                        Priority = upgrade["priority"]?.ToObject<int>() ?? 0,
                        Category = upgrade["category"]?.ToString() ?? "",
                        Description = upgrade["description"]?.ToString() ?? "",
                        Suggestion = upgrade["suggestion"]?.ToString() ?? ""
                    });
                }

                PriorityUpgradesList.ItemsSource = upgradeList;
                PriorityUpgradesPanel.Visibility = Visibility.Visible;
            }
            else
            {
                PriorityUpgradesPanel.Visibility = Visibility.Collapsed;
            }
        }

        private string FormatStatValue(double value, string unit)
        {
            if (string.IsNullOrEmpty(unit))
                return value.ToString("N0");

            return $"{value:N0}{unit}";
        }

        private string FormatGapValue(double gap, string unit)
        {
            var sign = gap >= 0 ? "+" : "";

            if (string.IsNullOrEmpty(unit))
                return $"{sign}{gap:N0}";

            return $"{sign}{gap:N0}{unit}";
        }

        private async Task LoadUpgradePath(string pobUrl, string characterName, int budgetChaos)
        {
            try
            {
                // Show loading indicator
                UpgradePathDescription.Text = "Loading upgrade path recommendations...";
                UpgradePathExpander.Visibility = Visibility.Visible;

                // Python 스크립트로 업그레이드 경로 가져오기 (with timeout)
                var timeoutTask = System.Threading.Tasks.Task.Delay(30000); // 30초 타임아웃
                var upgradeTask = System.Threading.Tasks.Task.Run(() =>
                    ExecuteUpgradePath(pobUrl, characterName, budgetChaos));

                var completedTask = await System.Threading.Tasks.Task.WhenAny(upgradeTask, timeoutTask);

                if (completedTask == timeoutTask)
                {
                    ShowNotification("Upgrade path request timed out. Please try again.", isError: true);
                    UpgradePathExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                var result = await upgradeTask;

                if (string.IsNullOrWhiteSpace(result))
                {
                    ShowNotification("Failed to load upgrade path. Please check your POB URL.", isError: true);
                    UpgradePathExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // JSON 파싱
                JObject? data;
                try
                {
                    data = JObject.Parse(result);
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"JSON parse error: {ex.Message}");
                    ShowNotification("Failed to parse upgrade path data.", isError: true);
                    UpgradePathExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // 에러 체크
                if (data["error"] != null)
                {
                    var errorMsg = data["error"]?.ToString() ?? "Unknown error";
                    ShowNotification($"Upgrade path error: {errorMsg}", isError: true);
                    UpgradePathExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // 업그레이드 경로 표시
                UpgradePathDescription.Text = "Based on your current build and target POB, here's the recommended upgrade path:";
                DisplayUpgradePath(data);
                UpgradePathExpander.Visibility = Visibility.Visible;

                // 업그레이드 경로 로드 후 패시브 트리 로드
                _ = LoadPassiveTreeRoadmap(pobUrl, characterName);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Upgrade path failed: {ex.Message}");
                ShowNotification($"Error loading upgrade path: {ex.Message}", isError: true);
                UpgradePathExpander.Visibility = Visibility.Collapsed;
            }
        }

        private string ExecuteUpgradePath(string pobUrl, string characterName, int budgetChaos)
        {
            // Use Trade API version for real trade data
            var scriptPath = _upgradePathTradeScriptPath;

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{scriptPath}\" --pob \"{pobUrl}\" --character \"{characterName}\" --budget {budgetChaos} --league Standard --json",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(scriptPath)
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start upgrade path process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            // 로깅 추가
            Debug.WriteLine($"[UpgradePath] Exit code: {process.ExitCode}");
            Debug.WriteLine($"[UpgradePath] Stderr: {error}");
            Debug.WriteLine($"[UpgradePath] Stdout length: {output?.Length ?? 0}");
            if (!string.IsNullOrEmpty(output) && output.Length < 500)
                Debug.WriteLine($"[UpgradePath] Output: {output}");

            // stdout에서 JSON 부분만 추출 (다른 로그 메시지 무시)
            if (!string.IsNullOrEmpty(output))
            {
                // JSON 시작 위치 찾기
                var jsonStart = output.IndexOf('{');
                if (jsonStart >= 0)
                {
                    var jsonOutput = output.Substring(jsonStart);
                    Debug.WriteLine($"[UpgradePath] Extracted JSON from position {jsonStart}");
                    return jsonOutput;
                }
            }

            if (process.ExitCode != 0 || string.IsNullOrEmpty(output))
            {
                Debug.WriteLine($"Upgrade path script error: {error}");
                return string.Empty;
            }

            return output;
        }

        private void DisplayUpgradePath(JObject data)
        {
            // 예산 및 총 비용 표시
            var budgetChaos = data["budget_chaos"]?.ToObject<int>() ?? 100;
            var totalCost = data["total_cost"]?.ToObject<int>() ?? 0;

            UpgradeBudgetText.Text = $" - Budget: {budgetChaos}c (Total: {totalCost}c)";

            // 업그레이드 스텝 표시
            var upgradeSteps = data["upgrade_steps"] as JArray;
            if (upgradeSteps != null && upgradeSteps.Count > 0)
            {
                var stepsList = new List<UpgradeStep>();

                foreach (var step in upgradeSteps)
                {
                    var recommendations = step["recommendations"] as JArray;
                    var recList = new List<string>();

                    if (recommendations != null)
                    {
                        foreach (var rec in recommendations)
                        {
                            recList.Add(rec.ToString());
                        }
                    }

                    // Trade results 파싱
                    var tradeResults = step["trade_results"] as JArray;
                    var tradeItemsList = new List<TradeItem>();

                    if (tradeResults != null)
                    {
                        foreach (var item in tradeResults)
                        {
                            tradeItemsList.Add(new TradeItem
                            {
                                Name = item["name"]?.ToString() ?? "",
                                Type = item["type"]?.ToString() ?? "",
                                PriceDisplay = item["price_display"]?.ToString() ?? "",
                                Seller = item["seller"]?.ToString() ?? "",
                                Whisper = item["whisper"]?.ToString() ?? ""
                            });
                        }
                    }

                    stepsList.Add(new UpgradeStep
                    {
                        Step = step["step"]?.ToObject<int>() ?? 0,
                        Priority = step["priority"]?.ToString() ?? "",
                        Title = step["title"]?.ToString() ?? "",
                        CostChaos = step["cost_chaos"]?.ToObject<int>() ?? 0,
                        Description = step["description"]?.ToString() ?? "",
                        Impact = step["impact"]?.ToString() ?? "",
                        Recommendations = recList,
                        TradeItems = tradeItemsList
                    });
                }

                UpgradesList.ItemsSource = stepsList;
            }
            else
            {
                UpgradePathExpander.Visibility = Visibility.Collapsed;
            }
        }

        private async Task LoadPassiveTreeRoadmap(string pobUrl, string characterName)
        {
            try
            {
                // Python 스크립트로 패시브 트리 로드맵 가져오기
                var result = await System.Threading.Tasks.Task.Run(() =>
                    ExecutePassiveTreeAnalyzer(pobUrl, characterName));

                if (string.IsNullOrWhiteSpace(result))
                {
                    PassiveTreeExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // JSON 파싱
                var data = JObject.Parse(result);

                // 에러 체크
                if (data["error"] != null)
                {
                    PassiveTreeExpander.Visibility = Visibility.Collapsed;
                    return;
                }

                // 패시브 트리 로드맵 표시
                DisplayPassiveTreeRoadmap(data);
                PassiveTreeExpander.Visibility = Visibility.Visible;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Passive tree roadmap failed: {ex.Message}");
                PassiveTreeExpander.Visibility = Visibility.Collapsed;
            }
        }

        private string ExecutePassiveTreeAnalyzer(string pobUrl, string characterName)
        {
            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{_passiveTreeScriptPath}\" --pob \"{pobUrl}\" --character \"{characterName}\" --json",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(_passiveTreeScriptPath)
            };

            // Enable UTF-8 mode for Python
            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null)
                throw new Exception("Failed to start passive tree analyzer process");

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                Debug.WriteLine($"Passive tree analyzer error: {error}");
                return string.Empty;
            }

            return output;
        }

        private void DisplayPassiveTreeRoadmap(JObject data)
        {
            // 레벨 및 포인트 정보 표시
            var currentLevel = data["current_level"]?.ToObject<int>() ?? 1;
            var targetLevel = data["target_level"]?.ToObject<int>() ?? 100;
            var pointsNeeded = data["points_needed"]?.ToObject<int>() ?? 0;

            PassiveCurrentLevelText.Text = $"Lv{currentLevel}";
            PassiveTargetLevelText.Text = $"Lv{targetLevel}";
            PassivePointsText.Text = $" - {pointsNeeded} points needed";

            // 로드맵 스테이지 표시
            var roadmap = data["roadmap"] as JArray;
            if (roadmap != null && roadmap.Count > 0)
            {
                var stagesList = new List<PassiveRoadmapStage>();

                foreach (var stage in roadmap)
                {
                    var nodes = stage["nodes"] as JArray;
                    var nodesList = new List<PassiveNode>();

                    if (nodes != null)
                    {
                        foreach (var node in nodes)
                        {
                            var stats = node["stats"] as JArray;
                            var statsList = new List<string>();

                            if (stats != null)
                            {
                                foreach (var stat in stats)
                                {
                                    statsList.Add(stat.ToString());
                                }
                            }

                            var nodeType = node["type"]?.ToString() ?? "";
                            var typeDisplay = "";

                            if (nodeType == "notable")
                                typeDisplay = "[NOTABLE]";
                            else if (nodeType == "keystone")
                                typeDisplay = "[KEYSTONE]";
                            else if (nodeType == "jewel")
                                typeDisplay = "[JEWEL]";

                            nodesList.Add(new PassiveNode
                            {
                                Name = node["name"]?.ToString() ?? "",
                                Type = nodeType,
                                TypeDisplay = typeDisplay,
                                StatsDisplay = statsList
                            });
                        }
                    }

                    // Benefits를 문자열 리스트로 변환
                    var benefits = stage["benefits"] as JObject;
                    var benefitsList = new List<string>();

                    if (benefits != null)
                    {
                        foreach (var benefit in benefits)
                        {
                            benefitsList.Add($"{benefit.Key}: {benefit.Value}");
                        }
                    }

                    stagesList.Add(new PassiveRoadmapStage
                    {
                        LevelRange = stage["level_range"]?.ToString() ?? "",
                        Points = stage["points"]?.ToObject<int>() ?? 0,
                        PriorityFocus = stage["priority_focus"]?.ToString() ?? "",
                        Nodes = nodesList,
                        BenefitsDisplay = benefitsList
                    });
                }

                PassiveRoadmapList.ItemsSource = stagesList;
            }
            else
            {
                PassiveTreeExpander.Visibility = Visibility.Collapsed;
            }
        }

        private void RegisterHotkeys()
        {
            try
            {
                var windowHandle = new System.Windows.Interop.WindowInteropHelper(this).Handle;

                // F5: 하이드아웃 이동
                _hideoutHotkey = new GlobalHotkey(Key.F5, KeyModifier.None, windowHandle);
                _hideoutHotkey.HotkeyPressed += (s, e) =>
                {
                    Debug.WriteLine("[HOTKEY] F5 pressed!");
                    ExecuteHideoutCommand();
                };

                // Ctrl+D: 아이템 시세 조회
                _priceCheckHotkey = new GlobalHotkey(Key.D, KeyModifier.Control, windowHandle);
                _priceCheckHotkey.HotkeyPressed += (s, e) =>
                {
                    ExecutePriceCheck();
                };

                // F3: ty @last 입력
                _thankYouHotkey = new GlobalHotkey(Key.F3, KeyModifier.None, windowHandle);
                _thankYouHotkey.HotkeyPressed += (s, e) =>
                {
                    ExecuteThankYouCommand();
                };
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to register hotkeys: {ex.Message}");
                MessageBox.Show($"핫키 등록 실패: {ex.Message}", "오류", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void UnregisterHotkeys()
        {
            _hideoutHotkey?.Dispose();
            _hideoutHotkey = null;
            _priceCheckHotkey?.Dispose();
            _priceCheckHotkey = null;
            _thankYouHotkey?.Dispose();
            _thankYouHotkey = null;
        }

        private void ExecuteHideoutCommand()
        {
            try
            {
                // POE 창 찾기 (POE1 또는 POE2)
                IntPtr poeWindow = FindWindow(null, "Path of Exile");
                if (poeWindow == IntPtr.Zero)
                {
                    poeWindow = FindWindow(null, "Path of Exile 2");
                }

                if (poeWindow == IntPtr.Zero)
                {
                    Debug.WriteLine("[F5] POE window not found");
                    ShowNotification("POE 게임이 실행 중이 아닙니다!");
                    return;
                }

                // 클립보드에 /hideout 명령어 복사
                Clipboard.SetText("/hideout");
                Debug.WriteLine("[F5] Copied '/hideout' to clipboard");

                // POE 창 활성화
                SetForegroundWindow(poeWindow);
                Thread.Sleep(50); // 창 활성화 대기

                // Enter 키 눌러서 채팅창 열기
                keybd_event(VK_RETURN, 0, 0, UIntPtr.Zero);
                keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(50);

                // Ctrl+V로 붙여넣기
                keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
                keybd_event(VK_V, 0, 0, UIntPtr.Zero);
                keybd_event(VK_V, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(50);

                // Enter 키 눌러서 명령어 실행
                keybd_event(VK_RETURN, 0, 0, UIntPtr.Zero);
                keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

                Debug.WriteLine("[F5] Hideout command sent to POE");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to execute hideout command: {ex.Message}");
            }
        }

        private void ExecuteThankYouCommand()
        {
            try
            {
                // POE 창 찾기
                IntPtr poeWindow = FindWindow(null, "Path of Exile");
                if (poeWindow == IntPtr.Zero)
                {
                    poeWindow = FindWindow(null, "Path of Exile 2");
                }

                if (poeWindow == IntPtr.Zero)
                {
                    return;
                }

                // POE 창 활성화
                SetForegroundWindow(poeWindow);
                Thread.Sleep(50);

                // 클립보드에 "ty @last" 복사
                Clipboard.SetText("ty @last");

                // Enter 키 (채팅 열기)
                keybd_event(VK_RETURN, 0, 0, UIntPtr.Zero);
                keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(50);

                // Ctrl+V (붙여넣기)
                keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
                keybd_event(VK_V, 0, 0, UIntPtr.Zero);
                keybd_event(VK_V, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(50);

                // Enter 키 (전송)
                keybd_event(VK_RETURN, 0, 0, UIntPtr.Zero);
                keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to execute thank you command: {ex.Message}");
            }
        }

        private async void ExecutePriceCheck()
        {
            try
            {
                await ExecutePriceCheckAsync();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ExecutePriceCheck] Error: {ex.Message}");
            }
        }

        private async Task ExecutePriceCheckAsync()
        {
            try
            {
                // 먼저 로딩 오버레이 표시
                Dispatcher.Invoke(() =>
                {
                    _priceOverlay?.Close();
                    _priceOverlay = new PathcraftAI.Overlay.PriceOverlayWindow();
                    // Trade 검색 콜백 설정
                    _priceOverlay.OnSearchRequested = async (selectedMods, searchRatio) =>
                    {
                        await HandleTradeSearchAsync(selectedMods, searchRatio);
                    };
                    _priceOverlay.ShowLoading("아이템 정보 복사 중...");
                    _priceOverlay.ShowAtCursor();
                });

                // POE 창 찾기 (Awakened처럼 Ctrl+C 자동 전송)
                IntPtr poeWindow = FindWindow(null, "Path of Exile");
                if (poeWindow == IntPtr.Zero)
                {
                    poeWindow = FindWindow(null, "Path of Exile 2");
                }

                if (poeWindow != IntPtr.Zero)
                {
                    // POE 창이 활성화되어 있으면 Ctrl+C 전송하여 아이템 복사
                    SetForegroundWindow(poeWindow);
                    await Task.Delay(100);

                    // 클립보드 초기화 (이전 내용 제거)
                    await Dispatcher.InvokeAsync(() =>
                    {
                        try { Clipboard.Clear(); } catch { }
                    });
                    await Task.Delay(50);

                    // Ctrl+C 전송
                    keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
                    keybd_event(VK_C, 0, 0, UIntPtr.Zero);
                    await Task.Delay(50);
                    keybd_event(VK_C, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                    keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

                    // 클립보드 업데이트 대기 (더 길게)
                    await Task.Delay(300);
                }

                // 클립보드에서 아이템 정보 읽기 (UI 스레드에서)
                string clipboardText = "";
                await Dispatcher.InvokeAsync(() =>
                {
                    try
                    {
                        if (Clipboard.ContainsText())
                        {
                            clipboardText = Clipboard.GetText();
                        }
                    }
                    catch { }
                });

                if (string.IsNullOrWhiteSpace(clipboardText))
                {
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError("오류", "클립보드가 비어있습니다"));
                    return;
                }

                // POE 아이템인지 확인 (영문: Rarity:/Item Class:, 한글: 희귀도:/아이템 종류:)
                bool isPoeItem = clipboardText.Contains("Rarity:") ||
                                 clipboardText.Contains("Item Class:") ||
                                 clipboardText.Contains("희귀도:") ||
                                 clipboardText.Contains("아이템 종류:");
                if (!isPoeItem)
                {
                    var preview = clipboardText.Length > 50 ? clipboardText.Substring(0, 50) + "..." : clipboardText;
                    LogDebug($"[Ctrl+D] Not POE item. Clipboard: {preview}");
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError("오류", $"POE 아이템이 아닙니다\n({preview.Replace("\n", " ").Replace("\r", "")})"));
                    return;
                }

                LogDebug($"[Ctrl+D] POE item detected, starting price check...");

                // 비동기로 가격 조회
                await CheckItemPriceAsync(clipboardText);
            }
            catch (Exception ex)
            {
                LogDebug($"[Ctrl+D] Error: {ex.Message}\n{ex.StackTrace}");
                await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError("오류", ex.Message));
            }
        }

        private async Task CheckItemPriceAsync(string clipboardText)
        {
            try
            {
                // 아이템 이름 추출 (Rarity/희귀도 다음 줄)
                var lines = clipboardText.Split('\n');
                string itemName = "아이템";
                bool foundRarity = false;
                foreach (var line in lines)
                {
                    // 영문/한글 클라이언트 모두 지원
                    if (line.StartsWith("Rarity:") || line.StartsWith("희귀도:"))
                    {
                        foundRarity = true;
                        continue;
                    }
                    if (foundRarity && !string.IsNullOrWhiteSpace(line) &&
                        !line.StartsWith("Item Class:") && !line.StartsWith("아이템 종류:"))
                    {
                        itemName = line.Trim();
                        break;
                    }
                }

                // 오버레이에 아이템 이름 업데이트
                await Dispatcher.InvokeAsync(() =>
                {
                    _priceOverlay?.ShowLoading(itemName);
                });

                // Python 스크립트로 가격 조회
                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                var priceCheckerScript = Path.Combine(parserDir!, "item_price_checker.py");

                LogDebug($"[Ctrl+D] Python path: {_pythonPath}");
                LogDebug($"[Ctrl+D] Script path: {priceCheckerScript}");
                LogDebug($"[Ctrl+D] Script exists: {File.Exists(priceCheckerScript)}");

                if (!File.Exists(priceCheckerScript))
                {
                    LogDebug($"[Ctrl+D] Script not found!");
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError(itemName, "시세 조회 스크립트를 찾을 수 없습니다."));
                    return;
                }

                // 클립보드 텍스트를 임시 파일로 저장 (특수문자 문제 회피)
                var tempFile = Path.Combine(Path.GetTempPath(), "poe_item_temp.txt");
                await File.WriteAllTextAsync(tempFile, clipboardText, System.Text.Encoding.UTF8);

                var result = await Task.Run(() =>
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = _pythonPath,
                        WorkingDirectory = parserDir,
                        RedirectStandardInput = true,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        StandardOutputEncoding = System.Text.Encoding.UTF8,
                        StandardErrorEncoding = System.Text.Encoding.UTF8,
                    };
                    psi.ArgumentList.Add(priceCheckerScript);

                    using var process = Process.Start(psi);
                    if (process == null)
                    {
                        return ("", "Failed to start Python process", -1);
                    }

                    // stdin으로 클립보드 내용 전달
                    process.StandardInput.Write(clipboardText);
                    process.StandardInput.Close();

                    var output = process.StandardOutput.ReadToEnd();
                    var errors = process.StandardError.ReadToEnd();
                    process.WaitForExit(10000);

                    return (output, errors, process.ExitCode);
                });

                // 디버깅 로그 (파일에 기록)
                if (!string.IsNullOrEmpty(result.Item2))
                {
                    LogDebug($"[Ctrl+D] Python stderr: {result.Item2}");
                }
                if (result.Item3 != 0)
                {
                    LogDebug($"[Ctrl+D] Python exit code: {result.Item3}");
                }

                var output = result.Item1;
                if (string.IsNullOrEmpty(output))
                {
                    LogDebug("[Ctrl+D] Empty result from Python script");
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError(itemName, "가격 조회 실패"));
                    return;
                }

                LogDebug($"[Ctrl+D] Python result: {output.Substring(0, Math.Min(500, output.Length))}...");

                // JSON 파싱 (stdout에서 JSON 부분만 추출)
                var jsonOutput = output.Trim();
                var jsonStart = jsonOutput.IndexOf('{');
                if (jsonStart > 0)
                {
                    jsonOutput = jsonOutput.Substring(jsonStart);
                }
                var json = JObject.Parse(jsonOutput);
                bool success = json["success"]?.Value<bool>() ?? false;

                if (!success)
                {
                    var error = json["error"]?.Value<string>() ?? "알 수 없는 오류";
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError(itemName, error));
                    return;
                }

                // 가격 정보 표시
                var item = json["item"];
                var price = json["price"];

                var priceInfo = new PathcraftAI.Overlay.PriceInfo
                {
                    ItemName = item?["name"]?.Value<string>() ?? itemName,
                    BaseType = item?["base_type"]?.Value<string>() ?? "",
                    ChaosPrice = price?["chaos"]?.Value<double>() ?? 0,
                    DivinePrice = price?["divine"]?.Value<double>() ?? 0,
                    DivineRate = price?["divine_rate"]?.Value<double>() ?? 150,
                    Note = price?["note"]?.Value<string>() ?? "",
                    Confidence = price?["confidence"]?.Value<string>() ?? "medium",
                    TradeUrl = price?["trade_url"]?.Value<string>(),
                    // Awakened PoE Trade 스타일 필드
                    UnitChaosPrice = price?["unit_chaos"]?.Value<double>() ?? 0,
                    StackSize = price?["stack_size"]?.Value<int>() ?? 1,
                    ItemsPerDivine = price?["items_per_divine"]?.Value<double>() ?? 0,
                };

                // 레어 아이템의 경우 모드 정보 추가
                var searchedMods = price?["searched_mods"] as JArray;
                if (searchedMods != null && searchedMods.Count > 0)
                {
                    priceInfo.SearchedMods = new System.Collections.Generic.List<PathcraftAI.Overlay.SearchedMod>();
                    foreach (var mod in searchedMods)
                    {
                        priceInfo.SearchedMods.Add(new PathcraftAI.Overlay.SearchedMod
                        {
                            Text = mod["text"]?.Value<string>() ?? "",
                            StatId = mod["stat_id"]?.Value<string>() ?? "",
                            Value = mod["value"]?.Value<double>() ?? 0,
                            MinSearch = mod["min_search"]?.Value<int?>(),
                            ModType = mod["mod_type"]?.Value<string>() ?? "explicit"
                        });
                    }
                }

                // Rate Limit 정보 추가
                var rateLimit = price?["rate_limit"];
                if (rateLimit != null)
                {
                    priceInfo.RateLimit = new PathcraftAI.Overlay.RateLimitInfo
                    {
                        Remaining = rateLimit["remaining"]?.Value<int>() ?? 10,
                        Total = rateLimit["total"]?.Value<int>() ?? 10,
                        IsBlocked = rateLimit["is_blocked"]?.Value<bool>() ?? false,
                        WaitSeconds = rateLimit["wait_seconds"]?.Value<int>() ?? 0,
                        Message = rateLimit["message"]?.Value<string>() ?? ""
                    };
                }

                LogDebug($"[Ctrl+D] Price found: {priceInfo.ChaosPrice}c, Divine: {priceInfo.DivinePrice}");

                // 레어/매직 아이템이면서 searched_mods가 있으면 모드만 표시 (가격 표시 안 함)
                if (priceInfo.SearchedMods != null && priceInfo.SearchedMods.Count > 0 &&
                    (priceInfo.ChaosPrice == 0 || priceInfo.Confidence == "pending"))
                {
                    // Rare/Magic item - show only mod checkboxes (no API call)
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowMods(
                        priceInfo.SearchedMods,
                        priceInfo.TradeUrl));
                }
                else
                {
                    // Unique/Currency/Normal - show price immediately
                    await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowPrice(priceInfo));
                }
            }
            catch (Exception ex)
            {
                LogDebug($"[Ctrl+D] CheckItemPriceAsync error: {ex.Message}\n{ex.StackTrace}");
                await Dispatcher.InvokeAsync(() => _priceOverlay?.ShowError("오류", ex.Message));
            }
        }

        /// <summary>
        /// Trade 검색 실행 (오버레이에서 버튼 클릭 시)
        /// </summary>
        private async Task HandleTradeSearchAsync(List<PathcraftAI.Overlay.ModItem> selectedMods, double searchRatio)
        {
            try
            {
                if (selectedMods.Count == 0)
                {
                    await Dispatcher.InvokeAsync(() =>
                    {
                        System.Windows.MessageBox.Show("검색할 모드를 선택해주세요.", "알림", MessageBoxButton.OK, MessageBoxImage.Information);
                    });
                    return;
                }

                Debug.WriteLine($"[Trade Search] Selected {selectedMods.Count} mods, ratio={searchRatio}");

                // 모드 정보를 JSON으로 변환
                var modsForSearch = new JArray();
                foreach (var mod in selectedMods)
                {
                    // Fractured 검색 여부에 따라 mod_type 결정
                    string modType = mod.IsFractured ? "fractured" : mod.ModType;

                    var modObj = new JObject
                    {
                        ["text"] = mod.OriginalText,
                        ["value"] = mod.Value,
                        ["min_search"] = searchRatio < 1.0 ? (int?)(mod.Value * searchRatio) : mod.MinSearch,
                        ["mod_type"] = modType
                    };
                    modsForSearch.Add(modObj);
                    Debug.WriteLine($"  - {mod.OriginalText} (value={mod.Value}, min={modObj["min_search"]}, type={modType})");
                }

                // Trade API 검색 URL 생성 (Python 스크립트 호출)
                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                var tradeApiScript = Path.Combine(parserDir!, "poe_trade_api.py");

                if (!File.Exists(tradeApiScript))
                {
                    Debug.WriteLine($"[Trade Search] Script not found: {tradeApiScript}");
                    return;
                }

                // 검색 요청 JSON 생성
                var searchRequest = new JObject
                {
                    ["mods"] = modsForSearch,
                    ["league"] = _currentLeague
                };

                var result = await Task.Run(() =>
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = _pythonPath,
                        WorkingDirectory = parserDir,
                        RedirectStandardInput = true,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        StandardOutputEncoding = System.Text.Encoding.UTF8,
                        StandardErrorEncoding = System.Text.Encoding.UTF8,
                    };
                    psi.ArgumentList.Add(tradeApiScript);
                    psi.ArgumentList.Add("--search-mods");  // Trade 검색 모드

                    using var process = Process.Start(psi);
                    if (process == null) return null;

                    // stdin으로 검색 요청 전달
                    process.StandardInput.Write(searchRequest.ToString());
                    process.StandardInput.Close();

                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit(15000);

                    if (!string.IsNullOrEmpty(error))
                    {
                        Debug.WriteLine($"[Trade Search] stderr: {error}");
                    }

                    return output;
                });

                if (!string.IsNullOrEmpty(result))
                {
                    Debug.WriteLine($"[Trade Search] Result: {result}");
                    var json = JObject.Parse(result);

                    // 검색 결과를 오버레이에 표시
                    await Dispatcher.InvokeAsync(() =>
                    {
                        if (_priceOverlay != null && _priceOverlay.IsVisible)
                        {
                            var searchResult = new TradeSearchResult
                            {
                                TradeUrl = json["trade_url"]?.Value<string>() ?? "",
                                TotalCount = json["total_count"]?.Value<int>() ?? 0,
                                MinPrice = json["min_price"]?.Value<double>(),
                                MaxPrice = json["max_price"]?.Value<double>(),
                                AvgPrice = json["avg_price"]?.Value<double>(),
                                RecommendedPrice = json["recommended_price"]?.Value<double>(),
                                PriceNote = json["price_note"]?.Value<string>()
                            };

                            _priceOverlay.ShowTradeSearchResult(searchResult);
                        }
                    });
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[Trade Search] Error: {ex.Message}");
            }
        }

        #region Leveling Guide

        private string _levelingGuideScriptPath = "";
        private string _currentMainSkillName = "";
        private string _currentClassName = "";
        private string _currentAscendancy = "";

        // LLM 레벨링 가이드 설정
        private bool _useLLMLevelingGuide = true;  // LLM 기반 사용 여부 (기본값: true)
        private string _llmProvider = "gemini";     // LLM 프로바이더 (gemini, claude, openai)
        private string _currentUserId = "anonymous"; // 사용자 ID (사용량 추적용)

        private async Task LoadLevelingGuide(string pobUrl)
        {
            try
            {
                // LLM 기반 레벨링 가이드 사용 (기본)
                if (_useLLMLevelingGuide)
                {
                    Debug.WriteLine($"[INFO] Using LLM-based leveling guide (provider: {_llmProvider})");

                    var llmResult = await Task.Run(() => RunLLMLevelingGuide(pobUrl, _currentUserId, _llmProvider));

                    if (!string.IsNullOrEmpty(llmResult))
                    {
                        try
                        {
                            var llmData = JObject.Parse(llmResult);

                            // 성공 시 LLM 가이드 표시
                            if (llmData["success"]?.ToObject<bool>() == true)
                            {
                                DisplayLLMLevelingGuide(llmData);
                                LevelingGuideExpander.Visibility = Visibility.Visible;
                                return;
                            }

                            // 실패 시 에러 로그 후 폴백
                            var errorMsg = llmData["error"]?.ToString() ?? "Unknown error";
                            Debug.WriteLine($"[WARN] LLM leveling guide failed: {errorMsg}, falling back to legacy system");
                        }
                        catch (Exception ex)
                        {
                            Debug.WriteLine($"[WARN] Failed to parse LLM result: {ex.Message}, falling back to legacy system");
                        }
                    }
                    else
                    {
                        Debug.WriteLine("[WARN] LLM leveling guide returned empty, falling back to legacy system");
                    }
                }

                // 폴백: 기존 skill_tag_system.py 기반 시스템
                Debug.WriteLine("[INFO] Using legacy skill_tag_system.py leveling guide");

                // skill_tag_system.py 스크립트 경로 설정
                if (string.IsNullOrEmpty(_levelingGuideScriptPath))
                {
                    var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                    _levelingGuideScriptPath = Path.Combine(parserDir!, "skill_tag_system.py");
                }

                if (!File.Exists(_levelingGuideScriptPath))
                {
                    Debug.WriteLine($"[WARNING] skill_tag_system.py not found at {_levelingGuideScriptPath}");
                    ShowLevelingGuideError("skill_tag_system.py 파일을 찾을 수 없습니다.");
                    return;
                }

                // 빌드 데이터 추출 (1순위: _currentUserBuild, 2순위: POB URL 파싱)
                string mainSkill = "";
                string className = "";
                string ascendancy = "";

                // 1순위: OAuth 연동된 사용자 빌드 데이터
                if (_currentUserBuild != null)
                {
                    mainSkill = _currentUserBuild["main_skill"]?.ToString() ?? "";
                    className = _currentUserBuild["class"]?.ToString() ?? "";
                    ascendancy = _currentUserBuild["ascendancy"]?.ToString() ?? "";

                    // main_skill이 없으면 gem_setups에서 추출
                    // gem_setups의 키는 라벨("Main Skill")이므로, links[0]에서 실제 스킬명 추출
                    if (string.IsNullOrEmpty(mainSkill))
                    {
                        var gemSetups = _currentUserBuild["gem_setups"] as JObject;
                        if (gemSetups != null && gemSetups.Count > 0)
                        {
                            var firstSetup = gemSetups.Properties().FirstOrDefault();
                            if (firstSetup != null)
                            {
                                var links = firstSetup.Value?["links"] as JArray;
                                mainSkill = links?.FirstOrDefault()?.ToString() ?? "";
                            }
                        }
                    }
                }

                // 2순위: POB URL에서 직접 파싱
                if (string.IsNullOrEmpty(mainSkill) && !string.IsNullOrEmpty(pobUrl))
                {
                    Debug.WriteLine($"[INFO] No user build data, parsing POB URL directly...");
                    var pobData = await Task.Run(() => ParsePobUrlForBuildInfo(pobUrl));
                    if (pobData != null)
                    {
                        mainSkill = pobData.MainSkill;
                        className = pobData.ClassName;
                        ascendancy = pobData.Ascendancy;
                        Debug.WriteLine($"[INFO] POB parsed: skill={mainSkill}, class={className}, asc={ascendancy}");
                    }
                }

                if (string.IsNullOrEmpty(mainSkill))
                {
                    ShowLevelingGuideError("빌드 데이터를 추출할 수 없습니다. POB URL을 확인해주세요.");
                    return;
                }

                Debug.WriteLine($"[INFO] Loading leveling guide for: {mainSkill}, {className}, {ascendancy}");

                // Python 스크립트 실행하여 레벨링 가이드 생성 (빌드 데이터 직접 전달)
                var result = await Task.Run(() => RunLevelingGuideScriptDirect(mainSkill, className, ascendancy));

                if (!string.IsNullOrEmpty(result))
                {
                    // 에러 JSON 체크
                    if (result.Contains("\"error\""))
                    {
                        var errorData = JObject.Parse(result);
                        var errorMsg = errorData["error"]?.ToString() ?? "Unknown error";
                        Debug.WriteLine($"[ERROR] Leveling guide error: {errorMsg}");
                        ShowLevelingGuideError($"레벨링 가이드 생성 실패: {errorMsg}");
                        return;
                    }

                    var guide = JObject.Parse(result);
                    DisplayLevelingGuide(guide);
                    LevelingGuideExpander.Visibility = Visibility.Visible;
                }
                else
                {
                    ShowLevelingGuideError("레벨링 가이드 데이터가 비어 있습니다.");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] LoadLevelingGuide: {ex.Message}");
                ShowLevelingGuideError($"레벨링 가이드 로드 오류: {ex.Message}");
            }
        }

        private void ShowLevelingGuideError(string message)
        {
            Dispatcher.Invoke(() =>
            {
                LevelingMainSkillText.Text = message;
                LevelingTagsText.Text = "";
                LevelingTipsList.ItemsSource = null;
                GemProgressionList.ItemsSource = null;
                LevelingGuideExpander.Visibility = Visibility.Visible;
            });
        }

        /// <summary>
        /// POB URL/Code에서 빌드 정보 추출을 위한 결과 클래스
        /// </summary>
        private class PobBuildInfo
        {
            public string MainSkill { get; set; } = "";
            public string ClassName { get; set; } = "";
            public string Ascendancy { get; set; } = "";
            public double Dps { get; set; } = 0;
            public double Ehp { get; set; } = 0;
            public List<string> SkillTags { get; set; } = new();
        }

        /// <summary>
        /// POB URL에서 빌드 정보 파싱 (메인 스킬, 클래스, 어센던시)
        /// </summary>
        private PobBuildInfo? ParsePobUrlForBuildInfo(string pobUrl)
        {
            // 디버그 로그 파일 경로
            var debugLogPath = Path.Combine(Path.GetTempPath(), "pathcraft_pob_debug.log");

            void WriteDebugLog(string message)
            {
                try
                {
                    var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                    File.AppendAllText(debugLogPath, $"[{timestamp}] {message}\n");
                    Debug.WriteLine($"[POB_DEBUG] {message}");
                }
                catch { /* 로그 실패는 무시 */ }
            }

            try
            {
                WriteDebugLog($"=== ParsePobUrlForBuildInfo START ===");
                WriteDebugLog($"Input URL: {pobUrl}");
                WriteDebugLog($"Python Path: {_pythonPath}");

                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                WriteDebugLog($"Parser Dir: {parserDir}");

                var tempScriptPath = Path.Combine(Path.GetTempPath(), "pob_quick_parse.py");

                // POB URL에서 빌드 정보만 빠르게 추출하는 Python 스크립트
                var pythonCode = $@"
import sys
import json
sys.path.insert(0, r'{parserDir}')

try:
    from pob_parser import get_pob_code_from_url, decode_pob_code, parse_pob_xml

    pob_url = r'{pobUrl.Replace("'", "\\'")}'

    # POB 코드 가져오기
    pob_code = get_pob_code_from_url(pob_url)
    if not pob_code:
        print(json.dumps({{'error': 'Failed to fetch POB code'}}))
        sys.exit(1)

    # XML 디코딩 (__XML_DIRECT__ 마커 처리)
    if pob_code.startswith('__XML_DIRECT__'):
        xml_data = pob_code[14:]  # 마커 제거, 직접 XML 사용
    else:
        xml_data = decode_pob_code(pob_code)
    if not xml_data:
        print(json.dumps({{'error': 'Failed to decode POB code'}}))
        sys.exit(1)

    # XML 파싱
    parsed = parse_pob_xml(xml_data, pob_url)
    if not parsed:
        print(json.dumps({{'error': 'Failed to parse POB XML'}}))
        sys.exit(1)

    # 메인 스킬 추출
    # gem_setups 구조: {{'스킬명': {{'links': '스킬1 - 스킬2 - ...', 'reasoning': None}}}}
    # 가장 많은 링크(서포트 젬)를 가진 스킬 그룹이 메인 스킬일 가능성 높음
    # 단, 트리거 서포트(CWDT, CoC 등) 포함 그룹은 제외
    main_skill = ''
    gem_setups = parsed.get('progression_stages', [{{}}])[0].get('gem_setups', {{}})
    if gem_setups:
        # 트리거 서포트 (이 서포트가 포함된 그룹은 메인 스킬이 아님)
        trigger_supports = ['Cast when Damage Taken', 'Cast On Critical Strike',
                           'Cast on Death', 'Manaforged Arrows', 'Automation']
        # 오라/저주/유틸리티 (메인 스킬이 아님)
        utility_skills = ['Grace', 'Determination', 'Hatred', 'Wrath', 'Anger',
                         'Purity of Elements', 'Zealotry', 'Malevolence', 'Pride',
                         'Frostbite', 'Despair', 'Enfeeble', 'Temporal Chains',
                         'Blood Rage', 'Steelskin', 'Molten Shell', 'Dash', 'Flame Dash',
                         'Portal', 'Clarity', 'Vitality', 'Discipline']

        max_links = 0
        best_skill = ''
        for key, value in gem_setups.items():
            links_str = value.get('links', '')
            if not links_str:
                continue

            # 트리거 서포트 포함 여부 확인
            has_trigger = any(t in links_str for t in trigger_supports)
            if has_trigger:
                continue

            gems = links_str.split(' - ')
            first_skill = gems[0].strip()

            # 유틸리티 스킬 제외
            if first_skill in utility_skills:
                continue

            link_count = len(gems)
            if link_count > max_links:
                max_links = link_count
                best_skill = first_skill

        # 필터링 후에도 스킬이 없으면 가장 많은 링크의 첫 스킬 사용
        if not best_skill:
            for key, value in gem_setups.items():
                links_str = value.get('links', '')
                if links_str:
                    gems = links_str.split(' - ')
                    if len(gems) > max_links:
                        max_links = len(gems)
                        best_skill = gems[0].strip()

        main_skill = best_skill if best_skill else list(gem_setups.keys())[0]

    # 결과 출력
    result = {{
        'main_skill': main_skill,
        'class_name': parsed.get('meta', {{}}).get('class', ''),
        'ascendancy': parsed.get('meta', {{}}).get('ascendancy', ''),
        'dps': parsed.get('stats', {{}}).get('dps', 0),
        'ehp': parsed.get('stats', {{}}).get('ehp', 0)
    }}
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    import traceback
    print(json.dumps({{'error': str(e), 'trace': traceback.format_exc()}}))
    sys.exit(1)
";

                File.WriteAllText(tempScriptPath, pythonCode, System.Text.Encoding.UTF8);
                WriteDebugLog($"Temp script written: {tempScriptPath}");
                WriteDebugLog($"Script size: {pythonCode.Length} chars");

                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = $"\"{tempScriptPath}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8,
                    WorkingDirectory = parserDir
                };

                psi.Environment["PYTHONUTF8"] = "1";

                WriteDebugLog("Starting Python process...");
                using var process = Process.Start(psi);
                if (process == null)
                {
                    WriteDebugLog("[ERROR] Failed to start Python process");
                    return null;
                }
                WriteDebugLog($"Process started, PID: {process.Id}");

                // 데드락 방지: stdout/stderr를 비동기로 읽기
                var outputTask = process.StandardOutput.ReadToEndAsync();
                var errorTask = process.StandardError.ReadToEndAsync();

                // 30초 타임아웃
                WriteDebugLog("Waiting for process (30s timeout)...");
                if (!process.WaitForExit(30000))
                {
                    WriteDebugLog("[ERROR] Process timed out after 30 seconds, killing...");
                    try { process.Kill(); } catch { }
                    return null;
                }

                var output = outputTask.Result;
                var error = errorTask.Result;

                WriteDebugLog($"Process exited, ExitCode: {process.ExitCode}");
                WriteDebugLog($"stdout length: {output?.Length ?? 0}");
                WriteDebugLog($"stderr length: {error?.Length ?? 0}");

                if (!string.IsNullOrEmpty(error))
                {
                    // stderr 처음 500자만 로그
                    var errorPreview = error.Length > 500 ? error.Substring(0, 500) + "..." : error;
                    WriteDebugLog($"stderr preview: {errorPreview}");
                }

                if (!string.IsNullOrEmpty(output))
                {
                    // stdout 처음 500자만 로그
                    var outputPreview = output.Length > 500 ? output.Substring(0, 500) + "..." : output;
                    WriteDebugLog($"stdout preview: {outputPreview}");
                }

                if (process.ExitCode != 0)
                {
                    WriteDebugLog($"[ERROR] Non-zero exit code: {process.ExitCode}");
                    return null;
                }

                if (string.IsNullOrEmpty(output))
                {
                    WriteDebugLog("[ERROR] Empty stdout");
                    return null;
                }

                WriteDebugLog("Parsing JSON output...");

                // stdout에서 JSON 부분만 추출 (로그 메시지 무시)
                var jsonOutput = output.Trim();
                var jsonStart = jsonOutput.IndexOf('{');
                if (jsonStart > 0)
                {
                    WriteDebugLog($"JSON extraction: found '{{' at position {jsonStart}");
                    jsonOutput = jsonOutput.Substring(jsonStart);
                }

                var json = JObject.Parse(jsonOutput);

                if (json["error"] != null)
                {
                    WriteDebugLog($"[ERROR] JSON contains error: {json["error"]}");
                    if (json["trace"] != null)
                    {
                        WriteDebugLog($"[ERROR] Traceback: {json["trace"]}");
                    }
                    return null;
                }

                var result = new PobBuildInfo
                {
                    MainSkill = json["main_skill"]?.ToString() ?? "",
                    ClassName = json["class_name"]?.ToString() ?? "",
                    Ascendancy = json["ascendancy"]?.ToString() ?? "",
                    Dps = json["dps"]?.Value<double>() ?? 0,
                    Ehp = json["ehp"]?.Value<double>() ?? 0
                };

                WriteDebugLog($"[SUCCESS] Parsed: MainSkill={result.MainSkill}, Class={result.ClassName}, Ascendancy={result.Ascendancy}");
                WriteDebugLog($"=== ParsePobUrlForBuildInfo END (SUCCESS) ===");
                return result;
            }
            catch (Exception ex)
            {
                // catch 블록에서도 로그 작성
                try
                {
                    var exLogPath = Path.Combine(Path.GetTempPath(), "pathcraft_pob_debug.log");
                    var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                    File.AppendAllText(exLogPath, $"[{timestamp}] [EXCEPTION] {ex.GetType().Name}: {ex.Message}\n");
                    File.AppendAllText(exLogPath, $"[{timestamp}] [EXCEPTION] StackTrace: {ex.StackTrace}\n");
                    File.AppendAllText(exLogPath, $"[{timestamp}] === ParsePobUrlForBuildInfo END (EXCEPTION) ===\n");
                }
                catch { }

                Debug.WriteLine($"[ERROR] ParsePobUrlForBuildInfo: {ex.Message}");
                return null;
            }
        }

        private string RunLevelingGuideScriptDirect(string mainSkill, string className, string ascendancy)
        {
            // 디버그 로그 파일
            var debugLogPath = Path.Combine(Path.GetTempPath(), "pathcraft_leveling_debug.log");
            void WriteDebugLog(string message)
            {
                try
                {
                    var timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
                    File.AppendAllText(debugLogPath, $"[{timestamp}] {message}\n");
                }
                catch { }
            }

            WriteDebugLog("========== RunLevelingGuideScriptDirect START ==========");
            WriteDebugLog($"mainSkill: {mainSkill}");
            WriteDebugLog($"className: {className}");
            WriteDebugLog($"ascendancy: {ascendancy}");

            // 빌드 데이터를 직접 받아서 레벨링 가이드 생성 (POB URL 파싱 없음)
            if (string.IsNullOrEmpty(mainSkill))
            {
                WriteDebugLog("[ERROR] No main skill provided");
                return "{\"error\": \"No main skill provided\"}";
            }

            Debug.WriteLine($"[INFO] Generating leveling guide for: {mainSkill}, {className}, {ascendancy}");

            var tempScriptPath = Path.Combine(Path.GetTempPath(), "leveling_guide_fallback.py");
            var pythonCode = $@"
import sys
import json
sys.path.insert(0, r'{Path.GetDirectoryName(_levelingGuideScriptPath)}')
from skill_tag_system import SkillTagSystem, ActGuideSearcher

try:
    skill_system = SkillTagSystem()
    searcher = ActGuideSearcher(skill_system)
    guide = searcher.generate_leveling_guide_summary('{mainSkill}', '{className}', '{ascendancy}', korean=True)

    ui_guide = {{
        'skill_name': guide.get('skill_name_kr', '{mainSkill}'),
        'skill_name_en': '{mainSkill}',
        'class_name': '{className}',
        'ascendancy': '{ascendancy}',
        'tags': guide.get('tags', []),
        'tips': guide.get('tips_kr', guide.get('tips', [])),
        'gem_progression': guide.get('gem_progression', []),
        'leveling_gear': guide.get('leveling_gear_kr', guide.get('leveling_gear', [])),
        'ascendancy_order': guide.get('ascendancy_order', []),
        'transition_info': guide.get('transition_info', None)
    }}

    print(json.dumps(ui_guide, ensure_ascii=False))
except Exception as e:
    import traceback
    print(json.dumps({{'error': str(e), 'trace': traceback.format_exc()}}))
    sys.exit(1)
";

            File.WriteAllText(tempScriptPath, pythonCode, System.Text.Encoding.UTF8);

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{tempScriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(_levelingGuideScriptPath)
            };

            psi.Environment["PYTHONUTF8"] = "1";
            psi.StandardErrorEncoding = System.Text.Encoding.UTF8;

            WriteDebugLog($"Python path: {_pythonPath}");
            WriteDebugLog($"Script path: {tempScriptPath}");
            WriteDebugLog($"Working directory: {Path.GetDirectoryName(_levelingGuideScriptPath)}");

            using var process = Process.Start(psi);
            if (process == null)
            {
                WriteDebugLog("[ERROR] Failed to start Python process");
                Debug.WriteLine("[ERROR] Failed to start Python process for leveling guide");
                return string.Empty;
            }

            WriteDebugLog($"Process started, PID: {process.Id}");

            // 데드락 방지: stdout/stderr 비동기 읽기
            var outputTask = process.StandardOutput.ReadToEndAsync();
            var errorTask = process.StandardError.ReadToEndAsync();

            // 30초 타임아웃
            if (!process.WaitForExit(30000))
            {
                WriteDebugLog("[ERROR] Process timed out after 30 seconds");
                Debug.WriteLine("[ERROR] Leveling guide process timed out");
                try { process.Kill(); } catch { }
                return string.Empty;
            }

            var output = outputTask.Result;
            var error = errorTask.Result;

            WriteDebugLog($"Exit code: {process.ExitCode}");
            WriteDebugLog($"stdout length: {output?.Length ?? 0}");
            WriteDebugLog($"stderr length: {error?.Length ?? 0}");
            WriteDebugLog($"stdout preview: {(output?.Length > 500 ? output.Substring(0, 500) + "..." : output)}");
            WriteDebugLog($"stderr: {error}");

            if (!string.IsNullOrEmpty(error))
            {
                Debug.WriteLine($"[DEBUG] Leveling guide stderr: {error}");
            }

            if (process.ExitCode != 0)
            {
                WriteDebugLog($"[ERROR] Non-zero exit code: {process.ExitCode}");
                Debug.WriteLine($"[ERROR] Leveling guide fallback error (exit={process.ExitCode}): {error}");
                return string.Empty;
            }

            WriteDebugLog("[SUCCESS] Process completed successfully");
            WriteDebugLog("========== RunLevelingGuideScriptDirect END ==========");
            return output?.Trim() ?? string.Empty;
        }

        /// <summary>
        /// LLM 기반 레벨링 가이드 생성 (Claude/GPT/Gemini)
        /// </summary>
        /// <param name="pobUrl">POB URL</param>
        /// <param name="userId">사용자 ID (사용량 추적용)</param>
        /// <param name="provider">LLM 프로바이더 (claude, openai, gemini)</param>
        /// <returns>JSON 결과 문자열</returns>
        private string RunLLMLevelingGuide(string pobUrl, string userId = "anonymous", string provider = "gemini")
        {
            var debugLogPath = Path.Combine(Path.GetTempPath(), "pathcraft_llm_leveling_debug.log");
            void WriteDebugLog(string message)
            {
                try
                {
                    var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                    File.AppendAllText(debugLogPath, $"[{timestamp}] {message}\n");
                    Debug.WriteLine($"[LLM_LEVELING] {message}");
                }
                catch { }
            }

            WriteDebugLog("========== RunLLMLevelingGuide START ==========");
            WriteDebugLog($"pobUrl: {pobUrl}");
            WriteDebugLog($"userId: {userId}");
            WriteDebugLog($"provider: {provider}");

            try
            {
                var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                var llmScriptPath = Path.Combine(parserDir!, "leveling_guide_llm.py");

                if (!File.Exists(llmScriptPath))
                {
                    WriteDebugLog($"[ERROR] LLM script not found: {llmScriptPath}");
                    return new JObject { ["error"] = "leveling_guide_llm.py not found" }.ToString();
                }

                WriteDebugLog($"LLM Script Path: {llmScriptPath}");

                // Python 스크립트 실행
                var psi = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = $"\"{llmScriptPath}\" --url \"{pobUrl}\" --provider {provider} --user \"{userId}\" --json",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8,
                    WorkingDirectory = parserDir
                };

                psi.Environment["PYTHONUTF8"] = "1";
                psi.Environment["PYTHONIOENCODING"] = "utf-8";

                WriteDebugLog($"Starting Python process: {_pythonPath} {psi.Arguments}");

                using var process = Process.Start(psi);
                if (process == null)
                {
                    WriteDebugLog("[ERROR] Failed to start Python process");
                    return new JObject { ["error"] = "Failed to start Python process" }.ToString();
                }

                WriteDebugLog($"Process started, PID: {process.Id}");

                // 비동기 읽기로 데드락 방지
                var outputTask = process.StandardOutput.ReadToEndAsync();
                var errorTask = process.StandardError.ReadToEndAsync();

                // 60초 타임아웃 (LLM 호출은 시간이 걸림)
                if (!process.WaitForExit(60000))
                {
                    WriteDebugLog("[ERROR] Process timed out after 60 seconds");
                    try { process.Kill(); } catch { }
                    return new JObject { ["error"] = "LLM request timed out" }.ToString();
                }

                var output = outputTask.Result;
                var error = errorTask.Result;

                WriteDebugLog($"Exit code: {process.ExitCode}");
                WriteDebugLog($"Output length: {output?.Length ?? 0}");
                if (!string.IsNullOrEmpty(error))
                {
                    WriteDebugLog($"Stderr: {error}");
                }

                if (process.ExitCode != 0)
                {
                    WriteDebugLog($"[ERROR] Non-zero exit code: {process.ExitCode}");
                    return new JObject { ["error"] = $"Script failed: {error}" }.ToString();
                }

                WriteDebugLog("[SUCCESS] LLM leveling guide generated");
                WriteDebugLog("========== RunLLMLevelingGuide END ==========");

                // stdout에서 JSON 부분만 추출 (로그 메시지 무시)
                if (!string.IsNullOrEmpty(output))
                {
                    var jsonStart = output.IndexOf('{');
                    if (jsonStart >= 0)
                    {
                        WriteDebugLog($"JSON extraction: found '{{' at position {jsonStart}");
                        return output.Substring(jsonStart);
                    }
                }
                return "";
            }
            catch (Exception ex)
            {
                WriteDebugLog($"[ERROR] Exception: {ex.Message}");
                return new JObject { ["error"] = ex.Message }.ToString();
            }
        }

        /// <summary>
        /// LLM 레벨링 가이드 결과를 UI에 표시
        /// </summary>
        private void DisplayLLMLevelingGuide(JObject result)
        {
            try
            {
                if (result["success"]?.ToObject<bool>() != true)
                {
                    var errorMsg = result["error"]?.ToString() ?? "Unknown error";
                    ShowLevelingGuideError($"LLM 레벨링 가이드 생성 실패: {errorMsg}");
                    return;
                }

                var buildInfo = result["build_info"] as JObject;
                var guide = result["leveling_guide"] as JObject;
                var provider = result["provider"]?.ToString() ?? "unknown";
                var cached = result["cached"]?.ToObject<bool>() ?? false;

                if (buildInfo != null)
                {
                    var skillName = buildInfo["main_skill"]?.ToString() ?? "Unknown";
                    var className = buildInfo["class"]?.ToString() ?? "";
                    var ascendancy = buildInfo["ascendancy"]?.ToString() ?? "";

                    _currentMainSkillName = skillName;
                    _currentClassName = className;
                    _currentAscendancy = ascendancy;

                    var cacheIndicator = cached ? " [캐시]" : "";
                    LevelingMainSkillText.Text = $"Main Skill: {skillName} ({provider}{cacheIndicator})";

                    var dps = buildInfo["dps"]?.ToObject<double>() ?? 0;
                    var ehp = buildInfo["ehp"]?.ToObject<double>() ?? 0;
                    LevelingTagsText.Text = $"Class: {className} / {ascendancy} | DPS: {dps:N0} | EHP: {ehp:N0}";
                }

                if (guide != null)
                {
                    // Leveling Stages → Gem Progression 형식으로 변환
                    var stages = guide["leveling_stages"] as JArray;
                    if (stages != null)
                    {
                        var gemList = new List<GemProgressionItem>();
                        var tipsList = new List<string>();

                        foreach (var stage in stages)
                        {
                            var levelRange = stage["level_range"]?.ToString() ?? "?";
                            var mainSkill = stage["main_skill"]?.ToString() ?? "";
                            var supports = stage["support_gems"] as JArray;
                            var tips = stage["tips"]?.ToString() ?? "";

                            // Gem Progression 항목 추가
                            var gemsStr = mainSkill;
                            if (supports != null && supports.Count > 0)
                            {
                                gemsStr += " + " + string.Join(", ", supports.Select(s => s.ToString()));
                            }

                            // level_range에서 시작 레벨 추출 (예: "1-12" → 1)
                            var startLevel = 1;
                            if (levelRange.Contains("-"))
                            {
                                int.TryParse(levelRange.Split('-')[0], out startLevel);
                            }

                            gemList.Add(new GemProgressionItem
                            {
                                Level = startLevel,
                                Gems = $"[{levelRange}] {gemsStr}"
                            });

                            // Tips 추가
                            if (!string.IsNullOrEmpty(tips))
                            {
                                tipsList.Add($"• [{levelRange}] {tips}");
                            }
                        }

                        GemProgressionList.ItemsSource = gemList;
                        LevelingTipsList.ItemsSource = tipsList;
                    }

                    // Gear Tips
                    var gearTips = guide["gear_tips"]?.ToString();
                    if (!string.IsNullOrEmpty(gearTips))
                    {
                        var gearList = new List<LevelingGearItem>
                        {
                            new LevelingGearItem { Level = 1, Item = "장비 팁", Reason = gearTips }
                        };
                        LevelingGearList.ItemsSource = gearList;
                    }

                    // Passive Priority
                    var passivePriority = guide["passive_priority"]?.ToString();
                    if (!string.IsNullOrEmpty(passivePriority))
                    {
                        AscendancyOrderList.ItemsSource = new List<string> { $"패시브: {passivePriority}" };
                    }
                }

                LevelingGuideExpander.Visibility = Visibility.Visible;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] DisplayLLMLevelingGuide: {ex.Message}");
                ShowLevelingGuideError($"LLM 가이드 표시 오류: {ex.Message}");
            }
        }

        private void DisplayLevelingGuide(JObject guideData)
        {
            try
            {
                // 메인 스킬 정보
                var skillName = guideData["skill_name"]?.ToString() ?? "Unknown";
                var className = guideData["class_name"]?.ToString() ?? "Unknown";
                var ascendancy = guideData["ascendancy"]?.ToString() ?? "";
                var tags = guideData["tags"] as JArray;

                _currentMainSkillName = skillName;
                _currentClassName = className;
                _currentAscendancy = ascendancy;

                LevelingMainSkillText.Text = $"Main Skill: {skillName}";

                if (tags != null && tags.Count > 0)
                {
                    var tagList = tags.Select(t => t.ToString()).ToList();
                    LevelingTagsText.Text = $"Tags: {string.Join(", ", tagList)}";
                }

                // Tips
                var tips = guideData["tips"] as JArray;
                if (tips != null)
                {
                    var tipsList = tips.Select(t => $"• {t}").ToList();
                    LevelingTipsList.ItemsSource = tipsList;
                }

                // Gem Progression
                var gemProg = guideData["gem_progression"] as JArray;
                if (gemProg != null)
                {
                    var gemList = new List<GemProgressionItem>();
                    foreach (var gem in gemProg)
                    {
                        gemList.Add(new GemProgressionItem
                        {
                            Level = gem["level"]?.ToObject<int>() ?? 0,
                            Gems = gem["gems"]?.ToString() ?? ""
                        });
                    }
                    GemProgressionList.ItemsSource = gemList;
                }

                // Leveling Gear
                var gearRec = guideData["leveling_gear"] as JArray;
                if (gearRec != null)
                {
                    var gearList = new List<LevelingGearItem>();
                    foreach (var gear in gearRec)
                    {
                        gearList.Add(new LevelingGearItem
                        {
                            Level = gear["level"]?.ToObject<int>() ?? 0,
                            Item = gear["item"]?.ToString() ?? "",
                            Reason = gear["reason"]?.ToString() ?? ""
                        });
                    }
                    LevelingGearList.ItemsSource = gearList;
                }

                // Ascendancy Order
                var ascOrder = guideData["ascendancy_order"] as JArray;
                if (ascOrder != null)
                {
                    var orderList = new List<string>();
                    for (int i = 0; i < ascOrder.Count; i++)
                    {
                        orderList.Add($"{i + 1}. {ascOrder[i]}");
                    }
                    AscendancyOrderList.ItemsSource = orderList;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] DisplayLevelingGuide: {ex.Message}");
            }
        }

        private void OpenYouTubeGuide_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var skillName = _currentMainSkillName;
                var className = _currentClassName;

                if (string.IsNullOrEmpty(skillName))
                {
                    skillName = "Penance Brand";
                }

                // YouTube 검색 URL 생성
                var searchQuery = $"{skillName} {className} leveling guide POE 3.27";
                var encodedQuery = Uri.EscapeDataString(searchQuery);
                var youtubeUrl = $"https://www.youtube.com/results?search_query={encodedQuery}";

                Process.Start(new ProcessStartInfo
                {
                    FileName = youtubeUrl,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] OpenYouTubeGuide: {ex.Message}");
            }
        }

        #endregion

        #region Leveling Guide Data Classes

        public class GemProgressionItem
        {
            public int Level { get; set; }
            public string Gems { get; set; } = "";
        }

        public class LevelingGearItem
        {
            public int Level { get; set; }
            public string Item { get; set; } = "";
            public string Reason { get; set; } = "";
        }

        #endregion

        #region Farming Strategy

        private string _farmingStrategyScriptPath = "";

        private async Task LoadFarmingStrategy(string pobUrl)
        {
            try
            {
                // farming_strategy_system.py 스크립트 경로 설정
                if (string.IsNullOrEmpty(_farmingStrategyScriptPath))
                {
                    var parserDir = Path.GetDirectoryName(_filterGeneratorScriptPath);
                    _farmingStrategyScriptPath = Path.Combine(parserDir!, "farming_strategy_system.py");
                }

                if (!File.Exists(_farmingStrategyScriptPath))
                {
                    Debug.WriteLine($"[WARNING] farming_strategy_system.py not found at {_farmingStrategyScriptPath}");
                    return;
                }

                // 빌드 데이터 추출 (1순위: _currentUserBuild, 2순위: POB URL 파싱)
                double dps = 0;
                double ehp = 0;
                string mainSkill = "";
                var skillTags = new List<string>();

                // 1순위: OAuth 연동된 사용자 빌드 데이터
                if (_currentUserBuild != null)
                {
                    // DPS 추출
                    var dpsValue = _currentUserBuild["dps"]?.ToString();
                    if (!string.IsNullOrEmpty(dpsValue))
                        double.TryParse(dpsValue, out dps);

                    // EHP 추출 (life + energy_shield)
                    var lifeValue = _currentUserBuild["life"]?.ToString();
                    var esValue = _currentUserBuild["energy_shield"]?.ToString();
                    double.TryParse(lifeValue ?? "0", out double life);
                    double.TryParse(esValue ?? "0", out double es);
                    ehp = Math.Max(life, es) * (es > life ? 1.5 : 1);

                    // 메인 스킬 추출
                    // gem_setups의 키는 라벨("Main Skill")이므로, links[0]에서 실제 스킬명 추출
                    mainSkill = _currentUserBuild["main_skill"]?.ToString() ?? "";
                    if (string.IsNullOrEmpty(mainSkill))
                    {
                        var gemSetups = _currentUserBuild["gem_setups"] as JObject;
                        if (gemSetups != null && gemSetups.Count > 0)
                        {
                            var firstSetup = gemSetups.Properties().FirstOrDefault();
                            if (firstSetup != null)
                            {
                                var links = firstSetup.Value?["links"] as JArray;
                                mainSkill = links?.FirstOrDefault()?.ToString() ?? "";
                            }
                        }
                    }

                    // 스킬 태그 추출
                    var tagsArray = _currentUserBuild["tags"] as JArray;
                    if (tagsArray != null)
                    {
                        skillTags = tagsArray.Select(t => t.ToString()).ToList();
                    }
                }

                // 2순위: POB URL에서 직접 파싱
                if (string.IsNullOrEmpty(mainSkill) && !string.IsNullOrEmpty(pobUrl))
                {
                    Debug.WriteLine($"[INFO] No user build data for farming, parsing POB URL directly...");
                    var pobData = await Task.Run(() => ParsePobUrlForBuildInfo(pobUrl));
                    if (pobData != null)
                    {
                        mainSkill = pobData.MainSkill;
                        dps = pobData.Dps;
                        ehp = pobData.Ehp;
                        Debug.WriteLine($"[INFO] POB parsed for farming: skill={mainSkill}, dps={dps}, ehp={ehp}");
                    }
                }

                if (string.IsNullOrEmpty(mainSkill) && dps == 0)
                {
                    Debug.WriteLine("[WARNING] No build data for farming strategy");
                    return;
                }

                Debug.WriteLine($"[INFO] Loading farming strategy for: DPS={dps}, EHP={ehp}, Skill={mainSkill}");

                // Python 스크립트 실행하여 파밍 전략 생성 (빌드 데이터 직접 전달)
                var result = await Task.Run(() => RunFarmingStrategyScriptDirect(dps, ehp, mainSkill, skillTags));

                if (!string.IsNullOrEmpty(result))
                {
                    var guideData = JObject.Parse(result);
                    DisplayFarmingStrategy(guideData);
                    FarmingStrategyExpander.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] LoadFarmingStrategy: {ex.Message}");
            }
        }

        private string RunFarmingStrategyScriptDirect(double dps, double ehp, string mainSkill, List<string> skillTags)
        {
            // 빌드 데이터를 직접 받아서 파밍 전략 생성 (POB URL 파싱 없음)
            var tempScriptPath = Path.Combine(Path.GetTempPath(), "farming_strategy_temp.py");
            var tagsJson = string.Join("\", \"", skillTags);
            if (!string.IsNullOrEmpty(tagsJson)) tagsJson = $"\"{tagsJson}\"";

            var pythonCode = $@"
import sys
import json
sys.path.insert(0, r'{Path.GetDirectoryName(_farmingStrategyScriptPath)}')
from farming_strategy_system import FarmingStrategySystem

# 빌드 정보 (C#에서 직접 전달받음)
build_info = {{
    'dps': {dps},
    'ehp': {ehp},
    'life_regen': 0,
    'skill_tags': [{tagsJson}],
    'main_skill': '{mainSkill}',
    'budget': 'medium'
}}

try:
    system = FarmingStrategySystem()
    guide = system.generate_farming_guide(build_info)
    print(json.dumps(guide, ensure_ascii=False))
except Exception as e:
    import traceback
    print(json.dumps({{'error': str(e), 'trace': traceback.format_exc()}}))
    sys.exit(1)
";

            File.WriteAllText(tempScriptPath, pythonCode, System.Text.Encoding.UTF8);

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{tempScriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                WorkingDirectory = Path.GetDirectoryName(_farmingStrategyScriptPath)
            };

            psi.Environment["PYTHONUTF8"] = "1";

            using var process = Process.Start(psi);
            if (process == null) return string.Empty;

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                Debug.WriteLine($"[ERROR] Farming strategy script error: {error}");
                return string.Empty;
            }

            return output.Trim();
        }

        private void DisplayFarmingStrategy(JObject guideData)
        {
            try
            {
                // 빌드 태그
                var buildTags = guideData["build_tags"] as JArray;
                if (buildTags != null && buildTags.Count > 0)
                {
                    FarmingBuildTagsText.Text = string.Join(", ", buildTags.Select(t => t.ToString()));
                }

                // 전략 목록
                var strategies = guideData["recommended_strategies"] as JArray;
                if (strategies != null)
                {
                    var strategyList = new List<FarmingStrategyItem>();
                    foreach (var strategy in strategies)
                    {
                        var maps = strategy["maps"] as JArray;
                        var mapList = new List<FarmingMapItem>();
                        if (maps != null)
                        {
                            foreach (var map in maps)
                            {
                                mapList.Add(new FarmingMapItem
                                {
                                    Name = map["name"]?.ToString() ?? "",
                                    Tier = map["tier"]?.ToObject<int>() ?? 0,
                                    Layout = map["layout"]?.ToString() ?? ""
                                });
                            }
                        }

                        var atlasPassives = strategy["atlas_passives"] as JArray;
                        var passiveList = atlasPassives?.Select(p => p.ToString()).ToList() ?? new List<string>();

                        var tips = strategy["tips"] as JArray;
                        var tipList = tips?.Select(t => $"• {t}").ToList() ?? new List<string>();

                        strategyList.Add(new FarmingStrategyItem
                        {
                            Name = strategy["name"]?.ToString() ?? "",
                            Description = strategy["description"]?.ToString() ?? "",
                            InvestmentDisplay = $"Investment: {strategy["investment"]}",
                            ReturnsDisplay = $"Returns: {strategy["returns"]}",
                            Maps = mapList,
                            AtlasPassives = passiveList,
                            Tips = tipList
                        });
                    }
                    FarmingStrategiesList.ItemsSource = strategyList;
                }

                // 일반 팁
                var generalTips = guideData["general_tips"] as JArray;
                if (generalTips != null)
                {
                    var tipList = generalTips.Select(t => $"• {t}").ToList();
                    FarmingGeneralTipsList.ItemsSource = tipList;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] DisplayFarmingStrategy: {ex.Message}");
            }
        }

        #endregion

        #region Farming Strategy Data Classes

        public class FarmingStrategyItem
        {
            public string Name { get; set; } = "";
            public string Description { get; set; } = "";
            public string InvestmentDisplay { get; set; } = "";
            public string ReturnsDisplay { get; set; } = "";
            public List<FarmingMapItem> Maps { get; set; } = new();
            public List<string> AtlasPassives { get; set; } = new();
            public List<string> Tips { get; set; } = new();
        }

        public class FarmingMapItem
        {
            public string Name { get; set; } = "";
            public int Tier { get; set; }
            public string Layout { get; set; } = "";
        }

        #endregion

        private void ShowNotification(string message, bool isError = false, bool isWarning = false)
        {
            // 간단한 토스트 알림 (향후 개선 가능)
            Dispatcher.Invoke(() =>
            {
                Color bgColor;
                if (isError)
                    bgColor = Color.FromArgb(200, 180, 0, 0);    // Red for errors
                else if (isWarning)
                    bgColor = Color.FromArgb(200, 180, 120, 0);  // Orange for warnings
                else
                    bgColor = Color.FromArgb(200, 0, 0, 0);      // Black for normal

                var notification = new System.Windows.Controls.TextBlock
                {
                    Text = message,
                    Foreground = Brushes.White,
                    Background = new SolidColorBrush(bgColor),
                    Padding = new Thickness(10),
                    FontSize = 14,
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Top,
                    Margin = new Thickness(0, 20, 0, 0)
                };

                // MainWindow의 Grid에 추가 (첫 번째 Grid 찾기)
                var grid = Content as System.Windows.Controls.Grid;
                if (grid != null)
                {
                    grid.Children.Add(notification);

                    // 에러는 4초, 일반은 2초 후 제거
                    var duration = isError ? 4 : 2;
                    var timer = new System.Windows.Threading.DispatcherTimer
                    {
                        Interval = TimeSpan.FromSeconds(duration)
                    };
                    timer.Tick += (s, e) =>
                    {
                        grid.Children.Remove(notification);
                        timer.Stop();
                    };
                    timer.Start();
                }
            });
        }

        #region Backup System

        /// <summary>
        /// 앱 종료 시 자동 백업
        /// </summary>
        private void MainWindow_Closing(object? sender, System.ComponentModel.CancelEventArgs e)
        {
            try
            {
                // 설정에서 자동 백업 여부 확인
                var settings = AppSettings.Load();
                if (settings.AutoBackupOnExit)
                {
                    Debug.WriteLine("[BACKUP] Creating auto backup on exit...");
                    var backupService = new BackupService(maxBackups: 5);
                    var result = backupService.CreateBackup("앱 종료 시 자동 백업");

                    if (result.Success)
                    {
                        Debug.WriteLine($"[BACKUP] Auto backup created: {result.BackupPath} ({result.BackupSize} bytes)");
                    }
                    else
                    {
                        Debug.WriteLine($"[BACKUP] Auto backup failed: {result.ErrorMessage}");
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[BACKUP] Error during auto backup: {ex.Message}");
                // 백업 실패해도 앱 종료는 허용
            }
        }

        /// <summary>
        /// 수동 백업 생성
        /// </summary>
        public void CreateManualBackup()
        {
            try
            {
                var backupService = new BackupService(maxBackups: 5);
                var result = backupService.CreateBackup("수동 백업");

                if (result.Success)
                {
                    MessageBox.Show(
                        $"백업이 성공적으로 생성되었습니다.\n\n" +
                        $"위치: {result.BackupPath}\n" +
                        $"크기: {result.BackupSize / 1024.0:F1} KB\n" +
                        $"항목: {result.BackedUpItems.Count}개",
                        "백업 완료",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
                else
                {
                    MessageBox.Show(
                        $"백업 생성에 실패했습니다.\n\n오류: {result.ErrorMessage}",
                        "백업 실패",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "백업 생성");
            }
        }

        /// <summary>
        /// 백업에서 복원
        /// </summary>
        public void RestoreFromBackup(string backupPath)
        {
            try
            {
                var confirmResult = MessageBox.Show(
                    "백업에서 복원하시겠습니까?\n\n" +
                    "현재 데이터가 백업 데이터로 덮어씌워집니다.\n" +
                    "이 작업은 되돌릴 수 없습니다.",
                    "복원 확인",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Warning);

                if (confirmResult != MessageBoxResult.Yes)
                    return;

                var backupService = new BackupService();
                var result = backupService.RestoreBackup(backupPath);

                if (result.Success)
                {
                    MessageBox.Show(
                        $"복원이 완료되었습니다.\n\n" +
                        $"복원된 항목: {result.RestoredItems.Count}개\n" +
                        $"- {string.Join("\n- ", result.RestoredItems)}\n\n" +
                        "변경 사항을 적용하려면 앱을 다시 시작해주세요.",
                        "복원 완료",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
                else
                {
                    MessageBox.Show(
                        $"복원에 실패했습니다.\n\n오류: {result.ErrorMessage}",
                        "복원 실패",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                ShowFriendlyError(ex, "백업 복원");
            }
        }

        #endregion
    }

    // 데이터 모델 클래스
    public class ComparisonRow
    {
        public string Stat { get; set; } = "";
        public string CurrentDisplay { get; set; } = "";
        public string TargetDisplay { get; set; } = "";
        public string GapDisplay { get; set; } = "";
        public string Status { get; set; } = "";
    }

    public class PriorityUpgrade
    {
        public int Priority { get; set; }
        public string Category { get; set; } = "";
        public string Description { get; set; } = "";
        public string Suggestion { get; set; } = "";
    }

    public class UpgradeStep
    {
        public int Step { get; set; }
        public string Priority { get; set; } = "";
        public string Title { get; set; } = "";
        public int CostChaos { get; set; }
        public string Description { get; set; } = "";
        public string Impact { get; set; } = "";
        public List<string> Recommendations { get; set; } = new List<string>();
        public List<TradeItem> TradeItems { get; set; } = new List<TradeItem>();

        public bool HasTradeItems => TradeItems != null && TradeItems.Count > 0;
    }

    public class TradeItem
    {
        public string Name { get; set; } = "";
        public string Type { get; set; } = "";
        public string PriceDisplay { get; set; } = "";
        public string Seller { get; set; } = "";
        public string Whisper { get; set; } = "";

        public string WhisperPreview
        {
            get
            {
                if (string.IsNullOrEmpty(Whisper))
                    return "";
                return Whisper.Length > 80 ? Whisper.Substring(0, 80) + "..." : Whisper;
            }
        }
    }

    public class PassiveRoadmapStage
    {
        public string LevelRange { get; set; } = "";
        public int Points { get; set; }
        public string PriorityFocus { get; set; } = "";
        public List<PassiveNode> Nodes { get; set; } = new List<PassiveNode>();
        public List<string> BenefitsDisplay { get; set; } = new List<string>();
    }

    public class PassiveNode
    {
        public string Name { get; set; } = "";
        public string Type { get; set; } = "";
        public string TypeDisplay { get; set; } = "";
        public List<string> StatsDisplay { get; set; } = new List<string>();
    }

    public class BoolToVisibilityConverter : System.Windows.Data.IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (value is bool boolValue)
                return boolValue ? Visibility.Visible : Visibility.Collapsed;
            return Visibility.Collapsed;
        }

        public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    // Helper class for upgrade suggestions
    public class UpgradeSuggestion
    {
        public string ItemName { get; set; } = "";
        public double ChaosValue { get; set; }
        public string Reason { get; set; } = "";
        public string TradeUrl { get; set; } = "";
        public bool HasTradeUrl => !string.IsNullOrEmpty(TradeUrl);
    }
}
