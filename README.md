# Virtual Loopback Device Setup on Raspberry Pi

This guide will walk you through the process of setting up a virtual loopback device on a Raspberry Pi. This allows you to record audio coming from the speakers while also playing the sound.

## Prerequisites

- Raspberry Pi with Raspbian or a similar OS installed.
- ALSA utilities installed (usually pre-installed with Raspbian).

## Hardware/Code setup

Full build instructions/parts list can be found [here](https://www.hackster.io/314reactor/westworld-prototype-skull-6ee7d9)

## Audio setup

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

### 3. Move the Configuration File

If you've created or modified the `asound.conf` file in a different location, move it to `/etc/`:

```sudo mv asound.conf /etc/```


### 4. Restart ALSA Utilities

To load the new configuration, restart the ALSA utilities:

```/etc/init.d/alsa-utils restart```

### Troubleshooting

If there are issues then run the find_loopback.py file:

```python3 find_loopback.py```

And see what the output is. If it is not 1,0 then change the asound.conf file to match the output.

As well as changing the loopback_name variable in config/audio_config.py

## Startup script

Copy setup/rc.local to /etc/rc.local

```sudo cp setup/rc.local /etc/rc.local```

This sets up the 'close_jaw.py' script to run on startup (which is required because on boot the servo opens the jaw for some reason).

## Local Whisper model setup

To download the models required for running Whisper locally, run the following script:

```python setup_models.py```

## Configuring the system

### Configuring Lakul (Speech Recognition with Whisper)

You need to copy the file `Lakul/config/whisper_config_template.py` into a file called `Lakul/config/whisper_config.py` and 
add your own API key from [OpenAI](https://platform.openai.com/); if you wish to use the online version (will be considerably
faster on a RPi 4 than the offline version, but of course will cost you money per inference).

You can then switch between local and online versions by changing the `offline_mode` variable in `Lakul/config/whisper_config.py`.

### Configuring the TTS (Text to Speech)

Under config/tts_config.py you can change the voice and speed of the TTS.

In order to use fakeyou you will need to set up an account [here](https://fakeyou.com/), copy config/fakeyou_config_template.py 
to config/fakeyou_config.py and add your login details and voice ID for the voice you want.

### Configuring ChattingGPT (Chatting with GPT-3)

Copy or rename 'ChattingGPT/config/api_config_template.py' to 'ChattingGPT/config/api_config.py' and add your own API key
from [OpenAI](https://platform.openai.com/)

## Running the code

To run a demo mode where the skull will just say some pre-defined phrases, run the following command:

```sudo python demo_activate.py```

For running the full system, run the following command:

```sudo python activate.py```

## Running tests

If you want to make some changes and need to test things are still working, or need to test the hardware has been set up correctly, then you can run the tests individually:

```sudo python tests/test_audio_jaw.py```

```sudo python tests/test_chatgpt.py```

```sudo python tests/test_microwave_sensor.py```

```sudo python tests/test_tts.py```

```sudo python tests/test_whisper.py```

Or, run the entire suite:

```sudo python test_suite.py```