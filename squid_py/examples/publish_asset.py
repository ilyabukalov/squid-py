

def publish_asset():
    template = get_registered_access_service_template(ocean_instance)
    config = ocean_instance.config
    purchase_endpoint = Brizo.get_purchase_endpoint(config)
    service_endpoint = Brizo.get_service_endpoint(config)
    ddo = ocean_instance.register_asset(
        Metadata.get_example(), ocean_instance.main_account,
        [ServiceDescriptor.access_service_descriptor(7, purchase_endpoint, service_endpoint, 360,
                                                     template.template_id)]
    )
