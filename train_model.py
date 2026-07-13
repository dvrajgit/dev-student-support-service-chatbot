from pathlib import Path
from typing import Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


MODEL_DIR = Path("model")
MODEL_DIR.mkdir(exist_ok=True)


def get_training_data():
    # Simple training examples that mirror the rule-based patterns
    texts = [
        "hello",
        "hi there",
        "hey",
        "what time do you open",
        "when are you open",
        "closing hours",
        "how do I register",
        "registration portal",
        "how to sign up for classes",
        "I want to register for a class",
        "how do I reset my password",
        "I need help with my account",
    ]

    labels = [
        "greeting",
        "greeting",
        "greeting",
        "hours",
        "hours",
        "hours",
        "registration",
        "registration",
        "registration",
        "registration",
        "unknown",
        "unknown",
    ]

    return texts, labels


def get_label_responses() -> Dict[str, str]:
    return {
        "greeting": "Hello! I can help with student services, registration, and general support.",
        "hours": "Our support desk is open Monday to Friday from 8:00 AM to 6:00 PM.",
        "registration": "You can register for classes through the student registration portal on the college website.",
        "unknown": "I can help with student support questions. Please contact the support team for further assistance.",
    }


def train_and_save():
    texts, labels = get_training_data()
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    pipeline.fit(texts, labels)

    # Save pipeline and metadata
    joblib.dump(pipeline, MODEL_DIR / "pipeline.joblib")
    joblib.dump(get_label_responses(), MODEL_DIR / "responses.joblib")
    print("Model trained and saved to model/")


if __name__ == "__main__":
    train_and_save()
