from squid_py.keeper.templates.template_manager import TemplateStoreManager

template_store_manager = TemplateStoreManager('TemplateStoreManager')


def test_template():
    assert template_store_manager.get_num_templates() == 1
