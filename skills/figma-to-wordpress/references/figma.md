# Figma: calls, inventory, tokens, assets, gaps

The Figma MCP server (remote or desktop) gives four calls that matter here. Tool names differ by server; the call
names are the same.

| Call | Use it for | Cost |
|---|---|---|
| `get_metadata` | The node tree (ids, names, sizes, positions) of a page or frame | Small to large: one frame at a time |
| `get_design_context` | One section's code-like description, values and assets, plus a screenshot | Large: one section at a time |
| `get_variable_defs` | Variables (colours, type, spacing) used by a node | Small |
| `get_screenshot` | A render of a node: saved to disk by its URL as the pixel diff's reference | Small when downloaded; image tokens only if opened |

Links: `https://www.figma.com/design/<fileKey>/<name>?node-id=12-345` means file `<fileKey>`, node `12:345`.

## In other tools

The Figma MCP server is connected once per machine in the tool that runs the build: Figma's remote server
(`https://mcp.figma.com/mcp`, signed in to Figma when the tool asks) or the desktop app's local server
(`http://127.0.0.1:3845/mcp`, turned on in the desktop app's preferences). Claude Code: `claude mcp add --transport
http figma <address>`; Codex: an `[mcp_servers.figma]` entry with its `url` in `~/.codex/config.toml`; Antigravity:
its MCP server settings (`mcp_config.json`); T3 Code: the agent it runs. Check the tool's MCP docs for the current
form. Tool names carry the server's prefix (for example `mcp__figma__get_design_context`); the calls are the same.
Not connected: tell the developer in one line how to connect it and wait (a blocker); never build by eye from
screenshots instead.

## Call discipline (keeps usage low)

- One node per call. Never `get_design_context` on a whole page; never the same node twice. What a call returns is
  saved to `_figma/spec/` (values) or `_figma/inventory.md` (structure) and re-read from disk afterwards.
- A "sparse" answer (Figma says so, or it only lists children): match the child ids to the screenshot and request
  the visible children in one parallel batch.
- `get_metadata` on a top-level page frame can return no children: call it on the frame's first child (often
  "Body" or "Main"), or read the structure from that frame's design context.
- The code `get_design_context` returns (React + Tailwind) is a high-fidelity, non-interactive prototype: take its
  values, rebuild it in the project's stack with real layout. Absolute positions become flex or grid.
- Interactions (hover, menus, sliders, accordions, tabs) are rarely in the returned code: read the prototype
  connections and the variants in the inventory, and build them as real interactive code.

## The inventory (once, at the start)

Read the file's pages with `get_metadata`, then each candidate page's top-level frames. Write `_figma/inventory.md`:

1. **Final page and frames.** Which Figma page is the build source; for each website page its desktop frame id and
   mobile frame id (and tablet if designed). No label says "final": take the latest complete set, say why, list the
   others as alternatives never built. Drafts, archives, low-opacity frames and loose renders are never built.
2. **Breakpoints.** The designed widths (usually 1440 and 375). These are the 1:1 widths; every other width only
   has to look right.
3. **Tokens.** `get_variable_defs` on the main frames. Few or no variables: infer them from the nodes (colours, font
   families, sizes, weights, line heights, letter spacing, radii, shadows, spacing steps, container width) and say
   they are inferred. Write `_figma/tokens.json`:
   `{"color": {"brand": "#f5412c"}, "font": {"sans": "Inter"}, "text": {"h1": {"size": 56, "line": 64, "weight": 600,
   "tracking": -1.12}}, "radius": {}, "shadow": {}, "space": {}, "container": 1440}`.
4. **Fonts.** Families and weights, and where each comes from (Google Fonts, a licensed file the client must send).
5. **Sections per page**, in order, each with its desktop and mobile node id and a short slug (`hero`, `services`,
   `faq`). A section used on several pages is noted once, as shared.
6. **Global parts.** Header, footer, mobile header, menus, pop-ups, cookie bar: where each is (components or copies).
7. **Media.** Video (source file or only a thumbnail?), GIF, Lottie, background video, maps, embeds.
8. **Motion.** Prototype animations, hover and scroll effects, carousels (a carousel becomes Swiper with drag and
   touch, loaded only where it is used; arrows and dots only if Figma shows them; no autoplay unless Figma says).
9. **Hidden layers.** Hidden or off-canvas content inside a frame: build it only if it is a state (menu open, tab
   two), never if it is an abandoned draft.
10. **Assets needing edits.** Images whose export is wrong (cropped, low resolution, baked-in background).
11. **Gaps.** What the site needs but Figma lacks: mobile menu open state, hover and focus states, form errors and
    success, thank-you page, 404, empty states, pages linked from the menu but not designed. Each gets a line: how it
    will be built from the design system.
12. **Copy.** Placeholder text ("TBC", lorem ipsum) and missing facts (address, phone, hours) for the client list.
13. **Comments.** Designer comments that change the build (read them once if the server offers comments).

Then: `progress.py init` and one `progress.py page` per page (`references/progress.md`).

## Spec per section (`_figma/spec/<page>--<section>.md`)

About 20 to 40 lines, values only, so a resumed chat never calls Figma again for a built section:

- node ids (desktop, mobile); the section's box at each designed width as one line each, which the check script
  reads: `box@1440: w=1440 h=760` and `box@375: w=375 h=812`;
- layout (columns, gaps, padding, alignment), type per text (token or values), colours as token names;
- `el@W` lines for each text style, button and image, and `state@W` lines for each variant (hover, focus, open
  menu, tab, slide), with Figma's values (syntax in `references/qa.md`); the check script measures them;
- each asset: file name in the project, its slot, rendered size at each width, export scale;
- interactions and states; the copy verbatim (or "see Figma" for long text, with the node id).

## Assets

- Export every image and SVG the section uses; the design context names them. Raster images at 2x the largest
  rendered size (sharp at DPR 2), then the build makes the responsive sizes (WordPress: the Media Library sizes;
  Next.js: `next/image`). SVGs keep their own width and height; icons stay SVG.
- File names are meaningful (`hero-team.jpg`, not `image-12.png`). No temporary Figma asset URLs left anywhere.
- Never redraw, recolour or substitute an asset. An export that is wrong in the file: list it under "Assets needing
  edits" and fix it only with a tool the developer has, true to the source.

## Comparing with Figma

Numbers first. The check script compares each section with Figma: its box, a pixel diff against Figma's 1x render
(`_figma/qa/figma/<page>--<section>@<W>.png`, downloaded once by the `get_screenshot` URL, `references/qa.md`),
and the `el@W` and `state@W` values. The read-only QA check opens images only for what failed. Never request the
same render twice, and never bring a render into the chat to compare by eye.
