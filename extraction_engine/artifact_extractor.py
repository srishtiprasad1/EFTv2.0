import json
import os


class ArtifactExtractor:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.index_file = os.path.join(self.case_path, "filesystem_index.json")

        self.output_file = os.path.join(self.case_path, "artifact_evidence.json")

        self.results = {
            "apps_detected": [],
            "artifacts": [],
            "file_types": {
                "databases": [],
                "media": [],
                "documents": []
            }
        }

    def load_index(self):

        if not os.path.exists(self.index_file):
            print("[-] Filesystem index not found")
            return []

        with open(self.index_file, "r") as f:
            return json.load(f)

    def search_artifacts(self, filesystem_index):

        artifact_patterns = {
            "WhatsApp": ["com.whatsapp", "whatsapp"],
            "Telegram": ["org.telegram", "telegram"],
            "Instagram": ["com.instagram", "instagram"],
            "Chrome": ["chrome"]
        }

        seen_paths = set()  # avoid duplicates

        for entry in filesystem_index:

            path = entry.get("path", "").lower()

            if not path:
                continue

            # -------- App Detection --------
            for app, indicators in artifact_patterns.items():

                if any(indicator in path for indicator in indicators):

                    if app not in self.results["apps_detected"]:
                        self.results["apps_detected"].append(app)

                    if path not in seen_paths:
                        self.results["artifacts"].append({
                            "app": app,
                            "path": entry["path"],
                            "extracted_path": None   # 🔥 future use
                        })
                        seen_paths.add(path)

            # -------- File Type Detection --------
            file_entry = {
                "path": entry["path"],
                "extracted_path": None   # 🔥 important for next module
            }

            if path.endswith(".db"):
                self.results["file_types"]["databases"].append(file_entry)

            elif path.endswith((".jpg", ".png", ".mp4", ".jpeg")):
                self.results["file_types"]["media"].append(file_entry)

            elif path.endswith((".pdf", ".docx", ".txt")):
                self.results["file_types"]["documents"].append(file_entry)

    def save_results(self):

        with open(self.output_file, "w") as f:
            json.dump(self.results, f, indent=4)

        print(f"[+] Artifact evidence saved to {self.output_file}")

    def print_summary(self):

        print("\n[+] Artifact Summary:")

        print(f"Apps detected: {', '.join(self.results['apps_detected']) if self.results['apps_detected'] else 'None'}")

        print(f"Databases found: {len(self.results['file_types']['databases'])}")
        print(f"Media files found: {len(self.results['file_types']['media'])}")
        print(f"Documents found: {len(self.results['file_types']['documents'])}")

    def run(self):

        print("[+] Extracting application artifacts...")

        filesystem_index = self.load_index()

        if not filesystem_index:
            return

        self.search_artifacts(filesystem_index)

        self.save_results()

        self.print_summary()

        if not self.results["apps_detected"]:
            print("[-] No application artifacts found")