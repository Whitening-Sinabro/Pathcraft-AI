using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace PathcraftAI.UI.Services.PassiveTree
{
    /// <summary>
    /// POE 패시브 트리 URL 인코더/디코더
    /// POB 포맷 v6 호환 - pathofexile.com 공식 URL과 호환
    /// </summary>
    public class PassiveTreeUrlCodec
    {
        private const int CurrentVersion = 6;
        private const string DefaultUrlPrefix = "https://www.pathofexile.com/passive-skill-tree/";

        /// <summary>
        /// 디코딩 결과
        /// </summary>
        public class DecodeResult
        {
            public bool Success { get; set; }
            public string? ErrorMessage { get; set; }
            public int Version { get; set; }
            public int ClassId { get; set; }
            public int AscendancyId { get; set; }
            public int SecondaryAscendancyId { get; set; }
            public List<int> NodeIds { get; set; } = new();
            public List<int> ClusterNodeIds { get; set; } = new();
            public List<MasteryEffect> MasteryEffects { get; set; } = new();
        }

        /// <summary>
        /// 마스터리 효과 정보
        /// </summary>
        public class MasteryEffect
        {
            public int EffectId { get; set; }
            public int NodeId { get; set; }
        }

        /// <summary>
        /// 패시브 트리 URL을 디코딩
        /// </summary>
        /// <param name="url">POE 패시브 트리 URL 또는 인코딩된 문자열</param>
        /// <returns>디코딩 결과</returns>
        public DecodeResult Decode(string url)
        {
            var result = new DecodeResult();

            try
            {
                // URL에서 인코딩된 부분만 추출
                string encoded = ExtractEncodedPart(url);
                if (string.IsNullOrEmpty(encoded))
                {
                    result.ErrorMessage = "Invalid URL format";
                    return result;
                }

                // Base64URL -> Base64 변환 후 디코딩
                byte[]? data = Base64UrlDecode(encoded);
                if (data == null || data.Length < 6)
                {
                    result.ErrorMessage = "Invalid tree link (unrecognised format)";
                    return result;
                }

                // 버전 파싱 (바이트 0-3, big-endian)
                int version = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3];
                if (version > 6)
                {
                    result.ErrorMessage = $"Invalid tree link (unknown version number '{version}')";
                    return result;
                }
                result.Version = version;

                // 클래스 ID (바이트 4)
                result.ClassId = data[4];

                // 어센던시 ID (바이트 5) - v4 이상
                if (version >= 4)
                {
                    int ascendancyByte = data[5];
                    result.AscendancyId = ascendancyByte & 0x03;           // 하위 2비트
                    result.SecondaryAscendancyId = (ascendancyByte >> 2) & 0x03;  // 비트 2-3
                }

                // 노드 시작 위치 결정
                int nodesStart = version >= 4 ? 7 : 6;

                // v5 이상: 노드 개수가 바이트 6에 있음
                int nodeCount = 0;
                int nodesEnd;
                if (version >= 5)
                {
                    nodeCount = data[6];
                    nodesEnd = nodesStart + (nodeCount * 2);
                }
                else
                {
                    nodesEnd = data.Length;
                }

                // 일반 노드 파싱 (2바이트씩, big-endian)
                for (int i = nodesStart; i < nodesEnd && i + 1 < data.Length; i += 2)
                {
                    int nodeId = (data[i] << 8) | data[i + 1];
                    result.NodeIds.Add(nodeId);
                }

                // v5 이상: 클러스터 노드 파싱
                if (version >= 5 && nodesEnd < data.Length)
                {
                    int clusterStart = nodesEnd;
                    int clusterCount = data[clusterStart];
                    int clusterEnd = clusterStart + 1 + (clusterCount * 2);

                    for (int i = clusterStart + 1; i < clusterEnd && i + 1 < data.Length; i += 2)
                    {
                        int clusterId = (data[i] << 8) | data[i + 1];
                        result.ClusterNodeIds.Add(clusterId);
                    }

                    // v6 이상: 마스터리 효과 파싱
                    if (version >= 6 && clusterEnd < data.Length)
                    {
                        int masteryStart = clusterEnd;
                        int masteryCount = data[masteryStart];

                        for (int i = masteryStart + 1; i < data.Length - 3; i += 4)
                        {
                            int effectId = (data[i] << 8) | data[i + 1];
                            int nodeId = (data[i + 2] << 8) | data[i + 3];
                            result.MasteryEffects.Add(new MasteryEffect
                            {
                                EffectId = effectId,
                                NodeId = nodeId
                            });
                        }
                    }
                }

                result.Success = true;
            }
            catch (Exception ex)
            {
                result.ErrorMessage = $"Decoding error: {ex.Message}";
            }

            return result;
        }

        /// <summary>
        /// 패시브 트리 데이터를 URL로 인코딩
        /// </summary>
        /// <param name="classId">클래스 ID (0-6)</param>
        /// <param name="ascendancyId">메인 어센던시 ID (0-3)</param>
        /// <param name="nodeIds">할당된 노드 ID 목록</param>
        /// <param name="prefix">URL 접두사 (기본: 공식 URL)</param>
        /// <param name="secondaryAscendancyId">세컨더리 어센던시 ID (0-3, Wildwood용)</param>
        /// <param name="masteryEffects">마스터리 효과 목록</param>
        /// <returns>인코딩된 URL</returns>
        public string Encode(
            int classId,
            int ascendancyId,
            IEnumerable<int> nodeIds,
            string? prefix = null,
            int secondaryAscendancyId = 0,
            IEnumerable<MasteryEffect>? masteryEffects = null)
        {
            var data = new List<byte>();

            // 버전 (4바이트, big-endian)
            data.Add(0);
            data.Add(0);
            data.Add(0);
            data.Add((byte)CurrentVersion);

            // 클래스 ID (1바이트)
            data.Add((byte)classId);

            // 어센던시 ID (1바이트) - 하위 2비트: 메인, 비트 2-3: 세컨더리
            int ascendancyByte = (ascendancyId & 0x03) | ((secondaryAscendancyId & 0x03) << 2);
            data.Add((byte)ascendancyByte);

            // 노드 필터링 및 정렬
            var filteredNodes = nodeIds
                .Where(id => id > 0 && id < 65536)  // 유효 범위만
                .OrderBy(id => id)
                .Take(255)  // 최대 255개
                .ToList();

            // 클러스터 노드 분리 (ID >= 65536)
            var clusterNodes = nodeIds
                .Where(id => id >= 65536)
                .Select(id => id - 65536)
                .OrderBy(id => id)
                .ToList();

            // 일반 노드 개수 (1바이트)
            data.Add((byte)filteredNodes.Count);

            // 일반 노드들 (2바이트씩, big-endian)
            foreach (int nodeId in filteredNodes)
            {
                data.Add((byte)(nodeId >> 8));
                data.Add((byte)(nodeId & 0xFF));
            }

            // 클러스터 노드 개수 (1바이트)
            data.Add((byte)clusterNodes.Count);

            // 클러스터 노드들 (2바이트씩)
            foreach (int nodeId in clusterNodes)
            {
                data.Add((byte)(nodeId >> 8));
                data.Add((byte)(nodeId & 0xFF));
            }

            // 마스터리 효과
            var masteries = masteryEffects?.ToList() ?? new List<MasteryEffect>();
            data.Add((byte)masteries.Count);

            foreach (var mastery in masteries)
            {
                data.Add((byte)(mastery.EffectId >> 8));
                data.Add((byte)(mastery.EffectId & 0xFF));
                data.Add((byte)(mastery.NodeId >> 8));
                data.Add((byte)(mastery.NodeId & 0xFF));
            }

            // Base64URL 인코딩
            string encoded = Base64UrlEncode(data.ToArray());

            return (prefix ?? DefaultUrlPrefix) + encoded;
        }

        /// <summary>
        /// URL에서 인코딩된 부분만 추출
        /// </summary>
        private string ExtractEncodedPart(string url)
        {
            if (string.IsNullOrWhiteSpace(url))
                return string.Empty;

            // URL 형식이면 마지막 경로 부분만 추출
            if (url.Contains('/'))
            {
                var lastPart = url.Split('/').LastOrDefault(s => !string.IsNullOrEmpty(s));
                return lastPart ?? string.Empty;
            }

            // 이미 인코딩된 문자열
            return url;
        }

        /// <summary>
        /// Base64URL 디코딩 (RFC4648 section 5)
        /// </summary>
        private byte[]? Base64UrlDecode(string input)
        {
            try
            {
                // Base64URL -> Base64 변환
                string base64 = input
                    .Replace('-', '+')
                    .Replace('_', '/');

                // 패딩 추가
                switch (base64.Length % 4)
                {
                    case 2: base64 += "=="; break;
                    case 3: base64 += "="; break;
                }

                return Convert.FromBase64String(base64);
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Base64URL 인코딩 (RFC4648 section 5)
        /// </summary>
        private string Base64UrlEncode(byte[] data)
        {
            string base64 = Convert.ToBase64String(data);

            // Base64 -> Base64URL 변환 (패딩 제거)
            return base64
                .Replace('+', '-')
                .Replace('/', '_')
                .TrimEnd('=');
        }

        /// <summary>
        /// 클래스 ID를 클래스 이름으로 변환
        /// </summary>
        public static string GetClassName(int classId)
        {
            return classId switch
            {
                0 => "Scion",
                1 => "Marauder",
                2 => "Ranger",
                3 => "Witch",
                4 => "Duelist",
                5 => "Templar",
                6 => "Shadow",
                _ => "Unknown"
            };
        }

        /// <summary>
        /// 클래스 이름을 클래스 ID로 변환
        /// </summary>
        public static int GetClassId(string className)
        {
            return className?.ToLowerInvariant() switch
            {
                "scion" => 0,
                "marauder" => 1,
                "ranger" => 2,
                "witch" => 3,
                "duelist" => 4,
                "templar" => 5,
                "shadow" => 6,
                _ => 0
            };
        }
    }
}
