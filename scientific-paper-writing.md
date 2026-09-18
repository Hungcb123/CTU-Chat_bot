---
name: scientific-paper-writing
description: >
  Guides the writing and revision of scientific research papers for Computer Science / AI venues
  (IEEE, ACM, Springer LNCS). Covers every section from Title through References with strict rules
  on neutral tone, hedging language, evidence-grounded claims, and LaTeX output.
  Use when the user asks to write, revise, review, or improve any part of a research paper,
  conference submission, or journal manuscript. Also use when the user mentions "paper", "manuscript",
  "submission", "abstract", "introduction", "related work", "methodology", "experiments", "conclusion",
  or "claim" in an academic context.
---

# Scientific Paper Writing Skill

## Overview

This skill provides comprehensive, section-by-section guidance for writing and revising scientific
research papers targeting Computer Science and AI venues (IEEE, ACM, Springer LNCS). It enforces
**neutral academic tone**, forbids unsupported strong claims, and outputs publication-ready LaTeX.

---

## ⚠️ CRITICAL RULE: NO STRONG CLAIMS

**This is the single most important rule in this entire skill.**

Before writing ANY sentence, mentally apply this filter:

> "Can I defend this claim with evidence presented in this paper?"
> If NO → **hedge it, qualify it, or remove it.**

### Forbidden Patterns (Strong Claims) — NEVER Use These

| ❌ Forbidden | ✅ Neutral Alternative |
|---|---|
| "X **proves** that..." | "X **suggests** that..." / "The results **indicate** that..." |
| "X **clearly shows**..." | "X **appears to indicate**..." |
| "X **significantly outperforms**..." | "X **achieves higher scores on the evaluated metrics than**..." |
| "X **is superior to**..." | "X **compares favorably with** ... on the tested benchmarks" |
| "X **solves** the problem of..." | "X **addresses** / **mitigates** the problem of..." |
| "X **guarantees**..." | "X **is designed to support**..." / "X **is intended to**..." |
| "X **is the first** to..." | "**To the best of our knowledge**, X is **among the first** to..." |
| "X **always**..." | "X **tends to** ... / **in the evaluated cases**..." |
| "X **never** fails..." | "X **did not exhibit failures in the tested scenarios**..." |
| "X **dramatically** improves..." | "X **is associated with improvements in**..." |
| "X **revolutionizes**..." | "X **offers a different approach to**..." |
| "This **novel** approach..." | "The **proposed** approach..." |
| "**Crucially** / **Importantly**..." | (Remove the intensifier, let the evidence speak) |
| "**Clearly** / **Obviously**..." | (Remove — if it were obvious, you wouldn't need to state it) |
| "Our method **achieves state-of-the-art**..." | "Our method **achieves competitive results** on the evaluated benchmarks..." |
| "X **eliminates** the need for..." | "X **reduces the reliance on**..." |
| "The results **confirm**..." | "The results **are consistent with**..." / "The results **support**..." |
| "X **is essential** for..." | "X **may contribute to** ... / **can support**..." |

### Hedging Language Bank — USE These Liberally

**Verbs (tentative):**
`suggest`, `indicate`, `appear to`, `tend to`, `seem to`, `may`, `might`, `could`,
`is associated with`, `is consistent with`, `support the hypothesis that`

**Adverbs / Qualifiers:**
`partially`, `to some extent`, `in certain cases`, `under the evaluated conditions`,
`within the scope of this study`, `on the tested benchmarks`, `in the current setting`,
`to the best of our knowledge`, `in practice`, `in principle`

**Framing phrases:**
- "These findings suggest that..."
- "The results are consistent with the interpretation that..."
- "One possible explanation is that..."
- "This observation may be attributed to..."
- "While these results are promising, further investigation is needed to..."
- "The evidence supports, but does not conclusively establish, that..."
- "In the evaluated setting, the proposed approach..."
- "These patterns are observed across the tested configurations, though generalization to other settings remains to be verified."

### Claim Strength Audit — Run Before Every Section Submission

For every claim in the paper, classify it:

| Level | Description | Action |
|---|---|---|
| **L1: Factual** | Directly measurable from data/tables | ✅ Keep as-is with citation to table/figure |
| **L2: Supported** | Reasonably inferred from presented evidence | ✅ Keep with hedging verb |
| **L3: Speculative** | Goes beyond presented evidence | ⚠️ Must hedge heavily or move to Future Work |
| **L4: Unsupported** | No evidence in paper | ❌ Remove or rewrite with evidence |

---

## Section-by-Section Writing Guide

### 1. Title

**Rules:**
- Must cite the core intervention/method, context/domain, and ideally a design keyword or main finding
- Use subtitles sparingly for study group names or clarifications
- Keep concise but informative (typically 10–15 words)
- Do NOT use marketing language ("revolutionary", "groundbreaking", "novel")

**Template:**
```
[Method Name]: [Design Keyword] [Core Technique] for [Application Domain]
```

**Example:**
```
CTU-Chat: Supervisor-Routed Multi-Agent RAG with Heterogeneous
Knowledge Allocation for University Counseling
```

---

### 2. Abstract

**Purpose:** A brief, self-contained summary of the entire paper. The reader should understand
*what was studied*, *how*, *key findings*, and *why it matters* — without reading the full paper.

**Structure (5-sentence pattern):**
1. **Topic/Problem** — What challenge does this address?
2. **Objective + Method** — What did you do and how?
3. **Key Results** — What are the main quantitative findings?
4. **Implication** — Why do these findings matter?
5. *(Optional)* Scope limitation or qualifier

**Rules:**
- Length: 150–300 words (follow venue guidelines)
- Highly condensed — no filler, no repetition
- NO citations in the abstract
- NO detailed discussion or interpretation
- NO vague statements like "results are discussed"
- Present key results with actual numbers
- **MUST use neutral language** — hedge the implication sentence

**Mistakes to Avoid:**
- Too much background (>2 sentences of context)
- No clear quantitative result
- Adding citations or detailed discussion
- Writing vague conclusions like "results are discussed" or "results are promising"

**LaTeX Template:**
```latex
\begin{abstract}
[Problem statement — 1-2 sentences].
We present [System/Method Name], a [brief description of approach].
[Core mechanism — 1-2 sentences describing how it works].
Evaluation on [benchmark/dataset] shows that [System] achieves
[metric1] of [value1] and [metric2] of [value2] on the [test set description].
These findings suggest that [hedged implication statement].
\end{abstract}
```

---

### 3. Introduction

**Structure (6-paragraph pattern):**

| Paragraph | Content | Color Code |
|---|---|---|
| 1. Topic Introduction | Broad context, why this domain matters | General → Specific |
| 2. Topic Background | Existing approaches, what has been done | Literature landscape |
| 3. Research Problem | Gaps, limitations, what remains unsolved | The "gap" paragraph |
| 4. Research Objective | What this paper aims to do, specific goals | "This paper presents..." |
| 5. Research Methodology | Brief overview of approach (expand in §3) | How you do it |
| 6. Paper Outline | Section-by-section roadmap | "The rest of this paper..." |

**Rules:**
- Funnel structure: broad context → specific gap → your contribution
- Each paragraph should have a clear topic sentence
- Citations are expected in paragraphs 1-3
- Contributions should be stated as observations, not as absolute claims
- End with a clear paper outline paragraph
- **A strong introduction clearly presents the background, identifies the gap, defines the objective, and outlines how your study addresses the problem**

**Tip:** The introduction should make the reader understand:
1. Why the problem matters
2. What others have done (and what's missing)
3. What you propose
4. How the paper is organized

**Neutral Phrasing for Contributions:**
```
❌ "We make the following groundbreaking contributions..."
✅ "The main contributions of this work are as follows:"

❌ "This is the first system that..."
✅ "To the best of our knowledge, this work is among the first to..."

❌ "Our approach fundamentally changes..."
✅ "The proposed approach offers a different perspective on..."
```

---

### 4. Related Work / Literature Review

**Purpose:** Establish the knowledge landscape, position your work relative to existing literature,
and justify why a new approach is needed.

**Structure:**
- Organize by **theme/topic**, NOT by paper
- Each subsection covers one research thread
- End each subsection with a transition showing how it motivates your work
- Final subsection: **Comparative Synthesis and Research Gaps**

**Rules:**
- Present prior work **fairly and accurately** — never misrepresent to make your work look better
- Use present tense for established knowledge, past tense for specific study findings
- Identify genuine gaps, not strawman limitations
- Connect gaps explicitly to your proposed approach
- Acknowledge overlap with existing methods honestly

**Neutral Phrasing:**
```
❌ "Previous approaches fail to..."
✅ "Previous approaches focus primarily on... but do not directly address..."

❌ "No prior work has considered..."
✅ "This aspect remains relatively underexplored in the existing literature."

❌ "Their method is inferior because..."
✅ "Their method addresses X but differs from the present work in its handling of Y."
```

---

### 5. Proposed Model / Methodology

**Purpose:** Describe **in detail** what you did and how, so that another researcher could
reproduce your work.

**Structure:**
1. Design principles / overview
2. Architecture / system overview (with figure reference)
3. Component-by-component description
4. Algorithms (pseudocode if applicable)
5. Implementation details

**Rules:**
- Describe in detail what you did and how
- Detail selection criteria for datasets/population
- Describe all techniques, analyses, and tools used
- Include ethical considerations where applicable
- Statistical methods should be described in dedicated paragraphs
- Use consistent notation throughout
- Every symbol/variable must be defined at first use
- Reference figures and tables inline
- Be precise about hyperparameters, configurations, and design choices

**LaTeX Template for Algorithm:**
```latex
\begin{algorithm}[t]
\caption{[Algorithm Name]}
\label{alg:name}
\begin{algorithmic}[1]
\Require [Input description]
\Ensure [Output description]
\State [Step 1]
\If{[condition]}
    \State [action]
\EndIf
\State \Return [output]
\end{algorithmic}
\end{algorithm}
```

---

### 6. Experimental Results

**Purpose:** Present empirical evidence that evaluates the proposed approach.

**Structure:**
1. Experimental setup (benchmark, dataset, protocols)
2. Evaluation metrics (define each metric clearly)
3. Baselines / comparison configurations
4. Results presentation (tables + figures)
5. Analysis and interpretation

**Rules:**
- **Present results objectively** — avoid commentary and interpretation in the results table itself
- Give a result for every method/metric presented in the experimental setup
- Use appropriate illustrations (tables for precise numbers, figures for trends)
- Report confidence intervals or variance when possible (especially with R > 1 runs)
- **NEVER cherry-pick results** — report all metrics, including where your method does NOT win
- Explicitly acknowledge when baselines outperform your method on specific metrics

**Neutral Phrasing for Results:**
```
❌ "Our method significantly outperforms all baselines."
✅ "The proposed configuration achieves the highest [metric] ([value]),
    while [baseline] retains the highest [other metric] ([value])."

❌ "The results clearly demonstrate the superiority of..."
✅ "The results indicate that [method] achieves higher scores
    on [metrics] compared to [baselines] in the evaluated setting."

❌ "This proves that our approach is optimal."
✅ "These results support the proposed approach in the evaluated setting,
    but do not establish that any individual component is universally optimal."
```

**Table Formatting (LaTeX):**
```latex
\begin{table}[t]
\caption{[Descriptive caption with dataset and metric info].}
\label{tab:name}
\centering
\begin{tabular}{l c c c}
\toprule
Configuration & Metric1 & Metric2 & Metric3 \\
\midrule
Baseline 1 & 0.xx & 0.xx & 0.xx \\
Baseline 2 & 0.xx & 0.xx & 0.xx \\
\textbf{Proposed} & \textbf{0.xx} & 0.xx & \textbf{0.xx} \\
\bottomrule
\end{tabular}
\end{table}
```

---

### 7. Discussion

**Purpose:** Interpret the results, explain their significance, and connect them back to the
research questions and broader literature.

**Structure:**
1. Recap of main findings
2. Comparison with prior work in context of literature
3. Explanation of observed patterns
4. Strengths of the approach
5. **Limitations** (MANDATORY — never skip this)
6. Implications for the field

**Rules:**
- Start with a recap of your main finding
- Put your results in perspective with other reports in the literature
- Explain significance and how findings contribute to knowledge
- **MUST outline strengths AND limitations honestly**
- Use hedging language throughout — discussion is inherently interpretive

**Limitations Checklist (must address ALL that apply):**
- [ ] Dataset size and representativeness
- [ ] Evaluation methodology limitations (automated vs. human judges)
- [ ] Generalizability beyond tested domain/institution/language
- [ ] Computational cost and scalability
- [ ] Domain-specific assumptions
- [ ] Statistical significance considerations
- [ ] Potential biases in data or evaluation

**Neutral Phrasing:**
```
❌ "Our system has no significant limitations."
✅ "The evaluation remains limited to [specific scope],
    and further work is needed to assess generalizability."

❌ "This proves our hypothesis."
✅ "These findings are consistent with the hypothesis that...,
    though alternative explanations cannot be excluded."
```

---

### 8. Conclusion

**Purpose:** The final takeaway. Explain what the findings mean, why they matter, and what
should happen next.

**Structure (5-point pattern):**
1. **Restate aim** — what the study set out to do
2. **Summarize main findings** — key quantitative results
3. **Interpret significance** — what these findings mean
4. **State practical implications or recommendations**
5. **End with future work directions**

**Rules:**
- Do NOT repeat the abstract word for word
- Do NOT introduce new data or results
- Do NOT make claims not supported by the presented results
- MUST end with a clear takeaway or future direction
- Keep it reflective and developed (not just a copy of the abstract)

**Mistakes to Avoid:**
- Repeating the abstract verbatim
- Introducing new experimental data
- Making claims not supported by results
- Ending without a clear takeaway

**Neutral Phrasing:**
```
❌ "In conclusion, we have proven that X is the best approach for Y."
✅ "Taken together, these findings suggest that [approach]
    is a promising direction for [domain], though further evaluation
    across [broader scope] is needed to assess generalizability."

❌ "Our system will revolutionize..."
✅ "The proposed architecture demonstrates potential for...,
    and future work will explore..."
```

---

### 9. References

**Rules:**
- List ALL sources used as a basis for your work
- **Check accuracy of every reference**, even if copied from other papers
- Follow the exact citation style required by the venue (IEEE, ACM, Springer)
- Ensure every citation in the text has a corresponding reference entry
- Ensure every reference entry is cited at least once in the text
- Prefer published, peer-reviewed sources over preprints when available
- Include DOIs when available

---

## Writing Style Rules

### General Academic Writing Standards

1. **Use third person or first person plural** ("we propose", "the system processes")
   — avoid "I" in multi-author papers
2. **Use active voice** when describing your contributions, passive voice for general knowledge
3. **Be precise** — avoid vague quantifiers ("a lot", "many", "very")
4. **Define all acronyms** at first use: "Retrieval-Augmented Generation (RAG)"
5. **Maintain consistent terminology** — don't alternate between synonyms for technical terms
6. **One idea per paragraph** — start each paragraph with a topic sentence
7. **Use parallel structure** in lists and enumerations
8. **Avoid colloquialisms and informal language**

### Sentence-Level Quality Checks

- [ ] Is every sentence necessary? (Remove filler)
- [ ] Is every technical term defined at first use?
- [ ] Is every claim backed by evidence or a citation?
- [ ] Are all numbers presented with consistent precision?
- [ ] Are all figure/table references correct?

### LaTeX Best Practices

- Use `\cref{}` or `\autoref{}` for cross-references
- Use `\textbf{}` for emphasis in tables, not colors
- Use `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`) for tables
- Use `\label{}` immediately after `\caption{}`
- Use non-breaking spaces before references: `Figure~\ref{fig:arch}`
- Use `\url{}` or `\href{}` for URLs
- Place floats (figures/tables) at top of page with `[t]`

---

## Pre-Submission Checklist

Run through this checklist before any submission:

### Content Quality
- [ ] Every section follows the structure outlined above
- [ ] Abstract is 150–300 words, self-contained, has quantitative results
- [ ] Introduction has clear gap → contribution → outline flow
- [ ] Related work is organized by theme, ends with synthesis
- [ ] Methodology is reproducible (parameters, configurations, tools listed)
- [ ] All claimed results have corresponding table/figure evidence
- [ ] Discussion includes honest limitations section
- [ ] Conclusion does not introduce new data

### Claim Neutrality (⚠️ MOST IMPORTANT)
- [ ] **ZERO instances** of "prove", "clearly show", "superior", "best", "novel" used as strong claims
- [ ] All comparative claims are qualified with "in the evaluated setting" or similar
- [ ] All interpretive statements use hedging verbs (suggest, indicate, appear to)
- [ ] Limitations are explicitly stated
- [ ] No absolute claims ("always", "never", "guarantees")
- [ ] Contribution statements use measured language
- [ ] Results that favor baselines over proposed method are honestly reported

### Formatting & References
- [ ] Paper follows venue template exactly
- [ ] All figures and tables are referenced in text
- [ ] All acronyms defined at first use
- [ ] Reference list is complete and formatted correctly
- [ ] All references have correct author names, year, venue
- [ ] Page limit is respected
- [ ] Supplementary material is properly linked (if applicable)

### Reproducibility
- [ ] Hyperparameters and configurations are fully specified
- [ ] Dataset description is complete (size, splits, collection method)
- [ ] Computational infrastructure is documented
- [ ] Code/data availability statement is included (if venue requires)
- [ ] Random seeds or variance measures are reported

---

## Workflow: Writing a Paper from Scratch

When asked to write a complete paper or a section, follow this sequence:

1. **Understand the research** — Ask for: research questions, methodology, results data, target venue
2. **Draft the outline** — Create a section-by-section outline with key points
3. **Write bottom-up** — Methods → Results → Discussion → Introduction → Abstract → Conclusion
   (Write Abstract and Conclusion LAST, after all content is finalized)
4. **Claim audit** — Run the Claim Strength Audit on every paragraph
5. **Style check** — Apply the Writing Style Rules and Sentence-Level Quality Checks
6. **Pre-submission checklist** — Run the full checklist above
7. **Output LaTeX** — Generate publication-ready `.tex` file

---

## Workflow: Revising an Existing Paper

When asked to review or revise an existing manuscript:

1. **Read the full paper** to understand context and flow
2. **Identify strong claims** — Search for forbidden patterns (see table above)
3. **Classify each claim** using the L1–L4 audit
4. **Propose neutral alternatives** — Show before/after for each change
5. **Check section completeness** — Verify against the section guides above
6. **Verify cross-references** — Tables, figures, equations all referenced correctly
7. **Run pre-submission checklist**
8. **Output a revision report** with diff-style changes

---

## Common Mistakes in CS/AI Papers

| Mistake | Fix |
|---|---|
| Claiming SOTA without comprehensive baselines | Compare with relevant baselines, qualify claims |
| Ignoring metrics where baselines win | Report ALL metrics honestly |
| Overfitting narrative to results | Let data speak, acknowledge unexpected patterns |
| Abstract/Conclusion overlap >70% | Write conclusion as reflection, not abstract copy |
| Missing limitations | Always include at least 3–5 honest limitations |
| Undefined notation | Define every symbol at first use |
| "As shown in Table X" without interpretation | Add a sentence interpreting what the table shows |
| Inconsistent tense | Present for general knowledge, past for your experiments |
| Name-dropping without synthesis | Group by theme, synthesize gaps at the end |
| Vague future work ("more experiments") | Be specific: what experiments, what data, what questions |

---

## Additional Rules for AI/ML Papers

1. **Report variance** — If you run R > 1 repetitions, report mean ± std or confidence intervals
2. **Ablation transparency** — When removing components, explain what the isolated effect is
   vs. what a bundled comparison shows
3. **LLM-as-judge caveat** — When using LLM-based evaluation, acknowledge potential bias
   and describe mitigation steps (reference-grounded, greedy decoding, multiple runs)
4. **Computational cost** — Report training/inference time and hardware requirements
5. **Negative results** — Briefly discuss configurations that did NOT improve performance;
   this builds credibility and helps the community
6. **Reproducibility statement** — Include code availability, data availability, or clear
   configuration specifications

---

## Abstract vs. Conclusion — Key Differences

These two sections are often confused. Here is how they differ:

| Aspect | Abstract | Conclusion |
|---|---|---|
| **Location** | Beginning of the study | End of the study |
| **Main purpose** | Quick overview of the entire study | Final answer and meaning of the study |
| **Answers** | What did you study, how, and what did you find? | What do the findings mean, and what should we take away? |
| **Content** | Problem, purpose, methodology, key findings | Key findings, interpretation, contribution, implications, limitations, recommendations |
| **Length** | Usually brief: ~150–300 words | Usually much longer |
| **Detail** | Highly condensed | More developed and reflective |
| **Literature citations** | Usually avoided | May be used where appropriate |
| **Research questions** | Briefly indicates whether/how they were answered | Explicitly demonstrates how they were answered |
| **Recommendations** | Usually not included | Often included |
| **Contribution** | Briefly stated | Explained more fully |
| **Reader's goal** | Decide whether the study is relevant | Understand what the study ultimately means |

---

## Output Format

When generating paper content, ALWAYS output in LaTeX format unless the user explicitly
requests otherwise. Use the venue-appropriate document class:

```latex
% IEEE
\documentclass[conference]{IEEEtran}

% ACM
\documentclass[sigconf]{acmart}

% Springer LNCS
\documentclass[runningheads]{llncs}
```

Include appropriate packages at the top:
```latex
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{xcolor}
```
