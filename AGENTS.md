# Pathcraft-AI agent instructions

## POE1 item filters

Before creating, recolouring, or modifying any POE1 `.filter` file, read
[`Docs/POE1_LOOT_FILTER_DESIGN_SYSTEM.md`](Docs/POE1_LOOT_FILTER_DESIGN_SYSTEM.md) in full.

Treat filter logic, SSF/build overrides, strictness, visual tokens, and sounds as separate layers. Do not invent colours rule by rule. Before implementation, ask whether the user wants one progressive filter or three manually switched 1/3/5 filters. Extract build targets from PoB Notes/guides when available, but do not treat every equipped item as required; unresolved or missing targets belong in the app's Korean/English item-name search flow. Preserve the original source, generate every requested output from one canonical specification, and run the validation checklist in that document before installing a filter into the game directory.
