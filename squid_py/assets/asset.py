from squid_py.ddo import DDO
from squid_py.service_agreement import ServiceTypes


class Asset(DDO):
    @property
    def encrypted_files(self):
        metadata_service = self.get_service(service_type=ServiceTypes.METADATA)
        files = metadata_service.get_values()['metadata']['base']['encryptedFiles']
        # files = files if isinstance(files, str) else files[0]
        return files

    @property
    def files(self):
        metadata_service = self.get_service(service_type=ServiceTypes.METADATA)
        files = metadata_service.get_values()['metadata']['base']['files']
        return files
