from utils import logging_system
from Lakul.integrate_stt import SpeechtoTextHandler

# Microphone / USB PnP Sound Device

SpeechtoText = SpeechtoTextHandler("Microphone")
SpeechtoText.model_size = "tiny"
SpeechtoText.offline_mode = True
SpeechtoText.initiate_recording()
print(SpeechtoText.run_inference())
