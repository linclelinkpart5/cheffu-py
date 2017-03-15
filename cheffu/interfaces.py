from collections import namedtuple

# Data Types

def assert_string(obj):
    assert isinstance(obj, str)

    return obj

def assert_partition(obj):
    assert isinstance(obj, dict)

    assert 'keep' in obj
    assert isinstance(obj['keep'], int)
    assert obj['keep'] > 0

    assert 'pass' in obj
    assert isinstance(obj['pass'], int)
    assert obj['pass'] > 0

    return obj

def assert_quantity(obj):
    assert isinstance(obj, dict)

    assert 'base' in obj
    assert isinstance(obj['base'], int)
    assert obj['base'] > 0

    obj['base_den'] = obj.get('base_den', 1)
    assert isinstance(obj['base_den'], int)
    assert obj['base_den'] > 0

    obj['range'] = obj.get('range', 0)
    assert isinstance(obj['range'], int)
    assert obj['range'] >= 0

    obj['range_den'] = obj.get('range_den', 1)
    assert isinstance(obj['range_den'], int)
    assert obj['range_den'] > 0

    obj['less_ok'] = obj.get('less_ok', True)
    assert isinstance(obj['less_ok'], bool)

    obj['more_ok'] = obj.get('more_ok', True)
    assert isinstance(obj['more_ok'], bool)

    return obj

# Interfaces

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

# Concrete Tokens

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
        Equipment,
        #Has_Volume,
        #Has_Dimension,
        #Contains_Foodstuff,
        Placable,
    ):
    pass

class Appliance(
        Tool,
        Vessel,
        Placable,
    ):
    pass

class Environment(
        Equipment,
        #Contains_Placable,
    ):
    pass

# Operational Tokens

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

class Separate(
        Action,
        Photoable,
        Annotatable,
        Partitionable,
    ):
    pass

# Meta Tokens

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

class TagSet(
        Meta,
    ):
    pass

class Modifier(
        Meta,
    ):
    pass

class Pseudoselect(
        Partition,
    ):
    pass

class Fraction(
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

#### 'INGR',
#### 'TOOL',
#### 'VESS',
#### 'APPL',
#### 'ENVR',
#### 'DIVI',
#### 'SEPR',
# 'CONF',
# 'MELD',
# 'PLAC',
#### 'TRNS',
# 'BIND',
#### 'VERB',
#### 'ADDI',
# 'DISC',
# 'EMPT',
# 'PREC',
#### 'MODI',
#### 'ANNO',
#### 'PHOT',
#### 'TSET',
# 'TGET',
#### 'QMAS',
#### 'QVOL',
#### 'QCNT',