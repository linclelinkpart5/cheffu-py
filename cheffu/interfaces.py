import collections
import types
import enum
import typing as typ
import collections.abc as abc

import modgrammar as mg
import voluptuous as vp
import voluptuous.humanize as vph

import cheffu.grammars as cgrm
import cheffu.argument_schema as asc
import cheffu.parallel as par


class Priority(enum.Enum):
    GRAPH_GEN = 0
    STACK_GEN = 1


class Pipeline(typ.NamedTuple):
    inputs: typ.Sequence[typ.Type['Token']] = ()
    outputs: typ.Sequence[typ.Type['Token']] = ()


class Token:
    keyword: str = None
    arg_grammar: mg.Grammar = None
    arg_vp_schema: vp.Schema = None
    sigil: typ.Optional[str] = None
    priority: Priority = Priority.STACK_GEN
    pipelines: typ.Sequence[Pipeline] = ()

    def __init__(self):
        self.data = None

    @classmethod
    def get_definable_tokens(cls: typ.Type):
        unique_seen = set()

        def spelunk(c):
            for subclass in c.__subclasses__():
                yield from spelunk(subclass)
                if subclass.keyword:
                    if subclass not in unique_seen:
                        yield subclass
                        unique_seen.add(subclass)

        yield from spelunk(cls)

    def process_stack(self, stack: typ.List['Token']):
        raise NotImplemented()

    def process_graph(self, nodule_edge_map: par.NoduleEdgeMap, current_nodule: par.Nodule):
        raise NotImplemented()


class Modifiable(Token,):
    def __init__(self):
        super().__init__()
        self._modis = collections.OrderedDict()

    def add_modifier(self, modi):
        self._modis[modi] = None

    def get_modifiers(self):
        return tuple(self._modis.keys())


class Annotatable(Token,):
    def __init__(self):
        super().__init__()
        self._annos = collections.OrderedDict()

    def add_annotation(self, anno):
        self._annos[anno] = None

    def get_annotations(self):
        return tuple(self._annos.keys())


class Photoable(Token,):
    def __init__(self):
        super().__init__()
        self._photos = collections.OrderedDict()

    def add_photo(self, photo):
        self._photos[photo] = None

    def get_photos(self):
        return tuple(self._photos.keys())


class Taggable(Token,):
    def __init__(self):
        super().__init__()
        self._tags = collections.OrderedDict()

    def add_tag(self, tag):
        self._tags[tag] = None

    def get_tags(self):
        return tuple(self._tags.keys())


# TODO: Not all Concretes should be Modifiable/Annotatable (e.g. Systems)
class Concrete(Modifiable, Annotatable, Photoable, Taggable,):
    def __init__(self):
        super().__init__()


class Placable(Concrete,):
    def __init__(self):
        super().__init__()


class Foodstuff(Concrete,):
    def __init__(self):
        super().__init__()


class Equipment(Concrete,):
    def __init__(self):
        super().__init__()


class Container(Equipment,):
    def __init__(self):
        super().__init__()


class Implement(Equipment,):
    def __init__(self):
        super().__init__()


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


class Action(Token,):
    def __init__(self):
        super().__init__()


class Meta(Token,):
    def __init__(self):
        super().__init__()


class Partition(Meta,):
    def __init__(self):
        super().__init__()


class Measurement(Meta,):
    def __init__(self):
        super().__init__()


class Quantity(Partition, Measurement,):
    def __init__(self):
        super().__init__()


class Partitionable(Token,):
    def __init__(self):
        super().__init__()


class Measurable(Token,):
    def __init__(self):
        super().__init__()


class Passthru(Token,):
    def __init__(self):
        super().__init__()


class ControlFlow(Token,):
    def __init__(self):
        super().__init__()

# Tokens ###############################################################################################################


class Ingredient(Foodstuff, Measurable, Placable,):
    keyword = 'INGR'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Tool(Equipment, Placable,):
    keyword = 'TOOL'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Vessel(Container, Placable,):
    keyword = 'VESS'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Appliance(Container, Placable,):
    keyword = 'APPL'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Environment(Equipment,):
    keyword = 'ENVR'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Verb(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'VERB'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Add(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'ADDI'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE

    def __init__(self):
        super().__init__()


class AddTo(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'ADDT'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE

    def __init__(self):
        super().__init__()


class Move(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'MOVE'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE

    def __init__(self):
        super().__init__()


class MoveFrom(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'MOVF'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE

    def __init__(self):
        super().__init__()


class Divide(Action, Photoable, Annotatable, Partitionable,):
    keyword = 'DIVI'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Reserve(Action, Photoable, Annotatable, Partitionable,):
    keyword = 'RESV'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Configure(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'CONF'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Meld(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'MELD'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Place(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'PLAC'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Remove(Action, Modifiable, Annotatable, Photoable,):
    keyword = 'REMO'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Bind(Action, Passthru,):
    keyword = 'BIND'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Discard(Action, Photoable,):
    keyword = 'DISC'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Empty(Action, Photoable,):
    keyword = 'EMPT'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Simultaneous(Action, Passthru,):
    keyword = 'SIMU'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Condition(Meta,):
    keyword = 'SIMU'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Modifier(Meta,):
    keyword = 'MODI'
    arg_grammar = cgrm.String
    sigil = ','
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Annotation(Meta,):
    keyword = 'ANNO'
    arg_grammar = cgrm.String
    sigil = ';'
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Photo(Meta,):
    keyword = 'PHOT'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class LookupSet(Meta,):
    keyword = 'LSET'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class LookupGet(ControlFlow,):
    keyword = 'LGET'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class Fraction(Partition,):
    keyword = 'FRAC'
    arg_grammar = cgrm.Partition
    arg_vp_schema = asc.ArgumentSchemas.FRACTION

    def __init__(self):
        super().__init__()


class Pseudoselect(Partition,):
    keyword = 'PSEU'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING

    def __init__(self):
        super().__init__()


class QuantityMass(Quantity,):
    keyword = 'QMAS'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_MASS

    def __init__(self):
        super().__init__()


class QuantityVolume(Quantity,):
    keyword = 'QVOL'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_VOLUME

    def __init__(self):
        super().__init__()


class QuantityCount(Quantity,):
    keyword = 'QCNT'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_COUNT

    def __init__(self):
        super().__init__()


class Time(Meta,):
    keyword = 'TIME'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_TIME

    def __init__(self):
        super().__init__()


class VariantTag(Meta,):
    keyword = 'VTAG'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.VARIANT_TAG_SET

    def __init__(self):
        super().__init__()


class Group(ControlFlow,):
    keyword = 'GRUP'
    arg_grammar = None

    # This method emulates a callable voluptuous Schema.
    @staticmethod
    def arg_vp_schema(data):
        other_schemas = tuple(t.vp_schema for t in Token.get_definable_tokens())
        schema = vp.Schema([vp.Any(*other_schemas)])
        return schema(data)

    # arg_vp_schema = __arg_vp_schema

    def __init__(self):
        super().__init__()


class Or(ControlFlow,):
    keyword = 'OROP'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE

    def __init__(self):
        super().__init__()


class Repeat(ControlFlow,):
    # How to handle nested Repeat and Group/VariantTag instances, and vice-versa?
    keyword = 'REPT'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NON_NEG_INT

    def __init__(self):
        super().__init__()


KeywordToType = {
    t.keyword: t for t in Token.get_definable_tokens()
}


def get_from_td(token_dict: typ.Mapping[str, typ.Any]) -> typ.Tuple[str, typ.Any]:
    assert isinstance(token_dict, abc.Mapping)
    assert len(token_dict) == 1
    found_keyword, found_argument = next(iter(token_dict.items()))
    return found_keyword, found_argument


def process(token_dicts: typ.Sequence[typ.Mapping[str, typ.Any]]):
    # Process token dicts into token instances
    token_insts = []
    for token_dict in token_dicts:
        # Look up the keyword and argument from the TD
        keyword, argument = get_from_td(token_dict)

        # Use keyword to look up interface
        interface: typ.Type[Token] = KeywordToType[keyword]

        # Create an instance of the specified token
        token_inst = interface()

        # Set argument in token instance
        token_inst.process_token_argument(argument)

        token_insts.append(token_inst)

    # return token_insts

    # In priority order, process tokens in multiple passes
    for priority_choice in Priority.__members__.values():
        new_token_insts = []
        for token_inst in token_insts:
            if token_inst.priority == priority_choice:
                # Process
                pass
