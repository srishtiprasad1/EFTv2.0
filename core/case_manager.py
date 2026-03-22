import os
import json
from datetime import datetime


class CaseManager:

    def __init__(self, case_id, investigator_name):
        self.case_id = case_id
        self.investigator_name = investigator_name
        self.case_path = os.path.join("cases", case_id)

    def create_case(self):

        if not os.path.exists(self.case_path):
            os.makedirs(self.case_path)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        case_metadata = {

            "case_info": {
                "case_id": self.case_id,
                "investigator": self.investigator_name,
                "created_at": timestamp
            },

            "evidence": {
                "disk_image": {
                    "path": None,
                    "sha256": None
                },
                "memory_dump": {
                    "path": None,
                    "sha256": None
                }
            },

            "history": [
                {
                    "timestamp": timestamp,
                    "action": "case_created",
                    "details": {
                        "investigator": self.investigator_name
                    }
                }
            ]
        }

        metadata_file = os.path.join(self.case_path, "case.json")

        with open(metadata_file, "w") as f:
            json.dump(case_metadata, f, indent=4)

        print(f"[+] Case '{self.case_id}' created successfully.")
        print(f"[+] Case directory: {self.case_path}")