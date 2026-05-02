import os
import json
import sqlite3


class SQLiteExtractor:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.artifact_file = os.path.join(self.case_path, "artifact_evidence.json")

        self.output_file = os.path.join(self.case_path, "sqlite_data.json")

        self.results = []

    def load_artifacts(self):

        if not os.path.exists(self.artifact_file):
            print("[-] No artifact file found")
            return []

        with open(self.artifact_file, "r") as f:
            data = json.load(f)

        return data.get("file_types", {}).get("databases", [])

    def extract_db(self, db_path):

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            db_info = {
                "database": db_path,
                "tables": []
            }

            for table in tables:

                table_name = table[0]

                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()

                    db_info["tables"].append({
                        "table": table_name,
                        "sample_rows": rows
                    })

                except Exception:
                    continue

            conn.close()
            return db_info

        except Exception:
            return None

    def run(self):

        print("[+] Running SQLite Extraction...")

        db_entries = self.load_artifacts()

        if not db_entries:
            print("[-] No database files found")
            return

        for entry in db_entries:

            db_path = entry.get("extracted_path")

            if not db_path or not os.path.exists(db_path):
                continue

            result = self.extract_db(db_path)

            if result:
                self.results.append(result)

        with open(self.output_file, "w") as f:
            json.dump(self.results, f, indent=4)

        print(f"[+] SQLite data saved to {self.output_file}")