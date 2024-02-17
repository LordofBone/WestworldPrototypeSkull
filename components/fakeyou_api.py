import os

from dotenv import load_dotenv

load_dotenv()

username = os.getenv("FAKEYOU_USERNAME")
password = os.getenv("FAKEYOU_PASSWORD")
voice_model = os.getenv("FAKEYOU_VOICE_MODEL_ID")
