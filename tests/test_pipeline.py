from decision_qa import (
    ChoiceQuestion,
    ConversionConfig,
    DecisionResult,
    MockClient,
    SystemOneClient,
    accuracy,
    brier,
    brier_multiclass,
    build_dataset,
    convert_banking77,
    ece,
    fit_threshold,
    read_jsonl,
)
from decision_qa.qa_to_dm import QaExample
from decision_qa.questions import NoulQuestion, ScoreQuestion


def test_conversion_schema(tmp_path):
    path = build_dataset(
        "banking77",
        tmp_path / "banking.jsonl",
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


def test_score_questions_vary():
    rows = [
        QaExample(
            id=f"row-{index}",
            source="banking77",
            context="I lost my card",
            question="What is the user's intent?",
            answer="lost_or_stolen_card",
            label="lost_or_stolen_card",
            alternatives=["lost_or_stolen_card", "card_arrival", "exchange_rate"],
        )
        for index in range(4)
    ]
    records = convert_banking77(rows, ConversionConfig(seed=2))
    golds = {
        next(q for q in record.questions if isinstance(q, ScoreQuestion)).gold_index
        for record in records
    }
    assert golds == {0, 2}


def test_banking_uses_alternative_label_pool():
    names = [f"intent_{index}" for index in range(20)]
    rows = [
        QaExample(
            id="one",
            source="banking77",
            context="message",
            question="intent?",
            answer="intent_0",
            label="intent_0",
            alternatives=names,
        )
    ]
    record = convert_banking77(rows, ConversionConfig(n_distractors=3, seed=3))[0]
    choice = next(q for q in record.questions if isinstance(q, ChoiceQuestion))
    assert len(choice.options) == 4
    assert set(choice.options) <= set(names)
    assert choice.options[choice.gold_index] == "intent_0"


def test_accuracy_does_not_count_ties():
    question = ChoiceQuestion(label="q", options=["a", "b"], gold_index=1)
    result = DecisionResult(question_label="q", probabilities={"a": 0.5, "b": 0.5})
    assert accuracy([result], [question]) == 0.0


def test_brier_multiclass():
    question = ChoiceQuestion(label="q", options=["a", "b"], gold_index=0)
    result = DecisionResult(question_label="q", probabilities={"a": 0.8, "b": 0.2})
    assert abs(brier_multiclass([result], [question]) - 0.08) < 1e-9


def test_fit_threshold_returns_lowest_cutoff():
    threshold = fit_threshold([0.9, 0.9, 0.4], [1, 1, 0], target_precision=0.9)
    assert 0.4 < threshold <= 0.9
    assert fit_threshold([0.9, 0.8], [1, 1], target_precision=0.9) == 0.0


def test_parser_keeps_missing_label_at_zero():
    questions = [ChoiceQuestion(label="q", options=["a", "b", "c"])]
    data = {"answers": [{"label": "q", "probabilities": {"a": 0.7, "b": 0.3}}]}
    result = SystemOneClient._parse(data, questions)[0]
    assert result.probabilities["c"] == 0.0
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-9


def test_mock_and_metrics():
    records = [
        QaExample(
            id="one",
            source="banking77",
            context="I lost my card",
            question="intent?",
            answer="lost_or_stolen_card",
            label="lost_or_stolen_card",
            alternatives=["lost_or_stolen_card", "card_arrival"],
        )
    ]
    record = convert_banking77(records, ConversionConfig(seed=4))[0]
    client = MockClient(seed=3)
    results = client.decision(record.state, record.questions)
    probs = [max(result.probabilities.values()) for result in results]
    correct = [int(value >= 0.5) for value in probs]
    assert 0.0 <= brier(probs) <= 1.0
    assert 0.0 <= ece(probs, correct) <= 1.0
