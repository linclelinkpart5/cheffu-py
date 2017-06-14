import typing as typ

import types
import abc


TokenSpecPred = typ.Callable[[typ.Type], bool]


class TokenSpec(metaclass=abc.ABCMeta):
    """Base token spec/interface."""

    @classmethod
    def yield_subclasses(cls, *, include_self=False):
        """Yields all subclasses of this class, optionally including itself."""
        unique_seen = set()

        def spelunk(c: typ.Type):
            for subclass in c.__subclasses__():
                yield from spelunk(subclass)

                if subclass not in unique_seen:
                    yield subclass
                    unique_seen.add(subclass)

        yield from spelunk(cls)

        if include_self and cls not in unique_seen:
            yield cls
            unique_seen.add(cls)

    @classmethod
    def yield_leaf_subclasses(cls, *, include_self=False):
        yield from (x for x in cls.yield_subclasses(include_self=include_self) if not x.__subclasses__())


class Modifiable(TokenSpec):
    """Able to have modifiers attached."""
    pass


class Annotatable(TokenSpec):
    """Able to have annotations attached."""
    pass


class Photoable(TokenSpec):
    """Able to have photos attached."""
    pass


class Taggable(TokenSpec):
    """Able to have lookup tags assigned."""
    pass


class Concrete(Photoable, Taggable):
    """A physical object, able to be represented directly on the stack."""
    pass


class Placable(Concrete):
    """Able to be placed in an environment."""
    pass


class Configurable(Concrete):
    """Able to be configured during use, such as a machine setting. This should be a quick configuration."""
    pass


class Foodstuff(Concrete):
    """A concrete item composed of food or edibles."""
    pass


class System(Concrete):
    """A bundle consisting of a vessel and a foodstuff."""
    pass


class Mixture(Foodstuff):
    pass


class Equipment(Concrete):
    pass


class Vessel(Equipment):
    pass


class Implement(Equipment):
    pass


class Action(Photoable):
    pass


class Meta(TokenSpec):
    pass


class Partition(Meta):
    pass


class Measurement(Meta):
    pass


class Quantity(Partition, Measurement):
    pass


class Measurable(TokenSpec):
    pass


class Partitionable(Measurable):
    pass


class Passthru(TokenSpec):
    pass


class Process(TokenSpec):
    pass


class Timeable(TokenSpec):
    pass


class ControlFlow(TokenSpec):
    pass


class Ingredient(Modifiable, Annotatable, Foodstuff, Placable, Measurable):
    pass


class Tool(Modifiable, Annotatable, Implement, Placable):
    pass


class Container(Modifiable, Annotatable, Vessel, Placable):
    pass


class Appliance(Modifiable, Annotatable, Vessel, Implement, Placable, Configurable):
    pass


class Environment(Modifiable, Annotatable, Equipment, Configurable):
    pass


class Verb(Action, Modifiable, Annotatable):
    pass


class Add(Action, Modifiable, Annotatable):
    pass


class AddTo(Action, Modifiable, Annotatable):
    pass


class Move(Action, Modifiable, Annotatable):
    pass


class MoveFrom(Action, Modifiable, Annotatable):
    pass


class Divide(Action, Annotatable, Partitionable):
    pass


class Reserve(Action, Annotatable, Partitionable):
    pass


class Configure(Action, Modifiable, Annotatable):
    pass


class Meld(Action, Modifiable, Annotatable):
    pass


class Place(Action, Modifiable, Annotatable):
    pass


class Remove(Action, Modifiable, Annotatable):
    pass


class Discard(Action, Photoable):
    pass


class Empty(Action, Photoable):
    pass


class Simultaneous(Meta, Passthru):
    pass


class With(Meta, Passthru):
    pass


class Using(Meta, Passthru):
    pass


class Precondition(Meta):
    pass


class Modifier(Meta):
    pass


class Annotation(Meta):
    pass


class Photo(Meta):
    pass


class LookupSet(Meta):
    pass


class LookupGet(ControlFlow):
    pass


class Fraction(Partition):
    pass


class Pseudoselect(Partition):
    pass


class QuantityMass(Quantity):
    pass


class QuantityVolume(Quantity):
    pass


class QuantityCount(Quantity):
    pass


class Time(Meta):
    pass


class Until(Meta):
    pass


def Haz():
    registry = {}

    def get_haz_name(cls):
        return 'Has{}'.format(cls.__name__)

    def create_or_get_entry(cls):
        cls_haz_name = get_haz_name(cls)

        if cls_haz_name not in registry:
            parent_haz_clses = tuple(create_or_get_entry(parent_cls) for parent_cls in cls.__bases__)
            registry[cls_haz_name] = types.new_class(cls_haz_name, bases=parent_haz_clses)

        return registry[cls_haz_name]

    return lambda cls: create_or_get_entry(cls)

Haz = Haz()
