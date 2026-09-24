"""하코 초반 아틀라스 페이지 조립: steps.html(표 행) + hc_route.svg + template.html."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = (HERE / 'steps.html').read_text(encoding='utf-8')
svg = (HERE.parent / 'atlas_src' / 'hc_route.svg').read_text(encoding='utf-8')
tpl = (HERE / 'template.html').read_text(encoding='utf-8')
sub = (HERE / 'sub_rows.html').read_text(encoding='utf-8')
full = (HERE.parent / 'atlas_src' / 'full_order.svg').read_text(encoding='utf-8')
(HERE / 'hc_atlas.html').write_text(tpl.replace('{{ROWS}}', rows).replace('{{SVG}}', svg).replace('{{SUBROWS}}', sub).replace('{{FULLSVG}}', full).replace('{{STAGEJSON}}', (HERE.parent / 'atlas_src' / 'stage_lists.json').read_text(encoding='utf-8')), encoding='utf-8')
print('ok')
