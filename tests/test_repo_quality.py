import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED = {"\u2014", "\u2192", "\u00d7", "\u00b7"}


def test_notebook_code_parity():
    english = sorted((ROOT / "notebooks" / "en").glob("*.ipynb"))
    assert len(english) == 7
    for path in english:
        italian = ROOT / "notebooks" / "it" / path.name
        assert italian.exists()
        en_cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
        it_cells = json.loads(italian.read_text(encoding="utf-8"))["cells"]
        en_code = [cell["source"] for cell in en_cells if cell["cell_type"] == "code"]
        it_code = [cell["source"] for cell in it_cells if cell["cell_type"] == "code"]
        assert en_code == it_code


def test_notebook_images_exist():
    images = ROOT / "notebooks" / "images"
    expected = {
        "decision_model_flow.png",
        "question_types.png",
        "backend_choices.png",
        "qa_to_decision_dataset.png",
        "training_pipeline.png",
        "agent_loop.png",
    }
    assert expected <= {path.name for path in images.glob("*.png")}
    for folder in ("en", "it"):
        for path in (ROOT / "notebooks" / folder).glob("*.ipynb"):
            text = path.read_text(encoding="utf-8")
            for name in re.findall(r"\.\./images/([A-Za-z0-9_.-]+)", text):
                assert (images / name).exists(), f"missing image {name} in {path}"


def test_no_uncommon_characters():
    allowed_suffixes = {
        ".md",
        ".py",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".ipynb",
        ".example",
        ".gitignore",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", ".cache", "__pycache__"} for part in path.parts):
            continue
        if path.suffix not in allowed_suffixes and path.name not in {".gitignore", ".env.example"}:
            continue
        text = path.read_text(encoding="utf-8")
        found = BANNED & set(text)
        assert not found, f"uncommon characters {found} in {path}"
