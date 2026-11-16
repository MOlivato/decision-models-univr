# Learning resources

A local library of free, English learning material for the decision models project.
Papers are open access from arXiv. Blog posts and documentation pages were saved as
PDF from their public web pages. No paid account is needed to read any of them.

Start with the two audit papers (2609.32160 and 2609.37647), then the evaluation and
calibration papers, then the security papers before starting the agent phase.

## Papers

| File | Title | Why read it |
|---|---|---|
| [2609.32160.pdf](papers/2609.32160.pdf) | Typed Decision Models: An Early Evidence Audit and Evaluation Checklist | Reviews 28 early papers and gives a 14 item evaluation checklist |
| [2609.37647.pdf](papers/2609.37647.pdf) | Evaluating and Benchmarking the System One Model Jev | Zero shot results on 37 datasets, with calibration findings |
| [2609.33209.pdf](papers/2609.33209.pdf) | Beyond Calibration: Do a Typed Decision Model's Probabilities Obey the Probability Axioms? | Label free coherence checks on the probabilities |
| [2610.17016.pdf](papers/2610.17016.pdf) | ProbabilityBench | Measures probability quality using KL divergence |
| [2609.31142.pdf](papers/2609.31142.pdf) | JevAdvBench | Adversarial benchmark, shows the state is untrusted input |
| [2609.33401.pdf](papers/2609.33401.pdf) | Evaluating System One Models for Agent Security Decisions | Calibration can hide failures on specific attack groups |
| [2609.30216.pdf](papers/2609.30216.pdf) | Jev in the Wild | Survey of 2170 public GitHub projects using decision models |
| [2609.28940.pdf](papers/2609.28940.pdf) | Calibrated Decision Models for Autonomous Penetration Testing Harnesses | Decision models inside LLM agents |
| [2609.29283.pdf](papers/2609.29283.pdf) | From Text Decisions to Pixels | Native image decision interface on small open models |
| [2610.18272.pdf](papers/2610.18272.pdf) | JevGPT: Thinking Fast and Slow in Autonomous Research | Decision model used for question answering over documents |
| [2609.23986.pdf](papers/2609.23986.pdf) | Jev-Mem | Decision model controlling agent memory and retrieval |

Each file is named with its arXiv identifier. The source is `https://arxiv.org/abs/<id>`.

## Blog posts and documentation pages

| File | Source | Topic |
|---|---|---|
| [tev1-train-your-own-decision-model.pdf](blogs/tev1-train-your-own-decision-model.pdf) | Together AI | Train a decision model cheaply |
| [clef-decision-models.pdf](blogs/clef-decision-models.pdf) | Cloudflare | Open weights decision model from Qwen |
| [d1-decision-model.pdf](blogs/d1-decision-model.pdf) | Liquid AI | Multimodal decision model |
| [strands-decider.pdf](blogs/strands-decider.pdf) | AWS Strands Labs | Small decision model with a pointer head |
| [jev-vs-claude-classification.pdf](blogs/jev-vs-claude-classification.pdf) | OpenRouter | Accuracy, latency, and cost comparison |
| [llm-judge-vs-feature-extraction.pdf](blogs/llm-judge-vs-feature-extraction.pdf) | Agent Journal | One judgment call versus many scored dimensions |
| [jev-measured.pdf](blogs/jev-measured.pdf) | Aman Kumar | Classifier or filter, with a threshold procedure |
| [jev-does-not-play-dice.pdf](blogs/jev-does-not-play-dice.pdf) | Kanta Hayashi AI | Calibration failure on known probabilities |
| [jev-search-deep-evaluation.pdf](blogs/jev-search-deep-evaluation.pdf) | Independent author | Search stopping, memory reranking, multi hop selection |
| [typesafe-introduction.pdf](blogs/typesafe-introduction.pdf) | TypeSafe docs | Introduction to the three question types |
| [typesafe-patterns.pdf](blogs/typesafe-patterns.pdf) | TypeSafe docs | Patterns for building with decision models |
| [awesome-decision-models.pdf](blogs/awesome-decision-models.pdf) | Anotia Wang | Curated index of the whole ecosystem |

## How these were saved

Papers were downloaded directly from `https://arxiv.org/pdf/<id>`.
Web pages were printed to PDF with headless Chromium from their public URLs.
If a page changes, repeat the download to refresh the local copy.

All files are for study. Please respect the licenses of the original sources when
reusing any material.
