import pytsk3


class DiskAnalyzer:

    def __init__(self, image_path):
        self.image_path = image_path
        self.img = None
        self.volume = None
        self.partitions = []

    def open_image(self):

        print(f"[+] Opening disk image: {self.image_path}")

        try:
            self.img = pytsk3.Img_Info(self.image_path)
            print("[+] Disk image opened successfully")

        except Exception as e:
            print(f"[-] Failed to open disk image: {e}")

    def detect_partitions(self):

        print("[+] Detecting partitions...")

        try:
            self.volume = pytsk3.Volume_Info(self.img)

            for i, partition in enumerate(self.volume):

                part_info = {
                    "index": i,
                    "start": partition.start,
                    "length": partition.len,
                    "description": partition.desc.decode()
                }

                self.partitions.append(part_info)

            print("[+] Partitions detected")

        except Exception as e:
            print(f"[-] Partition detection failed: {e}")

    def display_partitions(self):

        print("\nDetected Partitions:\n")

        for part in self.partitions:

            size_mb = (part["length"] * 512) / (1024 * 1024)

            print(
                f'{part["index"]}  '
                f'{part["description"]}  '
                f'{round(size_mb,2)} MB'
            )

    def get_partition_selection(self):

        print("\nSelect partition(s) to scan")

        print("Example: 1,3")
        print("Or type ALL\n")

        choice = input("Enter selection: ").strip()

        if choice.upper() == "ALL":
            return [p["index"] for p in self.partitions]

        selected = []

        for num in choice.split(","):
            try:
                selected.append(int(num.strip()))
            except:
                pass

        return selected

    def mount_partition(self, partition_index):

        partition = self.partitions[partition_index]

        offset = partition["start"] * 512

        try:

            fs = pytsk3.FS_Info(self.img, offset=offset)

            print(
                f"[+] Mounted partition {partition_index}"
            )

            return fs

        except Exception as e:

            print(
                f"[-] Failed to mount partition {partition_index}: {e}"
            )

            return None

    def analyze(self):

        self.open_image()

        if self.img is None:
            return

        self.detect_partitions()

        if not self.partitions:
            return

        self.display_partitions()

        selected = self.get_partition_selection()

        filesystems = []

        for index in selected:

            fs = self.mount_partition(index)

            if fs:
                filesystems.append(fs)

        return filesystems