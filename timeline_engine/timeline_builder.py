import json
import os


class TimelineBuilder:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.index_file = os.path.join(self.case_path, "filesystem_index.json")
        self.artifact_file = os.path.join(self.case_path, "artifact_evidence.json")

        self.timeline = []

    def load_filesystem_index(self):

        with open(self.index_file, "r") as f:
            return json.load(f)

    def load_artifacts(self):

        with open(self.artifact_file, "r") as f:
            return json.load(f)

    def build_filesystem_events(self, filesystem_index):

        for entry in filesystem_index:

            if entry["modified"]:

                event = {
                    "timestamp": entry["modified"],
                    "event": "file_modified",
                    "path": entry["path"]
                }

                self.timeline.append(event)

    def build_artifact_events(self, artifacts):

        for artifact in artifacts["artifacts"]:

            event = {
                "timestamp": "unknown",
                "event": f"{artifact['app']} artifact detected",
                "path": artifact["path"]
            }

            self.timeline.append(event)

    def save_timeline(self):

        timeline_file = os.path.join(self.case_path, "timeline.json")

        self.timeline.sort(key=lambda x: str(x["timestamp"]))

        with open(timeline_file, "w") as f:
            json.dump(self.timeline, f, indent=4)

        print(f"[+] Timeline saved to {timeline_file}")

    def run(self):

        print("[+] Building forensic timeline...")

        filesystem_index = self.load_filesystem_index()

        artifacts = self.load_artifacts()

        self.build_filesystem_events(filesystem_index)

        self.build_artifact_events(artifacts)

        self.save_timeline()