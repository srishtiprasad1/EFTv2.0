import hashlib
import json
import os
from datetime import datetime


class HashVerifier:

    @staticmethod
    def calculate_sha256(file_path):
        """
        Compute SHA256 by streaming file (small memory footprint).
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    @staticmethod
    def store_hash(case_id, target, sha256_value):
        """
        Store only the sha256 value into case.json under evidence.<target>.sha256
        and append a structured history entry.
        target: "disk_image" or "memory_dump"
        """
        case_json_path = os.path.join("cases", case_id, "case.json")

        if not os.path.exists(case_json_path):
            raise FileNotFoundError(f"case.json not found for case {case_id}")

        with open(case_json_path, "r") as f:
            case_data = json.load(f)

        # update hash only
        case_data["evidence"][target]["sha256"] = sha256_value

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "action": "hash_calculated",
            "details": {
                "target": target,
                "sha256": sha256_value
            }
        }

        case_data["history"].append(history_entry)

        with open(case_json_path, "w") as f:
            json.dump(case_data, f, indent=4)

        print(f"[+] SHA256 stored for {target}: {sha256_value}")