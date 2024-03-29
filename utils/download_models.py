import gdown

from config.tts_config import determ_model_path, stoch_model_path


def download_models():
    """
    Download the Nix TTS models from Google Drive.
    :return:
    """
    print(determ_model_path)
    url = "https://drive.google.com/drive/folders/1-E5kEOhGRW4KiLuQDWiCJsBukkoPtwsu"
    gdown.download_folder(url, output=str(determ_model_path), quiet=False, use_cookies=False)

    url = "https://drive.google.com/drive/folders/1jNr8i2thYDoGxZv-G_o9mHWjNxnaHVhK"
    gdown.download_folder(url, output=str(stoch_model_path), quiet=False, use_cookies=False)


if __name__ == "__main__":
    download_models()
