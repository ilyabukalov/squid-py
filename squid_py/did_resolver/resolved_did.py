from squid_py.did_resolver.resolver_value_type import ResolverValueType


class ResolvedDID:
    """Class that handles the resolved DID information"""

    def __init__(self):
        """init the object with an empty set of hops"""
        self._items = []
        self._value = None

    def add_data(self, data, value):
        """
        Add a resolved event data item to the list of resolved items
        as this could be the last item in the chain.

        :param data: dictionary of the DIDRegistry event data
        :param value: formated value depending on the data['value_type'] string, bytes32

        """
        self._items.append(data)
        self._value = value

    @property
    def did_bytes(self):
        """return the resolved did in bytes"""
        if self._items:
            return self._items[-1]['did_bytes']
        return None

    @property
    def owner(self):
        """return the resolved owner address"""
        if self._items:
            return self._items[-1]['owner']
        return None

    @property
    def key(self):
        """return the resolved key"""
        if self._items:
            return self._items[-1]['key']
        return None

    @property
    def block_number(self):
        """return the resolved block number"""
        if self._items:
            return self._items[-1]['block_number']
        return None

    @property
    def value(self):
        """return the resolved value can be a URL/DDO(on chain)/DID(string)"""
        return self._value

    @property
    def value_type(self):
        """return the resolved value type"""
        if self._items:
            return self._items[-1]['value_type']
        return None

    @property
    def is_url(self):
        """return True if the resolved value is an URL"""
        return self._items and self._items[-1]['value_type'] == ResolverValueType.URL

    @property
    def url(self):
        """return the resolved URL"""
        if self.is_url:
            return self._value
        return None

    @property
    def items(self):
        """return the list of DIDRegistry items used to get to this resolved value
        the last item is the resolved item"""
        return self._items
