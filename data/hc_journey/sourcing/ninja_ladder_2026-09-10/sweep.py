import json
import time
import sys

from fetch_ninja import fetch_and_save

SLUGS = {
    'hc': 'hc-forbidden-rites',
    'hcssf': 'hc-ssf-forbidden-rites',
}

CLASSES = [
    'Smith of Kitava', 'Warbringer', 'Titan', 'Gemling Legionnaire',
    'Witchhunter', 'Tactician', 'Invoker', 'Acolyte of Chayula',
    'Disciple of Varashta', 'Chronomancer', 'Stormweaver', 'Lich',
    'Blood Mage', 'Infernalist', 'Deadeye', 'Pathfinder', 'Amazon',
    'Ritualist', 'Oracle', 'Shaman', 'Abyssal Lich', 'Whisperer',
    'Djinn',
]

def main():
    results = {}  # (league, filter_label) -> (total, rows)
    baselines = {}
    for league, slug in SLUGS.items():
        total, rows, fname = fetch_and_save(slug, None, 'base')
        baselines[league] = total
        results[(league, 'base')] = (total, rows)
        print(f'[{league}] base total={total} rows={len(rows)}', flush=True)
        time.sleep(3)

    for league, slug in SLUGS.items():
        base_total = baselines[league]
        for cls in CLASSES:
            try:
                total, rows, fname = fetch_and_save(slug, {'class': cls}, cls)
            except Exception as e:
                print(f'[{league}] class={cls} ERROR {e}', flush=True)
                time.sleep(3)
                continue
            matched = (total != base_total)
            print(f'[{league}] class={cls} total={total} matched_filter={matched}', flush=True)
            if matched:
                results[(league, f'class:{cls}')] = (total, rows)
            time.sleep(3)

    # Serialize summary
    out = {}
    for (league, label), (total, rows) in results.items():
        out.setdefault(league, []).append({'filter': label, 'total': total, 'rows': rows})
    with open('sweep_results.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('DONE, wrote sweep_results.json')

if __name__ == '__main__':
    main()
