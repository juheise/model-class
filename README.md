# Model Class Decorator Toolkit

These are some decorators to make life easier for property-based model classes.

## Installation

```
pip install model-class
```

## Concept

A model class is similar to a dataclass, with the difference that it uses *nodes* instead of public fields. A node is an augmented property, that can be marked as *walkable*, *EQ-able* and *representable*. When applied to a class, the model class decorator will find node-properties and automatically generate ´__eq__´, ´__hash__´, ´__str__´ and ´__repr__´ methods, as required. This allows fine grained configuration of which properties are included in comparing and which ones are included in string representations.

The use of properties, as opposed to public fields, allows more control about what actions can be performed during property access. By marking properties with a decorator, the code shows clearly what's going on without any invisible magic.

## Examples

```python
from model_class import model_class, node

@model_class
class Foo:
    
    def __init__(self, foo):
        self.foo = foo
    
    @property
    @node  # node decorator ensures the method is included in __eq__ and __repr__
    def foo(self):
        return self._foo

    @foo.setter
    def foo(self, foo):
        if foo is None:
            raise ValueError("foo may not be None")
        self._foo = foo
```