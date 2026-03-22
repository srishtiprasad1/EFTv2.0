import json
import os


class ReportGenerator:

    def __init__(self, case_id):

        self.case_id = case_id
        self.case_path = os.path.join("cases", case_id)

        self.case_file = os.path.join(self.case_path, "case.json")
        self.emulator_file = os.path.join(self.case_path, "emulator_evidence.json")
        self.artifact_file = os.path.join(self.case_path, "artifact_evidence.json")
        self.timeline_file = os.path.join(self.case_path, "timeline.json")

    def load_json(self, path):

        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)

        return {}

    def generate_summary(self):

        case = self.load_json(self.case_file)
        emulator = self.load_json(self.emulator_file)
        artifacts = self.load_json(self.artifact_file)
        timeline = self.load_json(self.timeline_file)

        summary_file = os.path.join(self.case_path, "report_summary.txt")

        with open(summary_file, "w") as f:

            f.write("EFT v2.0 Investigation Summary\n")
            f.write("--------------------------------\n\n")

            f.write(f"Case ID: {case['case_info']['case_id']}\n")
            f.write(f"Investigator: {case['case_info']['investigator']}\n\n")

            f.write(f"Emulator Detected: {emulator.get('emulator_detected', False)}\n\n")

            if artifacts.get("apps_detected"):

                f.write("Applications Detected:\n")

                for app in artifacts["apps_detected"]:
                    f.write(f"- {app}\n")

                f.write("\n")

            f.write(f"Timeline Events: {len(timeline)}\n")

        print(f"[+] Summary report generated: {summary_file}")

    def generate_detailed(self):

        case = self.load_json(self.case_file)
        emulator = self.load_json(self.emulator_file)
        artifacts = self.load_json(self.artifact_file)
        timeline = self.load_json(self.timeline_file)

        detailed_report = {
            "case": case,
            "emulator_detection": emulator,
            "artifact_analysis": artifacts,
            "timeline": timeline
        }

        detailed_file = os.path.join(self.case_path, "report_detailed.json")

        with open(detailed_file, "w") as f:
            json.dump(detailed_report, f, indent=4)

        print(f"[+] Detailed report generated: {detailed_file}")

    def run(self):

        print("[+] Generating forensic report...")

        self.generate_summary()

        self.generate_detailed()