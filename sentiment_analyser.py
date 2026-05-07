from transformers import pipeline


classifier = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)


def analyze_sentiment(headline):
    if not headline or not headline.strip():
        raise ValueError("Headline cannot be empty.")

    result = classifier(headline, truncation=True)[0]

    return {
        "label": result["label"],
        "score": result["score"]
    }


if __name__ == "__main__":
    sample_headlines = [
        "Microsoft beats earnings expectations and raises its outlook.",
        "Tesla shares fall after weaker-than-expected vehicle deliveries.",
        "Apple reports quarterly results in line with analyst estimates."
    ]

    for headline in sample_headlines:
        sentiment = analyze_sentiment(headline)

        print("Headline:", headline)
        print("Label:", sentiment["label"])
        print("Score:", round(sentiment["score"], 4))
        print("-" * 80)
