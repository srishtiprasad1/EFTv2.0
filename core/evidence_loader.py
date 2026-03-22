import os
import json
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


class EvidenceLoader:

    def __init__(self, case_id):
        self.case_id = case_id
        self.disk_image_path = None
        self.memory_dump_path = None

    def browse_file(self, title):

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        path = filedialog.askopenfilename(title=title)

        root.destroy()

        return path

    def update_case_json_with_path(self, target, path):

        case_json_path = os.path.join("cases", self.case_id, "case.json")

        with open(case_json_path, "r") as f:
            case_data = json.load(f)

        case_data["evidence"][target]["path"] = path

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        history_entry = {
            "timestamp": timestamp,
            "action": f"{target}_loaded",
            "details": {
                "path": path
            }
        }

        case_data["history"].append(history_entry)

        with open(case_json_path, "w") as f:
            json.dump(case_data, f, indent=4)

    def select_disk_image(self):

        while True:

            path = input("Enter Disk Image Path (Press ENTER to browse): ").strip()

            if path == "":
                path = self.browse_file("Select Disk Image")

            if path and os.path.exists(path):

                self.disk_image_path = path
                self.update_case_json_with_path("disk_image", path)

                print(f"[+] Disk image loaded: {path}")
                break

            else:
                print("[-] Invalid path. Try again.")

    def select_memory_dump(self):

        while True:

            path = input("Enter Memory Dump Path (Press ENTER to browse): ").strip()

            if path == "":
                path = self.browse_file("Select Memory Dump")

            if path and os.path.exists(path):

                self.memory_dump_path = path
                self.update_case_json_with_path("memory_dump", path)

                print(f"[+] Memory dump loaded: {path}")
                break

            else:
                print("[-] Invalid path. Try again.")

    def confirm_selection(self):

        while True:

            print("\nCurrent Evidence Selection")

            print(f"Disk Image: {self.disk_image_path}")
            print(f"Memory Dump: {self.memory_dump_path}")

            print("\nOptions:")
            print("1 Change Disk Image")
            print("2 Change Memory Dump")
            print("3 Continue")

            choice = input("Enter choice: ")

            if choice == "1":
                self.select_disk_image()

            elif choice == "2":
                self.select_memory_dump()

            elif choice == "3":
                print("[+] Evidence confirmed.")
                break

            else:
                print("Invalid option.")

    def choose_evidence_type(self):

        while True:

            print("\nSelect Evidence Type:")
            print("1 Disk Image Only")
            print("2 Memory Dump Only")
            print("3 Both")

            choice = input("Enter choice: ")

            if choice == "1":
                self.select_disk_image()
                break

            elif choice == "2":
                self.select_memory_dump()
                break

            elif choice == "3":
                self.select_disk_image()
                self.select_memory_dump()
                break

            else:
                print("Invalid choice. Try again.")

        self.confirm_selection()