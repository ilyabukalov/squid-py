from squid_py.ddo.ddo import DDO


class Asset(DDO):
    @property
    def encrypted_files(self):
        files = self.metadata['base']['encryptedFiles']
        # files = files if isinstance(files, str) else files[0]
        return files

    @property
    def files(self):
        files = self.metadata['base']['files']
        return files
