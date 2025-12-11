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
        print(" 2. Read User (by username)")
        print(" 3. Update User (by username)")
        print(" 4. Delete User (by username)")
        print(" 5. Login User")
        print(" 6. Return to Phoenix Console")

        choice = input("Enter choice [1–6]: ").strip()

        if choice == "1":
            email = input("Email: ")
            password = input("Password: ")
            username = input("Username: ")
            archetype = input("Archetype (optional): ")
            payload = {
                "email": email,
                "password": password,
                "username": username,
                "archetype": archetype,
            }
            r = requests.post(API_URL + "/", json=payload)
            try:
                print("Response:", r.json())
            except ValueError:
                print("Raw Response:", r.text)

        elif choice == "2":
            username = input("Username to read: ")
            r = requests.get(API_URL + f"/by-username/{username}")
            try:
                print("Response:", r.json())
            except ValueError:
                print("Raw Response:", r.text)

        elif choice == "3":
            username = input("Username to update: ")
            email = input("New Email (blank to skip): ")
            archetype = input("New Archetype (blank to skip): ")
            payload = {}
            if email:
                payload["email"] = email
            if archetype:
                payload["archetype"] = archetype
            r = requests.put(API_URL + f"/by-username/{username}", json=payload)
            try:
                print("Response:", r.json())
            except ValueError:
                print("Raw Response:", r.text)

        elif choice == "4":
            username = input("Username to delete: ")
            r = requests.delete(API_URL + f"/by-username/{username}")
            try:
                print("Response:", r.json())
            except ValueError:
                print("Raw Response:", r.text)

        elif choice == "5":
            email = input("Email: ")
            password = input("Password: ")
            payload = {"email": email, "password": password}
            r = requests.post(API_URL + "/login", json=payload)
            try:
                print("Response:", r.json())
            except ValueError:
                print("Raw Response:", r.text)

        elif choice == "6":
            print("Returning to Phoenix Console…")
            break

        else:
            print("Invalid choice. Try again.")
