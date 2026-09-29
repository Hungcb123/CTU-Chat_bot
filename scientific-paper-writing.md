---
name: scientific-paper-writing
description: >
  Guides the writing and revision of scientific research papers for Computer Science / AI venues
  (IEEE, ACM, Springer LNCS). Covers every section from Title through References with strict rules
  on neutral tone, hedging language, evidence-grounded claims, structural frameworks (IMRaD, 6-part
  Introduction, 5-step Abstract & Conclusion), and publication-ready LaTeX output.
  Use when the user asks to write, revise, review, or improve any part of a research paper,
  conference submission, or journal manuscript. Also use when the user mentions "paper", "manuscript",
  "submission", "abstract", "introduction", "related work", "methodology", "experiments", "conclusion",
  or "claim" in an academic context.
---

# Scientific Paper Writing Skill

## Overview

This skill provides comprehensive, section-by-section guidance for writing and revising scientific
research papers targeting Computer Science and AI venues (IEEE, ACM, Springer LNCS). It synthesizes
rigorous peer-reviewed publishing standards (including Elsevier's IMRaD framework, Peter Munene's
comparative architecture, and Muhammad Muneeb's structural introduction model), enforces **neutral
academic tone**, forbids unsupported strong claims, and outputs publication-ready LaTeX.

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

**Core Rules:**
- **Cite Core Intervention, Context/Domain, Design & Main Finding** (Elsevier guideline): Clearly indicate what was investigated, the technical mechanism, and the application setting.
- **Use subtitles sparingly** for study group names, system variants, or specific benchmark scopes.
- Keep concise but informative (typically 10–15 words).
- Do NOT use marketing or hyperbolic language ("revolutionary", "groundbreaking", "novel", "game-changing").

**Standard Patterns:**
```
[System Name]: [Design Keyword/Intervention] [Core Architecture] for [Application Domain]
```
*or*
```
[Core Technique] with [Key Mechanism] for [Domain/Problem]: An Empirical Investigation
```

**Examples:**
- *Good (Descriptive & Grounded):*
  ```
  CTU-Chat: Supervisor-Routed Multi-Agent RAG with Heterogeneous
  Knowledge Allocation for University Counseling
  ```
- *Bad (Vague & Promotional):*
  ```
  A Novel and Revolutionary AI Chatbot that Solves University Counseling
  ```

---

### 2. Abstract

**Purpose:** A brief, self-contained summary of the entire paper. It must be **comprehensible by itself** without requiring the reader to consult the main text. It tells the reader *what was studied, how it was studied, the key findings, and why it matters*.

#### The 5-Step Writing Process
1. **Start with the topic or problem:** Establish the specific domain challenge.
2. **State the objective or research question:** Explicitly state what the study set out to do.
3. **Mention the method briefly:** Specify the proposed framework, datasets, or experimental approach.
4. **Present the key result:** Provide concrete, quantitative metrics (numbers, confidence intervals, effect sizes).
5. **End with the main implication:** Conclude with a hedged statement on what these findings mean for the field.

#### Annotated Example Abstract
```
[Topic / Problem]
Rock slope instability remains a major challenge in mountainous road projects.

[Objective + Method]
This study investigated the effect of discontinuity orientation on slope stability
using field mapping and numerical modelling.

[Key Result]
The results showed that adverse joint orientation reduced the factor of safety
significantly by 24.6% under saturated conditions.

[Implication]
The findings highlight the need for orientation-based support design in rock slopes,
suggesting that structural geological mapping should precede stabilization planning.
```

#### Rules & Best Practices:
- **Length:** Strictly 150–250 words (Springer LNCS) or 150–300 words (general).
- **Self-contained (IMRaD in miniature):** Introduction $\rightarrow$ Methods $\rightarrow$ Results $\rightarrow$ Conclusion.
- **NO citations:** Avoid literature citations entirely in the abstract.
- **NO detailed discussion:** Keep interpretation concise; save extended analysis for the Discussion section.
- **NO vague placeholders:** Never write "results are discussed", "promising results were obtained", or "various aspects are analyzed". State the actual key numbers.
- **Hedged implication:** The final sentence must use tentative language (`suggests that`, `can support`, `is consistent with`).

#### Mistakes to Avoid:
- ❌ Too much background (>2 sentences of generic context).
- ❌ Omitting concrete quantitative results.
- ❌ Copying sentences verbatim from the Introduction or Conclusion.
- ❌ Defining obscure acronyms without context.

#### LaTeX Template:
```latex
\begin{abstract}
[Problem statement and domain challenge --- 1--2 sentences].
We present [System/Method Name], a [brief description of core approach and architecture].
[Core mechanism and method --- 1--2 sentences describing how it operates and data used].
Evaluation on [benchmark/dataset] shows that [System] achieves
[metric1] of [value1] and [metric2] of [value2] ([confidence interval or baseline comparison]).
These findings suggest that [hedged implication statement under the evaluated conditions].

\keywords{First Keyword \and Second Keyword \and Third Keyword.}
\end{abstract}
```

---

### 3. Introduction

**Purpose:** Lead the reader from a broad general context to the specific research gap, state the precise objectives, summarize the proposed methodology, and outline the structure of the paper.

#### The 6-Part Structural Framework

| Part | Component | Description & Role |
|:---|:---|:---|
| **1** | **Topic Introduction** | Broad context, societal/practical relevance, and domain importance (supported by authoritative citations/statistics). |
| **2** | **Topic Background** | Technical landscape, evolution of current solutions, and what has been achieved so far in the literature. |
| **3** | **Research Problem / Gap** | Precise limitations of existing approaches: what remains unsolved, brittle, or unexplored (the "knowledge gap"). |
| **4** | **Research Objective** | Formal, explicit statement of study aims, broken down into primary and secondary targets: (i) ..., (ii) ... (or formal Research Questions RQ1, RQ2...). |
| **5** | **Research Methodology** | Concrete overview of the proposed framework, datasets/benchmarks, preprocessing, and target evaluation metrics. |
| **6** | **Paper Outline** | Section-by-section roadmap for the remainder of the manuscript. |

> 💡 **Golden Rule:** *"A strong introduction clearly presents the background, identifies the gap, defines the objective, and outlines how your study addresses the problem."*

#### Annotated Example Introduction
```text
[1. Topic Introduction]
Air pollution has become a major environmental and public health concern globally.
According to the World Health Organization, exposure to polluted air contributes to
millions of premature deaths each year and increases the risk of cardiovascular
diseases (WHO, 2023). Accurate prediction of air quality levels is essential for
effective decision-making and for minimizing adverse impacts on human health.

[2. Topic Background]
Traditional air quality forecasting methods rely on statistical models and machine
learning techniques that require manual feature engineering. With the advancement of
deep learning, data-driven models have shown superior ability to learn intricate patterns
automatically. For example, Li et al. (2021) applied Long Short-Term Memory (LSTM)
networks for PM2.5 prediction and achieved promising results compared to conventional models.

[3. Research Problem / Gap]
Despite these advances, several challenges remain in existing studies. Many models are
trained and evaluated on data from a single city, limiting their generalizability to
different regions with varying climatic conditions (Gupta et al., 2019). Moreover,
most studies focus on short-term prediction and do not consider the impact of
meteorological factors comprehensively. These limitations highlight the need for a
more robust, accurate, and generalizable framework that can operate across diverse urban environments.

[4. Research Objective]
The main objective of this study is to develop and evaluate a deep learning-based hybrid
model for accurate and generalizable air quality prediction. Specifically, the study aims to:
(i) integrate meteorological and pollutant variables to improve prediction accuracy, and
(ii) assess the transferability of the proposed model across multiple cities with diverse conditions.

[5. Research Methodology]
To achieve the above objectives, this study proposes a hybrid deep learning framework
that combines Convolutional Neural Networks (CNN) and Long Short-Term Memory (LSTM) networks.
The model is trained on multi-city air quality datasets collected from publicly available monitoring
stations. Data preprocessing, normalization, and feature selection are performed to ensure
data quality. The model's performance is evaluated using standard metrics such as RMSE,
MAE, R², and MAPE, and compared with established baseline models.

[6. Paper Outline]
The rest of this paper is organized as follows. Section 2 reviews related work on air quality
prediction and identifies open challenges. Section 3 describes the dataset, preprocessing steps,
and the proposed hybrid architecture. Section 4 presents the experimental results and comparative
evaluations. Section 5 discusses the findings and practical implications. Finally, Section 6 concludes
the study and outlines directions for future research.
```

#### Rules for Contributions & Objectives:
- Present contributions as verifiable engineering/scientific achievements, NOT marketing claims.
- **Never claim uniqueness or absolute primacy:**
  - ❌ *"We propose the first ever system that completely solves..."*
  - ✅ *"To the best of our knowledge, this work is among the first to examine bounded multi-agent tool routing under..."*
  - ✅ *"Specifically, this work provides three primary contributions: (1) an implemented supervisor architecture...; (2) an empirical evaluation across 51 tools...; and (3) an ablation study assessing component-level contributions."*

---

### 4. Related Work / Literature Review

**Purpose:** Establish the current state of knowledge, position your work relative to existing approaches, and demonstrate why the identified research gap justifies a new solution.

**Structure:**
- **Organize by theme/topic**, NOT chronologically or paper-by-paper.
- Group related studies into logical streams (e.g., Sparse vs. Dense Retrieval, Graph Reasoning, Multi-Agent Orchestration).
- End each subsection with a brief transition showing how it motivates your approach.
- Final subsection: **Comparative Synthesis and Research Gaps** (summarizes how your work bridges the gaps).

**Rules:**
- Present prior work **fairly and objectively** — never misrepresent baselines to make your approach look better.
- Use present tense for established facts/theories, past tense for specific experimental findings of past papers.
- Identify genuine structural or empirical limitations, not artificial strawmen.

---

### 5. Proposed Model / Methodology

**Purpose:** Describe **in detail what you did and how**, with sufficient precision to enable an independent researcher to replicate the entire study.

#### Comprehensive Methodology Checklist (Elsevier / IMRaD Standard):
- [ ] **System Architecture / Formulation:** Formal definition of inputs, outputs, state representations, and mathematical notation.
- [ ] **Selection Criteria for Datasets / Benchmarks:** Detail data sources, inclusion/exclusion criteria, cohort splits, and preprocessing pipelines.
- [ ] **Detailed Description of Interventions & Tools:** Explain every component, module, query template, or prompt contract.
- [ ] **Target Endpoints / Evaluation Criteria:** Define primary endpoints (e.g., end-to-end task success) and secondary endpoints (e.g., latency, token consumption, parameter exact match).
- [ ] **Statistical Methods (Dedicated Paragraph):** Explicitly document statistical protocols: number of repeated trials ($R$), random seed control, confidence interval calculation (e.g., bootstrap percentiles), significance testing (e.g., Wilcoxon, McNemar), and variance reporting.
- [ ] **Ethical & Governance Considerations:** Document data privacy, license compliance, institutional oversight, and human-evaluation ethics where applicable.

---

### 6. Experimental Results

**Purpose:** Present empirical evidence and quantitative measurements that address the research questions.

#### Two Paramount Rules for Results:
1. **Rule 1: Avoid Commentary and Interpretation:**
   Present the data objectively. State what the numbers are. Save speculative explanations, causal reasoning, and broader field implications for the **Discussion** section.
2. **Rule 2: The 1-to-1 Correspondence Rule (Methods $\leftrightarrow$ Results):**
   *Give a result for EVERY method, baseline, metric, or ablation presented in the Methodology section.* If a baseline or configuration was introduced in §3/§4, its performance must appear in the results tables. Conversely, never introduce a surprise method in the results that was not described in the experimental setup.

#### Rules for Tables & Figures:
- Use **Tables** for exact numerical comparisons, confidence intervals, and multi-metric evaluations.
- Use **Figures** for trends, scaling behavior, distributions, and ablation curves.
- **Report ALL metrics honestly:** Never omit a metric just because a baseline performed better. Transparently highlight where baselines match or exceed the proposed approach.

**Neutral Phrasing for Results:**
```
❌ "Our method decisively crushes all competing baselines across the board."
✅ "The proposed configuration achieves higher scores on Context Recall (0.6534 vs. 0.5349)
    and Faithfulness (0.8636 vs. 0.8042) compared to the lexical baseline,
    while requiring higher mean latency (21.86 s vs. 7.08 ms)."
```

---

### 7. Discussion

**Purpose:** Put your results in perspective with the broader scientific literature, interpret the findings, explain underlying mechanisms, and explicitly analyze limitations.

#### 4-Part Discussion Structure (Elsevier Model):
1. **Recap of Main Findings:** Concisely restate the central empirical answers to the research questions without repeating raw tables.
2. **Perspective with Literature:** Compare observed results with prior studies (e.g., *"This finding aligns with reports by Zhang et al. (2022) regarding dense retrieval drift on rare entities, but differs in..."*).
3. **Significance & Contribution to Knowledge:** Explain *how* and *why* these results advance the state of the art or institutional practice.
4. **Strengths and Limitations (MANDATORY):** A comprehensive, honest appraisal of study constraints:
   - Data scope (e.g., single-institution vs. multi-institution).
   - Evaluation methodology (automated LLM judges vs. blind human trials).
   - Computational overhead and operational trade-offs.
   - Failure modes observed in edge cases.

---

### 8. Conclusion

**Purpose:** Provide the final takeaway of the paper. It explains *what the findings mean, why they matter, and what should happen next*.

#### The 5-Step Writing Process
1. **Restate the aim of the study:** What problem was tackled and what was built/evaluated.
2. **Summarize the main findings:** Concrete summary of how the research questions were answered.
3. **Interpret their significance:** What this implies for researchers and practitioners.
4. **State practical implications or recommendations:** Actionable guidance for real-world adoption.
5. **End with strong closing insights or future directions:** Specific, high-impact avenues for subsequent research.

#### Annotated Example Conclusion
```text
[1. Restate Aim]
This study developed and evaluated a supervisor-routed multi-agent RAG framework
with heterogeneous knowledge allocation for university counseling.

[2. Main Findings]
The experimental evaluation confirmed that domain specialization improves decision-level
pass rate by 9.3 percentage points over a global Top-10 baseline under tool ambiguity,
while requiring 52.4% fewer input tokens than monolithic full-registry execution.

[3. Meaning / Significance]
These findings demonstrate that representation-specific evidence paths---graph traversal
for curricula, deterministic calculation for statutory fees, and hybrid retrieval for
regulations---can effectively accommodate heterogeneous institutional knowledge.

[4. Practical Implications / Recommendations]
In practical deployments, specialist routing is recommended when tool ambiguity and
bounded evidence access are primary concerns, whereas single-agent gates remain
preferable when operational latency and token budgets are constrained.

[5. Future Work]
Future work should focus on reducing dispatch latency through speculative tool routing,
validating cross-institutional transfer across bilingual curricula, and conducting
longitudinal user studies in live student advisory centers.
```

---

### 9. References

**Core Rules:**
- List all sources cited in the text; ensure strict 1-to-1 correspondence between in-text citations and reference list.
- **Verify accuracy of every reference, even when copied from other papers:** Double-check author names, titles, publication years, venue/journal names, and volume/page numbers.
- Ensure DOIs are provided wherever available in standard format (`https://doi.org/...`).
- Adhere strictly to the venue's bibliographic format (`splncs04` for Springer LNCS, IEEEtran for IEEE, ACM-Reference-Format for ACM).

---

## Abstract vs. Conclusion — Complete Structural Comparison

The Abstract and Conclusion serve fundamentally different purposes and cater to different reader objectives.

| Aspect | Abstract | Conclusion |
|:---|:---|:---|
| **Location** | Beginning of the manuscript | End of the manuscript |
| **Main Purpose** | Gives a quick, self-contained overview of the entire study | Provides the final takeaway, meaning, and broader implications |
| **Key Question Answered** | *What did you study, how did you study it, and what did you find?* | *What do the findings mean, why do they matter, and what should we take away?* |
| **Content Elements** | Problem statement, objective, core methodology, key quantitative results, brief implication | Restated aim, summary of findings addressing RQs, interpretation of significance, practical implications, limitations, recommendations, future work |
| **Length** | Strictly condensed: typically 150–250 words (LNCS) or 150–300 words | Substantially longer, developed across multiple paragraphs |
| **Level of Detail** | Highly condensed, concise summary | Developed, reflective, contextualized, and analytical |
| **Literature Citations** | Strictly avoided (no citations) | May be cited where appropriate to contextualize findings against prior literature |
| **Research Questions** | Briefly mentions what was evaluated or hypothesized | Explicitly demonstrates **how each Research Question (RQ1, RQ2...) was answered** |
| **Recommendations** | Usually omitted | Frequently included as actionable guidance for practitioners |
| **Contributions** | Stated in 1 brief sentence | Explained fully in relation to operational trade-offs and theoretical impact |
| **Reader's Goal** | Deciding whether the paper is relevant to read | Understanding the ultimate meaning, reliability, and future impact of the work |

---

## Pre-Submission Quality Audit Checklist

Run through this master checklist before finalizing any scientific manuscript:

### 1. Structural Completeness
- [ ] **Title:** Reflects core intervention, context, and methodology without marketing buzzwords.
- [ ] **Abstract:** Follows the 5-step process (Problem $\rightarrow$ Objective $\rightarrow$ Method $\rightarrow$ Results $\rightarrow$ Implication), between 150–250 words, zero citations.
- [ ] **Introduction:** Follows the 6-part framework (Topic Intro $\rightarrow$ Background $\rightarrow$ Gap $\rightarrow$ Objectives (i)/(ii) $\rightarrow$ Methodology & Metrics $\rightarrow$ Outline).
- [ ] **Related Work:** Organized by theme, ends with a comparative gap synthesis.
- [ ] **Methodology:** Includes selection criteria, tool mechanics, dedicated statistical methods paragraph, and ethical considerations.
- [ ] **Results:** Follows the 1-to-1 correspondence rule with Methods; free of speculative commentary.
- [ ] **Discussion:** Evaluates results against prior literature and includes an honest limitations section.
- [ ] **Conclusion:** Follows the 5-step process; explicitly addresses each Research Question; does not copy the abstract verbatim.
- [ ] **References:** 100% verified for metadata accuracy; DOIs included.

### 2. Tone & Academic Rigor (⚠️ CRITICAL)
- [ ] Zero instances of forbidden strong claims ("proves", "clearly shows", "superior", "guarantees", "novel").
- [ ] All comparative claims bounded by "under the evaluated conditions" or "on the tested benchmarks".
- [ ] Hedging language applied to all interpretive assertions (`suggests`, `indicates`, `is consistent with`).
- [ ] Baseline advantages transparently acknowledged.
