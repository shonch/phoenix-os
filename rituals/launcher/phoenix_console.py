# phoenix_console.py — Emotional OS Launcher (Canon Edition)
# Author: Shon Heersink & Copilot

import os
import importlib.util

import sys

phoenix_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

if phoenix_root not in sys.path:
    sys.path.insert(0, phoenix_root)


def show_banner():
    print("╔════════════════════════════════════════════════════╗")
    print("║                                                    ║")
    print("║        🕊️  PHOENIX OS — Emotional Ritual Engine     ║")
    print("║                                                    ║")
    print("║   You are mythic. You are sovereign. You are here. ║")
    print("║   This system honors your grief, your longing,     ║")
    print("║   your fragments, and your legacy.                 ║")
    print("║                                                    ║")
    print("║   Every script is a threshold. Every choice a vow. ║")
    print("║                                                    ║")
    print("╚════════════════════════════════════════════════════╝")

def launch_module_by_path(relative_path):
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        full_path = os.path.join(base_dir, relative_path)
        module_name = os.path.splitext(os.path.basename(full_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.run()
    except FileNotFoundError:
        print(f"⚠️ File '{relative_path}' not found.")
    except AttributeError:
        print(f"⚠️ Module '{relative_path}' does not contain a 'run()' function.")
    except Exception as e:
        import traceback
        print("⚠️ Error launching module:")
        traceback.print_exc()

def menu():
    show_banner()
    while True:
        print("\n🔥 Welcome to Phoenix OS")
        print("Choose your ritual:")
        print(" 1. Log Emotion")
        print(" 2. Detective Protocol")
        print(" 3. Threshold Guard")
        print(" 4. Anti-Grind Override")
        print(" 5. Grind Protocol")
        print(" 6. Mirror Reflection")
        print(" 7. Emerge Revelation")
        print(" 8. Inspect Phoenix Collections")
        print(" 9. Emotional Programming Rituals")
        print("10. Log Pulse Fragment")
        print("11. Phoenix Recovery — Reclaim Unrecognized Fragments")
        print("12. Search Phoenix Emotional Records")
        print("13. Valhalla Tracker — Module Status Ritual")
        print("14. Symbolic Tag Ritual — Manage Emotional Overlays")
        print("15. Exit")  # Moved to end
        print("16. User Management Ritual — Shape Sovereign Identities")

        choice = input("Enter choice [1–15]: ").strip()

        if choice == "1":
            launch_module_by_path("logging/log_emotion.py")
        elif choice == "2":
            launch_module_by_path("sleuthing/detective.py")
        elif choice == "3":
            launch_module_by_path("thresholds/threshold_guard.py")
        elif choice == "4":
            launch_module_by_path("defense/anti_grind.py")
        elif choice == "5":
            launch_module_by_path("defense/grind_protocol.py")
        elif choice == "6":
            launch_module_by_path("reflection/mirror.py")
        elif choice == "7":
            launch_module_by_path("thresholds/emerge.py")
        elif choice == "8":
            launch_module_by_path("py/inspect_collections.py")
        elif choice == "9":
            launch_module_by_path("py/emotional_programming.py")
        elif choice == "10":
            launch_module_by_path("logging/pulse.py")
        elif choice == "11":
            launch_module_by_path("../ingestion/phoenix_recover.py")
        elif choice == "12":
            launch_module_by_path("py/search_phoenix.py")
        elif choice == "13":
            launch_module_by_path("../ingestion/valhalla_tracker.py")
        elif choice == "14":
            launch_module_by_path("py/tag_manager.py")
        elif choice == "15":
            print("🕊️ Ritual session complete. Phoenix rests.")
        elif choice == "16":
            launch_module_by_path("launcher/manage_users.py")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
