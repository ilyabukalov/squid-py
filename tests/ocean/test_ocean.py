"""Test ocean class."""
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
#     Copyright [yyyy] [name of copyright owner]
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

import logging

import pytest
from web3 import Web3

from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.brizo.brizo import Brizo
from squid_py.ddo.ddo import DDO
from squid_py.ddo.metadata import Metadata
from squid_py.did import DID
from squid_py.exceptions import OceanDIDNotFound
from squid_py.keeper import Keeper
from tests.resources.helper_functions import get_resource_path, verify_signature, log_event
from tests.resources.mocks.brizo_mock import BrizoMock
from tests.resources.tiers import e2e_test


@e2e_test
def test_ocean_instance(publisher_ocean_instance):
    assert publisher_ocean_instance.tokens
    assert publisher_ocean_instance.agreements
    assert publisher_ocean_instance.assets
    assert publisher_ocean_instance.accounts
    assert publisher_ocean_instance.services


@e2e_test
def test_register_asset(publisher_ocean_instance):
    logging.debug("".format())
    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher = publisher_ocean_instance.main_account

    # ensure Ocean token balance
    if publisher_ocean_instance.accounts.balance(publisher).ocn == 0:
        publisher_ocean_instance.accounts.request_tokens(publisher, 200)

    # You will need some token to make this transfer!
    assert publisher_ocean_instance.accounts.balance(publisher).ocn > 0

    ##########################################################
    # Create an asset DDO with valid metadata
    ##########################################################
    asset = DDO(json_filename=sample_ddo_path)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    publisher_ocean_instance.assets.create(asset.metadata, publisher)


@e2e_test
def test_resolve_did(publisher_ocean_instance):
    # prep ddo
    metadata = Metadata.get_example()
    publisher = publisher_ocean_instance.main_account
    original_ddo = publisher_ocean_instance.assets.create(metadata, publisher)

    # happy path
    did = original_ddo.did
    ddo = publisher_ocean_instance.assets.resolve(did).as_dictionary()
    original = original_ddo.as_dictionary()
    assert ddo['publicKey'] == original['publicKey']
    assert ddo['authentication'] == original['authentication']
    assert ddo['service']
    assert original['service']
    assert ddo['service'][:-1] == original['service'][:-1]
    # assert ddo == original_ddo.as_dictionary(), 'Resolved ddo does not match original.'

    # Can't resolve unregistered asset
    unregistered_did = DID.did()
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(unregistered_did)

    # Raise error on bad did
    invalid_did = "did:op:0123456789"
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(invalid_did)


@e2e_test
def test_sign_agreement(publisher_ocean_instance, consumer_ocean_instance, registered_ddo):
    # point consumer_ocean_instance's brizo mock to the publisher's ocean instance
    Brizo.set_http_client(
        BrizoMock(publisher_ocean_instance, publisher_ocean_instance.main_account))

    consumer_ocn = consumer_ocean_instance
    consumer_acc = consumer_ocn.main_account
    keeper = Keeper.get_instance()

    pub_ocn = publisher_ocean_instance
    publisher_acc = pub_ocn.main_account

    service_definition_id = '1'
    did = registered_ddo.did
    asset_id = registered_ddo.asset_id
    ddo = consumer_ocn.assets.resolve(did)
    service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
    price = service_agreement.get_price()

    # Give consumer some tokens
    keeper.dispenser.request_tokens(price*2, consumer_acc)

    agreement_id, signature = consumer_ocean_instance.agreements.prepare(
        did, service_agreement.service_definition_id, consumer_acc)

    success = publisher_ocean_instance.agreements.create(
        did,
        service_agreement.service_definition_id,
        agreement_id,
        signature,
        consumer_acc.address,
        publisher_acc
    )
    assert success, 'createAgreement failed.'

    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        10,
        log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AgreementCreated '

    # Verify condition types (condition contracts)
    agreement_values = keeper.agreement_manager.get_agreement(agreement_id)
    assert agreement_values.did == asset_id, ''
    cond_types = keeper.escrow_access_secretstore_template.get_condition_types()
    for i, cond_id in enumerate(agreement_values.condition_ids):
        cond = keeper.condition_manager.get_condition(cond_id)
        assert cond.type_ref == cond_types[i]
        assert int(cond.state) == 1

    access_cond_id, lock_cond_id, escrow_cond_id = agreement_values.condition_ids
    # Fulfill lock_reward_condition
    starting_balance = keeper.token.get_token_balance(keeper.escrow_reward_condition.address)
    keeper.unlock_account(consumer_acc)
    keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_acc)
    keeper.unlock_account(consumer_acc)
    keeper.lock_reward_condition.fulfill(agreement_id, keeper.escrow_reward_condition.address,
                                         price, consumer_acc)
    assert keeper.token.get_token_balance(keeper.escrow_reward_condition.address) == (
            price + starting_balance), ''
    assert keeper.condition_manager.get_condition_state(lock_cond_id) == 2, ''
    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockRewardCondition.Fulfilled'

    # Fulfill access_secret_store_condition
    keeper.unlock_account(publisher_acc)
    keeper.access_secret_store_condition.fulfill(
        agreement_id, asset_id, consumer_acc.address, publisher_acc)
    assert keeper.condition_manager.get_condition_state(access_cond_id) == 2, ''
    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AccessSecretStoreCondition.Fulfilled'

    # Fulfill escrow_reward_condition
    keeper.unlock_account(publisher_acc)
    keeper.escrow_reward_condition.fulfill(
        agreement_id, price, publisher_acc.address,
        consumer_acc.address, lock_cond_id,
        access_cond_id, publisher_acc
    )
    assert keeper.condition_manager.get_condition_state(escrow_cond_id) == 2, ''
    event = keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.escrow_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for EscrowReward.Fulfilled'

    # path = consumer_ocean_instance.assets.consume(
    #     agreement_id, did, service_definition_id,
    #     consumer_acc, ConfigProvider.get_config().downloads_path
    # )
    # print('All good, files are here: %s' % path)


@e2e_test
def test_verify_signature(consumer_ocean_instance):
    """
    squid-py currently uses `web3.eth.sign()` to sign the service agreement hash. This signing
    method
    uses ethereum `eth_sign` on the ethereum client which automatically prepends the
    message with text defined in EIP-191 as version 'E': `b'\\x19Ethereum Signed Message:\\n'`
    concatenated with the number of bytes in the message.

    It is more convenient to sign a message using `web3.eth.sign()` because it only requires the
    account address
    whereas `web3.eth.account.signHash()` requires a private_key to sign the message.
    `web3.eth.account.signHash()` also does not prepend anything to the message before signing.
    Messages signed via Metamask in pleuston use the latter method and current fail to verify in
    squid-py/brizo.
    The signature verification fails because recoverHash is being used on a prepended message but
    the signature
    created by `web3.eth.account.signHash()` does not add a prefix before signing.
    """

    # Signature created from Metamask (same as using `web3.eth.account.signHash()`)
    address = '0x8248039e67801Ac0B9d0e38201E963194abdb540'
    hex_agr_hash = '0xc8ea6bf6f4f4e2bf26a645dd4a1be20f5151c74964026c36efc2149bfae5f924'
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    assert hex_agr_hash == '0x' + agreement_hash.hex()
    signature = (
        '0x200ce6aa55f0b4080c5f3a5dbe8385d2d196b0380cbdf388f79b6b004223c68a4f7972deb36417df8599155da2f903e43fe7e7eb40214db6bd6e55fd4c4fcf2a1c'
    )
    verify_signature(address, agreement_hash, signature, 1)

    # Signature created using `web3.eth.sign()` (squid-py, squid-js with no metamask)
    address = "0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e"
    hex_agr_hash = "0xeeaae0098b39fdf8fab6733152dd0ef54729ac486f9846450780c5cc9d44f5e8"
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    signature = (
        "0x44fa549d33f5993f73e96f91cad01d9b37830da78494e35bda32a280d1b864ac020a761e872633c8149a5b63b65a1143f9f5a3be35822a9e90e0187d4a1f9d101c"
    )
    assert hex_agr_hash == '0x' + agreement_hash.hex()
    verify_signature(address, agreement_hash, signature, 0)
