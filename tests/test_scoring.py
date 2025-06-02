import pytest
from dizionaut.services import scoring


def test_phrase_probability_single_word():
    assert scoring.phrase_probability("house") == 0.0


def test_phrase_probability_with_punctuation():
    assert scoring.phrase_probability("Hold it, bastard!") >= 0.9


def test_phrase_probability_long_phrase():
    assert scoring.phrase_probability("This is a long sentence.") >= 0.9


def test_score_basic_translation():
    translation = {
        "match": 0.9,
        "quality": 80,
        "created-by": "MateCat",
        "translation": "house",
        "usage-count": 10,
        "penalty": 0,
    }
    result = scoring.score(translation)
    assert 0.0 <= result <= 1.0


def test_score_with_penalty_and_low_usage():
    translation = {
        "match": 0.7,
        "quality": 40,
        "created-by": "Wikipedia",
        "translation": "something vague",
        "usage-count": 0,
        "penalty": 0.5,
    }
    result = scoring.score(translation)
    assert result < 0.5


def test_score_with_empty_translation():
    translation = {
        "match": 0.6,
        "quality": 50,
        "created-by": "Unknown",
        "translation": "And so it was written, behold! The day of judgment shall come to pass.",
        "usage-count": 0,
        "penalty": 0,
    }
    result = scoring.score(translation)
    assert result < 0.2  # should be heavily penalized due to phrase probability
