import typing as typ

import modgrammar as mg
import types
import abc

import cheffu.argument_schema as asc
import cheffu.grammars as cgrm


# class Priority(enum.Enum):
#     GRAPH_GEN = 0
#     STACK_GEN = 1

TokenSpecSequence = typ.Sequence['TokenSpec']

# Would ideally be Callable[[TokenSpec, ...], TokenSpec], but not legal.
PipelineMethod = typ.Callable[..., 'TokenSpec']


class Pipeline(typ.NamedTuple):
    input_types: TokenSpecSequence
    output_types: TokenSpecSequence
    # method: PipelineMethod

PipelineSequence = typ.Sequence[Pipeline]


def reverse_input_order(pipeline_sequence: PipelineSequence):
    def helper():
        for pipeline in pipeline_sequence:
            yield pipeline._replace(input_types=tuple(reversed(pipeline.input_types)))

    return tuple(helper())


class SelfRef:
    """Sentinel class for use in pipeline definitions, for cases when a class outputs itself."""
    pass


class Ref(typ.NamedTuple):
    """Sentinel for use in pipeline definitions. This allows for listing classes that have not yet been defined."""
    target: str


class TokenSpec(metaclass=abc.ABCMeta):
    """Base token spec/interface."""
    pass
    # keyword: ctpt.TokenKeyword = None
    # arg_grammar: mg.Grammar = None
    # pipelines: PipelineSequence = ()
    # consolidate: bool = False
    #
    # @classmethod
    # def yield_defined_token_specs(cls: typ.Type):
    #     """Yields all subclasses of this class (excluding itself) that are defined. Classes that have a non-null
    #     keyword are considered 'defined'.
    #     """
    #     unique_seen = set()
    #
    #     def spelunk(c):
    #         for subclass in c.__subclasses__():
    #             yield from spelunk(subclass)
    #             if subclass.keyword is not None:
    #                 if subclass not in unique_seen:
    #                     yield subclass
    #                     unique_seen.add(subclass)
    #
    #     yield from spelunk(cls)
    #
    # @classmethod
    # def parse_arg(cls, *, arg_str: str) -> ctpt.TokenData:
    #     parser = cls.arg_grammar.parser()
    #     result = parser.parse_string(arg_str)
    #     result_val = result.value()
    #     return result_val


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
    pass


class Placable(Concrete):
    pass


class Configurable(Concrete):
    pass


class Foodstuff(Concrete):
    pass


class System(Concrete):
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


class Partitionable(TokenSpec):
    pass


class Measurable(TokenSpec):
    pass


class Passthru(TokenSpec):
    pass


class ControlFlow(TokenSpec):
    pass


class Ingredient(Modifiable, Annotatable, Foodstuff, Placable, Measurable):
    keyword = 'INGR'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(), output_types=(SelfRef,)),
    )


class Tool(Modifiable, Annotatable, Implement, Placable):
    keyword = 'TOOL'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(), output_types=(SelfRef,)),
    )


class Container(Modifiable, Annotatable, Vessel, Placable):
    keyword = 'CONT'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(), output_types=(SelfRef,)),
    )


class Appliance(Modifiable, Annotatable, Vessel, Implement, Placable, Configurable):
    keyword = 'APPL'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(), output_types=(SelfRef,)),
    )


class Environment(Modifiable, Annotatable, Equipment, Configurable):
    keyword = 'ENVR'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(), output_types=(SelfRef,)),
    )


class Verb(Action, Modifiable, Annotatable):
    keyword = 'VERB'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING
    pipelines = (
        Pipeline(input_types=(Foodstuff,), output_types=(Mixture,)),
        Pipeline(input_types=(System,), output_types=(System,)),
    )


class Add(Action, Modifiable, Annotatable):
    keyword = 'ADDI'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE
    pipelines = (
        Pipeline(input_types=(Vessel, Foodstuff), output_types=(System,)),
        Pipeline(input_types=(Foodstuff, Foodstuff), output_types=(Mixture,)),
        Pipeline(input_types=(System, Foodstuff), output_types=(System,)),
        Pipeline(input_types=(Vessel, System), output_types=(System,)),
        Pipeline(input_types=(Foodstuff, System), output_types=(Mixture,)),
        Pipeline(input_types=(System, System), output_types=(System,)),
    )


class AddTo(Add):
    keyword = 'ADDT'
    pipelines = reverse_input_order(Add.pipelines)


class Move(Action, Modifiable, Annotatable):
    keyword = 'MOVE'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING_OR_NONE
    pipelines = (
        Pipeline(input_types=(System, Vessel), output_types=(Vessel, System,)),
        Pipeline(input_types=(System, Foodstuff), output_types=(Vessel, Mixture,)),
        Pipeline(input_types=(System, System), output_types=(Vessel, System,)),
    )


class MoveFrom(Move):
    keyword = 'MOVF'
    pipelines = reverse_input_order(Move.pipelines)


class Divide(Action, Annotatable, Partitionable):
    keyword = 'DIVI'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE
    pipelines = (
        Pipeline(input_types=(Foodstuff,), output_types=(Mixture, Mixture,)),
        Pipeline(input_types=(System,), output_types=(System, Mixture,)),
    )


class Reserve(Action, Annotatable, Partitionable):
    keyword = 'RESV'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Configure(Action, Modifiable, Annotatable):
    keyword = 'CONF'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Meld(Action, Modifiable, Annotatable):
    keyword = 'MELD'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Place(Action, Modifiable, Annotatable):
    keyword = 'PLAC'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Remove(Action, Modifiable, Annotatable):
    keyword = 'REMO'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Discard(Action, Photoable):
    keyword = 'DISC'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Empty(Action, Photoable):
    keyword = 'EMPT'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Simultaneous(Action, Passthru):
    keyword = 'SIMU'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.NONE


class With(Meta, Passthru):
    keyword = 'WITH'
    arg_grammar = None
    arg_vp_schema = asc.ArgumentSchemas.NONE


class Using(Meta, Passthru):
    keyword = 'USIN'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Precondition(Meta):
    keyword = 'PREC'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Modifier(Meta):
    keyword = 'MODI'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Annotation(Meta):
    keyword = 'ANNO'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Photo(Meta):
    keyword = 'PHOT'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class LookupSet(Meta):
    keyword = 'LSET'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class LookupGet(ControlFlow):
    keyword = 'LGET'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


class Fraction(Partition):
    keyword = 'FRAC'
    arg_grammar = cgrm.Partition
    arg_vp_schema = asc.ArgumentSchemas.FRACTION


class Pseudoselect(Partition):
    keyword = 'PSEU'
    arg_grammar = cgrm.Phrase
    arg_vp_schema = asc.ArgumentSchemas.STRING


class QuantityMass(Quantity):
    keyword = 'QMAS'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_MASS


class QuantityVolume(Quantity):
    keyword = 'QVOL'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_VOLUME


class QuantityCount(Quantity):
    keyword = 'QCNT'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_COUNT


class Time(Meta):
    keyword = 'TIME'
    arg_grammar = cgrm.Quantity
    arg_vp_schema = asc.ArgumentSchemas.QUANTITY_TIME


class Until(Meta):
    keyword = 'UNTL'
    arg_grammar = cgrm.String
    arg_vp_schema = asc.ArgumentSchemas.STRING


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
