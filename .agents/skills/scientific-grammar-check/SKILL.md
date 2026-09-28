---
name: scientific-grammar-check
description: Comprehensive grammar and style checker for scientific papers to eliminate common AI writing flaws, dense sentences, and misused terminology.
---

# Scientific Paper Grammar and Style Checker

This skill provides guidelines for reviewing and correcting scientific writing (specifically for Computer Science / AI papers). AI models often produce text that sounds professional but suffers from logic, phrasing, and stylistic flaws. Use these rules when proofreading, reviewing, or writing scientific papers.

## 1. Core Rules: Common AI Writing Flaws

When reviewing paper content, aggressively scan for and fix the following 3 major AI flaws:

### 1.1. Illogical Verb/Collocation Pairings
AI often pairs words that sound impressive but lack formal logic.
- **Rule**: Do NOT use verbs that don't logically apply to the noun.
- **Examples to fix**:
  - ❌ "motivate a gap" (Challenges highlight gaps, they don't motivate them). -> ✅ "highlight a gap" / "reveal a gap".
  - ❌ "repair a conflict" (Repair is for physical objects/hardware). -> ✅ "resolve a conflict" / "address a conflict".
  - ❌ "support reliability" -> ✅ "enhance reliability".

### 1.2. Dense Sentences (Câu quá đặc)
AI frequently crams too many clauses, nouns, and verbs into a single sentence, making it suffocating to read.
- **Rule**: Break down sentences longer than 35-40 words or those containing nested independent clauses. Humans rarely write ultra-dense sentences.
- **Example to fix**:
  - ❌ "Collectively, the ablations distinguish two functional roles: specialist policies, heterogeneous evidence, and deterministic calculation drive accuracy at the current 11-tool scale, while tool isolation (S2-A2) functions as an efficiency mechanism whose accuracy contribution is examined under larger registry scales."
  - ✅ "Collectively, the ablations distinguish two functional roles. First, specialist policies, heterogeneous evidence, and deterministic calculators drive accuracy at the 11-tool scale. Second, tool isolation (S2-A2) acts primarily as an efficiency mechanism; its contribution to accuracy is further examined at larger registry scales."

### 1.3. Out-of-Context Cliché Vocabulary
AI often borrows terminology from other fields (medicine, law) and incorrectly forces them into Computer Science papers.
- **Rule**: Avoid overly grandiose or domain-incorrect words.
- **Examples to fix**:
  - ❌ "Primary Endpoint" (Clinical trial terminology) -> ✅ "Primary Evaluation Metrics".
  - ❌ "Fairness principle and execution contract" (Ethics/distributed systems terms used out of context) -> ✅ "Baseline equivalence and execution bounds".
  - ❌ "Latency Decomposition" or "Considerations" (Unnecessarily grand) -> ✅ "Operational Trade-offs" or "Usage".
  - ❌ "Degradation interaction" (Made-up AI phrase) -> ✅ "Relative difference in performance degradation".
  - ❌ "Token footprint" -> ✅ "Token consumption".

## 2. Stylistic Guidelines

- **No Standalone Noun Phrases**: Do not write a noun phrase as an isolated sentence unless it is a formatted heading.
  - ❌ "Central hypothesis." -> ✅ "**Central Hypothesis:** When a system..."
- **No Rhetorical Questions**: Avoid posing a question and immediately answering it. It is convoluted.
  - ❌ "A bounded architecture raises the question of how queries are handled. The system adopts..." -> ✅ "To handle queries spanning multiple domains, the system adopts..."
- **Grammar & Prepositions**: Ensure proper grammatical logic and prepositions.
  - ❌ "Agent changes from 86% to 83%" (An agent doesn't change, its success rate does) -> ✅ "The agent's success rate drops from 86% to 83%".
  - ❌ "suffer prompt expansion" (Missing preposition) -> ✅ "suffer from prompt expansion".
- **Avoid "-ing" Rhyming**: Avoid consecutive words ending in "-ing" which sounds probabilistically generated.
  - ❌ "...motivating coupling dense embeddings..." -> ✅ "...which necessitates the coupling of dense embeddings..."
- **Subject-Verb Agreement for Gerunds**: Avoid using a gerund (V-ing) awkwardly as a subject for an active verb.
  - ❌ "Synthesizing the reviewed approaches identifies three gaps..." -> ✅ "An analysis of the reviewed literature reveals three primary gaps..."
- **Avoid cliché phrases**:
  - ❌ "The contribution lies in composing..." -> ✅ "The primary contribution is the integration of..."

## 3. Workflow

When requested to check grammar using this skill:
1. Read the provided text or LaTeX file.
2. Scan specifically for the errors listed above.
3. Rewrite dense sentences into shorter, digestible parts.
4. Replace forced collocations and out-of-context terms with direct, natural Computer Science terminology.
5. Provide a diff or table summarizing the changes made, explaining why the original text exhibited AI-like flaws.
