from EventHive.event_hive_runner import EventActor
from config.custom_events import DetectEvent, MovementEvent, TalkEvent


class ConversationEngine(EventActor):
    def initiate_conversation_system(self, event):
        """
        This method is called when the event type is "HUMAN_DETECTED"
        :param event:
        :return:
        """
        self.produce_event(TalkEvent(["CONVERSE"], 1))
        self.produce_event(MovementEvent(["JAW_TTS_AUDIO"], 1))
        return True

    def get_event_handlers(self):
        """
        This method returns a dictionary of event handlers.
        :return:
        """
        return {
            ("HUMAN_DETECTED",): self.initiate_conversation_system
        }

    def get_consumable_events(self):
        """
        This method returns a list of event types that this consumer can consume.
        :return:
        """
        return [DetectEvent]
