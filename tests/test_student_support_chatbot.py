import unittest

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


if __name__ == "__main__":
    unittest.main()
