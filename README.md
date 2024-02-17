# Westworld Prototype Skull

This guide will walk you through the process of setting up the Westworld Prototype Skull on a Raspberry Pi.

## Prerequisites

- Raspberry Pi with Raspbian or a similar OS installed.
- ALSA utilities installed (usually pre-installed with Raspbian).

## Hardware/Code setup

Full build instructions/parts list can be
found [here](https://www.hackster.io/314reactor/westworld-prototype-skull-6ee7d9)

Software runs on RPi OS Bullseye (64-bit)

It's also a good idea to increase the swap size to 2048MB to prevent the RPi from running out of memory:

```sudo dphys-swapfile swapoff```

```sudo nano /etc/dphys-swapfile```

and set:

```CONF_SWAPSIZE=2048```

Then run:

```sudo dphys-swapfile setup```

```sudo dphys-swapfile swapon```

Full instructions for changing swap can be found [here](https://pimylifeup.com/raspberry-pi-swap-file/)

### Cloning the repository

Navigate to your home directory and clone the repository:

```cd ~```

```git clone --recursive https://github.com/LordofBone/WestworldPrototypeSkull.git```

```cd WestworldPrototypeSkull```

## Installing dependencies

You can install the dependencies in a virtual environment:

```sudo apt-get install virtualenv```

```virtualenv venv```

```source venv/bin/activate```

```sudo pip install -r requirements.txt```

(Needs to be run as sudo as the Inventor HAT Mini library below requires it)

For the local Whisper STT installation:

`pip install git+https://github.com/openai/whisper.git`

and to update it:
`pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git`

### Installing the Inventor Hat Mini library

Library installation info [here](https://github.com/pimoroni/inventorhatmini-python#getting-the-library)

Be sure to follow the audio setup instructions below as well.

It's also worth disabling HDMI audio out to prevent the audio from playing through the HDMI port:

```sudo nano /boot/config.txt```

Change line "dtoverlay=vc4-kms-v3d" to "dtoverlay=vc4-kms-v3d,noaudio" and reboot.

And finally install:

```sudo apt install python3-gst-1.0```

Also ensure I2C is enabled on the Raspberry Pi:

```sudo raspi-config```

Select 'Interfacing Options' and then 'I2C' and enable it.

It's also a good idea to use alsamixer to adjust the volume of the microphone:

```alsamixer```

Hit F4 to go to the capture screen.

Find the USB PnP Sound Device and adjust to volume to around 30% and then hit ESC to exit.

### Installing Ollama (for local LLM chatbot)

Guide for installing Ollama on Linux [here](https://ollama.ai/download/linux)

Then to download the LLM and configure it, run:

```./setup/build_llm.sh```

### Installing e-speak (for TTS)

```sudo apt-get install espeak```

## Audio setup

This guide will walk you through the process of setting up a virtual loopback device on a Raspberry Pi. This allows you
to record audio coming from the speakers without having to use the microphone.

### 1. Load the Loopback Module

To create a virtual loopback device, you need to load the `snd-aloop` module:

```sudo nano /etc/modules```

And add the end of the file:

```snd-aloop```

And the reboot the Raspberry Pi:

```sudo reboot now```

### 2. Configure ALSA

Create or modify the `/etc/asound.conf` file with the following content:

```JSON
# .asoundrc
pcm.multi {
    type route;
    slave.pcm {
        type multi;
        slaves.a.pcm "output";
        slaves.b.pcm "loopin";
        slaves.a.channels 2;
        slaves.b.channels 2;
        bindings.0.slave a;
        bindings.0.channel 0;
        bindings.1.slave a;
        bindings.1.channel 1;
        bindings.2.slave b;
        bindings.2.channel 0;
        bindings.3.slave b;
        bindings.3.channel 1;
    }

    ttable.0.0 1;
    ttable.1.1 1;
    ttable.0.2 1;
    ttable.1.3 1;
}

pcm.!default {
	type plug
	slave.pcm "multi"
}

pcm.output {
	type hw
	card 1
}

pcm.loopin {
	type plug
	slave.pcm "hw:Loopback,1,0"
}

pcm.loopout {
	type plug
	slave.pcm "hw:Loopback,0,0"
}
```

Or can copy and paste the asound.conf file in this repo:

```sudo cp setup/asound.conf /etc/```

### 3. Move the Configuration File

If you've created or modified the `asound.conf` file in a different location, move it to `/etc/`:

```sudo mv asound.conf /etc/```

### 4. Restart ALSA Utilities

To load the new configuration, restart the ALSA utilities:

```/etc/init.d/alsa-utils restart```

### 5. Disable HDMI audio out

To disable HDMI audio out, edit the `/boot/config.txt` file:

```sudo nano /boot/config.txt```

And change the following line:

```dtparam=audio=on```

to:

```dtparam=audio=off```

### 6. Reboot

Reboot the Raspberry Pi:

```sudo reboot now```

### Troubleshooting

If there are issues then run the find_loopback.py file:

```python find_loopback.py```

And see what the output is. If it is not 1,0 then change the asound.conf file to match the output.

As well as changing the loopback_name variable in config/audio_config.py

You can also run the following code to check the audio quality, this will record via the mic and then output the audio
to the speakers:

```sudo python mic_quality_check.py```

## Startup script

Copy setup/rc.local to /etc/rc.local

```sudo cp setup/rc.local /etc/rc.local```

And change the <USERHOME> to the user home where the code was cloned to.

This sets up the 'close_jaw.py' script to run on startup (which is required because on boot the servo opens the jaw for
some reason).

## Nix TTS model setup

To download the models required for running Nix, run the following script:

```python setup_models.py```

## Configuring the system

### Setting the API keys

Make a file in the root of your project:

```.env```

And add the following line:
```OPENAI_API_KEY=<your_api_key>```
```FAKEYOU_USERNAME=<your_username>```
```FAKEYOU_PASSWORD=<your_password>```
```FAKEYOU_VOICE_MODEL_ID=<your_voice_model_id>```

Adding your own API key from [OpenAI](https://platform.openai.com/)

Here is a guide on how to get an API key from OpenAI: 
[OpenAI API Key Guide](https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/)

In order to use fakeyou you will need to set up an account [here](https://fakeyou.com/) and add the username/password and voice ID of your
choice to the .env file.

Each request to the OpenAI API will cost you money, so be careful with how many requests you make.

### Configuring Lakul (Speech Recognition with Whisper)

You can set the variable `offline_mode` under config/stt_config to False if you wish to use the OpenAI API version 
(will be considerably faster than the offline version, but of course will cost you money per inference).

You can also change the size of the local model being used with the `model_size` variable; 
the available_models are = ["tiny", "base", "small", "medium", "large"]

As well as being able to adjust the silence threshold parameters.

### Configuring the TTS (Text to Speech)

Under config/tts_config.py you can change the TTS system that is being used and the voice for it.

You can switch between the different TTS engines by changing the `tts_mode` variable to either pyttsx3, fakeyou, nix
or openai.

### Configuring ChattingGPT (Chatting with either ChatGPT or Ollama local LLM)

You can set the `chat_backend` variable to either `gpt` or `ollama` to switch between using the OpenAI ChatGPT API
or run the local Ollama LLM.

If you just want to run a local LLM chatbot, then you can use Ollama by setting the `chat_backend` variable to
'ollama' and ensuring the above Ollama setup has been completed.

There is a `role` variable that enables you to set the role of the chatbot to get different responses. Currently
defaults to a newly made Westworld host prototype.

You can also adjust the `use_history` variable to enable a more conversational chatbot for either GPT or Ollama.

You can set up the chatbot by going to the `setup` folder and running:

```sudo chmod +x build_llm.sh```

```./build_llm.sh```

This will build the model `westworld-prototype` with the configuration from the Modelfile.

You can also modify the Modelfile to change parameters such as the role and the length of responses (this is currently
set to 8 tokens so that it doesn't take too long on a RPi Zero 2W, but you can increase this if you have a more powerful
device).

If you want to use a different model you can change the `ollama_model` variable, currently defaults to
"westworld-prototype", if you do want to use a different model, you will need to download it with Ollama, for example:

```ollama pull llama2```

Then setting:

```ollama_model = "llama2"```

## Running the code

To run a demo mode where the skull will just say some pre-defined phrases, run the following command:

```sudo python demo_activate.py```

For running the full system, run the following command:

```sudo python activate.py```

## Running tests

If you want to make some changes and need to test things are still working, or need to test the hardware has been set up
correctly, then you can run the tests individually:

**Be aware that some of these tests can activate APIs such as FakeYou and OpenAI, so be careful when running them, as it could incur costs.**

```sudo python tests/test_audio_jaw.py```

```sudo python tests/test_chatgpt.py```

```sudo python tests/test_tts.py```

```sudo python tests/test_whisper.py```

Or, run the entire suite:

```sudo python test_suite.py```

These all need to be run as sudo as the Inventor HAT Mini library requires it.