import typing as t
from reprlib import recursive_repr


def _represent_attribute(obj, attr):
    v = getattr(obj, attr, None)
    quote = "'" if type(v) is str else ""
    return f"{attr}={quote}{v}{quote}"


def _represent_object(obj, attrs=None):
    if attrs is None:
        attrs = [name for name in dir(obj) if not name.startswith("_")]
    return f"{obj.__class__.__name__}({', '.join([_represent_attribute(obj, a) for a in attrs])})"


def _compare_objects(self, other, *compare_attributes):

    if other is self:
        return True
    if not issubclass(other.__class__, self.__class__):
        return False

    for atr in compare_attributes:
        a = getattr(self, atr)
        b = getattr(other, atr)
        if a != b:
            return False

    return True


def _compute_hash(obj, attrs: t.Sequence[str]) -> int:
    data = []
    for attr in attrs:
        data.append(hash(getattr(obj, attr)))
    return hash(tuple(data))


def model_class(_maybe_wrapped=None):
    """
    Allow model class decorators to become effective (node, virtual_node, value_node).
    Model class has auto generated __hash__, __repr__, __str__ and __eq__ methods and
    child_properties property
    """

    def wrap(cls):

        def __eq__(self, other):
            return _compare_objects(self, other, *eq_properties)

        def __hash__(self):
            return _compute_hash(self, eq_properties)

        @recursive_repr(fillvalue="...")
        def __repr__(self):
            return _represent_object(self, repr_properties)

        property_names = [p for p in dir(cls) if isinstance(getattr(cls, p), property)]
        eq_properties = [
            name for name in property_names
            if getattr(getattr(cls, name).fget, "eq_able", False)
        ]
        repr_properties = [
            name for name in property_names
            if getattr(getattr(cls, name).fget, "representable", False)
        ]
        child_properties = tuple(
            name for name in property_names
            if getattr(getattr(cls, name).fget, "walkable", False)
        )

        setattr(cls, "__eq__", __eq__)
        setattr(cls, "__hash__", __hash__)
        setattr(cls, "__repr__", __repr__)
        setattr(cls, "__str__", __repr__)
        setattr(cls, "child_properties", property(lambda self: child_properties))
        return cls

    if _maybe_wrapped:
        return wrap(_maybe_wrapped)

    return wrap


def node(wrapped=False, *, walk: bool = True, eq: bool = True, repr: bool = True):
    if wrapped:
        wrapped.walkable = walk
        wrapped.representable = repr
        wrapped.eq_able = eq
        return wrapped

    def decorator(fn):
        fn.walkable = walk
        fn.representable = repr
        fn.eq_able = eq
        return fn

    return decorator


def virtual_node(fn):
    """
    not walkable, not eq-able but representable
    """
    fn.walkable = False
    fn.representable = True
    fn.eq_able = False
    return fn


def value_node(fn):
    """
    not walkable but eq-able and representable
    """
    fn.walkable = False
    fn.representable = True
    fn.eq_able = True
    return fn
