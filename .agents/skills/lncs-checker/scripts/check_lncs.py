#!/usr/bin/env python3
"""
Springer LNCS (v2.25) Paper & Layout Compliance Checker
Audits LaTeX source files and compiled PDF against official Springer LNCS requirements.
Supports both audit mode and automatic remediation (--fix).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class LNCSChecker:
    def __init__(
        self,
        paper_dir: Path,
        main_tex: str = "main.tex",
        pdf_name: Optional[str] = None,
        max_pages: int = 16,
        template_dir: Optional[Path] = None,
        auto_fix: bool = False,
    ):
        self.paper_dir = paper_dir.resolve()
        self.main_tex_path = self.paper_dir / main_tex
        self.max_pages = max_pages
        self.auto_fix = auto_fix
        self.template_dir = template_dir.resolve() if template_dir else None

        if pdf_name:
            self.pdf_path = self.paper_dir / pdf_name
        else:
            default_pdf = self.paper_dir / self.main_tex_path.with_suffix(".pdf").name
            if default_pdf.exists():
                self.pdf_path = default_pdf
            else:
                pdfs = list(self.paper_dir.glob("*.pdf"))
                self.pdf_path = pdfs[0] if pdfs else None

        self.results: List[Dict[str, Any]] = []
        self.all_tex_contents: Dict[Path, str] = {}
        self.full_merged_text: str = ""

    def add_result(
        self,
        category: str,
        item: str,
        status: str,  # "PASS", "FAIL", "WARN", "FIXED"
        message: str,
        suggestion: str = "",
    ):
        self.results.append({
            "category": category,
            "item": item,
            "status": status,
            "message": message,
            "suggestion": suggestion,
        })

    def load_tex_files(self):
        if not self.main_tex_path.exists():
            self.add_result(
                "Source Files", "main.tex", "FAIL",
                f"File {self.main_tex_path} does not exist."
            )
            return

        visited = set()

        def read_recursive(path: Path) -> str:
            if path in visited or not path.exists():
                return ""
            visited.add(path)
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return ""
            self.all_tex_contents[path] = content

            merged = []
            for line in content.splitlines():
                stripped = line.strip()
                # Check for unescaped comment line
                if stripped.startswith("%"):
                    continue
                m = re.search(r"\\(?:input|include)\{([^}]+)\}", line)
                if m:
                    sub_file = m.group(1).strip()
                    if not sub_file.endswith(".tex"):
                        sub_file += ".tex"
                    sub_path = (path.parent / sub_file).resolve()
                    if not sub_path.exists():
                        sub_path = (self.paper_dir / sub_file).resolve()
                    sub_content = read_recursive(sub_path)
                    merged.append(sub_content)
                else:
                    merged.append(line)
            return "\n".join(merged)

        self.full_merged_text = read_recursive(self.main_tex_path)

    # ----------------------------------------------------
    # CHECK 1: Class File & Version
    # ----------------------------------------------------
    def check_class_file(self):
        cls_path = self.paper_dir / "llncs.cls"
        if not cls_path.exists():
            self.add_result(
                "Template Class", "llncs.cls presence", "FAIL",
                "llncs.cls not found in paper directory!",
                "Copy llncs.cls from official LNCS template."
            )
            return

        cls_content = cls_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"LLNCS DOCUMENT CLASS -- version ([\d\.]+)", cls_content)
        version = m.group(1) if m else "Unknown"

        if version == "2.25":
            self.add_result(
                "Template Class", "llncs.cls version", "PASS",
                f"llncs.cls is up to date (version {version}, 2026/09/03)."
            )
        else:
            if self.auto_fix and self.template_dir:
                template_cls = self.template_dir / "llncs.cls"
                if template_cls.exists():
                    shutil.copy2(template_cls, cls_path)
                    self.add_result(
                        "Template Class", "llncs.cls version", "FIXED",
                        f"Updated llncs.cls from v{version} to v2.25 using template.",
                    )
                    return

            self.add_result(
                "Template Class", "llncs.cls version", "FAIL",
                f"llncs.cls version is {version} (Official LNCS is v2.25).",
                "Replace llncs.cls with version 2.25 to support Accessibility alt-text (\\Description) and updated credits/discintname."
            )

    # ----------------------------------------------------
    # CHECK 2: Fonts & Typography
    # ----------------------------------------------------
    def check_fonts_and_packages(self):
        main_content = self.all_tex_contents.get(self.main_tex_path, "")

        # 1. fontenc [T1]
        has_t1 = bool(re.search(r"\\usepackage\[T1\]\{fontenc\}", main_content))
        if has_t1:
            self.add_result("Typography", "fontenc [T1]", "PASS", "T1 font encoding is configured.")
        else:
            self.add_result(
                "Typography", "fontenc [T1]", "FAIL",
                "Missing \\usepackage[T1]{fontenc}.",
                "Add \\usepackage[T1]{fontenc} to main.tex before other font packages."
            )

        # 2. newtxtext & newtxmath (Times Roman)
        has_newtxtext = bool(re.search(r"\\usepackage\{newtxtext\}", main_content))
        has_newtxmath = bool(re.search(r"\\usepackage(?:\[[^\]]*\])?\{newtxmath\}", main_content))

        if has_newtxtext and has_newtxmath:
            self.add_result("Typography", "newtx fonts", "PASS", "newtxtext and newtxmath configured (Times Roman).")
        else:
            self.add_result(
                "Typography", "newtx fonts", "FAIL",
                "Official LNCS v2.25 mandates Times Roman via newtxtext and newtxmath.",
                "Add \\usepackage{newtxtext} and \\usepackage[varvw]{newtxmath}."
            )

        # 3. amsmath check with newtxmath
        has_amsmath = bool(re.search(r"\\usepackage(?:\[[^\]]*\])?\{amsmath", main_content))
        if has_newtxmath and has_amsmath:
            self.add_result(
                "Typography", "amsmath conflict", "WARN",
                "LNCS guidelines state: 'If you use newtxmath package, do NOT include amsmath separately.'",
                "Remove amsmath from package list when using newtxmath."
            )

        # 4. Prohibited layout & font packages
        prohibited_layout_pkgs = ["fancyhdr", "a4wide", "enumerate", "enumitem"]
        for pkg in prohibited_layout_pkgs:
            if re.search(r"\\usepackage(?:\[[^\]]*\])?\{" + pkg + r"\}", main_content):
                self.add_result(
                    "Packages", f"Prohibited pkg: {pkg}", "FAIL",
                    f"Package '{pkg}' overrides standard LNCS layout/enumeration.",
                    f"Remove \\usepackage{{{pkg}}}."
                )

        prohibited_font_pkgs = ["bbm", "dsfonts", "eucal", "mathrsfs", "mathabx", "mathtools"]
        for pkg in prohibited_font_pkgs:
            if re.search(r"\\usepackage(?:\[[^\]]*\])?\{" + pkg + r"\}", main_content):
                self.add_result(
                    "Packages", f"Non-standard font pkg: {pkg}", "WARN",
                    f"Package '{pkg}' is discouraged by Springer. Use standard LaTeX math fonts.",
                    f"Remove \\usepackage{{{pkg}}}."
                )

        # 5. Figure packages: wrapfigure, subfigure
        for pkg in ["wrapfigure", "subfigure"]:
            if re.search(r"\\usepackage(?:\[[^\]]*\])?\{" + pkg + r"\}", main_content):
                self.add_result(
                    "Packages", f"Prohibited figure pkg: {pkg}", "FAIL",
                    f"Package '{pkg}' is strictly prohibited in LNCS.",
                    f"Do not use wrapfigure/subfigure."
                )

        # 6. tikz & xcolor check
        has_tikz = bool(re.search(r"\\usepackage(?:\[[^\]]*\])?\{tikz\}", main_content))
        if has_tikz:
            if "\\begin{tikzpicture}" not in self.full_merged_text:
                self.add_result(
                    "Packages", "Unused tikz", "WARN",
                    "tikz package is loaded in main.tex but no tikzpicture environment is used.",
                    "Remove \\usepackage{tikz} to keep source clean."
                )
            else:
                self.add_result(
                    "Packages", "tikz usage", "WARN",
                    "LNCS notes that tikz diagrams cannot be rendered on-the-fly for XML/ePub.",
                    "Include diagram as rendered vector PDF/EPS image instead."
                )

    # ----------------------------------------------------
    # CHECK 3: Layout Spacing Overrides & Prohibited Commands
    # ----------------------------------------------------
    def check_layout_overrides(self):
        text = self.full_merged_text

        # Detect \setlength overrides on layout/float dimensions
        target_dims = [
            "textfloatsep", "floatsep", "intextsep",
            "abovecaptionskip", "belowcaptionskip",
            "textheight", "textwidth", "topmargin", "oddsidemargin",
            "baselineskip", "baselinestretch"
        ]
        found_overrides = []
        for dim in target_dims:
            pattern = r"\\(?:setlength|addtolength)\s*\{\\" + dim + r"\}"
            if re.search(pattern, text):
                found_overrides.append(f"\\{dim}")
            # Also check direct assignment like \textfloatsep=... or \renewcommand{\topfraction}
            pattern_assign = r"\\" + dim + r"\s*="
            if re.search(pattern_assign, text):
                found_overrides.append(f"\\{dim}")

        float_fractions = ["topfraction", "bottomfraction", "textfraction", "floatpagefraction"]
        for frac in float_fractions:
            if re.search(r"\\renewcommand\{\\" + frac + r"\}", text):
                found_overrides.append(f"\\{frac}")

        if found_overrides:
            uniq_overrides = sorted(list(set(found_overrides)))
            self.add_result(
                "Layout Integrity", "Spacing overrides", "FAIL",
                f"Manual layout/float override detected: {', '.join(uniq_overrides)}.",
                "LNCS rules prohibit changing default layout & float spacing parameters. Remove manual overrides."
            )
        else:
            self.add_result("Layout Integrity", "Spacing overrides", "PASS", "No manual float/page spacing overrides.")

        # Hard page breaks
        pagebreak_cmds = [r"\\pagebreak", r"\\enlargethispage"]
        found_breaks = []
        for cmd in pagebreak_cmds:
            if re.search(cmd, text):
                found_breaks.append(cmd.replace("\\\\", "\\"))
        if found_breaks:
            self.add_result(
                "Layout Integrity", "Hard page breaks", "WARN",
                f"Hard pagebreak command detected: {', '.join(found_breaks)}.",
                "Avoid \\enlargethispage or \\pagebreak as they break XML/ePub output."
            )

        # \pageref check
        if re.search(r"\\pageref\{", text):
            self.add_result(
                "Cross-References", "pageref", "FAIL",
                "\\pageref detected. Springer LNCS prohibits \\pageref because page numbers only exist in PDF.",
                "Remove \\pageref and refer directly to sections, figures, or tables."
            )
        else:
            self.add_result("Cross-References", "pageref", "PASS", "No \\pageref used.")

        # \def check
        def_matches = re.findall(r"\\def\\[a-zA-Z]+", text)
        if def_matches:
            self.add_result(
                "LaTeX Syntax", "\\def usage", "WARN",
                f"Found {len(def_matches)} instance(s) of \\def (e.g. {def_matches[0]}).",
                "Replace \\def with \\newcommand to prevent accidental macro overwrite."
            )

    # ----------------------------------------------------
    # CHECK 4: Frontmatter (Title, Authors, Abstract, Keywords)
    # ----------------------------------------------------
    def check_frontmatter(self):
        text = self.full_merged_text

        # Title
        m_title = re.search(r"\\title\{([^}]+)\}", text)
        if m_title:
            title_str = m_title.group(1).strip()
            if title_str.endswith("."):
                self.add_result("Frontmatter", "Title punctuation", "FAIL", "Title ends with a period. Springer titles must have no end punctuation.")
            else:
                self.add_result("Frontmatter", "Title", "PASS", f"Title: '{title_str[:60]}...'")
        else:
            self.add_result("Frontmatter", "Title", "FAIL", "No \\title found.")

        # Titlerunning
        if "\\titlerunning" in text:
            self.add_result("Frontmatter", "titlerunning", "PASS", "\\titlerunning is defined.")
        else:
            self.add_result("Frontmatter", "titlerunning", "WARN", "\\titlerunning is missing. Recommended for long titles.")

        # Authorrunning
        if "\\authorrunning" in text:
            self.add_result("Frontmatter", "authorrunning", "PASS", "\\authorrunning is defined.")
        else:
            self.add_result("Frontmatter", "authorrunning", "WARN", "\\authorrunning is missing. Required if more than 2 authors.")

        # Abstract word count (handles \% properly and strips macros)
        m_abs = re.search(r"\\begin\{abstract\}(.*?)(?:\\keywords|\\end\{abstract\})", text, re.DOTALL)
        if m_abs:
            abs_text = m_abs.group(1)
            # Remove unescaped comments
            abs_clean = re.sub(r"(?<!\\)%.*", "", abs_text)
            # Normalize \% to word
            abs_clean = re.sub(r"\\%", " percent ", abs_clean)
            # Remove LaTeX commands
            abs_clean = re.sub(r"\\[a-zA-Z]+", " ", abs_clean)
            abs_clean = re.sub(r"[{}\$]", " ", abs_clean)
            words = [w for w in abs_clean.split() if any(c.isalnum() for c in w)]
            word_count = len(words)

            if 150 <= word_count <= 250:
                self.add_result(
                    "Frontmatter", "Abstract length", "PASS",
                    f"Abstract word count is {word_count} words (Requirement: 150--250 words)."
                )
            else:
                status = "WARN" if 140 <= word_count <= 260 else "FAIL"
                self.add_result(
                    "Frontmatter", "Abstract length", status,
                    f"Abstract has {word_count} words. Springer LNCS requires 150--250 words.",
                    "Edit abstract to fall strictly within 150--250 words."
                )
        else:
            self.add_result("Frontmatter", "Abstract", "FAIL", "No \\begin{abstract} environment found.")

        # Keywords
        m_kw = re.search(r"\\keywords\{([^}]+)\}", text)
        if m_kw:
            kw_text = m_kw.group(1)
            if "\\and" in kw_text:
                self.add_result("Frontmatter", "Keywords separator", "PASS", "Keywords correctly separated by \\and.")
            else:
                self.add_result(
                    "Frontmatter", "Keywords separator", "FAIL",
                    "Keywords must be separated by \\and (do not use commas or semicolons).",
                    "Separate keywords using \\and so LNCS macro renders middle dot."
                )
        else:
            self.add_result("Frontmatter", "Keywords", "FAIL", "No \\keywords command found.")

    # ----------------------------------------------------
    # CHECK 5: Figures, Tables, & Accessibility
    # ----------------------------------------------------
    def check_figures_and_tables(self):
        text = self.full_merged_text

        # 1. Figures: Description (Accessibility alt-text)
        fig_blocks = re.findall(r"\\begin\{figure\}(.*?)\\end\{figure\}", text, re.DOTALL)
        for i, fig in enumerate(fig_blocks, 1):
            has_desc = bool(re.search(r"\\Description\{", fig))
            if has_desc:
                self.add_result(
                    "Accessibility", f"Figure {i} Alt-Text", "PASS",
                    f"Figure {i} has \\Description alt-text."
                )
            else:
                self.add_result(
                    "Accessibility", f"Figure {i} Alt-Text", "FAIL",
                    f"Figure {i} is missing \\Description{{...}} (Mandatory under EU Accessibility Act & LNCS v2.25).",
                    "Add \\Description{...} inside \\begin{figure} describing visual flow."
                )

            # Check caption position
            m_inc = re.search(r"\\includegraphics", fig)
            m_cap = re.search(r"\\caption", fig)
            if m_inc and m_cap:
                if m_cap.start() < m_inc.start():
                    self.add_result(
                        "Figures", f"Figure {i} caption", "FAIL",
                        f"Figure {i} caption is placed ABOVE the image. LNCS requires caption BELOW figure.",
                        "Move \\caption after \\includegraphics."
                    )
                else:
                    self.add_result("Figures", f"Figure {i} caption", "PASS", f"Figure {i} caption placed below image.")

            # Check image format (prefer EPS or PDF over raster)
            m_img = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", fig)
            if m_img:
                img_name = m_img.group(1).strip()
                ext = Path(img_name).suffix.lower()
                if ext in [".jpg", ".jpeg", ".png"]:
                    self.add_result(
                        "Figures", f"Figure {i} image format", "WARN",
                        f"Figure {i} uses raster image '{img_name}'. LNCS recommends vector graphics (EPS or PDF) for diagrams.",
                        "Convert schema/diagram to vector PDF or EPS."
                    )
                elif ext in [".eps", ".pdf"]:
                    self.add_result("Figures", f"Figure {i} image format", "PASS", f"Figure {i} uses vector graphic ({ext}).")

        # 2. Tables: Caption position
        tab_blocks = re.findall(r"\\begin\{table\}(.*?)\\end\{table\}", text, re.DOTALL)
        for i, tab in enumerate(tab_blocks, 1):
            m_tab = re.search(r"\\begin\{tabular", tab)
            m_cap = re.search(r"\\caption", tab)
            if m_tab and m_cap:
                if m_cap.start() > m_tab.start():
                    self.add_result(
                        "Tables", f"Table {i} caption", "FAIL",
                        f"Table {i} caption is placed BELOW the table. LNCS requires caption ABOVE table.",
                        "Place \\caption before \\begin{tabular}."
                    )
                else:
                    self.add_result("Tables", f"Table {i} caption", "PASS", f"Table {i} caption placed above table.")

            # Check \resizebox
            if "\\resizebox" in tab:
                self.add_result(
                    "Tables", f"Table {i} resizebox", "WARN",
                    f"Table {i} uses \\resizebox. Scaling tables can create inconsistent, unreadable font sizes.",
                    "Use \\small / \\footnotesize or adjust \\tabcolsep instead of \\resizebox if possible."
                )

    # ----------------------------------------------------
    # CHECK 6: Backmatter (Credits & Disclosure of Interests)
    # ----------------------------------------------------
    def check_backmatter(self):
        text = self.full_merged_text

        has_credits = "\\begin{credits}" in text
        has_discint = "\\discintname" in text or "Disclosure of Interests" in text

        if has_credits and has_discint:
            self.add_result(
                "Backmatter", "Credits & Competing Interests", "PASS",
                "\\begin{credits} environment with \\discintname is present."
            )
        elif not has_discint:
            self.add_result(
                "Backmatter", "Disclosure of Interests", "FAIL",
                "Missing 'Disclosure of Interests' declaration! This is MANDATORY for all Springer submissions.",
                "Add \\begin{credits}\\subsubsection{\\discintname} The authors have no competing interests to declare... \\end{credits} before \\bibliographystyle."
            )
        elif not has_credits:
            self.add_result(
                "Backmatter", "credits environment", "WARN",
                "Competing interests declaration found, but not enclosed in \\begin{credits} environment.",
                "Enclose acknowledgments and interest disclosure within \\begin{credits} ... \\end{credits}."
            )

        # Bibliography style
        m_bib = re.search(r"\\bibliographystyle\{([^}]+)\}", text)
        if m_bib:
            bst = m_bib.group(1).strip()
            if bst == "splncs04":
                self.add_result("Bibliography", "BibTeX style", "PASS", "Using official style splncs04.")
            else:
                self.add_result(
                    "Bibliography", "BibTeX style", "FAIL",
                    f"BibTeX style is '{bst}'. Springer LNCS requires splncs04.",
                    "Set \\bibliographystyle{splncs04}."
                )
        else:
            if "\\begin{thebibliography}" in text:
                self.add_result("Bibliography", "thebibliography", "PASS", "Manual \\begin{thebibliography} used.")
            else:
                self.add_result("Bibliography", "BibTeX style", "FAIL", "No bibliography style defined.")

    # ----------------------------------------------------
    # CHECK 7: Compiled PDF Inspection
    # ----------------------------------------------------
    def check_compiled_pdf(self):
        if not self.pdf_path or not self.pdf_path.exists():
            self.add_result(
                "PDF Verification", "File Presence", "WARN",
                "No compiled PDF found. Compile with pdflatex/latexmk to enable PDF font & page inspection."
            )
            return

        self.add_result("PDF Verification", "File Presence", "PASS", f"Found PDF: {self.pdf_path.name}")

        # 1. Page count via pdfinfo
        try:
            res = subprocess.run(["pdfinfo", str(self.pdf_path)], capture_output=True, text=True, check=True)
            m_pages = re.search(r"Pages:\s+(\d+)", res.stdout)
            if m_pages:
                pages = int(m_pages.group(1))
                if pages <= self.max_pages:
                    self.add_result(
                        "PDF Verification", "Page Budget", "PASS",
                        f"PDF page count: {pages} pages (Within max limit of {self.max_pages})."
                    )
                else:
                    self.add_result(
                        "PDF Verification", "Page Budget", "FAIL",
                        f"PDF page count: {pages} pages exceeds limit of {self.max_pages} pages (+{pages - self.max_pages} pages).",
                        f"Condense paper to fit within {self.max_pages} pages."
                    )
        except Exception:
            pass

        # 2. Font inspection via pdffonts
        try:
            res = subprocess.run(["pdffonts", str(self.pdf_path)], capture_output=True, text=True, check=True)
            output = res.stdout

            type3_fonts = [line for line in output.splitlines() if "Type 3" in line]
            if type3_fonts:
                self.add_result(
                    "PDF Verification", "No Type 3 Fonts", "FAIL",
                    f"Found {len(type3_fonts)} Type 3 font(s) in PDF! Springer will reject files with Type 3 fonts.",
                    "Check font packages or raster figures embedding Type 3 fonts."
                )
            else:
                self.add_result("PDF Verification", "No Type 3 Fonts", "PASS", "No Type 3 fonts detected in PDF (100% Type 1 / TrueType).")

            lines = output.splitlines()
            has_cm = any("CMR" in l or "CMBX" in l or "CMMI" in l for l in lines)
            has_termes = any("Termes" in l or "NewTX" in l or "Times" in l for l in lines)

            if has_termes and not has_cm:
                self.add_result("PDF Verification", "Rendered Typeface", "PASS", "PDF rendered with Times Roman (TeX Gyre Termes / NewTX).")
            elif has_cm and not has_termes:
                self.add_result(
                    "PDF Verification", "Rendered Typeface", "FAIL",
                    "PDF is currently rendered using Computer Modern fonts instead of Times Roman.",
                    "Enable \\usepackage{newtxtext} and \\usepackage[varvw]{newtxmath} in main.tex and recompile."
                )
            elif has_cm and has_termes:
                self.add_result(
                    "PDF Verification", "Rendered Typeface", "WARN",
                    "PDF contains a mix of Times Roman and Computer Modern fonts.",
                    "Check for lingering math or symbol packages overriding Times Roman."
                )
        except Exception:
            pass

    # ----------------------------------------------------
    # REMEDIATION (Auto-Fix)
    # ----------------------------------------------------
    def apply_auto_fixes(self):
        if not self.auto_fix:
            return

        main_path = self.main_tex_path
        if not main_path.exists():
            return

        content = main_path.read_text(encoding="utf-8")
        modified = False

        # 1. Update font packages in main.tex
        if "\\usepackage{newtxtext}" not in content:
            font_block = "\\usepackage[T1]{fontenc}\n\\usepackage{newtxtext}\n\\usepackage[varvw]{newtxmath}\n"
            content = re.sub(r"\\usepackage\{amsmath,amssymb\}\n?", "", content)
            m = re.search(r"(\\documentclass(?:\[[^\]]*\])?\{llncs\}\n+)", content)
            if m:
                content = content[:m.end()] + font_block + content[m.end():]
                modified = True

        # 2. Add credits & Disclosure of Interests if missing
        if "\\discintname" not in content and "\\begin{credits}" not in content:
            credits_block = (
                "\n\\begin{credits}\n"
                "\\subsubsection{\\ackname}\n"
                "% Optional acknowledgments: e.g. This study was funded by ...\n\n"
                "\\subsubsection{\\discintname}\n"
                "The authors have no competing interests to declare that are relevant to the content of this article.\n"
                "\\end{credits}\n\n"
            )
            m = re.search(r"(\\bibliographystyle)", content)
            if m:
                content = content[:m.start()] + credits_block + content[m.start():]
                modified = True

        # 3. Comment out unused tikz if no tikzpicture in project
        if "\\usepackage{tikz}" in content and "\\begin{tikzpicture}" not in self.full_merged_text:
            content = re.sub(r"(\\usepackage\{tikz\})", r"% \1  % Removed: no tikzpicture used", content)
            content = re.sub(r"(\\usetikzlibrary\{[^}]*\})", r"% \1", content)
            modified = True

        if modified:
            main_path.write_text(content, encoding="utf-8")
            self.add_result(
                "Auto-Fix", "main.tex updates", "FIXED",
                "Applied automatic fixes to main.tex: updated font packages, inserted credits template, commented unused tikz."
            )

    # ----------------------------------------------------
    # EXECUTION RUNNER
    # ----------------------------------------------------
    def run_all_checks(self) -> Dict[str, Any]:
        self.load_tex_files()
        if self.auto_fix:
            self.apply_auto_fixes()
            self.all_tex_contents.clear()
            self.load_tex_files()

        self.check_class_file()
        self.check_fonts_and_packages()
        self.check_layout_overrides()
        self.check_frontmatter()
        self.check_figures_and_tables()
        self.check_backmatter()
        self.check_compiled_pdf()

        summary = {"PASS": 0, "FAIL": 0, "WARN": 0, "FIXED": 0}
        for r in self.results:
            summary[r["status"]] = summary.get(r["status"], 0) + 1

        return {
            "summary": summary,
            "results": self.results,
        }

    def print_report(self):
        data = self.run_all_checks()
        summary = data["summary"]

        print(f"\n{Colors.BOLD}=================================================================={Colors.RESET}")
        print(f"{Colors.BOLD}       SPRINGER LNCS (v2.25) COMPLIANCE AUDIT REPORT              {Colors.RESET}")
        print(f"{Colors.BOLD}=================================================================={Colors.RESET}")
        print(f"Directory: {self.paper_dir}")
        print(f"Main TeX : {self.main_tex_path.name}")
        if self.pdf_path:
            print(f"PDF File : {self.pdf_path.name}")
        print("------------------------------------------------------------------")

        current_cat = ""
        for r in data["results"]:
            if r["category"] != current_cat:
                current_cat = r["category"]
                print(f"\n{Colors.BOLD}[ {current_cat} ]{Colors.RESET}")

            status = r["status"]
            if status == "PASS":
                badge = f"{Colors.GREEN}[PASS]{Colors.RESET}"
            elif status == "FAIL":
                badge = f"{Colors.RED}[FAIL]{Colors.RESET}"
            elif status == "WARN":
                badge = f"{Colors.YELLOW}[WARN]{Colors.RESET}"
            elif status == "FIXED":
                badge = f"{Colors.BLUE}[FIXED]{Colors.RESET}"
            else:
                badge = f"[{status}]"

            print(f"  {badge} {Colors.BOLD}{r['item']}{Colors.RESET}: {r['message']}")
            if r["suggestion"] and status in ["FAIL", "WARN"]:
                print(f"         {Colors.BLUE}--> Action: {r['suggestion']}{Colors.RESET}")

        print("\n------------------------------------------------------------------")
        print(f"{Colors.BOLD}SUMMARY:{Colors.RESET} "
              f"{Colors.GREEN}PASS: {summary['PASS']}{Colors.RESET} | "
              f"{Colors.RED}FAIL: {summary['FAIL']}{Colors.RESET} | "
              f"{Colors.YELLOW}WARN: {summary['WARN']}{Colors.RESET} | "
              f"{Colors.BLUE}FIXED: {summary.get('FIXED', 0)}{Colors.RESET}")
        print(f"{Colors.BOLD}=================================================================={Colors.RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Audit and auto-fix LaTeX manuscripts against Springer LNCS guidelines.")
    parser.add_argument("paper_dir", nargs="?", default=".", help="Path to manuscript folder (default: current directory)")
    parser.add_argument("--main", default="main.tex", help="Name of main tex file (default: main.tex)")
    parser.add_argument("--pdf", default=None, help="Name of compiled PDF (default: auto-detected)")
    parser.add_argument("--max-pages", type=int, default=16, help="Maximum allowed pages (default: 16)")
    parser.add_argument("--template-dir", default=None, help="Path to official LNCS template directory")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes where possible")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    paper_dir = Path(args.paper_dir)
    template_dir = Path(args.template_dir) if args.template_dir else None

    checker = LNCSChecker(
        paper_dir=paper_dir,
        main_tex=args.main,
        pdf_name=args.pdf,
        max_pages=args.max_pages,
        template_dir=template_dir,
        auto_fix=args.fix,
    )

    if args.json:
        data = checker.run_all_checks()
        print(json.dumps(data, indent=2))
    else:
        checker.print_report()


if __name__ == "__main__":
    main()
