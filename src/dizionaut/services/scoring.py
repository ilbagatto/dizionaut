import re


SOURCE_WEIGHTS = {
    "MateCat": 0.8,
    "Wikipedia": 0.5,
    "MT!": 0.3,
}
DEFAULT_SOURCE_WEIGHT = 0.2


def phrase_probability(text: str) -> float:
    """Estimate how likely the text is a full phrase rather than a single word."""
    words = len(text.split())
    has_punctuation = bool(re.search(r"[!?.,\"“”«»]", text))

    score = 0.0
    if words >= 3:
        score += 0.5
    if words >= 5:
        score += 0.2
    if has_punctuation:
        score += 0.4

    return min(score, 1.0)


def score(translation: dict) -> float:
    """
    Compute a heuristic score for a translation entry from MyMemory.

    The score is based on:
    - match value (0.0–1.0)
    - quality value (0–100, normalized to 0.0–1.0)
    - source weight (based on known reliability)
    - usage frequency (normalized up to 1.0)
    - penalty (provided by the API)
    - length penalty for long results
    - phrase penalty for multi-word and/or punctuated expressions

    Args:
        translation (dict): A dictionary representing a single translation item.

    Returns:
        float: A score between 0.0 and 1.0, higher is better.
    """    
    match = translation.get("match", 0) or 0  # from 0.0 to 1.0
    quality = float(translation.get("quality", 0) or 0) / 100.0  # from 0.0 to 1.0
    source = translation.get("created-by", "") or ""
    source_weight = (
        SOURCE_WEIGHTS.get(source, DEFAULT_SOURCE_WEIGHT) or DEFAULT_SOURCE_WEIGHT
    )

    text = translation.get("translation", "")
    words = len(text.split())

    # Exponential penalty for long phrases
    length_penalty = 1.0 / (words**0.7) if words > 0 else 0.1

    usage_count = int(translation.get("usage-count", 0) or 0)
    usage_weight = min(usage_count / 5.0, 1.0)

    penalty = float(translation.get("penalty", 0) or 0)
    penalty_factor = 1.0 - min(penalty, 1.0)

    # Phrase penalty
    phrase_prob = phrase_probability(text)
    phrase_penalty = 1.0 - 0.6 * phrase_prob  # up to 60% penalty

    # Final score
    score = (
        (
            0.35 * match
            + 0.2 * quality
            + 0.2 * source_weight
            + 0.15 * usage_weight
            + 0.05 * length_penalty
        )
        * penalty_factor
        * phrase_penalty
    )

    return score


def quality_marker(score: float) -> str:
    if score >= 0.9:
        return "🟢"
    elif score >= 0.7:
        return "🟡"
    elif score >= 0.5:
        return "🟠"
    else:
        return "🔴"
