# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The project is **MYkrokosmos** (formerly 너의 별자리는?), a Korean-language experience-graph web app prototype for university students (see README.md for the feature list).

- `MYkrokosmos/MYkrokosmos.html` is the whole app: one self-contained HTML file with inline CSS and vanilla JS. The only external dependencies are d3 7.8.5 (cdnjs) and the Noto Sans KR Google Font.
- There is no build step or package manifest. `qa/qa.py` is a Playwright browser QA script (uses `qa/sample_state.json`). To run it, open `MYkrokosmos/MYkrokosmos.html` in a browser.
- The same page is also published as a claude.ai Artifact. When publishing it there, strip the leading `<!doctype html>…<body>` wrapper and the trailing `</body></html>`, because the Artifact tool adds its own skeleton.
- State lives in `localStorage` under the key `byeoljari.v1`. The tutorial runs on in-memory sample data (`makeSample`) and never persists it.
- "AI" features (tag suggestions, writing-guide questions, analysis comment) are rule-based: see `DICT`, `DOMAIN_HINTS`, `ASPECTS`/`TAG_Q` and `analysisText`.
- The graph follows 조합 시안 A from the design canvas: a photo-like ground painted once on `#graph-bg` (`paintSkyGround`), experience stars drawn as halo stars coloured by activity type (`STARLIGHT`/`TYPE_LIGHT`) with no labels on the sky (hover tooltip `showTip`, click opens the panel placed next to the star by `placePanel`), and experiences clustered by activity type inside dashed zones. Majors are not drawn on the sky. Virtual stars are called 관측 예정 별 and drawn as faint stars. On first open `openWelcome` asks for a required name before the tutorial.
- UI copy is Korean, in a polite 해요체 tone. The visual direction is based on Apple's website.

Adjusting File

dummy line
