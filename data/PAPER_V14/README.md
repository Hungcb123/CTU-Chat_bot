# LaTeX manuscript scaffold

Target manuscript: **Evidence-Aware Agentic GraphRAG for Bilingual University
Administrative Question Answering**.

## Template

The source includes Springer `llncs.cls` version 2.25 and `splncs04.bst` conforming to the official Springer LNCS proceedings template (`rule paper/LaTeX2e+Proceedings+Template+ZIP`), which provides enhanced accessibility alt-text support (`\Description`), updated `credits` environment, and modern Times fonts (`newtxtext`, `newtxmath`).


The class file is the only authority for page size, margins, fonts, headings,
running heads, and spacing. Do not add an `article` fallback, `twocolumn`,
`geometry`, custom fonts, heading packages, or page-style overrides.

## Build

Install a TeX distribution such as MiKTeX or TeX Live, then run:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

or:

```powershell
latexmk -pdf main.tex
```

## Evidence discipline

- Replace red `[TBD: ...]` markers only with frozen, reproducible results.
- Main tables must use only `review_status=verified` questions.
- Keep draft/smoke results out of the abstract, conclusion, and claimed
  contributions.
- Measure internal full-text seed quality separately; never count the seed
  itself as graph-expanded contribution.
- Report exact model/index versions, trace IDs, graph reasons, latency, and
  failures.
- Treat REBot/CatRAG as the direct predecessor baseline; do not compare its
  published F1 value directly with answer-quality metrics from a different test.

Benchmark artifacts are generated from `Muagsy/evaluation`; source formulas and
runtime behavior are implemented under `Muagsy/backend/app`.
