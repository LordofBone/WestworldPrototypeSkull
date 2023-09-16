import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

import openai
import unittest
from unittest.mock import patch, MagicMock
from ChattingGPT.integrate_chatgpt import IntegrateChatGPT

# Mocked API response for ChatCompletion without history
mock_response_without_history = {
    'choices': [{
        'message': {
            'content': 'Hello! How can I help you today?'
        }
    }]
}

# Mocked API response for ChatCompletion with history
mock_response_with_history = {
    'choices': [{
        'message': {
            'content': 'I am just a model, but I am functioning well. Thanks for asking!'
        }
    }]
}


class TestIntegrateChatGPT(unittest.TestCase):

    @patch("openai.ChatCompletion.create", return_value=mock_response_without_history)
    def test_response_without_history(self, mock_create):
        chat_gpt = IntegrateChatGPT(role="you are a helpful assistant", use_history=False)
        response = chat_gpt.get_response("hello there")
        self.assertEqual(response, 'Hello! How can I help you today?')

    @patch("openai.ChatCompletion.create", side_effect=[mock_response_without_history, mock_response_with_history])
    def test_response_with_history(self, mock_create):
        chat_gpt = IntegrateChatGPT(role="you are a helpful assistant", use_history=True)
        response_1 = chat_gpt.get_response("hello there")
        self.assertEqual(response_1, 'Hello! How can I help you today?')

        response_2 = chat_gpt.get_response("how are you today?")
        self.assertEqual(response_2, 'I am just a model, but I am functioning well. Thanks for asking!')

    def test_initialization(self):
        chat_gpt = IntegrateChatGPT(role="you are a helpful assistant", use_history=True)
        self.assertEqual(chat_gpt.context, "you are a helpful assistant")
        self.assertTrue(chat_gpt.use_history)
        self.assertEqual(chat_gpt.conversation_history[0]['role'], 'system')
        self.assertEqual(chat_gpt.conversation_history[0]['content'], "you are a helpful assistant")

    def test_api_connection(self):
        chat_gpt = IntegrateChatGPT(role="you are a helpful assistant", use_history=False)
        try:
            response = chat_gpt.get_response("hello")
            self.assertIsInstance(response, str)  # Ensure the response is a string
        except openai.error.AuthenticationError:
            self.fail("API authentication failed!")  # This makes the test fail if this specific error is caught


if __name__ == "__main__":
    unittest.main()
