# manage_users.py — Phoenix Console User Management Ritual
# Author: Shon Heersink & Copilot

import requests

API_URL = "http://localhost:8000/users"  # adjust if running on a different port

def run():
    print("╔════════════════════════════════════════════════════╗")
    print("║   👤 USER MANAGEMENT RITUAL                        ║")
    print("║                                                    ║")
    print("║   Each user is a sovereign stone in the cathedral. ║")
    print("║   Here you summon, gaze upon, reshape, or archive. ║")
    print("╚════════════════════════════════════════════════════╝")

    while True:
        print("\nChoose your identity ritual:")
        print(" 1. Create User")
        print(" 2. Read User")
        print(" 3. Update User")
        print(" 4. Delete User")
        print(" 5. Return to Phoenix Console")

        choice = input("Enter choice [1–5]: ").strip()

        if choice == "1":
            user_id = input("User ID: ")
            email = input("Email: ")
            password = input("Password: ")
            payload = {
                "user_id": user_id,
                "email": email,
                "password_hash": password,  # will be hashed server‑side
            }
            r = requests.post(API_URL + "/", json=payload)
            print("Response:", r.json())

        elif choice == "2":
            user_id = input("User ID to read: ")
            r = requests.get(API_URL + f"/{user_id}")
            print("Response:", r.json())

        elif choice == "3":
            user_id = input("User ID to update: ")
            note = input("New note (optional): ")
            payload = {"note": note}
            r = requests.put(API_URL + f"/{user_id}", json=payload)
            print("Response:", r.json())

        elif choice == "4":
            user_id = input("User ID to delete: ")
            r = requests.delete(API_URL + f"/{user_id}")
            print("Response:", "Deleted" if r.status_code == 204 else r.json())

        elif choice == "5":
            print("🕊️ Returning to Phoenix Console…")
            break
        else:
            print("Invalid choice. Try again.")
