# Virtual Loopback Device Setup on Raspberry Pi

This guide will walk you through the process of setting up a virtual loopback device on a Raspberry Pi. This allows you to record audio coming from the speakers while also playing the sound.

## Prerequisites

- Raspberry Pi with Raspbian or a similar OS installed.
- ALSA utilities installed (usually pre-installed with Raspbian).

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

## Startup script

Copy setup/rc.local to /etc/rc.local

```sudo cp setup/rc.local /etc/rc.local```

This sets up the 'close_jaw.py' script to run on startup (which is required because on boot the servo opens the jaw for some reason).

## Troubleshooting

If there are issues then run the find_loopback.py file:

```python3 find_loopback.py```

And see what the output is. If it is not 1,0 then change the asound.conf file to match the output.

As well as changing the loopback_name variable in config/audio_config.py