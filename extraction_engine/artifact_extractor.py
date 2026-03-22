import json
import os


class ArtifactExtractor:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.index_file = os.path.join(self.case_path, "filesystem_index.json")
        self.emulator_file = os.path.join(self.case_path, "emulator_evidence.json")

        self.results = {
            "apps_detected": [],
            "artifacts": []
        }

    def load_index(self):

        with open(self.index_file, "r") as f:
            return json.load(f)

    def load_emulator_data(self):

        with open(self.emulator_file, "r") as f:
            return json.load(f)

    def search_artifacts(self, filesystem_index):

        artifact_patterns = {
            "WhatsApp": "com.whatsapp",
            "Telegram": "org.telegram.messenger",
            "Instagram": "com.instagram.android",
            "Chrome": "com.android.chrome"
        }

        for entry in filesystem_index:

            path = entry["path"].lower()

            for app, indicator in artifact_patterns.items():

                if indicator in path:

                    if app not in self.results["apps_detected"]:
                        self.results["apps_detected"].append(app)

                    self.results["artifacts"].append({
                        "app": app,
                        "path": entry["path"]
                    })

    def save_results(self):

        output_file = os.path.join(self.case_path, "artifact_evidence.json")

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=4)

        print(f"[+] Artifact evidence saved to {output_file}")

    def run(self):

        print("[+] Extracting application artifacts...")

        filesystem_index = self.load_index()

        self.search_artifacts(filesystem_index)

        self.save_results()

        if self.results["apps_detected"]:
            print(f"[+] Applications detected: {', '.join(self.results['apps_detected'])}")
        else:
            print("[-] No application artifacts found")