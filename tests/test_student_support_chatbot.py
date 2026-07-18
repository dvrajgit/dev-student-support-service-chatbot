import unittest
from unittest.mock import Mock, patch

import requests

from app import app
from student_support_chatbot import StudentSupportChatbot


class StudentSupportChatbotTests(unittest.TestCase):
    def setUp(self):
        self.chatbot = StudentSupportChatbot()

    def test_greeting_response(self):
        response = self.chatbot.respond("hello")
        self.assertIn("Hello!", response)

    def test_hours_response(self):
        response = self.chatbot.respond("What are your hours?")
        self.assertIn("Monday to Friday", response)

    def test_registration_response(self):
        response = self.chatbot.respond("How do I register for classes?")
        self.assertIn("registration portal", response)

    def test_unknown_question_response(self):
        response = self.chatbot.respond("How do I reset my password?")
        self.assertIn("support team", response)

    def test_groq_rate_limit_response_does_not_leak_api_key(self):
        api_key = "secret-test-key"
        response = Mock()
        response.status_code = 429
        response.raise_for_status.side_effect = requests.HTTPError(response=response)

        with patch("student_support_chatbot.requests.post", return_value=response) as post:
            reply = self.chatbot.respond("iit delhi admissions", api_key=api_key, mode="academic")

        self.assertIn("rate-limited", reply)
        self.assertNotIn(api_key, reply)
        self.assertNotIn("api.groq.com", reply)
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], f"Bearer {api_key}")
        self.assertEqual(post.call_args.args[0], "https://api.groq.com/openai/v1/chat/completions")


class AppLoginTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def test_chat_requires_login(self):
        response = self.client.post("/api/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 401)

    def test_login_allows_chat(self):
        login_response = self.client.post(
            "/api/login",
            json={"username": "student", "password": "student123"},
        )
        self.assertEqual(login_response.status_code, 200)

        chat_response = self.client.post("/api/chat", json={"message": "hello"})
        self.assertEqual(chat_response.status_code, 200)
        self.assertIn("Hello!", chat_response.get_json()["reply"])


if __name__ == "__main__":
    unittest.main()
