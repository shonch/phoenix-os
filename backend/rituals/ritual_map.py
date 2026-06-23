from .pulse_builder import build_pulse_request
from .emotion_builder import build_emotion_request
from .grind_builder import build_grind_request
from .anti_grind_builder import build_anti_grind_request
from .detective_builder import build_detective_request
from .mirror_builder import build_mirror_request
from .emerge_builder import build_emerge_request
from .threshold_builder import build_threshold_request

ritual_map = {
    "pulse": build_pulse_request,
    "emotion": build_emotion_request,
    "grind": build_grind_request,
    "anti_grind": build_anti_grind_request,
    "detective": build_detective_request,
    "mirror": build_mirror_request,
    "emerge": build_emerge_request,
    "threshold": build_threshold_request,
}

