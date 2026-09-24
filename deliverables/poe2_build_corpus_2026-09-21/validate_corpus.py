"""Validate the delivered factual corpus, not gameplay or build viability."""
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
REQUIRED = ('id family_id family_name variant game patch league mode creator url '
            'published_at updated_at accessed_at retrieval_status popularity class ascendancy '
            'main_skills damage_structure defense_structure skills equipment resource_constraints '
            'stages alternatives similarities_differences gaps_conflicts patch_sensitive_dependencies '
            'claims source_ids approval_status').split()

def canonical_url(url):
    s = urlsplit(url)
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path.rstrip('/'), '', ''))

def run():
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    records = catalog['records']
    sources = [json.loads(x) for x in (ROOT / 'sources.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    source_by_id = {s['source_id']: s for s in sources}
    issues = []
    warnings = []
    ledger = json.loads((ROOT / 'review_ledger.json').read_text(encoding='utf-8'))
    reviewed = {c['record_id']: c for c in ledger['checks']}
    cutoff = datetime(2026, 9, 22, tzinfo=timezone.utc)
    def date_value(value, owner, field):
        if value in (None, '', 'unknown'):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
        except (ValueError, AttributeError):
            issues.append({'id': owner, 'check': 'unparseable_date', 'field': field, 'value': value})
            return None
    for row in records + sources:
        owner = row.get('id', row.get('source_id'))
        access = date_value(row.get('accessed_at'), owner, 'accessed_at')
        if access is None:
            issues.append({'id': owner, 'check': 'access_time_missing'})
        elif access >= cutoff:
            issues.append({'id': owner, 'check': 'access_after_cutoff'})
        for field in ('published_at', 'updated_at'):
            value = date_value(row.get(field), owner, field)
            if access and value and value > access:
                issues.append({'id': owner, 'check': 'future_source_date', 'field': field})
    for label, vals in [('record_id', [r['id'] for r in records]), ('source_id', [s['source_id'] for s in sources])]:
        for val, n in Counter(vals).items():
            if n > 1:
                issues.append({'check': 'duplicate_' + label, 'value': val, 'count': n})
    for r in records:
        for field in REQUIRED:
            if field not in r:
                issues.append({'id': r['id'], 'check': 'missing_field', 'field': field})
        if r.get('game') != 'POE2' or r.get('approval_status') != 'collected_not_game_validated':
            issues.append({'id': r['id'], 'check': 'scope_or_approval'})
        refs = r.get('source_ids', [])
        popularity = r.get('popularity') or {}
        if popularity.get('source_id') not in source_by_id:
            issues.append({'id': r['id'], 'check': 'popularity_source_missing'})
        if not popularity.get('type') or not popularity.get('scope'):
            issues.append({'id': r['id'], 'check': 'popularity_metric_scope_missing'})
        date_value(popularity.get('observed_at'), r['id'], 'popularity.observed_at')
        for sid in refs:
            if sid not in source_by_id:
                issues.append({'id': r['id'], 'check': 'dangling_source', 'source_id': sid})
        for field in ['claims', 'skills', 'equipment', 'stages']:
            for item in r.get(field, []):
                if not isinstance(item, dict):
                    issues.append({'id': r['id'], 'check': 'unstructured_evidence', 'field': field})
                    continue
                sid = item.get('source_id')
                if sid not in source_by_id or not item.get('locator'):
                    issues.append({'id': r['id'], 'check': 'untraceable_item', 'field': field, 'source_id': sid})
        if r.get('retrieval_status') == 'deep_stage_extracted':
            concrete = [s for s in r.get('stages', []) if s.get('conditions') not in (None, '', [], 'unknown') or s.get('transition') not in (None, '', [], 'unknown')]
            if not concrete:
                issues.append({'id': r['id'], 'check': 'deep_without_condition'})
            c = reviewed.get(r['id'], {})
            if c.get('record_comparison') != 'accepted_after_bounded_repairs' or c.get('url') != r['url'] or not c.get('page_facts'):
                issues.append({'id': r['id'], 'check': 'deep_without_manager_original_review'})
        if not isinstance(r.get('patch'), dict) or not r.get('patch', {}).get('provenance'):
            issues.append({'id': r['id'], 'check': 'patch_provenance_missing'})
        mode = r.get('mode', {})
        if not isinstance(mode, dict) or any(k not in mode for k in ('death', 'economy')):
            issues.append({'id': r['id'], 'check': 'mode_axes_missing'})
        if r.get('retrieval_status') in ('detail_extracted', 'deep_stage_extracted'):
            matched = [source_by_id[sid] for sid in refs if sid in source_by_id and canonical_url(source_by_id[sid]['url']) == canonical_url(r['url'])]
            if not matched or all(s.get('retrieval_status') in ('discovery_only', 'blocked', 'failed') for s in matched):
                issues.append({'id': r['id'], 'check': 'detail_without_opened_primary_source'})
        if not (ROOT / 'build_notes' / (r['id'] + '.md')).exists():
            issues.append({'id': r['id'], 'check': 'note_missing'})
        if not r.get('main_skills'):
            issues.append({'id': r['id'], 'check': 'missing_core_skill'})
        for item in r.get('equipment', []):
            if item.get('role') not in ('required', 'example', 'alternative', 'unknown'):
                issues.append({'id': r['id'], 'check': 'equipment_role'})
        for claim in r.get('claims', []):
            if claim.get('kind') not in ('creator_claim', 'direct_page_fact', 'inference'):
                issues.append({'id': r['id'], 'check': 'claim_kind'})
    by_url = {}
    for r in records:
        by_url.setdefault(canonical_url(r['url']), []).append(r)
    duplicates = []
    for url, group in by_url.items():
        if len(group) > 1:
            duplicates.append({'url': url, 'ids': [r['id'] for r in group], 'variants': [r['variant'] for r in group]})
            if len({r['family_id'] for r in group}) > 1:
                issues.append({'check': 'same_url_family_conflict', 'url': url})
    with (ROOT / 'catalog.csv').open(encoding='utf-8-sig', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    if [r['id'] for r in csv_rows] != [r['id'] for r in records]:
        issues.append({'check': 'csv_json_id_order_mismatch'})
    for j, c in zip(records, csv_rows):
        for key in ['family_id','url','retrieval_status','approval_status']:
            if str(j[key]) != c[key]:
                issues.append({'id': j['id'], 'check': 'csv_json_value_mismatch', 'field': key})
    detailed = [r for r in records if r['retrieval_status'] in ('detail_extracted', 'deep_stage_extracted')]
    deep = [r for r in records if r['retrieval_status'] == 'deep_stage_extracted']
    counts = dict(records=len(records), distinct_families=len({r['family_id'] for r in detailed}),
                  distinct_guide_urls=len({canonical_url(r['url']) for r in detailed}),
                  detail_extracted_records=len(detailed), deep_stage_records=len(deep),
                  deep_distinct_guide_urls=len({canonical_url(r['url']) for r in deep}),
                  sources=len(sources), retrieval_status=dict(Counter(r['retrieval_status'] for r in records)))
    counts['distinct_persisted_source_urls'] = len({canonical_url(s['url']) for s in sources})
    counts['distinct_opened_source_urls'] = len({canonical_url(s['url']) for s in sources if s['retrieval_status'] in ('opened','detail_extracted','deep_stage_extracted')})
    counts['manager_reviewed_deep_urls'] = len({canonical_url(r['url']) for r in deep if r['id'] in reviewed})
    goals = dict(families_20=counts['distinct_families'] >= 20,
                 guide_urls_30=counts['distinct_guide_urls'] >= 30,
                 deep_guide_urls_12=counts['deep_distinct_guide_urls'] >= 12)
    report = dict(scope='local data contract; not gameplay verification', status='PASS' if not issues else 'FAIL',
                  counts=counts, goals=goals, issues=issues, warnings=warnings, duplicate_urls=duplicates,
                  source_retrieval=dict(Counter(s['retrieval_status'] for s in sources)),
                  limits=['All counted deep gates received manager original-page review; other fields use bounded worker evidence and selected manager checks.',
                          'Unknown fields and source conflicts remain; structural PASS does not approve builds.',
                          'Baseline Seongbin and Skadoosh are separate and excluded from new counts.'])
    (ROOT / 'validation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not issues else 1

if __name__ == '__main__':
    raise SystemExit(run())
