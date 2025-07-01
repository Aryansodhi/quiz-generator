from keybert import KeyBERT # type: ignore

# Initialize KeyBERT with a sentence-transformers model
kw_model = KeyBERT(model="distilbert-base-nli-stsb-mean-tokens")

def extract_topics(text: str, top_n: int = 5) -> list[str]:
    """
    Given a long string `text`, return the top_n keyphrases.
    """
    # Extract keyphrases (1–2 words each); adjust ngram range if you like longer phrases
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n
    )
    # keywords is a list of (phrase, score) tuples; we only need the phrase
    return [phrase for phrase, score in keywords]
