from core.case_manager import CaseManager
from core.evidence_loader import EvidenceLoader
from core.hash_verifier import HashVerifier
from disk_engine.disk_analyzer import DiskAnalyzer
from disk_engine.filesystem_parser import FilesystemParser
from detection_engine.emulator_detector import EmulatorDetector
from extraction_engine.artifact_extractor import ArtifactExtractor
from timeline_engine.timeline_builder import TimelineBuilder
from reporting.report_generator import ReportGenerator


def main():
    print("=== EFT v2.0 ===")

    case_id = input("Enter Case ID: ").strip()
    investigator = input("Enter Investigator Name: ").strip()

    # 1) Create case (creates cases/<case_id>/case.json with initial structure)
    case_manager = CaseManager(case_id, investigator)
    case_manager.create_case()

    # 2) Load evidence (paths are written into case.json by EvidenceLoader)
    loader = EvidenceLoader(case_id)
    loader.choose_evidence_type()

    # 3) Hash verification: compute hashes and store them in case.json
    if loader.disk_image_path:
        print("\nCalculating SHA256 for Disk Image...")
        disk_hash = HashVerifier.calculate_sha256(loader.disk_image_path)
        # store only hash (EvidenceLoader already stored path)
        HashVerifier.store_hash(case_id, "disk_image", disk_hash)

    if loader.memory_dump_path:
        print("\nCalculating SHA256 for Memory Dump...")
        mem_hash = HashVerifier.calculate_sha256(loader.memory_dump_path)
        HashVerifier.store_hash(case_id, "memory_dump", mem_hash)

    if loader.disk_image_path:

        print("\n[+] Starting Disk Analysis")

        analyzer = DiskAnalyzer(loader.disk_image_path)

        filesystems = analyzer.analyze()

        if not filesystems:
            print("[-] No filesystems detected")
            return

        for i, fs in enumerate(filesystems):
            parser = FilesystemParser(fs, i, case_id)
            parser.start()

        print(f"[+] {len(filesystems)} filesystem(s) ready for analysis")

        # Emulator detection
        detector = EmulatorDetector(case_id)
        detector.run()

        #Artifacts extractor
        extractor = ArtifactExtractor(case_id)
        extractor.run()

        #timeline builder
        timeline = TimelineBuilder(case_id)
        timeline.run()

        report = ReportGenerator(case_id)
        report.run()

    print("\n[+] Evidence registration & integrity logging complete.")
    print(f"[+] Case directory: cases/{case_id}")


if __name__ == "__main__":
    main()