import os
import re
import json
import copy
import random
from datetime import datetime, timedelta
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

        # Load the university data JSON file for Academic mode grounding
        self.univ_data_str = ""
        univ_data_path = Path("university_data.json")
        if univ_data_path.exists():
            try:
                with open(univ_data_path, "r", encoding="utf-8") as f:
                    self.univ_data_str = json.dumps(json.load(f), indent=2)
            except Exception:
                self.univ_data_str = ""

        # Load internship template database for dynamic Internship mode
        self.internship_template = None
        internship_path = Path("internship_template.json")
        if internship_path.exists():
            try:
                with open(internship_path, "r", encoding="utf-8") as f:
                    self.internship_template = json.load(f)
            except Exception:
                self.internship_template = None


    def respond(self, message: str, api_key: str = None, mode: str = None) -> str:
        if not message or not message.strip():
            return "Please provide a question or request so I can help."

        # If a specialized mode is selected, bypass pattern/ML and route to Gemini.
        if mode in ("academic", "internship"):
            effective_key = api_key or os.getenv("GEMINI_API_KEY")
            if not effective_key:
                return "To use Academic or Internship modes, please set the GEMINI_API_KEY environment variable or save it in your browser's localStorage."
            try:
                if mode == "academic":
                    prompt_text = (
                        "System: You are an expert Academic Advisor at Apex Global University. "
                        "You must answer the student's question accurately using ONLY the official university data provided below. "
                        "Keep your response structured, concise, and professional. If the answer cannot be found in the provided data, "
                        "politely inform the student of the relevant department/advising email address found in the contact emails, "
                        "or say you do not have that specific detail but they can check with advising.\n\n"
                        f"Official University Data:\n{self.univ_data_str}\n\n"
                        f"Student Question: {message}\nAdvisor Answer:"
                    )
                else:  # internship
                    fresh_data = self._get_fresh_internships()
                    today_str = datetime.now().strftime("%d %B %Y")
                    prompt_text = (
                        f"System: You are an expert Career & Internship Advisor. Today's date is {today_str}. "
                        "Below is a LIVE feed of current internship openings across Government, PSU, Startup, and MNC/Private sectors. "
                        "Each listing shows the organization, role, stipend, duration, location, eligibility, required skills, apply URL, and application deadline. "
                        "Use ONLY the data below to answer the student's question accurately. "
                        "Format your response in a clean, structured way with key details. "
                        "If the student asks for a specific sector, filter and show only those listings. "
                        "Always mention deadlines clearly so students can act in time.\n\n"
                        f"LIVE Internship Listings (as of {today_str}):\n{fresh_data}\n\n"
                        f"Student Question: {message}\nAdvisor Answer:"
                    )
                return self._call_gemini(prompt_text, api_key=effective_key)
            except Exception as e:
                return f"Error contacting Gemini API: {str(e)}"

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
        effective_key = api_key or os.getenv("GEMINI_API_KEY")
        if effective_key:
            try:
                return self._call_gemini(message, api_key=effective_key)
            except Exception:
                # Fall back to the default message if Gemini fails
                return "I can help with student support questions. Please contact the support team for further assistance."

        return "I can help with student support questions. Please contact the support team for further assistance."

    def _get_fresh_internships(self) -> str:
        """Generate a fresh snapshot of internship opportunities with
        dynamically computed deadlines relative to today's date."""
        if not self.internship_template:
            return "No internship data available at this time."

        today = datetime.now()
        sectors = self.internship_template.get("sectors", {})
        output_sections = []

        sector_labels = {
            "government":  "🏛️  GOVERNMENT INTERNSHIPS",
            "psu":         "⚙️  PSU (PUBLIC SECTOR UNDERTAKINGS)",
            "startup":     "🚀  STARTUP INTERNSHIPS",
            "mnc_private": "🌐  MNC & PRIVATE COMPANIES",
        }

        for sector_key, label in sector_labels.items():
            listings = sectors.get(sector_key, [])
            if not listings:
                continue
            # Randomly select most listings to simulate a refreshed live feed
            count = random.randint(max(3, len(listings) - 1), len(listings))
            selected = random.sample(listings, min(count, len(listings)))

            section_lines = [f"\n{label}"]
            section_lines.append("-" * 50)

            for item in selected:
                days = item.get("deadline_days_from_today", random.randint(7, 30))
                # Add a small random jitter of ±2 days so deadlines feel fresh
                jitter = random.randint(-2, 2)
                deadline_date = today + timedelta(days=max(1, days + jitter))
                deadline_str = deadline_date.strftime("%d %B %Y")

                section_lines.append(
                    f"  Organization : {item['organization']}\n"
                    f"  Role         : {item['role']}\n"
                    f"  Stipend      : {item['stipend']}\n"
                    f"  Duration     : {item['duration']}\n"
                    f"  Location     : {item['location']}\n"
                    f"  Eligibility  : {item['eligibility']}\n"
                    f"  Skills Needed: {', '.join(item.get('skills', []))}\n"
                    f"  Apply URL    : {item['apply_url']}\n"
                    f"  Deadline     : {deadline_str}\n"
                )

            output_sections.append("\n".join(section_lines))

        return "\n".join(output_sections)



    def _call_gemini(self, prompt: str, api_key: str = None) -> str:
        """Call the Gemini REST API (v1beta generateContent) using the provided
        API key or the GEMINI_API_KEY environment variable.
        The model can be overridden via the GEMINI_MODEL env var.
        Defaults to gemini-2.0-flash.
        """
        effective_key = api_key or os.getenv("GEMINI_API_KEY")
        if not effective_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        # Use the correct v1beta generateContent endpoint (not the deprecated v1beta2 generateText)
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        # Strip leading "models/" prefix if user set it in the env var
        model = model.replace("models/", "")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={effective_key}"

        # Gemini generateContent payload format
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 1024,
                "temperature": 0.7,
            }
        }

        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Parse: candidates[0].content.parts[0].text
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            pass

        # Fallback: try promptFeedback blockReason
        block = data.get("promptFeedback", {}).get("blockReason")
        if block:
            return f"Response blocked by safety filter: {block}"

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
