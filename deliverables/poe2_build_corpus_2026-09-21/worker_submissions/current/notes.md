# Collection notes — worker 1

Collection date: 2026-09-21 (Asia/Bangkok). Observed wall-clock checkpoints: 19:10:54.9138471 +07:00 through 19:18:01.3276035 +07:00; normalization continued afterward. Web source accessed_at uses day precision because web.run does not expose request timestamps; dates are ISO and not invented second-precision timestamps. Published dates remain null unless an opened guide explicitly identifies an upload date; the repeated date under an Updated label is not treated as publication.

## Public statistics receipt

Source: [poe.ninja public build overview](https://poe.ninja/poe2/builds), source_id w1_ninja. Playwright MCP navigation receipt timestamp 2026-09-21T12:13:10.556Z; rendered body inspected immediately afterward. The initial web.run open exposed zero text, but the actual browser succeeded. Public UI displayed Log in; no authentication was needed. Both Codex and Claude global Playwright configuration were inspected, project configurations checked, and the exposed Playwright MCP responded. No individual character pages or undocumented character APIs were retrieved.

| Displayed cohort | Death | Economy | Indexed characters | Top three displayed class shares |
|---|---|---|---:|---|
| Forbidden Rites | SC | Trade (inferred from unqualified league) | 124098 | Gemling Legionnaire 37.0%; Martial Artist 9.6%; Disciple of Varashta 9.0% |
| Runes of Aldur | SC | Trade (inferred) | 124353 | Spirit Walker 30.7%; Martial Artist 19.3%; Gemling Legionnaire 8.9% |
| HC Forbidden Rites | HC | Trade (inferred) | 3480 | Gemling Legionnaire 20.7%; Disciple of Varashta 19.8%; Martial Artist 12.0% |
| HC Runes of Aldur | HC | Trade (inferred) | 12462 | Not extracted |
| SSF Forbidden Rites | SC | SSF | 5164 | Gemling Legionnaire 22.6%; Disciple of Varashta 15.1%; Martial Artist 10.6% |
| SSF Runes of Aldur | SC | SSF | 26463 | Martial Artist 16.6%; Spirit Walker 14.4%; Gemling Legionnaire 9.2% |
| HC SSF Forbidden Rites | HC | SSF | 3391 | Gemling Legionnaire 15.0%; Disciple of Varashta 14.7%; Martial Artist 10.8% |
| HC SSF Runes of Aldur | HC | SSF | 8506 | Not extracted |

These are observed indexed cohorts, not counts of all players or guide users. SC/Trade for unqualified league names is an explicit interpretation, not a literal UI label. No patch number was rendered. Both named leagues appeared in Challenge Leagues; their dates and active-versus-ended status were not independently resolved.

## Provenance and limits

- Mobalytics guide header badges read 0.5.5 FR; some titles and bodies retain 0.5. No official patch authority was collected in this worker scope. The tier list says Return of the Ancients in its introduction and Runes of Aldur in commentary, and includes predictions. It cannot settle current season or observed build usage.
- Guide favorites are rounded when displayed with K and can differ from listing snapshots. Values belong to their original guide source, never to a whole family or gameplay population.
- One record represents one opened guide/configuration sample. Overview transitions can describe other named stages without their interactive gear panels being selected. Neither every selectable variant nor complete equipment/support payloads were captured.
- Family grouping is provisional and mechanism-based. Lich/Titan Twisted Empyrean share one family; Spark and Grim Pillar totems have different primary spells. Stage names alone never establish a deep extract.
- Mixed campaign/endgame pages whose URLs do not contain leveling/starter were kept under the explicit URL boundary. Worker2-owned URLs, the old 0.3 mortar guide, and prospective 1.0 promises are excluded from new counts. Seongbin/Skadoosh baseline is not counted.
- No video downloaded or viewed, no game validation, no 1.0 approval, no product/game configuration changes, and no publication. Playwright automatically emitted its server-managed navigation snapshot receipt; no raw page copy was intentionally retained in this corpus.

