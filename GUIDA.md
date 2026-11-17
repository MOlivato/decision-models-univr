# Guida

Guida per lo studente. Versione inglese: [GUIDELINE.md](GUIDELINE.md).
Panoramica: [README.md](README.md). Risorse: [docs/README.md](docs/README.md).

## Da dove iniziare

Questo repository accompagna la tesi e lo stage sui **decision models**. Un decision
model non genera testo: legge uno *stato* e domande con risposte dichiarate, e
restituisce una probabilità per ciascuna risposta. Le tre domande sono **Noul** (è
vero?), **Choice** (scegli tra N opzioni) e **Score** (livello di una scala ordinata).

Tutto il materiale è **gratuito o open**: dataset pubblici, modelli open, librerie
open-source e articoli open access. Non serve una chiave a pagamento.

## Setup

```bash
uv python install 3.12          # una volta, se Python 3.12 non è disponibile
uv sync                         # crea .venv con le dipendenze base
uv sync --extra train           # solo per il notebook 04
cp .env.example .env            # backend locale predefinito
uv run jupyter lab
```

Se non vuoi scaricare modelli, i notebook usano `MockClient`: funzionano offline e
senza chiavi. Quando hai un endpoint locale gratuito (Ollama o llama.cpp), sostituisci
il client con `SystemOneClient`: l'interfaccia è identica.

## Percorso consigliato

| Notebook | Cosa impari | Risultato |
|---|---|---|
| `00` | Configurazione e prima decisione | Una distribuzione di probabilità |
| `01` | I tre paradigmi, confidenza, astensione | Domande validate |
| `02` | Modello locale, route gratuita, lettura dei logit | Scelta del backend |
| `03` | Conversione di PubMedQA e Banking77 | `data/*_decisions.jsonl` |
| `04` | Fine-tuning LoRA di un piccolo modello open | `checkpoints/dm-lora` |
| `05` | Valutazione: accuratezza, Brier, ECE, soglie | Metriche e soglia |
| `06` | Ponte verso agente e Reinforcement Learning | Traccia delle ricompense |

Ogni notebook esiste in due versioni (`notebooks/it/` e `notebooks/en/`) con le stesse
celle di codice: modifica sempre entrambe.

## Flusso dei dati

1. `load_examples` legge un dataset pubblico gratuito, oppure il campione incluso se
   non c'è rete.
2. `convert_pubmedqa` e `convert_banking77` creano domande Noul, Choice e Score.
3. `build_dataset` scrive il JSONL secondo lo schema in `data/SCHEMA.md`.
4. Il notebook `04` addestra sui dati e il notebook `05` valuta le probabilità.

## Regole pratiche

- Non committare mai `.env`, chiavi, dataset scaricati o checkpoint.
- Il codice riutilizzabile va in `src/decision_qa/`, non nelle celle dei notebook.
- Una cella di codice deve mostrare una sola idea e terminare con un controllo.
- Prima di ogni commit esegui i tre comandi della sezione successiva.
- `AGENTS.md` è locale e gitignorato: non aggiungerlo forzatamente al repository.

## Controlli prima del commit

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
uv run python scripts/make_figures.py   # solo se modifichi un diagramma
```

Tutti e tre devono passare. Inoltre ogni cella di codice modificata deve essere
eseguita senza errori in entrambe le versioni linguistiche.

## Problemi comuni

- **Nessun modello locale attivo**: i notebook usano `MockClient`, deterministico e offline.
- **Hugging Face non raggiungibile**: il loader usa i campioni in `data/samples/`.
- **Endpoint sbagliato**: controlla `base_url` in `configs/` e stampa `cfg.endpoint`.
- **Extra di training mancante**: esegui `uv sync --extra train` e imposta
  `RUN_TRAINING = True` nel notebook `04`.

## Riferimenti utili

- Libreria locale: [docs/README.md](docs/README.md) con paper arXiv e articoli salvati.
- [awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models)
- [awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts)
- [JevBench](https://github.com/fstandhartinger/jevbench) (MIT)
- [Early Evidence Audit](https://arxiv.org/abs/2609.32160)
- [Beyond Calibration](https://arxiv.org/abs/2609.33209)
