import sys
import unittest
from pathlib import Path
from unittest.mock import patch

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from components.chatbot_system import IntegrateChatGPT, IntegrateOllama


class TestChatGPTIntegration(unittest.TestCase):
    # todo: figure out why these tests can cause chatgpt api to still be activated, even though it's being mocked
    @patch('ChattingGPT.components.chatgpt_functions.ChatGPTSystem._get_chatgpt_response')
    def test_chatgpt_without_history(self, mock_get_response):
        # Mock the response from ChatGPT when not using history
        mock_get_response.return_value = "Mocked ChatGPT Response Without History"

        chat_system = IntegrateChatGPT(use_history=False)
        response = chat_system.get_response("Test Input")

        self.assertEqual(response, "Mocked ChatGPT Response Without History")
        mock_get_response.assert_called_once()

    @patch('ChattingGPT.components.chatgpt_functions.ChatGPTSystem._get_chatgpt_response_with_history')
    def test_chatgpt_with_history(self, mock_get_response):
        # Mock the response from ChatGPT when using history
        mock_get_response.return_value = "Mocked ChatGPT Response With History"

        chat_system = IntegrateChatGPT(use_history=True)
        response = chat_system.get_response("Test Input")

        self.assertEqual(response, "Mocked ChatGPT Response With History")
        mock_get_response.assert_called_once()


class TestOllamaIntegration(unittest.TestCase):
    @patch('ChattingGPT.components.ollama_functions.OllamaSystem._get_llm_response')
    def test_ollama_without_history(self, mock_get_response):
        # Mock the response from Ollama when not using history
        mock_get_response.return_value = "Mocked Ollama Response Without History"

        ollama_system = IntegrateOllama(use_history=False)
        response = ollama_system.get_response("Test Input")

        self.assertEqual(response, "Mocked Ollama Response Without History")
        mock_get_response.assert_called_once()

    @patch('ChattingGPT.components.ollama_functions.OllamaSystem._get_llm_response_with_history')
    def test_ollama_with_history(self, mock_get_response):
        # Mock the response from Ollama when using history
        mock_get_response.return_value = "Mocked Ollama Response With History"

        ollama_system = IntegrateOllama(use_history=True)
        response = ollama_system.get_response("Test Input")

        self.assertEqual(response, "Mocked Ollama Response With History")
        mock_get_response.assert_called_once()


if __name__ == '__main__':
    unittest.main()
