import re
from typing import List, Tuple


class StudentSupportChatbot:
    def __init__(self):
        self.patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(r"\bhello\b|\bhi\b|\bhey\b", re.IGNORECASE), "Hello! I can help with student services, registration, and general support."),
            (re.compile(r"hours|open|closing|time", re.IGNORECASE), "Our support desk is open Monday to Friday from 8:00 AM to 6:00 PM."),
            (re.compile(r"register|registration|class", re.IGNORECASE), "You can register for classes through the student registration portal on the college website."),
        ]

    def respond(self, message: str) -> str:
        if not message or not message.strip():
            return "Please provide a question or request so I can help."

        for pattern, response in self.patterns:
            if pattern.search(message):
                return response

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
