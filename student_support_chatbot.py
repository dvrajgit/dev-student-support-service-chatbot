import os
import re
from typing import List, Tuple

import requests
import joblib
from pathlib import Path


class StudentSupportChatbot:
    def __init__(self):
        self.patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(r"\bhello\b|\bhi\b|\bhey\b", re.IGNORECASE), "Hello! I can help with student services, registration, and general support."),
            (re.compile(r"hours|open|closing|time", re.IGNORECASE), "Our support desk is open Monday to Friday from 8:00 AM to 6:00 PM."),
            (re.compile(r"register|registration|class", re.IGNORECASE), "You can register for classes through the student registration portal on the college website."),
        ]

        # Try to load an ML pipeline if available
        model_dir = Path("model")
        self.pipeline = None
        self.responses = None
        pipeline_path = model_dir / "pipeline.joblib"
        responses_path = model_dir / "responses.joblib"
        if pipeline_path.exists() and responses_path.exists():
            try:
                self.pipeline = joblib.load(pipeline_path)
                self.responses = joblib.load(responses_path)
            except Exception:
                self.pipeline = None
                self.responses = None

    def respond(self, message: str) -> str:
        if not message or not message.strip():
            return "Please provide a question or request so I can help."

        # If we have a trained ML pipeline, use it first.
        if self.pipeline and self.responses:
            try:
                label = self.pipeline.predict([message])[0]
                if label in self.responses:
                    return self.responses[label]
            except Exception:
                # if ML fails, fall back to pattern matching
                pass

        for pattern, response in self.patterns:
            if pattern.search(message):
                return response

        # If a Gemini API key is available, try generating a response from Gemini.
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                return self._call_gemini(message)
            except Exception:
                # Fall back to the default message if Gemini fails
                return "I can help with student support questions. Please contact the support team for further assistance."

        return "I can help with student support questions. Please contact the support team for further assistance."

    def _call_gemini(self, prompt: str) -> str:
        """Call Google Generative Language (Gemini) REST API using the API key in
        the `GEMINI_API_KEY` environment variable. The model can be set via
        `GEMINI_MODEL` (defaults to 'models/gemini-2.0').
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        model = os.getenv("GEMINI_MODEL", "models/gemini-2.0")
        url = f"https://generativelanguage.googleapis.com/v1beta2/{model}:generateText?key={api_key}"

        payload = {"prompt": {"text": prompt}, "maxOutputTokens": 256}

        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Try common response shapes.
        if isinstance(data, dict):
            # v1beta2 generateText: candidates -> output
            candidates = data.get("candidates")
            if candidates and isinstance(candidates, list):
                first = candidates[0]
                if isinstance(first, dict):
                    if "output" in first:
                        return first.get("output")
                    # fallback to nested content/parts
                    content = first.get("content") or {}
                    parts = content.get("parts") if isinstance(content, dict) else None
                    if parts and isinstance(parts, list) and parts[0].get("text"):
                        return parts[0].get("text")

            # Some endpoints return a top-level "output" key
            if "output" in data:
                return data.get("output")

        # If we couldn't parse a reply, return a generic fallback.
        return "I can help with student support questions. Please contact the support team for further assistance."


def main() -> None:
    chatbot = StudentSupportChatbot()
    print("Student Support Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(f"Bot: {chatbot.respond(user_input)}\n")


if __name__ == "__main__":
    main()
