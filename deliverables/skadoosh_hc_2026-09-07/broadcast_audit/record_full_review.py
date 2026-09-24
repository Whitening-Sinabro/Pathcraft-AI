"""Record only review performed in the audit session; never infer from file existence."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
path = root / 'review_notes.json'
data = json.loads(path.read_text(encoding='utf-8'))
data['reviewed_second_asr_chunks'] = {
    '2865212551': list(range(15)),
    '2866065347': list(range(18)),
    '2866749730': list(range(27)),
}
data['reviewed_30_second_boards'] = {
    '2865212551': list(range(0, 16953, 750)),
    '2866065347': list(range(0, 20678, 750)),
    '2866749730': list(range(0, 31343, 750)),
}
data['asr_method_limit'] = '두 ASR 모델 모두 동일한 원본 음성으로 생성. 서로 독립적인 출처 두 개가 아니며, 전체 음성을 사람이 청취한 검토가 아님. 빌드 설정은 원본 화면과 공개 캐릭터 데이터를 추가 대조.'
data['visual_method'] = '총 2,301개의 30초 간격 탐색 프레임을 93개 보드로 검토하고 주요 전환·설정을 1080p 원본 프레임으로 추가 확인. 전체 영상을 매초 재생한 검토는 아님.'
data['completion'] = False
for event in data['events']:
    event['transcript_verification'] = 'large-v3-turbo 및 large-v3 전체 전사 문맥 대조 완료. 원본 화면 대조 결과는 별도 evidence 항목으로 기록.'
    if event['video'] == '2866749730' and event['topic'] == '무기 세트 실수 수정':
        event['at'] = 2938
        event['finding'] = '00:48:58에 AWT를 세트 II로 지정해야 한다고 말하며 설정 수정. 이전 00:46:32는 장문 전사 블록 시작 시각으로 실제 발언 시각이 아님.'
        event['verification'] = 'VAD 없는 집중 전사 00:48:58–00:49:11 재확인; G 화면 확인 대기'
data['context_exclusions'] = [
    {'video': '2866749730', 'interval': [18300, 19890], 'reason': '식사 중 다른 스트리머 영상 시청. 본인 워브링어 설정과 구분.'},
    {'video': '2866749730', 'interval': [19890, 20500], 'reason': '다른 방송 클립 모음 시청. 사망·장비·스킬을 본인 캐릭터로 오인 금지.'},
    {'video': '2866749730', 'interval': [20520, 21390], 'reason': '방송 검은 화면(Eating). 음성은 있으나 화면 설정 확인 불가.'},
]
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Full transcript comparison and 93 contact boards recorded; key-scene audit remains open.')
