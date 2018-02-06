from collections import defaultdict


class LayeredAyeAye(object):
    """
    An interface-compatible implementation of AyeAye, which adheres to immutable principles, and thus stores
    updates as 'layers'. Internal representation is always in terms of Python POD types, and only converted
    to a LayeredAyeAye when returned from an accessor method. In that respect, LayeredAyeAye acts as a proxy
    which provides convenient property or attribute style lookup into the layered dictionaries.

    Note that access to attributes is against a recursively merged representation of the layers (which is not
    the case with AyeAye), where top layers take precedence over lower layers (in the case that the same key
    exists in multiple layers). However, this will only work where all layers which supply a particular key
    are in agreement on the type of the associated value, and this is enforced as a constraint so far as
    a dict value must be a dict in all layers (ValueError is raised).

        layer_1 = {'a': {'b': 1}}
        layer_2 = {'a': 2}  # 2 will override {'b': 1} from layer_1 entirely, as the types differ

        layer_1 = {'a': {'b': 1}}
        layer_2 = {'a': {'b': 2}}  # ok

        layer_1 = {'a': {'b': 1}}
        layer_2 = {'a': {'c': 2}}  # also ok
    """

    @classmethod
    def normalise_value(cls, v):
        return cls(v) if isinstance(v, (cls, dict)) else v

    def __init__(self, data=None):
        self._layers = []
        self._flat = None
        if data:
            self.update(data)

    def __unicode__(self):
        d = u', '.join([u"{}:{}".format(k, v) for k, v in self.flattened.iteritems()])
        return u'<LayeredAyeAye {}>'.format(d)

    def __str__(self):
        return self.__unicode__().encode("ascii", "replace")

    def keys(self):
        return (k for k in self.flattened.iterkeys())

    def values(self):
        return (self.normalise_value(v) for v in self.flattened.itervalues())

    def items(self):
        return ((k, self.normalise_value(v)) for k, v in self.flattened.items())

    @property
    def flattened(self):
        def flatten():
            result = defaultdict(dict)
            for layer in self._layers:
                for k, v in layer.items():
                    if isinstance(v, (dict, set)):
                        result[k].update(v.items())
                    # Could choose to extend dictionary types here, but the requirement is unclear
                    else:
                        result[k] = v

            return dict(result)

        if not self._flat:
            self._flat = flatten()
        return self._flat

    def __contains__(self, key):
        return any([key in layer for layer in self._layers])

    def as_dict(self):
        return self.flattened

    def layer(self, i):
        return self.__class__(self._layers[i])

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("{} instance has no attribute '{}'".format(self.__class__.__name__, attr))

    def __getitem__(self, key):
        item = self.flattened[key]

        if isinstance(item, list):
            return [self.normalise_value(s) if isinstance(s, (list, dict)) else s for s in item]
        else:
            return self.normalise_value(item)

    def update(self, new_layer):
        def validate(layer, baseline):
            # For each key in the new layer, check the value is type-consistent with previous layers. Recursively.
            for k, v in layer.items():
                if k in baseline.flattened:
                    types = (type(baseline.flattened[k]), type(v))
                    # TODO: review this type compatibility check. We mainly just want to check dict vs non-dict
                    if dict in types and types[0] != types[1]:
                        raise ValueError("Value of '{}' in new layer is inconsistent type".format(k))
                    if isinstance(v, (self.__class__, dict)):
                        validate(v, baseline[k])
            return layer
        self._layers.append(validate(new_layer, self))
        self._flat = None

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state