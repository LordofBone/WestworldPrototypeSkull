from EventHive.event_hive_runner import Event


class ListenEvent(Event):
    def __init__(self, content, priority):
        super().__init__("LISTEN_EVENT", content, priority)

    def get_event_type(self):
        return self.__class__


class TalkEvent(Event):
    def __init__(self, content, priority):
        super().__init__("LISTEN_EVENT", content, priority)

    def get_event_type(self):
        return self.__class__


class MovementEvent(Event):
    def __init__(self, content, priority):
        super().__init__("MOVEMENT_EVENT", content, priority)

    def get_event_type(self):
        return self.__class__


class DetectEvent(Event):
    def __init__(self, content, priority):
        super().__init__("DETECT_EVENT", content, priority)

    def get_event_type(self):
        return self.__class__


class STTEvent(Event):
    def __init__(self, content, priority):
        super().__init__("STT_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class STTDoneEvent(Event):
    def __init__(self, content, priority):
        super().__init__("STT_Done_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class TTSEvent(Event):
    def __init__(self, content, priority):
        super().__init__("TTS_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class BotEvent(Event):
    def __init__(self, content, priority):
        super().__init__("Bot_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class BotDoneEvent(Event):
    def __init__(self, content, priority):
        super().__init__("Bot_Done_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class ConversationDoneEvent(Event):
    def __init__(self, content, priority):
        super().__init__("Conversation_Done_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class HardwareEvent(Event):
    def __init__(self, content, priority):
        super().__init__("Hardware_Event", content, priority)

    def get_event_type(self):
        return self.__class__


class AudioDetectControllerEvent(Event):
    def __init__(self, content, priority):
        super().__init__("Audio_Detect_Controller_Event", content, priority)

    def get_event_type(self):
        return self.__class__
