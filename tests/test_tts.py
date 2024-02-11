import os
import sys
import unittest
from pathlib import Path

from playsound import playsound

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))
from components.tts_system import TTSOperationsNix, TTSOperationsOpenAI, TTSOperationsPyTTSx3, TTSOperationsFakeYou


class TestTTSSystems(unittest.TestCase):
    base_text = "This is a test of the {system_name} Text-to-Speech system."

    @classmethod
    def setUpClass(cls):
        # List of TTS operation instances to test
        cls.tts_operations = [
            TTSOperationsPyTTSx3(),  # this can be buggy and not save to file, need to find out why
            TTSOperationsNix(),
            # TTSOperationsOpenAI(),  # commented out to prevent accidental use of the OpenAI TTS system
            # TTSOperationsFakeYou(),  # commented out to prevent accidental use of the fakeyou TTS system
        ]

    def test_tts_operations(self):
        loop = 0
        for tts_op in self.tts_operations:
            loop += 1  # Increment loop counter
            class_name = tts_op.__class__.__name__
            # Use string formatting to include both the class name and the loop counter
            test_text = f"{self.base_text.format(system_name=class_name)} Loop: {loop}"

            print(f"Testing TTS system: {class_name}")

            # Generate TTS
            tts_op.generate_tts(test_text)

            # Check if the file exists
            filename = tts_op.filename
            self.assertTrue(os.path.exists(filename), f"Failed to generate TTS file for {class_name}")

            # Optionally, play the sound file here if needed
            playsound(filename)


if __name__ == '__main__':
    unittest.main()
