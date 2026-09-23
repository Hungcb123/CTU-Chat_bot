---
name: lncs-layout-checker
description: Comprehensive audit and auto-fix toolkit for Springer LNCS LaTeX papers and compiled PDFs against official LNCS v2.25 guidelines (layout, newtx fonts, credits/discintname, accessibility Description, abstract length, Type 3 fonts, page limits).
---

# Springer LNCS Layout & Compliance Checker (v2.25)

This skill provides an automated audit, validation, and remediation system for scientific papers targeting **Springer Lecture Notes in Computer Science (LNCS)** and related proceedings series. It verifies both **LaTeX source files** (`.tex`, `.cls`, `.bib`) and **compiled PDFs** against the official Springer guidelines.

---

## When to Use This Skill

Activate this skill whenever:
* You are preparing or revising a paper for a Springer LNCS conference/workshop (e.g., ECIR, MICCAI, PAKDD, ACIIDS, FAIR, etc.).
* The user asks to "check layout paper", "check LNCS format", "kiểm tra layout paper", "audit format bài báo", or verify compliance with publisher guidelines.
* You need to audit whether fonts, figures, tables, abstracts, or references satisfy Springer specifications before camera-ready submission.
* You need to automatically detect and fix common template discrepancies (e.g., outdated `llncs.cls`, missing accessibility alt-text, Computer Modern vs. Times Roman font, missing `Disclosure of Interests`).

---

## The LNCS v2.25 Standard (Official Specification)

| Domain | Rule / Requirement in LNCS v2.25 | Typical Failure in Drafts |
| :--- | :--- | :--- |
| **Document Class** | `llncs.cls` version **2.25** (2026/09/03) | Using legacy `llncs.cls` v2.20 (2018) |
| **Font Encoding** | `\usepackage[T1]{fontenc}` | Missing `fontenc` |
| **Body Typeface** | Times Roman via `\usepackage{newtxtext}` and `\usepackage[varvw]{newtxmath}` | Defaulting to Computer Modern (`CMR10`) |
| **Math Package** | Do NOT load `amsmath` separately if `newtxmath` is loaded | `\usepackage{amsmath,amssymb}` loaded separately |
| **Prohibited Packages** | No `fancyhdr`, `a4wide`, `enumerate`, `enumitem`, `wrapfigure`, `subfigure`, `mathtools` | Custom layout/enumeration packages loaded |
| **Spacing Overrides** | **Strictly prohibited**: Do not modify `\textfloatsep`, `\floatsep`, `\intextsep`, `\abovecaptionskip`, `\topfraction`, `\textheight` | Manual squeezing of float or page spacing |
| **Hard Breaks** | Avoid `\pagebreak`, `\enlargethispage`, `\pageref` | Used to artificially force page budget |
| **Abstract** | Strictly **150--250 words** | Under 150 words or exceeding 250 words |
| **Keywords** | Inside `abstract`, Title Case, separated by `\and` | Separated by commas or semicolons |
| **Headings** | Max 4 levels; **only Level 1 & 2 numbered**; Level 3 (`\subsubsection`) and Level 4 (`\paragraph`) are run-in unnumbered | Numbering 3rd level headings |
| **Figures** | Placed above caption (`\caption` below); vector (EPS/PDF) preferred | Caption above; raster JPG for line art |
| **Accessibility (Alt-Text)** | **MANDATORY**: `\Description{...}` inside `\begin{figure}` under EU Accessibility Act & WCAG | Missing `\Description{...}` |
| **Tables** | Caption placed **ABOVE** table; avoid `\resizebox` if font scales below 8pt | Caption below table; heavy `\resizebox` |
| **Backmatter** | **MANDATORY**: `\begin{credits}` containing `\subsubsection{\discintname}` before `\bibliographystyle` | Missing Disclosure of Interests declaration |
| **Bibliography** | `\bibliographystyle{splncs04}`; DOIs in `doi = {...}` | Using unsorted or non-standard styles |
| **PDF PostScript Fonts** | **100% Type 1 or TrueType**; zero Type 3 fonts | Type 3 bitmap fonts embedded in PDF |
| **Page Budget** | Maximum allowed pages according to track (default: 15 or 16 pages) | Paper spilling over to an extra trailing page |

---

## Automated Audit Tool: `check_lncs.py`

A dedicated Python audit engine is bundled with this skill at `scripts/check_lncs.py`.

### 1. Run Audit Only
```bash
python3 .agents/skills/lncs-layout-checker/scripts/check_lncs.py <path_to_paper_dir> [--main main.tex] [--max-pages 16]
```

### 2. Run Audit with JSON Output
```bash
python3 .agents/skills/lncs-layout-checker/scripts/check_lncs.py <path_to_paper_dir> --json
```

### 3. Run Auto-Fix Mode
```bash
python3 .agents/skills/lncs-layout-checker/scripts/check_lncs.py <path_to_paper_dir> --fix [--template-dir data/template_LNCS]
```
The `--fix` mode automatically:
1. Copies official `llncs.cls` v2.25 if `--template-dir` is provided.
2. Updates font packages in `main.tex` to `[T1]{fontenc}`, `newtxtext`, and `newtxmath`.
3. Comments out redundant `\usepackage{amsmath,amssymb}` and unused `\usepackage{tikz}`.
4. Injects the standard `credits` and `\discintname` scaffold right before `\bibliographystyle`.

---

## Detailed Step-by-Step Remediation Guide

### Step 1: Upgrading `llncs.cls` to v2.25
Replace the local `llncs.cls` in your paper directory with the file from `data/template_LNCS/llncs.cls`:
```bash
cp data/template_LNCS/llncs.cls <paper_dir>/llncs.cls
```
Verify version header:
```latex
% LLNCS DOCUMENT CLASS -- version 2.25 (03-Sep-2026)
```

### Step 2: Configuring Modern Times Roman Fonts
In `main.tex`, replace default/legacy fonts with:
```latex
\usepackage[T1]{fontenc}
\usepackage{newtxtext}
\usepackage[varvw]{newtxmath}
```
*Remove* `\usepackage{amsmath,amssymb}` as `newtxmath` handles Times-compatible AMS symbols natively without font clash.

### Step 3: Adding Accessibility Alt-Text to Figures
Under the EU Accessibility Act and Springer Nature WCAG compliance:
Every `\begin{figure}` must contain `\Description{...}`:
```latex
\begin{figure}[!htbp]
\centering
\includegraphics[width=\textwidth]{figures/architecture.pdf}
\Description{Diagram of the 3-tier CTU-Chat system showing the centralized supervisor router connected via contract repair to 4 specialized agents: academic graph agent, financial calculation tool, scholarship retriever, and general assistant.}
\caption{Implemented system architecture.}
\label{fig:architecture}
\end{figure}
```

### Step 4: Adding Mandatory Disclosure of Interests
Right before `\bibliographystyle{splncs04}`, insert:
```latex
\begin{credits}
\subsubsection{\ackname}
This study was funded by [Grant Name / University Research Fund under Grant Number XYZ].

\subsubsection{\discintname}
The authors have no competing interests to declare that are relevant to the content of this article.
\end{credits}
```

### Step 5: Removing Manual Layout Overrides
Remove manual spacing tweaks from `main.tex`:
```latex
% REMOVE these overrides to comply with Springer typesetting:
% \setlength{\textfloatsep}{...}
% \setlength{\floatsep}{...}
% \setlength{\intextsep}{...}
% \setlength{\abovecaptionskip}{...}
% \setlength{\belowcaptionskip}{...}
% \renewcommand{\topfraction}{...}
```

### Step 6: Verifying Compiled PDF
Recompile with `latexmk` or `pdflatex`:
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Then inspect:
1. **Fonts**:
   ```bash
   pdffonts main.pdf
   ```
   Confirm all fonts are Type 1 (e.g. `TeXGyreTermesX`, `NewTXMI`) and no Type 3 fonts exist.
2. **Page Count**:
   ```bash
   pdfinfo main.pdf | grep Pages
   ```
   Ensure page count strictly adheres to the conference limit (e.g., $\le 15$ or $\le 16$ pages).
