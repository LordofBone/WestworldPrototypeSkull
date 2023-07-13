# import os
# import sys
#
# # Get the directory of the current script
# current_dir = os.path.dirname(os.path.realpath(__file__))
#
# # Build the path to the model file
# obj_path = os.path.join(current_dir, '..', 'rendering','models', 'default', 'face.obj')
# textures_dir = os.path.join(current_dir, '..', 'rendering', 'textures')
# cubemaps_dir = os.path.join(textures_dir, 'cubemaps', 'default')
#
# # Build the path to the vertex shader file
# vertex_shader_path = os.path.join(current_dir, '..', 'rendering', 'shaders', 'default', 'simple.vert')
#
# # Build the path to the fragment shader file
# fragment_shader_path = os.path.join(current_dir, '..', 'rendering', 'shaders', 'default', 'lighting_toneMapping.frag')
#
# test_audio_path = os.path.join(current_dir, '..', 'audio', 'test.wav')
#
# tts_audio_path = os.path.join(current_dir, '..', 'audio', 'tts_output.wav')
#
# lakul_dir = os.path.join(current_dir, '..', 'Lakul')
#
# chatting_gpt_dir = os.path.join(current_dir, '..', 'ChattingGPT')
#
# event_hive_dir = os.path.join(current_dir, '..', 'EventHive')
#
# sys.path.append(lakul_dir)
#
# sys.path.append(chatting_gpt_dir)
#
# sys.path.append(event_hive_dir)
#
# print(event_hive_dir)

import sys
from pathlib import Path

# Get the directory of the current script
current_dir = Path(__file__).parent

# Define the root directory
root_dir = current_dir.parent

# Define all the necessary paths
obj_path = root_dir / "rendering" / "models" / "default" / "face.obj"
textures_dir = root_dir / "rendering" / "textures"
cubemaps_dir = textures_dir / "cubemaps" / "default"
vertex_shader_path = root_dir / "rendering" / "shaders" / "default" / "simple.vert"
fragment_shader_path = root_dir / "rendering" / "shaders" / "default" / "lighting_toneMapping.frag"
test_audio_path = root_dir / "audio" / "test.wav"
tts_audio_path = root_dir / "audio" / "tts_output.wav"
lakul_dir = root_dir / "Lakul"
chatting_gpt_dir = root_dir / "ChattingGPT"
event_hive_dir = root_dir / "EventHive"

# Add necessary paths to sys.path
sys.path.extend([str(lakul_dir), str(chatting_gpt_dir), str(event_hive_dir)])

print(event_hive_dir)
