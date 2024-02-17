import logging
from time import sleep

from ChattingGPT.integrate_chatgpt import IntegrateChatGPT, IntegrateOllama
from EventHive.event_hive_runner import EventActor
from config.chattinggpt_config import role, chat_backend, use_history, ollama_model
from config.custom_events import BotEvent, BotDoneEvent, ConversationDoneEvent

logger = logging.getLogger(__name__)
logger.debug("Initialized")


# Define a generic chat handler interface
class ChatHandler:
    def get_response(self, event_data):
        raise NotImplementedError


# Implement the real chat handler
class RealChatHandler(ChatHandler):
    def __init__(self):
        if chat_backend == "gpt":
            self.handler = IntegrateChatGPT(openai_api_key=open_ai_api_key, role=role, use_history=use_history)
            logger.debug("ChatGPT handler initialized")
        elif chat_backend == "ollama":
            self.handler = IntegrateOllama(model=ollama_model, role=role, use_history=use_history)
            logger.debug("Ollama handler initialized")
        else:
            raise ValueError("Unsupported chat backend")

    def get_response(self, event_data):
        return self.handler.get_response(event_data)


# Implement the test chat handler
class TestChatHandler(ChatHandler):
    def get_response(self, event_data):
        return "chatbot test response"


# ChatbotOperations modified to use the Strategy Pattern
class ChatbotOperations(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        self.chat_handler = TestChatHandler() if test_mode else RealChatHandler()

    def process_chatbot_response(self, event_type=None, event_data=None):
        bot_response = self.chat_handler.get_response(event_data)
        logger.debug(f"Bot response: {bot_response}")

        self.produce_event(BotDoneEvent(["BOT_FINISHED", bot_response], 1))
        sleep(1)
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))

        return True

    def get_event_handlers(self):
        return {
            "GET_BOT_RESPONSE": self.process_chatbot_response
        }

    def get_consumable_events(self):
        return [BotEvent]
