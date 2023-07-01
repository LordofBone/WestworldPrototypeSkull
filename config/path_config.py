import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))

# Build the path to the model file
obj_path = os.path.join(current_dir, '..', 'rendering','models', 'default', 'face.obj')
textures_dir = os.path.join(current_dir, '..', 'rendering', 'textures')
cubemaps_dir = os.path.join(textures_dir, 'cubemaps', 'default')

# Build the path to the vertex shader file
vertex_shader_path = os.path.join(current_dir, '..', 'rendering', 'shaders', 'default', 'simple.vert')

# Build the path to the fragment shader file
fragment_shader_path = os.path.join(current_dir, '..', 'rendering', 'shaders', 'default', 'lighting_toneMapping.frag')

test_audio_path = os.path.join(current_dir, '..', 'audio', 'test.wav')

lakul_dir = os.path.join(current_dir, '..', 'Lakul')

chatting_gpt_dir = os.path.join(current_dir, '..', 'ChattingGPT')

event_hive_dir = os.path.join(current_dir, '..', 'EventHive')
