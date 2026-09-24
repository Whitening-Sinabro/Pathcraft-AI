# Pathcraft-AI agent instructions

## Shared MCP/browser connection checks

Before reporting a requested MCP or authenticated browser unavailable, read
`C:/Users/User/.agents/MCP_BROWSER_CONNECTION_RULES.md` and check both Codex and
Claude global/project server configurations. Reuse the supported configured
connection and verify it with a real tool call. Do not stop at saying the server
is configured in the other client. Keep configuration, MCP connectivity,
browser profile/login, and successful playback as separate verified facts.

## POE1 item filters

Before creating, recolouring, or modifying any POE1 `.filter` file, read
[`Docs/POE1_LOOT_FILTER_DESIGN_SYSTEM.md`](Docs/POE1_LOOT_FILTER_DESIGN_SYSTEM.md) in full.

Treat filter logic, SSF/build overrides, strictness, visual tokens, and sounds as separate layers. Do not invent colours rule by rule. Before implementation, ask whether the user wants one progressive filter or three manually switched 1/3/5 filters. Extract build targets from PoB Notes/guides when available, but do not treat every equipped item as required; unresolved or missing targets belong in the app's Korean/English item-name search flow. Preserve the original source, generate every requested output from one canonical specification, and run the validation checklist in that document before installing a filter into the game directory.
