"""Asset module."""
from squid_py.ddo.ddo import DDO


class Asset(DDO):
    """Class representing an asset base in a DDO object."""

    @property
    def encrypted_files(self):
        """Return encryptedFiles field in the base metadata. """
        files = self.metadata['base']['encryptedFiles']
        return files
