import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from utils import logging_system
from ChattingGPT.integrate_chatgpt import IntegrateChatGPT

integrate_chatgpt_test_1 = IntegrateChatGPT(role="you are a helpful assistant")

print(integrate_chatgpt_test_1.get_response("hello there"))


integrate_chatgpt_test_2 = IntegrateChatGPT(role="you are a helpful assistant", use_history=True)

print(integrate_chatgpt_test_2.get_response("hello there"))

print(integrate_chatgpt_test_2.get_response("how are you today?"))

print(integrate_chatgpt_test_2.get_response("do you know python"))
