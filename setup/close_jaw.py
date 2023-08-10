import sys
from pathlib import Path

top_dir = Path(__file__).parent.parent

sys.path.append(str(top_dir))

from components.jaw_system import JawController

JawControllerInit = JawController()

JawControllerInit.close_jaw()
