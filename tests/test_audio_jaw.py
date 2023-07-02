import argparse
import logging
import os
import sys

# Configure logging level
logging.basicConfig(level=logging.DEBUG)


def test_audiofile_to_jaw():
    # Create an instance of the class and start it
    sync = AudioJawSync()
    sync.start(test_audio_path)


def test_mic_to_jaw(seconds_to_analyze=30):
    # Create an instance of the class and start it
    sync = AudioJawSync()
    sync.min_rms = 10
    sync.start(seconds_to_analyze=seconds_to_analyze)


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

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="Select 'audiofile' for audio file test or 'mic' for mic test.")
    parser.add_argument("--seconds", default=30, type=int, help="Specify the number of seconds to analyze for the mic "
                                                                "test.")

    # Parse the command line arguments
    args = parser.parse_args()

    # Run the selected test
    if args.mode == "audiofile":
        test_audiofile_to_jaw()
    elif args.mode == "mic":
        test_mic_to_jaw(seconds_to_analyze=args.seconds)
    else:
        print(f"Invalid mode selected. Please use 'audiofile' or 'mic'.")
