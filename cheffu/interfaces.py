from collections import namedtuple
from types import new_class
from inspect import getmro
from itertools import takewhile

class Token:
    pass

class Modifiable(Token,):
    pass

class Annotatable(Token,):
    pass

class Photoable(Token,):
    pass

class Taggable(Token,):
    pass

class Concrete(Modifiable, Annotatable, Photoable, Taggable,):
    pass

class Placable(Concrete,):
    pass

class Foodstuff(Concrete,):
    pass

class Equipment(Concrete,):
    pass

class Container(Equipment,):
    pass

class Implement(Equipment,):
    pass

# # An Ingredient is an Ingredient, not a HasIngredient!
# def make_has_tree(cls, curr_hp):
#     new_name = 'Has' + cls.__name__
#     nt = new_class(new_name, bases=curr_hp)
#
#     globals()[new_name] = nt
#
#     for subcls in cls.__subclasses__():
#         make_has_tree(subcls, (nt,))
#
#     del nt
#
# make_has_tree(Concrete, (Token,))

def Haz():
    registry = {}
    def get_haz_name(cls):
        return 'Has{}'.format(cls.__name__)

    def create_or_get_entry(cls):
        cls_haz_name = get_haz_name(cls)

        if cls_haz_name not in registry:
            parent_haz_clses = tuple(create_or_get_entry(parent_cls) for parent_cls in cls.__bases__)
            registry[cls_haz_name] = new_class(cls_haz_name, bases=parent_haz_clses)

        return registry[cls_haz_name]

    return lambda cls: create_or_get_entry(cls)

Haz = Haz()

class HasFoodstuff(Concrete,):
    pass

class HasContainer(Concrete,):
    pass

class Action(Token,):
    pass

class Meta(Token,):
    pass

class Partition(Meta,):
    pass

class Measurement(Meta,):
    pass

class Quantity(Partition, Measurement,):
    pass

class Partitionable(Token,):
    pass

class Measurable(Token,):
    pass

class Passthru(Token,):
    pass

class ControlFlow(Token,):
    pass

# Tokens

class Ingredient(Foodstuff, Measurable, Placable,):
    pass

class Tool(Equipment, Placable,):
    pass

class Vessel(Container, Placable,):
    pass

class Appliance(Container, Placable,):
    pass

class Environment(Equipment,):
    pass

class Verb(Action, Modifiable, Annotatable, Photoable,):
    pass

class Add(Action, Modifiable, Annotatable, Photoable,):
    pass

class AddTo(Action, Modifiable, Annotatable, Photoable,):
    pass

class Move(Action, Modifiable, Annotatable, Photoable,):
    pass

class MoveFrom(Action, Modifiable, Annotatable, Photoable,):
    pass

class Divide(Action, Photoable, Annotatable, Partitionable,):
    pass

class Reserve(Action, Photoable, Annotatable, Partitionable,):
    pass

class Configure(Action, Modifiable, Annotatable, Photoable,):
    pass

class Meld(Action, Modifiable, Annotatable, Photoable,):
    pass

class Place(Action, Modifiable, Annotatable, Photoable,):
    pass

class Remove(Action, Modifiable, Annotatable, Photoable,):
    pass

class Bind(Action, Passthru,):
    pass

class Discard(Action, Photoable,):
    pass

class Empty(Action, Photoable,):
    pass

class Simultaneous(Action, Passthru,):
    pass

class Condition(Meta,):
    pass

class Modifier(Meta,):
    pass

class Annotation(Meta,):
    pass

class Photo(Meta,):
    pass

class LookupSet(Meta,):
    pass

class Fraction(Partition,):
    pass

class Pseudoselect(Partition,):
    pass

class QuantityMass(Quantity,):
    pass

class QuantityVolume(Quantity,):
    pass

class QuantityCount(Quantity,):
    pass

class Time(Meta,):
    pass

class VariantTag(Meta,):
    pass

class Group(ControlFlow,):
    pass

class Or(ControlFlow,):
    pass

class Repeat(ControlFlow,):
    pass

class LookupGet(ControlFlow,):
    pass

# Internal Concretes

class System(HasFoodstuff, HasContainer,):
    pass

# from types import new_class

# def Haz():
#     registry = {}
#     def HazInner(cls):
#         cls_name = 'Has{}'.format(cls.__name__)
#         if cls_name not in registry:
#             registry[cls_name] = new_class(cls_name, bases=(Concrete,))
#         return registry[cls_name]
#     return HazInner
#
# Haz = Haz()

# class __Foodstuff(
#         Foodstuff,
#         Haz(Foodstuff)
#     ):
#     pass
#
# Foodstuff = __Foodstuff

# class __Container(
#         Container,
#         Haz(Container),
#     ):
#     pass
#
# Container = __Container
