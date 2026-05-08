from transformers import pipeline
import streamlit as st



# @st.cache_resource :  Streamlit loads FinBERT ONCE when the app starts
@st.cache_resource
def load_classifier():
    return pipeline(
        "text-classification",
        model="ProsusAI/finbert"
    )



def analyse_sentiment(headline):
    if not headline or not headline.strip():
        raise ValueError("Headline cannot be empty.")

    classifier = load_classifier()
    result = classifier(headline, truncation=True)[0]

    return {
        "label": result["label"],  # "positive", "negative", or "neutral"
        "score": result["score"]     # confidence from 0.0 to 1.0
    }
    


if __name__ == "__main__":
    samples = [
        "Microsoft beats earnings expectations and raises its outlook.",
        "Tesla shares fall after weaker-than-expected vehicle deliveries.",
        "Apple reports quarterly results in line with analyst estimates."
    ]

    for headline in samples:
        sentiment = analyse_sentiment(headline)

        print("Headline:", headline)
        print("Label:", sentiment["label"])
        print("Score:", round(sentiment["score"], 4))
        print("-" * 80)
