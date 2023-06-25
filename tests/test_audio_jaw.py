import logging

import os
import sys

# Configure logging level
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Get the current script's directory
    current_script_directory = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory
    parent_directory = os.path.dirname(current_script_directory)

    # Insert the parent directory into sys.path
    sys.path.insert(0, parent_directory)

    # Import the class to test
    from components.audio_jaw import AudioJawSync
    from config.path_config import test_audio_path

    # Configure logging level
    logging.basicConfig(level=logging.DEBUG)

    # Create an instance of the class and start it
    sync = AudioJawSync()
    sync.start(test_audio_path)
