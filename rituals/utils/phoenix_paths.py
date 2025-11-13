import os
import sys

def establish_phoenix_root():
    current_dir = os.path.dirname(__file__)
    phoenix_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    if phoenix_root not in sys.path:
        sys.path.insert(0, phoenix_root)
