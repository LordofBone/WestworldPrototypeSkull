import logging
from time import sleep

from better_profanity import profanity

from EventHive.event_hive_runner import EventActor
from Lakul.integrate_stt import SpeechtoTextHandler
from config.audio_config import microphone_name
from config.custom_events import STTEvent, STTDoneEvent, ConversationDoneEvent
from config.stt_config import profanity_censor_enabled, offline_mode, model_size, stt_audio_path

logger = logging.getLogger(__name__)
logger.debug("Initialized")


# Define a generic interface for STT operations
class STTHandlerInterface:
    def initiate_recording(self, max_seconds, silence_threshold, silence_duration):
        pass

    def run_inference(self):
        pass


# Implement the real STT operation handling
class RealSTTHandler(STTHandlerInterface):
    def __init__(self):
        self.STT_handler = SpeechtoTextHandler(stt_microphone_name=microphone_name, stt_audio_file=stt_audio_path,
                                               stt_offline_mode=offline_mode, stt_model_size=model_size,
                                               init_on_launch=False)
        self.STT_handler.init_models()

    def initiate_recording(self, max_seconds=60, silence_threshold=1000, silence_duration=2000):
        self.STT_handler.initiate_recording(max_seconds, silence_threshold, silence_duration)

    def run_inference(self):
        return self.STT_handler.run_inference()


# Implement the test STT operation handling
class TestSTTHandler(STTHandlerInterface):
    def initiate_recording(self, max_seconds=0, silence_threshold=0, silence_duration=0):
        logger.debug("Test mode: Skipping actual recording")

    def run_inference(self):
        return "stt test response"


class STTOperations(EventActor):
    def __init__(self, event_queue, test_mode=True):
        super().__init__(event_queue)
        self.profanity_censor_enabled = profanity_censor_enabled
        self.STT_handler = TestSTTHandler() if test_mode else RealSTTHandler()

    def run_inference(self):
        inference_output = self.STT_handler.run_inference()
        logger.debug(f"Unfiltered inference output: {inference_output}")

        if self.profanity_censor_enabled:
            inference_output = profanity.censor(inference_output, '-')

        logger.debug(f"Finished inferencing, output: {inference_output}")

        self.produce_event(STTDoneEvent(["STT_FINISHED", inference_output], 1))
        sleep(1)

    def record_and_infer(self, event_type=None, event_data=None):
        self.STT_handler.initiate_recording()
        self.run_inference()
        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 2))
        return True

    def get_event_handlers(self):
        return {
            "RECORD_INFER_SPEECH": self.record_and_infer,
        }

    def get_consumable_events(self):
        return [STTEvent]
