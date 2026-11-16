from decision_qa import ConversionConfig, MockClient, build_dataset, read_jsonl
from decision_qa.evaluate import brier, ece
from decision_qa.questions import ChoiceQuestion, NoulQuestion


def test_conversion_schema():
    path = build_dataset(
        "banking77",
        "data/_test_decisions.jsonl",
        limits={"train": 4, "val": 2, "test": 2},
        cfg=ConversionConfig(seed=1),
    )
    records = read_jsonl(path)
    assert len(records) == 8
    for record in records:
        for question in record.questions:
            if isinstance(question, ChoiceQuestion):
                assert 0 <= question.gold_index < len(question.options)
            if isinstance(question, NoulQuestion):
                assert question.statement.strip()


def test_mock_and_metrics():
    records = read_jsonl("data/_test_decisions.jsonl")
    client = MockClient(seed=3)
    probs = []
    for record in records:
        result = client.decision(record.state, record.questions)[0]
        probs.append(max(result.probabilities.values()))
    assert 0.0 <= brier(probs) <= 1.0
    assert 0.0 <= ece(probs, [int(p >= 0.5) for p in probs]) <= 1.0
