from contextlib import contextmanager
from inspect import signature

from squid_py.keeper.web3_provider import Web3Provider


@contextmanager
def inject_dependencies(klass, *args, **kwargs):
    dependencies = kwargs.pop('dependencies', {})
    if 'dependencies' in signature(klass).parameters:
        kwargs['dependencies'] = dependencies

    to_restore = []

    def patch_provider(object, property, mock):
        to_restore.append((object, property, getattr(object, property)))
        setattr(object, property, mock)

    def maybe_patch_provider(object, property, name):
        if name in dependencies:
            patch_provider(object, property, dependencies[name])

    maybe_patch_provider(Web3Provider, '_web3', 'web3')
    try:
        yield klass(*args, **kwargs)
    finally:
        for (object, property, value) in to_restore:
            setattr(object, property, value)
