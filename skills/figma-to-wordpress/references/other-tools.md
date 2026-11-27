# This skill's own steps in other tools (Codex, Antigravity, T3 Code and others)

SKILL.md > In other tools first: where a step names a Claude tool, convert-to-wordpress's `references/agents.md` >
Per tool (0.9.14 or later) says what to do instead. This skill's own steps there (moved word for word from SKILL.md
in 0.5.0):
- **Figma:** the Figma MCP server connected in this tool (`references/figma.md` > In other tools), else a blocker.
- **Asking:** the tool's question tool; without one, numbered options with the recommended one first, then wait.
- **The read-only QA check:** a subagent (Codex `spawn_agent`, Antigravity `invoke_subagent`), not a new chat.
- **Browser steps** (wp-admin, live checks, test leads): Antigravity drives the lead's Chrome through the
  chrome-devtools MCP (the kit's Per tool line and tab rules, 0.9.16 or later); its own pane only as a fallback.
- **The progress page:** the local file, `progress.py <dir> render --refresh 30 --open` once (`references/progress.md`).
- **Context:** Codex `/status`; no meter (Antigravity): checkpoint at every page end and phase end.
- **Shell:** every script is Python or Node; on Windows `py -3` or `python` where a step says `python3`.
