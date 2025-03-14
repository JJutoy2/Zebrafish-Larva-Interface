import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from Animations.okr_animation import setup_okr

a, b, c = setup_okr()
c.start()