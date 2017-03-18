from collections import namedtuple

class Token:
    pass

class Modifiable(
        Token,
    ):
    pass

class Annotatable(
        Token,
    ):
    pass

class Photoable(
        Token,
    ):
    pass

class Taggable(
        Token,
    ):
    pass

class Placable(
        Token
    ):
    pass

class Concrete(
        Modifiable,
        Annotatable,
        Photoable,
        Taggable,
    ):
    pass

class Foodstuff(
        Concrete,
    ):
    pass

class Equipment(
        Concrete,
    ):
    pass

class Container(
        Equipment,
    ):
    pass

class Implement(
        Equipment,
    ):
    pass

class Action(
        Token,
    ):
    pass

class Meta(
        Token,
    ):
    pass

class Partition(
        Meta,
    ):
    pass

class Measurement(
        Meta,
    ):
    pass

class Quantity(
        Partition,
        Measurement,
    ):
    pass

class Partitionable(
        Token,
    ):
    pass

class Measurable(
        Token,
    ):
    pass

class Passthru(
        Token,
    ):
    pass

class ControlFlow(
        Token,
    ):
    pass

# Tokens

class Ingredient(
        Foodstuff,
        Measurable,
        Placable,
    ):
    pass

class Tool(
        Equipment,
        Placable,
    ):
    pass

class Vessel(
        Container,
        Placable,
    ):
    pass

class Appliance(
        Container,
        Placable,
    ):
    pass

class Environment(
        Equipment,
    ):
    pass

class Verb(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Add(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class AddTo(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Move(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class MoveFrom(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Divide(
        Action,
        Photoable,
        Annotatable,
        Partitionable,
    ):
    pass

class Reserve(
        Action,
        Photoable,
        Annotatable,
        Partitionable,
    ):
    pass

class Configure(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Meld(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Place(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Remove(
        Action,
        Modifiable,
        Annotatable,
        Photoable,
    ):
    pass

class Bind(
        Action,
        Passthru,
    ):
    pass

class Discard(
        Action,
        Photoable,
    ):
    pass

class Empty(
        Action,
        Photoable,
    ):
    pass

class Simultaneous(
        Action,
        Passthru,
    ):
    pass

class Condition(
        Meta,
    ):
    pass

class Modifier(
        Meta,
    ):
    pass

class Annotation(
        Meta,
    ):
    pass

class Photo(
        Meta,
    ):
    pass

class LookupSet(
        Meta,
    ):
    pass

class Fraction(
        Partition,
    ):
    pass

class Pseudoselect(
        Partition,
    ):
    pass

class QuantityMass(
        Quantity,
    ):
    pass

class QuantityVolume(
        Quantity,
    ):
    pass

class QuantityCount(
        Quantity,
    ):
    pass

class Time(
        Meta,
    ):
    pass

class VariantTag(
        Meta,
    ):
    pass

class Group(
        ControlFlow,
    ):
    pass

class Or(
        ControlFlow,
    ):
    pass

class Repeat(
        ControlFlow,
    ):
    pass

class LookupGet(
        ControlFlow,
    ):
    pass
