# Guida

Guida per lo studente (inglese: [GUIDELINE.md](GUIDELINE.md); panoramica: [README.md](README.md)).

## Da dove iniziare

Questo repository accompagna la tesi e lo stage sui **decision models**. Un decision
model non genera testo: legge uno *stato* e domande con risposte dichiarate, e restituisce
una probabilità per ciascuna risposta. Le tre domande sono **Noul** (è vero?), **Choice**
(scegli tra N opzioni) e **Score** (livello di una scala).

Tutto il materiale è **gratuito o open**: dataset pubblici, modelli open, librerie
open-source e articoli open access. Non serve una chiave a pagamento.

## Setup

```bash
uv sync                    # crea .venv con Python 3.12
uv sync --extra train      # solo per il notebook 04
cp .env.example .env       # backend locale predefinito
uv run jupyter lab
```

Se non vuoi scaricare modelli, i notebook usano `MockClient`: funzionano offline e
senza chiavi. Quando hai un endpoint locale gratuito (Ollama / llama.cpp), sostituiscilo
con `SystemOneClient`: l'interfaccia è identica.

## Percorso consigliato

| Notebook | Cosa impari |
|---|---|
| `00` | Configurazione e prima decisione |
| `01` | I tre paradigmi di domanda, confidenza, astensione |
| `02` | Modello locale, route gratuita, lettura dei logit |
| `03` | conversione di PubMedQA e Banking77 nel formato `data/SCHEMA.md` |
| `04` | Fine-tuning LoRA di un piccolo modello open |
| `05` | Valutazione: accuratezza, Brier, ECE, soglie |
| `06` | Ponte verso agente e Reinforcement Learning |

Ogni notebook esiste in due versioni (`notebooks/it/` e `notebooks/en/`) con le
stesse celle di codice: modifica sempre entrambe.

## Regole pratiche

- Non committare mai `.env`, chiavi, dataset scaricati o checkpoint.
- Il codice riutilizzabile va in `src/decision_qa/`, non nelle celle.
- Prima di ogni commit: `uv run ruff format src tests`, `uv run ruff check src tests`
  e `uv run pytest -q`.
- `AGENTS.md` è locale e gitignorato: non aggiungerlo forzatamente al repository.

## Riferimenti utili

[awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models),
[awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts),
[JevBench](https://github.com/fstandhartinger/jevbench) (MIT),
[Early Evidence Audit](https://arxiv.org/abs/2609.32160),
[Beyond Calibration](https://arxiv.org/abs/2609.33209).
