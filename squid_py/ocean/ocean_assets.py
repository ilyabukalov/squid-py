"""Ocean module."""
#                                   Apache License
#                             Version 2.0, January 2004
#                          http://www.apache.org/licenses/
#
#     TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
#
#     1. Definitions.
#
#        "License" shall mean the terms and conditions for use, reproduction,
#        and distribution as defined by Sections 1 through 9 of this document.
#
#        "Licensor" shall mean the copyright owner or entity authorized by
#        the copyright owner that is granting the License.
#
#        "Legal Entity" shall mean the union of the acting entity and all
#        other entities that control, are controlled by, or are under common
#        control with that entity. For the purposes of this definition,
#        "control" means (i) the power, direct or indirect, to cause the
#        direction or management of such entity, whether by contract or
#        otherwise, or (ii) ownership of fifty percent (50%) or more of the
#        outstanding shares, or (iii) beneficial ownership of such entity.
#
#        "You" (or "Your") shall mean an individual or Legal Entity
#        exercising permissions granted by this License.
#
#        "Source" form shall mean the preferred form for making modifications,
#        including but not limited to software source code, documentation
#        source, and configuration files.
#
#        "Object" form shall mean any form resulting from mechanical
#        transformation or translation of a Source form, including but
#        not limited to compiled object code, generated documentation,
#        and conversions to other media types.
#
#        "Work" shall mean the work of authorship, whether in Source or
#        Object form, made available under the License, as indicated by a
#        copyright notice that is included in or attached to the work
#        (an example is provided in the Appendix below).
#
#        "Derivative Works" shall mean any work, whether in Source or Object
#        form, that is based on (or derived from) the Work and for which the
#        editorial revisions, annotations, elaborations, or other modifications
#        represent, as a whole, an original work of authorship. For the purposes
#        of this License, Derivative Works shall not include works that remain
#        separable from, or merely link (or bind by name) to the interfaces of,
#        the Work and Derivative Works thereof.
#
#        "Contribution" shall mean any work of authorship, including
#        the original version of the Work and any modifications or additions
#        to that Work or Derivative Works thereof, that is intentionally
#        submitted to Licensor for inclusion in the Work by the copyright owner
#        or by an individual or Legal Entity authorized to submit on behalf of
#        the copyright owner. For the purposes of this definition, "submitted"
#        means any form of electronic, verbal, or written communication sent
#        to the Licensor or its representatives, including but not limited to
#        communication on electronic mailing lists, source code control systems,
#        and issue tracking systems that are managed by, or on behalf of, the
#        Licensor for the purpose of discussing and improving the Work, but
#        excluding communication that is conspicuously marked or otherwise
#        designated in writing by the copyright owner as "Not a Contribution."
#
#        "Contributor" shall mean Licensor and any individual or Legal Entity
#        on behalf of whom a Contribution has been received by Licensor and
#        subsequently incorporated within the Work.
#
#     2. Grant of Copyright License. Subject to the terms and conditions of
#        this License, each Contributor hereby grants to You a perpetual,
#        worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#        copyright license to reproduce, prepare Derivative Works of,
#        publicly display, publicly perform, sublicense, and distribute the
#        Work and such Derivative Works in Source or Object form.
#
#     3. Grant of Patent License. Subject to the terms and conditions of
#        this License, each Contributor hereby grants to You a perpetual,
#        worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#        (except as stated in this section) patent license to make, have made,
#        use, offer to sell, sell, import, and otherwise transfer the Work,
#        where such license applies only to those patent claims licensable
#        by such Contributor that are necessarily infringed by their
#        Contribution(s) alone or by combination of their Contribution(s)
#        with the Work to which such Contribution(s) was submitted. If You
#        institute patent litigation against any entity (including a
#        cross-claim or counterclaim in a lawsuit) alleging that the Work
#        or a Contribution incorporated within the Work constitutes direct
#        or contributory patent infringement, then any patent licenses
#        granted to You under this License for that Work shall terminate
#        as of the date such litigation is filed.
#
#     4. Redistribution. You may reproduce and distribute copies of the
#        Work or Derivative Works thereof in any medium, with or without
#        modifications, and in Source or Object form, provided that You
#        meet the following conditions:
#
#        (a) You must give any other recipients of the Work or
#            Derivative Works a copy of this License; and
#
#        (b) You must cause any modified files to carry prominent notices
#            stating that You changed the files; and
#
#        (c) You must retain, in the Source form of any Derivative Works
#            that You distribute, all copyright, patent, trademark, and
#            attribution notices from the Source form of the Work,
#            excluding those notices that do not pertain to any part of
#            the Derivative Works; and
#
#        (d) If the Work includes a "NOTICE" text file as part of its
#            distribution, then any Derivative Works that You distribute must
#            include a readable copy of the attribution notices contained
#            within such NOTICE file, excluding those notices that do not
#            pertain to any part of the Derivative Works, in at least one
#            of the following places: within a NOTICE text file distributed
#            as part of the Derivative Works; within the Source form or
#            documentation, if provided along with the Derivative Works; or,
#            within a display generated by the Derivative Works, if and
#            wherever such third-party notices normally appear. The contents
#            of the NOTICE file are for informational purposes only and
#            do not modify the License. You may add Your own attribution
#            notices within Derivative Works that You distribute, alongside
#            or as an addendum to the NOTICE text from the Work, provided
#            that such additional attribution notices cannot be construed
#            as modifying the License.
#
#        You may add Your own copyright statement to Your modifications and
#        may provide additional or different license terms and conditions
#        for use, reproduction, or distribution of Your modifications, or
#        for any such Derivative Works as a whole, provided Your use,
#        reproduction, and distribution of the Work otherwise complies with
#        the conditions stated in this License.
#
#     5. Submission of Contributions. Unless You explicitly state otherwise,
#        any Contribution intentionally submitted for inclusion in the Work
#        by You to the Licensor shall be under the terms and conditions of
#        this License, without any additional terms or conditions.
#        Notwithstanding the above, nothing herein shall supersede or modify
#        the terms of any separate license agreement you may have executed
#        with Licensor regarding such Contributions.
#
#     6. Trademarks. This License does not grant permission to use the trade
#        names, trademarks, service marks, or product names of the Licensor,
#        except as required for reasonable and customary use in describing the
#        origin of the Work and reproducing the content of the NOTICE file.
#
#     7. Disclaimer of Warranty. Unless required by applicable law or
#        agreed to in writing, Licensor provides the Work (and each
#        Contributor provides its Contributions) on an "AS IS" BASIS,
#        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#        implied, including, without limitation, any warranties or conditions
#        of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
#        PARTICULAR PURPOSE. You are solely responsible for determining the
#        appropriateness of using or redistributing the Work and assume any
#        risks associated with Your exercise of permissions under this License.
#
#     8. Limitation of Liability. In no event and under no legal theory,
#        whether in tort (including negligence), contract, or otherwise,
#        unless required by applicable law (such as deliberate and grossly
#        negligent acts) or agreed to in writing, shall any Contributor be
#        liable to You for damages, including any direct, indirect, special,
#        incidental, or consequential damages of any character arising as a
#        result of this License or out of the use or inability to use the
#        Work (including but not limited to damages for loss of goodwill,
#        work stoppage, computer failure or malfunction, or any and all
#        other commercial damages or losses), even if such Contributor
#        has been advised of the possibility of such damages.
#
#     9. Accepting Warranty or Additional Liability. While redistributing
#        the Work or Derivative Works thereof, You may choose to offer,
#        and charge a fee for, acceptance of support, warranty, indemnity,
#        or other liability obligations and/or rights consistent with this
#        License. However, in accepting such obligations, You may act only
#        on Your own behalf and on Your sole responsibility, not on behalf
#        of any other Contributor, and only if You agree to indemnify,
#        defend, and hold each Contributor harmless for any liability
#        incurred by, or claims asserted against, such Contributor by reason
#        of your accepting any such warranty or additional liability.
#
#     END OF TERMS AND CONDITIONS
#
#     APPENDIX: How to apply the Apache License to your work.
#
#        To apply the Apache License to your work, attach the following
#        boilerplate notice, with the fields enclosed by brackets "[]"
#        replaced with your own identifying information. (Don't include
#        the brackets!)  The text should be enclosed in the appropriate
#        comment syntax for the file format. We also recommend that a
#        file or class name and description of purpose be included on the
#        same "printed page" as the copyright notice for easier
#        identification within third-party archives.
#
#   Copyright 2018 BigchainDB GmbH
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import copy
import json
import logging
import os

from squid_py.agreements.service_factory import ServiceDescriptor, ServiceFactory
from squid_py.agreements.service_types import ServiceTypes
from squid_py.agreements.utils import (
    make_public_key_and_authentication,
)
from squid_py.aquarius.aquarius_provider import AquariusProvider
from squid_py.aquarius.exceptions import AquariusGenericError
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.ddo.ddo import DDO
from squid_py.ddo.metadata import Metadata, MetadataBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.did import DID, did_to_id
from squid_py.exceptions import (
    OceanDIDAlreadyExist,
    OceanInvalidMetadata,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store.secret_store_provider import SecretStoreProvider

logger = logging.getLogger('ocean')


class OceanAssets:
    """Ocean assets class."""

    def __init__(self, keeper, did_resolver, agreements, asset_consumer, config):
        self._keeper = keeper
        self._did_resolver = did_resolver
        self._agreements = agreements
        self._asset_consumer = asset_consumer
        self._config = config
        self._aquarius_url = config.aquarius_url

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self._config.has_option('resources', 'downloads.path'):
            downloads_path = self._config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

    def _get_aquarius(self, url=None):
        return AquariusProvider.get_aquarius(url or self._aquarius_url)

    def _get_secret_store(self, account):
        return SecretStoreProvider.get_secret_store(
            self._config.secret_store_url, self._config.parity_url, account
        )

    def create(self, metadata, publisher_account, service_descriptors=None):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Metadata store (
        Aquarius).

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher_account: Account of the publisher registering this asset
        :param service_descriptors: list of ServiceDescriptor tuples of length 2.
            The first item must be one of ServiceTypes and the second
            item is a dict of parameters and values required by the service
        :return: DDO instance
        """
        assert isinstance(metadata, dict), f'Expected metadata of type dict, got {type(metadata)}'
        if not metadata or not Metadata.validate(metadata):
            raise OceanInvalidMetadata('Metadata seems invalid. Please make sure'
                                       ' the required metadata values are filled in.')

        # copy metadata so we don't change the original
        metadata_copy = copy.deepcopy(metadata)

        # Create a DDO object
        did = DID.did()
        logger.debug(f'Generating new did: {did}')
        # Check if it's already registered first!
        if did in self._get_aquarius().list_assets():
            raise OceanDIDAlreadyExist(
                f'Asset id {did} is already registered to another asset.')

        ddo = DDO(did)

        # Add public key and authentication
        self._keeper.unlock_account(publisher_account)
        pub_key, auth = make_public_key_and_authentication(did, publisher_account.address,
                                                           Web3Provider.get_web3())
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        priv_key = ddo.add_signature()
        ddo.add_proof(1, publisher_account.address, private_key=priv_key)

        # Setup metadata service
        # First replace `files` with encrypted `files`
        assert metadata_copy['base'][
            'files'], 'files is required in the metadata base attributes.'
        assert Metadata.validate(metadata), 'metadata seems invalid.'
        logger.debug('Encrypting content urls in the metadata.')
        files_encrypted = self._get_secret_store(publisher_account) \
            .encrypt_document(
            did_to_id(did),
            json.dumps(metadata_copy['base']['files']),
        )

        metadata_copy['base']['checksum'] = ddo.generate_checksum(did, metadata)

        # only assign if the encryption worked
        if files_encrypted:
            logger.info(f'Content urls encrypted successfully {files_encrypted}')
            del metadata_copy['base']['files']
            metadata_copy['base']['encryptedFiles'] = files_encrypted
        else:
            raise AssertionError('Encrypting the files failed. Make sure the secret store is'
                                 ' setup properly in your config file.')

        # DDO url and `Metadata` service
        ddo_service_endpoint = self._get_aquarius().get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy,
                                                                              ddo_service_endpoint)
        if not service_descriptors:
            service_descriptors = [ServiceDescriptor.authorization_service_descriptor(
                self._config.secret_store_url)]
            brizo = BrizoProvider.get_brizo()
            service_descriptors += [ServiceDescriptor.access_service_descriptor(
                metadata[MetadataBase.KEY]['price'],
                brizo.get_purchase_endpoint(self._config),
                brizo.get_service_endpoint(self._config),
                3600,
                self._keeper.escrow_access_secretstore_template.address
            )]
        else:
            service_types = set(map(lambda x: x[0], service_descriptors))
            if ServiceTypes.AUTHORIZATION not in service_types:
                service_descriptors += [ServiceDescriptor.authorization_service_descriptor(
                    self._config.secret_store_url)]
            else:
                brizo = BrizoProvider.get_brizo()
                service_descriptors += [ServiceDescriptor.access_service_descriptor(
                    metadata[MetadataBase.KEY]['price'],
                    brizo.get_purchase_endpoint(self._config),
                    brizo.get_service_endpoint(self._config),
                    3600,
                    self._keeper.escrow_access_secretstore_template.address
                )]

        # Add all services to ddo
        service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(did, service_descriptors):
            ddo.add_service(service)

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}, '
            f'`Access` service purchase @{ddo.services[0].endpoints.service}.')
        response = None
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self._get_aquarius().publish_asset_ddo(ddo)
            logger.debug('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')

        if not response:
            return None

        # register on-chain
        self._keeper.unlock_account(publisher_account)
        self._keeper.did_registry.register(
            did,
            checksum=Web3Provider.get_web3().sha3(text=metadata_copy['base']['checksum']),
            url=ddo_service_endpoint,
            account=publisher_account
        )
        logger.info(f'DDO with DID {did} successfully registered on chain.')
        return ddo

    def retire(self, did):
        """
        Retire this did of Aquarius

        :param did: DID, str
        :return: bool
        """
        try:
            ddo = self.resolve(did)
            metadata_service = ddo.find_service_by_type(ServiceTypes.METADATA)
            self._get_aquarius(metadata_service.endpoints.service).retire_asset_ddo(did)
            return True
        except AquariusGenericError as err:
            logger.error(err)
            return False

    def resolve(self, did):
        """
        When you pass a did retrieve the ddo associated.

        :param did: DID, str
        :return: DDO instance
        """
        return self._did_resolver.resolve(did)

    def search(self, text, sort=None, offset=100, page=0, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.

        :param text: String with the value that you are searching
        :param sort: Dictionary to choose order base in some value
        :param offset: Number of elements shows by page
        :param page: Page number
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query
        """
        logger.info(f'Searching asset containing: {text}')
        return [DDO(dictionary=ddo_dict) for ddo_dict in
                self._get_aquarius(aquarius_url).text_search(text, sort, offset, page)]

    def query(self, query, aquarius_url=None):
        """
        Search an asset in oceanDB using search query.

        :param query: dict with query parameters
            (e.g.) {"offset": 100, "page": 0, "sort": {"value": 1},
                    query: {"service:{$elemMatch:{"metadata": {$exists : true}}}}}
                    Here, OceanDB instance of mongodb can leverage power of mongo queries in
                    'query' attribute.
                    For more info -
                    https://docs.mongodb.com/manual/reference/method/db.collection.find
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query.
        """
        logger.info(f'Searching asset query: {query}')
        aquarius = self._get_aquarius(aquarius_url)
        return [DDO(dictionary=ddo_dict) for ddo_dict in aquarius.query_search(query)]

    def order(self, did, service_definition_id, consumer_account):
        """
        Sign service agreement.

        Sign the service agreement defined in the service section identified
        by `service_definition_id` in the ddo and send the signed agreement to the purchase endpoint
        associated with this service.

        :param did: str starting with the prefix `did:op:` and followed by the asset id which is
        a hex str
        :param service_definition_id: str the service definition id identifying a specific
        service in the DDO (DID document)
        :param consumer_account: ethereum address of consumer signing the agreement and
        initiating a purchase/access transaction
        :return: tuple(agreement_id, signature) the service agreement id (can be used to query
            the keeper-contracts for the status of the service agreement) and signed agreement hash
        """
        assert consumer_account.address in self._keeper.accounts, f'Unrecognized consumer ' \
            f'address `consumer_account`'

        agreement_id, signature = self._agreements.prepare(
            did, service_definition_id, consumer_account
        )
        self._agreements.send(did, agreement_id, service_definition_id, signature, consumer_account)
        return agreement_id

    def consume(self, service_agreement_id, did, service_definition_id, consumer_account,
                destination):
        """
        Consume the asset data.

        Using the service endpoint defined in the ddo's service pointed to by service_definition_id.
        Consumer's permissions is checked implicitly by the secret-store during decryption
        of the contentUrls.
        The service endpoint is expected to also verify the consumer's permissions to consume this
        asset.
        This method downloads and saves the asset datafiles to disk.

        :param service_agreement_id: str
        :param did: DID, str
        :param service_definition_id: str
        :param consumer_account: Account address, str
        :param destination: str path
        :return: str path to saved files
        """
        ddo = self.resolve(did)
        return self._asset_consumer.download(
            service_agreement_id,
            service_definition_id,
            ddo,
            consumer_account,
            destination,
            BrizoProvider.get_brizo(),
            self._get_secret_store(consumer_account)
        )

    def validate(self, metadata):
        """
        Validate that the metadata is ok to be stored in aquarius.

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :return: bool
        """
        return self._get_aquarius(self._aquarius_url).validate_metadata(metadata)
