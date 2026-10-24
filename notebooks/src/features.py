import re
import textstat
from textblob import TextBlob

# Words that often appear in suspenseful endings
SUSPENSE = {"suddenly", "scream", "dead", "blood", "gun", "run", "gone",
            "secret", "dark", "never", "help", "betray", "unknown", "who", "why"}

# The exact list of features the model will use (order matters!)
FEATURES = [
    "word_count", "avg_sentence_len", "dialogue_ratio", "readability",
    "sentiment", "end_questions", "end_exclaims", "end_ellipsis",
    "end_suspense_words", "sentiment_shift", "ends_in_dialogue",
    "cliffhanger_score",
]


def extract_features(text):
    """Takes ONE chapter (a string) and returns a dictionary of numbers."""
    words = text.split()
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]

    ending = " ".join(words[-150:])      # the last 150 words
    beginning = " ".join(words[:150])    # the first 150 words

    end_questions = ending.count("?")
    end_exclaims = ending.count("!")
    end_ellipsis = ending.count("...") + ending.count("…")
    end_suspense = sum(
        w.lower().strip(".,!?\"'…") in SUSPENSE for w in ending.split()
    )
    sentiment_shift = (TextBlob(ending).sentiment.polarity
                       - TextBlob(beginning).sentiment.polarity)
    ends_in_dialogue = int(text.strip()[-1] in "\"”")

    # My own invention: combine the clues into ONE "Cliffhanger Score"
    cliffhanger_score = (end_questions * 2 + end_exclaims + end_ellipsis
                         + end_suspense * 1.5 + ends_in_dialogue * 2
                         + abs(sentiment_shift) * 5)

    return {
        "word_count": len(words),
        "avg_sentence_len": len(words) / max(len(sentences), 1),
        "dialogue_ratio": sum(text.count(q) for q in ['"', "“", "”"]) / max(len(words), 1),
        "readability": textstat.flesch_reading_ease(text),
        "sentiment": TextBlob(text).sentiment.polarity,
        "end_questions": end_questions,
        "end_exclaims": end_exclaims,
        "end_ellipsis": end_ellipsis,
        "end_suspense_words": end_suspense,
        "sentiment_shift": sentiment_shift,
        "ends_in_dialogue": ends_in_dialogue,
        "cliffhanger_score": cliffhanger_score,
    }