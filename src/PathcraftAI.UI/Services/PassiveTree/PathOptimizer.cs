using System;
using System.Collections.Generic;
using System.Linq;

namespace PathcraftAI.UI.Services.PassiveTree
{
    /// <summary>
    /// 패시브 트리 최적 경로 계산기
    /// Dijkstra 알고리즘 기반으로 목표 노드까지 최소 포인트로 도달하는 경로 계산
    /// </summary>
    public class PathOptimizer
    {
        private readonly PassiveTreeData _treeData;
        private readonly Dictionary<string, HashSet<string>> _adjacencyList;

        public PathOptimizer(PassiveTreeData treeData)
        {
            _treeData = treeData;
            _adjacencyList = BuildAdjacencyList();
        }

        /// <summary>
        /// 노드 연결 그래프 구축
        /// </summary>
        private Dictionary<string, HashSet<string>> BuildAdjacencyList()
        {
            var adj = new Dictionary<string, HashSet<string>>();

            foreach (var kvp in _treeData.Nodes)
            {
                string nodeId = kvp.Key;
                var node = kvp.Value;

                if (!adj.ContainsKey(nodeId))
                    adj[nodeId] = new HashSet<string>();

                // out 연결
                foreach (var outId in node.OutConnections)
                {
                    adj[nodeId].Add(outId);
                    if (!adj.ContainsKey(outId))
                        adj[outId] = new HashSet<string>();
                    adj[outId].Add(nodeId);  // 양방향
                }

                // in 연결
                foreach (var inId in node.InConnections)
                {
                    adj[nodeId].Add(inId);
                    if (!adj.ContainsKey(inId))
                        adj[inId] = new HashSet<string>();
                    adj[inId].Add(nodeId);  // 양방향
                }
            }

            return adj;
        }

        /// <summary>
        /// 시작 노드에서 목표 노드까지의 최단 경로 찾기 (Dijkstra)
        /// </summary>
        /// <param name="startNodeId">시작 노드 ID</param>
        /// <param name="targetNodeId">목표 노드 ID</param>
        /// <param name="allocatedNodes">이미 할당된 노드들 (비용 0)</param>
        /// <returns>최단 경로의 노드 ID 목록 (시작 노드 제외)</returns>
        public List<string> FindShortestPath(
            string startNodeId,
            string targetNodeId,
            HashSet<string>? allocatedNodes = null)
        {
            allocatedNodes ??= new HashSet<string>();

            if (!_adjacencyList.ContainsKey(startNodeId) || !_adjacencyList.ContainsKey(targetNodeId))
                return new List<string>();

            if (startNodeId == targetNodeId)
                return new List<string>();

            // Dijkstra 알고리즘
            var distances = new Dictionary<string, int>();
            var previous = new Dictionary<string, string?>();
            var visited = new HashSet<string>();
            var pq = new PriorityQueue<string, int>();

            foreach (var nodeId in _adjacencyList.Keys)
            {
                distances[nodeId] = int.MaxValue;
                previous[nodeId] = null;
            }

            distances[startNodeId] = 0;
            pq.Enqueue(startNodeId, 0);

            while (pq.Count > 0)
            {
                string current = pq.Dequeue();

                if (visited.Contains(current))
                    continue;
                visited.Add(current);

                if (current == targetNodeId)
                    break;

                if (!_adjacencyList.TryGetValue(current, out var neighbors))
                    continue;

                foreach (string neighbor in neighbors)
                {
                    if (visited.Contains(neighbor))
                        continue;

                    // 이미 할당된 노드는 비용 0, 아니면 1
                    int cost = allocatedNodes.Contains(neighbor) ? 0 : 1;
                    int newDist = distances[current] + cost;

                    if (newDist < distances[neighbor])
                    {
                        distances[neighbor] = newDist;
                        previous[neighbor] = current;
                        pq.Enqueue(neighbor, newDist);
                    }
                }
            }

            // 경로 재구성
            if (distances[targetNodeId] == int.MaxValue)
                return new List<string>();  // 도달 불가

            var path = new List<string>();
            string? node = targetNodeId;
            while (node != null && node != startNodeId)
            {
                path.Add(node);
                node = previous[node];
            }

            path.Reverse();
            return path;
        }

        /// <summary>
        /// 여러 목표 노드들에 도달하는 최적 경로 찾기 (Steiner Tree 근사)
        /// 그리디 알고리즘: 현재 트리에서 가장 가까운 목표를 반복적으로 추가
        /// </summary>
        /// <param name="startNodeId">시작 노드 ID (클래스 시작 노드)</param>
        /// <param name="targetNodeIds">목표 노드 ID 목록</param>
        /// <param name="allocatedNodes">이미 할당된 노드들</param>
        /// <returns>최적 경로에 포함된 모든 노드 ID</returns>
        public HashSet<string> FindOptimalPathToTargets(
            string startNodeId,
            IEnumerable<string> targetNodeIds,
            HashSet<string>? allocatedNodes = null)
        {
            allocatedNodes ??= new HashSet<string>();
            var result = new HashSet<string>(allocatedNodes) { startNodeId };
            var remainingTargets = new HashSet<string>(targetNodeIds);

            // 이미 할당된 목표 제거
            remainingTargets.ExceptWith(result);

            while (remainingTargets.Count > 0)
            {
                string? bestTarget = null;
                List<string>? bestPath = null;
                int bestCost = int.MaxValue;

                // 현재 트리에서 가장 가까운 목표 찾기
                foreach (string target in remainingTargets)
                {
                    // 현재 트리의 모든 노드에서 목표까지의 최단 경로 찾기
                    foreach (string treeNode in result)
                    {
                        var path = FindShortestPath(treeNode, target, result);
                        if (path.Count > 0)
                        {
                            // 새로 추가해야 할 노드 수 계산
                            int cost = path.Count(p => !result.Contains(p));
                            if (cost < bestCost)
                            {
                                bestCost = cost;
                                bestTarget = target;
                                bestPath = path;
                            }
                        }
                    }
                }

                if (bestTarget == null || bestPath == null)
                    break;  // 더 이상 도달 가능한 목표 없음

                // 경로 추가
                foreach (string node in bestPath)
                {
                    result.Add(node);
                }
                remainingTargets.Remove(bestTarget);
            }

            return result;
        }

        /// <summary>
        /// 클래스 시작 노드 ID 가져오기
        /// </summary>
        public string? GetClassStartNode(int classId)
        {
            string className = PassiveTreeUrlCodec.GetClassName(classId).ToLowerInvariant();

            if (_treeData.ClassStarts.TryGetValue(className, out string? startNodeId))
                return startNodeId;

            // 대소문자 무시 검색
            foreach (var kvp in _treeData.ClassStarts)
            {
                if (kvp.Key.Equals(className, StringComparison.OrdinalIgnoreCase))
                    return kvp.Value;
            }

            // 노드에서 직접 검색
            foreach (var kvp in _treeData.Nodes)
            {
                var node = kvp.Value;
                if (node.ClassStartIndex == classId && node.TypeString == "class_start")
                    return kvp.Key;
            }

            return null;
        }

        /// <summary>
        /// 노드 ID로 노드 정보 가져오기
        /// </summary>
        public TreeNode? GetNode(string nodeId)
        {
            return _treeData.Nodes.TryGetValue(nodeId, out var node) ? node : null;
        }

        /// <summary>
        /// 두 노드가 연결되어 있는지 확인
        /// </summary>
        public bool AreConnected(string nodeId1, string nodeId2)
        {
            if (!_adjacencyList.TryGetValue(nodeId1, out var neighbors))
                return false;
            return neighbors.Contains(nodeId2);
        }

        /// <summary>
        /// 할당된 노드들이 시작 노드에서 모두 연결되어 있는지 검증
        /// </summary>
        public bool ValidateConnectivity(string startNodeId, HashSet<string> allocatedNodes)
        {
            if (!allocatedNodes.Contains(startNodeId))
                return false;

            // BFS로 연결성 확인
            var visited = new HashSet<string>();
            var queue = new Queue<string>();
            queue.Enqueue(startNodeId);
            visited.Add(startNodeId);

            while (queue.Count > 0)
            {
                string current = queue.Dequeue();

                if (!_adjacencyList.TryGetValue(current, out var neighbors))
                    continue;

                foreach (string neighbor in neighbors)
                {
                    if (!visited.Contains(neighbor) && allocatedNodes.Contains(neighbor))
                    {
                        visited.Add(neighbor);
                        queue.Enqueue(neighbor);
                    }
                }
            }

            // 모든 할당된 노드가 방문되었는지 확인
            return allocatedNodes.All(n => visited.Contains(n));
        }

        /// <summary>
        /// 포인트 사용량 계산 (시작 노드 제외)
        /// </summary>
        public int CalculatePointsUsed(HashSet<string> allocatedNodes, string startNodeId)
        {
            int count = 0;
            foreach (string nodeId in allocatedNodes)
            {
                if (nodeId == startNodeId)
                    continue;

                if (_treeData.Nodes.TryGetValue(nodeId, out var node))
                {
                    // 클래스/어센던시 시작 노드는 포인트 사용 안 함
                    if (node.Type != NodeType.ClassStart && node.Type != NodeType.AscendancyStart)
                    {
                        count++;
                    }
                }
            }
            return count;
        }

        /// <summary>
        /// 특정 노드 ID 목록의 스탯 합계 계산
        /// </summary>
        public Dictionary<string, int> CalculateStats(IEnumerable<string> nodeIds)
        {
            var stats = new Dictionary<string, int>();

            foreach (string nodeId in nodeIds)
            {
                if (!_treeData.Nodes.TryGetValue(nodeId, out var node))
                    continue;

                foreach (string stat in node.Stats)
                {
                    // 간단한 파싱: "+X to ..." 또는 "X% increased ..." 형태
                    var match = System.Text.RegularExpressions.Regex.Match(
                        stat, @"^[+]?(\d+)");
                    if (match.Success && int.TryParse(match.Groups[1].Value, out int value))
                    {
                        string key = stat.Substring(match.Length).Trim();
                        if (!stats.ContainsKey(key))
                            stats[key] = 0;
                        stats[key] += value;
                    }
                }
            }

            return stats;
        }
    }
}
