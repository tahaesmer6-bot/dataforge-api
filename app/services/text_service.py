import re
import math
from collections import Counter


def analyze_text(text: str) -> dict:
    """Comprehensive text analysis."""
    if not text or not text.strip():
        return {"error": "Empty text provided"}

    # Basic counts
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs) if paragraphs else 1
    line_count = len(text.splitlines())

    # Word frequency
    word_lower = [w.lower() for w in words]
    word_freq = Counter(word_lower)
    top_words = word_freq.most_common(10)

    # Average lengths
    avg_word_length = round(sum(len(w) for w in words) / max(word_count, 1), 2)
    avg_sentence_length = round(word_count / max(sentence_count, 1), 2)

    # Reading time (avg 200 words/min for reading, 130 for speaking)
    reading_time_minutes = round(word_count / 200, 2)
    speaking_time_minutes = round(word_count / 130, 2)

    # Readability metrics
    syllable_count = _count_syllables_text(text)
    avg_syllables_per_word = round(syllable_count / max(word_count, 1), 2)

    # Flesch Reading Ease
    flesch_score = _flesch_reading_ease(word_count, sentence_count, syllable_count)
    flesch_grade = _flesch_grade(flesch_score)

    # Flesch-Kincaid Grade Level
    fk_grade = _flesch_kincaid_grade(word_count, sentence_count, syllable_count)

    # Unique words ratio
    unique_words = len(set(word_lower))
    vocabulary_richness = round(unique_words / max(word_count, 1), 4)

    # Sentiment (basic)
    sentiment = _basic_sentiment(text)

    # Character breakdown
    uppercase_count = sum(1 for c in text if c.isupper())
    lowercase_count = sum(1 for c in text if c.islower())
    digit_count = sum(1 for c in text if c.isdigit())
    special_count = sum(1 for c in text if not c.isalnum() and not c.isspace())

    return {
        "counts": {
            "characters": char_count,
            "characters_no_spaces": char_no_spaces,
            "words": word_count,
            "unique_words": unique_words,
            "sentences": sentence_count,
            "paragraphs": paragraph_count,
            "lines": line_count,
            "syllables": syllable_count,
        },
        "averages": {
            "word_length": avg_word_length,
            "sentence_length": avg_sentence_length,
            "syllables_per_word": avg_syllables_per_word,
        },
        "reading_time": {
            "minutes": reading_time_minutes,
            "seconds": round(reading_time_minutes * 60),
            "display": _format_time(reading_time_minutes),
        },
        "speaking_time": {
            "minutes": speaking_time_minutes,
            "seconds": round(speaking_time_minutes * 60),
            "display": _format_time(speaking_time_minutes),
        },
        "readability": {
            "flesch_reading_ease": flesch_score,
            "flesch_grade": flesch_grade,
            "flesch_kincaid_grade_level": fk_grade,
        },
        "vocabulary": {
            "richness": vocabulary_richness,
            "top_words": [{"word": w, "count": c} for w, c in top_words],
        },
        "character_breakdown": {
            "uppercase": uppercase_count,
            "lowercase": lowercase_count,
            "digits": digit_count,
            "special": special_count,
            "spaces": char_count - char_no_spaces,
        },
        "sentiment": sentiment,
    }


def _count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip()
    if len(word) <= 2:
        return 1

    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Adjust for silent e
    if word.endswith("e") and count > 1:
        count -= 1

    # Adjust for -le ending
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1

    return max(1, count)


def _count_syllables_text(text: str) -> int:
    """Count total syllables in text."""
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return sum(_count_syllables(w) for w in words)


def _flesch_reading_ease(words: int, sentences: int, syllables: int) -> float:
    """Calculate Flesch Reading Ease score."""
    if words == 0 or sentences == 0:
        return 0.0
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return round(max(0, min(100, score)), 2)


def _flesch_grade(score: float) -> str:
    """Convert Flesch score to grade description."""
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (College)"
    else:
        return "Very Difficult (Graduate)"


def _flesch_kincaid_grade(words: int, sentences: int, syllables: int) -> float:
    """Calculate Flesch-Kincaid Grade Level."""
    if words == 0 or sentences == 0:
        return 0.0
    grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    return round(max(0, grade), 2)


def _format_time(minutes: float) -> str:
    """Format minutes to human readable."""
    if minutes < 1:
        return f"{round(minutes * 60)} sec"
    elif minutes < 60:
        m = int(minutes)
        s = int((minutes - m) * 60)
        return f"{m} min {s} sec" if s > 0 else f"{m} min"
    else:
        h = int(minutes // 60)
        m = int(minutes % 60)
        return f"{h} hr {m} min"


def _basic_sentiment(text: str) -> dict:
    """Basic rule-based sentiment analysis."""
    positive_words = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "awesome", "love", "like", "happy", "joy", "beautiful", "best",
        "perfect", "brilliant", "superb", "outstanding", "positive",
        "remarkable", "impressive", "delightful", "pleasant", "magnificent",
        "successful", "favorable", "helpful", "exciting", "incredible",
    }
    negative_words = {
        "bad", "terrible", "awful", "horrible", "hate", "dislike", "worst",
        "ugly", "sad", "angry", "poor", "disappointing", "negative",
        "disgusting", "dreadful", "pathetic", "useless", "boring",
        "annoying", "frustrating", "miserable", "painful", "hopeless",
        "inferior", "unpleasant", "offensive", "mediocre", "lousy",
    }

    words = re.findall(r'\b\w+\b', text.lower())
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    total = pos_count + neg_count

    if total == 0:
        polarity = "neutral"
        score = 0.0
    elif pos_count > neg_count:
        polarity = "positive"
        score = round(pos_count / total, 4)
    elif neg_count > pos_count:
        polarity = "negative"
        score = round(-neg_count / total, 4)
    else:
        polarity = "neutral"
        score = 0.0

    return {
        "polarity": polarity,
        "score": score,
        "positive_words_found": pos_count,
        "negative_words_found": neg_count,
    }
