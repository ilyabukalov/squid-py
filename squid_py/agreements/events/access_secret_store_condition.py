from squid_py import ConfigProvider
from squid_py.brizo import BrizoProvider
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.keeper import Keeper
from squid_py.secret_store import SecretStoreProvider


def fulfill_escrow_reward_condition(
    event, agreement_id, did,
    service_agreement, service_definition_id, price,
    consumer_address, publisher_account):
    pass


def refund_reward(*args):
    pass


def consume_asset(
    agreement_id, did, service_agreement, service_definition_id,
    encrypted_files, publisher_address, consumer_account,
    consume_callback
):
    if consume_callback:
        config = ConfigProvider.get_config()
        secret_store = SecretStoreProvider.get_secret_store(
            config.secret_store_url, config.parity_url, consumer_account
        )
        brizo = BrizoProvider.get_brizo()

        consume_callback(
            agreement_id,
            service_agreement.service_definition_id,
            DIDResolver(Keeper.get_instance().did_registry).resolve(did),
            consumer_account,
            ConfigProvider.get_config().downloads_path,
            brizo,
            secret_store
        )

    #     logger.info('Done consuming asset.')
    #
    # else:
    #     logger.info('Handling consume asset but the consume callback is not set. The user '
    #                 'can trigger consume asset directly using the agreementId and assetId.')


fulfillEscrowRewardCondition = fulfill_escrow_reward_condition
