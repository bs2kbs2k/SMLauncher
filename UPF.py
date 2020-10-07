import json
import sys
import zipfile
from os.path import normpath

import safetar


class UPF:
    def __init__(self, upf_file):
        # Open the file and basic stuff
        self.UPF_file = upf_file
        if not zipfile.is_zipfile(upf_file):
            raise ValueError("Incorrect file format")
        self.zip_file = zipfile.ZipFile(upf_file)
        self.overwrites = [normpath(file.filename) for file in self.zip_file.infolist() if
                           not file.is_dir() and file.filename == "overwrites/"]
        if "UPF.json" not in self.zip_file.namelist():
            raise ValueError("Not a UPF file")

        # File sanity check
        try:
            self.metadata = json.load(self.zip_file.open("UPF.json"))
        except KeyError:
            raise RuntimeError("UPF.json is in the file list but doesn't exist. WTH?")
        except json.JSONDecodeError:
            raise ValueError("Metadata is not a valid JSON")

        # Metadata sanity check
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata invalid: top-level object is not a object")
        if "version" not in self.metadata:
            raise ValueError("Metadata invalid: No version attribute")
        if "name" not in self.metadata:
            raise ValueError("Metadata invalid: No name attribute")
        if "id" not in self.metadata:
            raise ValueError("Metadata invalid: No id attribute")
        if "format_version" not in self.metadata:
            raise ValueError("Metadata invalid: No format_version attribute")

        # Supported version
        if self.metadata["format_version"] not in ["1.0"]:
            raise ValueError("Unsupported metadata format version; Please update the program")

        self.version = self.metadata["version"]
        self.name = self.metadata["name"]
        self.name = self.metadata["id"]
        self.author = self.metadata["author"] if "author" in self.metadata else "Unknown"

    def list_overwrites(self):
        return self.overwrites

    def extract(self, location, log_file=sys.stdout):
        self.zip_file.extractall(location, safetar.safemembers(self.zip_file.infolist(), log_file))
