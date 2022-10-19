import pytest

from model_class import model_class, node


def test_that_setting_exclude_excludes_autorepr_for_property():

    @model_class
    class M:

        @property
        @node(repr=False)
        def x(self):
            return "this should be excluded"

        @property
        @node
        def y(self):
            return "this should be included"

    assert repr(M()) == "M(y='this should be included')"


def test_exclude_for_equality():

    @model_class
    class T:
        def __init__(self, x):
            self._x = x

        @property
        @node(eq=False)
        def x(self):
            return self._x

    assert T(2) == T(3)


def test_exclude_for_equality_with_inheritance():

    @model_class
    class T:
        def __init__(self, x):
            self.__x = x

        @property
        @node(eq=False)
        def x(self):
            return self.__x

    @model_class
    class TT(T):

        def __init__(self, x, y):
            super().__init__(x)
            self._y = y

        @property
        @node(eq=False)
        def y(self):
            return self._y

    assert TT(2, 3) == TT(5, 6)


def test_model_class_without_args():

    @model_class
    class M:

        @property
        @node
        def x(self):
            return "this should be included"

        @property
        @node
        def y(self):
            return "this should be included"

    assert repr(M()) == "M(x='this should be included', y='this should be included')"


@model_class
class C1:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    @node
    def x(self):
        return self._x

    @property
    @node
    def y(self):
        return self._y


@model_class
class C2:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    @node
    def x(self):
        return self._x

    @property
    @node
    def y(self):
        return self._y


@pytest.mark.parametrize("a, b, expect_eq", [
    (C1(1, 1), C2("1", "1"), False),
    (C1(1, 2), C1(1, 2), True),
    (C1(1, 2), C1(3, 4), False),
])
def test_eq_hash_contract(a, b, expect_eq):
    assert (a == b) == expect_eq
    assert (hash(a) == hash(b)) == expect_eq


def test_auto_represent_object():

    @model_class
    class RepresentMe:
        @property
        @node
        def x(self):
            return "xx"

        @property
        @node
        def y(self):
            return "yy"

        @property
        @node
        def z(self):
            return "zz"

    assert repr(RepresentMe()) == "RepresentMe(x='xx', y='yy', z='zz')"


def test_that_with_inheritance_only_topmost_representation_comes_through():

    @model_class
    class Base:
        @property
        @node
        def x(self):
            return "xx"

    @model_class
    class RepresentMe(Base):
        @property
        @node
        def y(self):
            return "yy"

    assert repr(RepresentMe()) == "RepresentMe(x='xx', y='yy')"


def test_that_representation_is_just_class_name_if_represent_attrs_is_not_specified():

    @model_class
    class RepresentMe:
        def __init__(self):
            self.x = "xx"
            self.y = "yy"
            self.z = "zz"

    assert repr(RepresentMe()) == "RepresentMe()"


def test_representation_does_not_stack_overflow():

    @model_class
    class RepresentMe:
        @property
        @node
        def x(self):
            return self

    assert repr(RepresentMe()) == "RepresentMe(x=...)"


def test_auto_eq_simple():

    @model_class
    class A:
        def __init__(self, value):
            self.value = value

        @property
        @node
        def a(self):
            return self.value

    assert A(1) == A(1)
    assert A(1) != A(2)


def test_auto_eq_multiple_properties():

    @model_class
    class A:
        def __init__(self, a, b, c):
            self._a = a
            self._b = b
            self._c = c

        @property
        @node
        def a(self):
            return self._a

        @property
        @node
        def b(self):
            return self._b

        @property
        @node
        def c(self):
            return self._c

    assert A(1, 2, 3) == A(1, 2, 3)
    assert A(1, 2, 3) != A(3, 2, 1)
    assert A(1, 2, 3) != A(1, 3, 2)
    assert A(1, 2, 3) != A(2, 1, 3)
    assert A(1, 2, 3) != A(2, 3, 1)


def test_auto_eq_ignore():

    @model_class
    class A:
        def __init__(self, a, b):
            self._a = a
            self._b = b

        @property
        @node
        def a(self):
            return self._a

        @property
        @node(eq=False, repr=False)
        def b(self):
            return self._b

    assert A(1, 2) == A(1, 2)
    assert A(1, 2) == A(1, 3)
    assert A(1, 2) != A(3, 2)


def test_that_auto_eq_can_deal_with_inheritance():

    @model_class
    class A:

        def __init__(self, a):
            self._a = a

        @property
        @node
        def a(self):
            return self._a

    @model_class
    class B(A):

        def __init__(self, a, b):
            super().__init__(a)
            self._b = b

        @property
        @node
        def b(self):
            return self._b

    assert B(1, 2) == B(1, 2)
    assert B(2, 1) != B(1, 2)


@model_class
class T:

    def __init__(self, a=None, b=None, c=None):
        self._a = a
        self._b = b
        self._c = c

    @property
    @node
    def a(self):
        return self._a

    @property
    @node
    def b(self):
        return self._b

    @property
    @node
    def c(self):
        return self._c


@model_class
class TT:
    def __init__(self, ts):
        self._ts = ts

    @property
    @node
    def ts(self):
        return self._ts


t = T()


@pytest.mark.parametrize("a, b, expected", [

    (T(1, 2, 3), T(1, 2, 3), True),
    (T(), T(), True),
    (T(1), T(1), True),
    (T(1, 2, 3), T(3, 2, 1), False),
    (T(1, 2, 3), list(), False),
    (t, t, True),

    # cases with list comparison
    (TT([T(1, 2, 3), T(3, 2, 1)]), TT([T(1, 2, 3), T(3, 2, 1)]), True),
    (TT([T(1, 2, 3), T(3, 2, 1)]), TT([T(3, 2, 1), T(1, 2, 3)]), False),
    (TT([T(1, 2, 3), T(3, 2, 1)]), TT([T(1, 2, 3)]), False),
    (TT([T(1, 2, 3), T(3, 2, 1)]), TT([T(1, 2, 3), T(1, 1, 1)]), False),
    (TT([T(1, 2, 3), T(3, 2, 1)]), TT([]), False),
    (TT([]), TT([]), True)
])
def test_is_object_equal(a, b, expected):
    assert (a == b) == expected


def test_child_properties():

    @model_class
    class Foo:
        @property
        @node
        def a(self): ...
        @property
        @node
        def b(self): ...
        @property
        @node
        def c(self): ...

    assert Foo().child_properties == ("a", "b", "c")


def test_inherited_child_properties():

    @model_class
    class Foo:
        @property
        @node
        def a(self): ...
        @property
        @node
        def b(self): ...
        @property
        @node
        def c(self): ...

    @model_class
    class Bar(Foo): ...

    assert Bar().child_properties == ("a", "b", "c")


def test_ignored_non_node_property():
    @model_class
    class Foo:
        x = 0
        @property
        def foo(self):
            # a function that never returns the same value twice in a row
            # guaranteed to be unequal for subsequent call
            # the expectation is that it is ignored for equality because it is not a node
            Foo.x += 1
            return Foo.x

    a = Foo()
    b = Foo()
    assert a == b
    assert hash(a) == hash(b)
    assert str(a) == str(b) == "Foo()"
    assert repr(a) == repr(b) == "Foo()"
    assert a.child_properties == b.child_properties == ()
