import logging

from better_profanity import profanity

from EventHive.event_hive_runner import EventActor
from Lakul.integrate_stt import SpeechtoTextHandler
from config.audio_config import microphone_name
from config.custom_events import STTEvent, STTDoneEvent, ConversationDoneEvent
from config.stt_config import profanity_censor_enabled, offline_mode, model_size, stt_audio_path

logger = logging.getLogger(__name__)

logger.debug("Initialized")


class STTOperations(EventActor):
    def __init__(self, event_queue):
        super().__init__(event_queue)

        self.profanity_censor_enabled = profanity_censor_enabled

        self.STT_handler = SpeechtoTextHandler(stt_microphone_name=microphone_name, stt_audio_file=stt_audio_path,
                                               stt_offline_mode=offline_mode, stt_model_size=model_size)

    def initiate_recording(self, max_seconds=60, silence_threshold=100, silence_duration=200):
        """
        Initiate recording.
        :return:
        """
        logger.debug("Listening")

        self.STT_handler.initiate_recording(max_seconds=60, silence_threshold=1000, silence_duration=2000)

        logger.debug("Finished listening")

    def run_inference(self):
        """
        Run speech inference.
        :return:
        """
        logger.debug("Inferencing")

        inference_output = self.STT_handler.run_inference()

        logger.debug(f"Unfiltered inference output: {inference_output}")

        if self.profanity_censor_enabled:
            inference_output = profanity.censor(inference_output, '-')

        logger.debug(f"Finished inferencing, output: {inference_output}")

        self.produce_event(STTDoneEvent(["STT_FINISHED", inference_output], 1))

    def record_and_infer(self):
        """
        This function is used to record audio and run inference.
        :return:
        """
        self.initiate_recording()
        self.run_inference()

        self.produce_event(ConversationDoneEvent(["CONVERSATION_ACTION_FINISHED"], 1))

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            "RECORD_INFER_SPEECH": self.record_and_infer,
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [STTEvent]
