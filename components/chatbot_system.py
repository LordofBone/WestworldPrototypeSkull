import logging

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT, IntegrateOllama
from EventHive.event_hive_runner import EventActor
from config.chattinggpt_config import openai_api_key, role, chat_backend, use_history, ollama_model
from config.custom_events import BotEvent, BotDoneEvent, ConversationDoneEvent

logger = logging.getLogger(__name__)

logger.debug("Initialized")


class ChatbotOperations(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        if chat_backend == "gpt":
            self.ChatGPT_handler = IntegrateChatGPT(openai_api_key=openai_api_key, role=role, use_history=use_history)
        elif chat_backend == "ollama":
            self.ChatGPT_handler = IntegrateOllama(model=ollama_model, role=role, use_history=use_history)

    def process_chatbot_response(self, event_type=None, event_data=None):
        """
        Process the chatbot response.
        :return:
        """
        bot_response = self.ChatGPT_handler.get_response(event_data)

        logger.debug(f"Bot response: {bot_response}")

        self.produce_event(BotDoneEvent(["BOT_FINISHED", bot_response], 1))

        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "GET_BOT_RESPONSE": self.process_chatbot_response,
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [BotEvent]
