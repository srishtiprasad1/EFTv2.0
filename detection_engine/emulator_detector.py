import json
import os


class EmulatorDetector:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.index_file = os.path.join(self.case_path, "filesystem_index.json")

        self.results = {
            "emulator_detected": False,
            "emulators": [],
            "emulator_disks": []
        }

    def load_index(self):

        with open(self.index_file, "r") as f:
            return json.load(f)

    def detect_emulators(self, filesystem_index):

        emulator_paths = {
            "BlueStacks": ["BlueStacks", "HD-Player.exe"],
            "Nox": ["Nox", "nox.exe"],
            "AndroidStudio": [".android", "avd"],
            "Waydroid": ["waydroid"]
        }

        emulator_disk_extensions = [".vmdk", ".qcow2", ".img", ".vdi"]

        for entry in filesystem_index:

            path = entry["path"].lower()

            # Path based detection
            for emulator, indicators in emulator_paths.items():

                for indicator in indicators:

                    if indicator.lower() in path:

                        self.results["emulator_detected"] = True

                        self.results["emulators"].append({
                            "name": emulator,
                            "evidence": path
                        })

            # Disk artifact detection
            for ext in emulator_disk_extensions:

                if path.endswith(ext):

                    self.results["emulator_disks"].append(path)

    def save_results(self):

        evidence_file = os.path.join(self.case_path, "emulator_evidence.json")

        with open(evidence_file, "w") as f:
            json.dump(self.results, f, indent=4)

        print(f"[+] Emulator evidence saved to {evidence_file}")

    def run(self):

        print("[+] Running emulator detection...")

        filesystem_index = self.load_index()

        self.detect_emulators(filesystem_index)

        self.save_results()

        if self.results["emulator_detected"]:

            print("[+] Emulator detected!")

        else:

            print("[-] No emulator artifacts found")