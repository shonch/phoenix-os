# phoenix_portfolio/backend/rituals/ritual_map.py

from .pulse_builder import build_pulse_fragment
from .emotion_builder import build_emotion_fragment
from .grind_builder import build_grind_fragment
from .anti_grind_builder import build_anti_grind_fragment
from .detective_builder import build_detective_fragment
from .mirror_builder import build_mirror_fragment
from .emerge_builder import build_emerge_fragment
from .threshold_builder import build_threshold_fragment

ritual_map = {
    "pulse": build_pulse_fragment,
    "emotion": build_emotion_fragment,
    "grind": build_grind_fragment,
    "anti_grind": build_anti_grind_fragment,
    "detective": build_detective_fragment,
    "mirror": build_mirror_fragment,
    "emerge": build_emerge_fragment,
    "threshold": build_threshold_fragment,
}

