import pytsk3
import json
import os
import traceback
from datetime import datetime


class FilesystemParser:
    def __init__(self, fs, partition_id, case_id, index_filename="filesystem_index.json"):
        self.fs = fs
        self.partition_id = partition_id
        self.case_id = case_id
        self.index = []
        self.index_filename = index_filename
        self.errors = []

    def safe_name(self, entry):
        """
        Return decoded name string or None.
        """
        try:
            name_obj = getattr(entry, "info", None)
            if not name_obj:
                return None
            name_field = getattr(name_obj.name, "name", None)
            if not name_field:
                return None
            # name_field may already be str in some bindings, handle both
            if isinstance(name_field, bytes):
                return name_field.decode(errors="ignore")
            return str(name_field)
        except Exception:
            return None

    def parse_directory(self, directory, parent_path="/"):
        """
        Recursively parse entries of a pytsk3 directory object.
        parent_path should be a POSIX style path ("/" root).
        """
        for entry in directory:
            try:
                name = self.safe_name(entry)
                if not name or name in (".", ".."):
                    continue

                # Build canonical path
                if parent_path == "/":
                    full_path = f"/{name}"
                else:
                    full_path = f"{parent_path}/{name}"

                meta = getattr(entry, "info", None)
                meta = getattr(meta, "meta", None)

                if meta:
                    try:
                        size = int(getattr(meta, "size", 0))
                    except Exception:
                        size = 0
                    created = self.convert_time(getattr(meta, "crtime", None))
                    modified = self.convert_time(getattr(meta, "mtime", None))
                else:
                    size = 0
                    created = None
                    modified = None

                # Determine type safely
                entry_type = "file"
                try:
                    if meta and getattr(meta, "type", None) == pytsk3.TSK_FS_META_TYPE_DIR:
                        entry_type = "directory"
                except Exception:
                    entry_type = "file"

                record = {
                    "path": full_path,
                    "type": entry_type,
                    "size": size,
                    "created": created,
                    "modified": modified,
                    "partition": self.partition_id
                }

                self.index.append(record)

                # Recurse only for directories
                if entry_type == "directory":
                    try:
                        sub_directory = entry.as_directory()
                        self.parse_directory(sub_directory, full_path)
                    except Exception as e:
                        # log and continue
                        self.errors.append({
                            "path": full_path,
                            "error": f"as_directory failed: {str(e)}",
                            "trace": traceback.format_exc()
                        })
                        continue

            except Exception as e:
                # log entry-level errors but continue parsing other entries
                self.errors.append({
                    "entry_repr": repr(entry),
                    "error": str(e),
                    "trace": traceback.format_exc()
                })
                continue

    def convert_time(self, timestamp):
        if not timestamp:
            return None
        try:
            # timestamp might be an int or float
            return datetime.utcfromtimestamp(int(timestamp)).isoformat() + "Z"
        except Exception:
            try:
                return datetime.utcfromtimestamp(float(timestamp)).isoformat() + "Z"
            except Exception:
                return None

    def start(self):
        try:
            root = self.fs.open_dir(path="/")
        except Exception as e:
            print(f"[-] Failed to open root directory for partition {self.partition_id}: {e}")
            return

        print(f"[+] Parsing filesystem (Partition {self.partition_id})")
        self.parse_directory(root, parent_path="/")
        print(f"[+] Indexed {len(self.index)} entries (partition {self.partition_id})")

        # Save index and any errors
        self.save_index()
        if self.errors:
            self.save_errors()

    def save_index(self):
        case_path = os.path.join("cases", self.case_id)
        os.makedirs(case_path, exist_ok=True)
        index_file = os.path.join(case_path, self.index_filename)

        # Load existing index (if any) then append new records
        existing_data = []
        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                # If existing file is corrupt or very large, keep it safe by backing up
                try:
                    backup = index_file + ".bak"
                    os.replace(index_file, backup)
                    print(f"[!] Existing index corrupted — backed up to {backup}")
                except Exception:
                    pass
                existing_data = []

        existing_data.extend(self.index)

        # Write combined index (may be large)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

        print(f"[+] Filesystem index updated: {index_file}")

    def save_errors(self):
        case_path = os.path.join("cases", self.case_id)
        err_file = os.path.join(case_path, f"filesystem_parser_errors_partition_{self.partition_id}.json")
        with open(err_file, "w", encoding="utf-8") as f:
            json.dump(self.errors, f, indent=2, ensure_ascii=False)
        print(f"[!] Parser logged {len(self.errors)} errors to {err_file}")