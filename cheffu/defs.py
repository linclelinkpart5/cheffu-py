from collections import namedtuple
from types import new_class

import interfaces as ci

from argument_schema import ArgumentSchemas as asc

from voluptuous import Schema

IOSeq = namedtuple(
    'IOSeq',
    (
        'input_seq',
        'output_seq'
    ),
)

Pipeline = namedtuple(
    'Pipeline',
    (
        'inputs',       # Expected inputs, to be popped from stack
        'outputs',      # Expected outputs, to be pushed onto stack
        'process',
    ),
)

TokenInitDef = namedtuple(
    'TokenInitDef',
    (
        'klass',        # Class to use to represent this token (data and interface)
        'keyword',      # Token keyword, used in JSON
        'arg_schema',   # Schema that argument needs to validate against
        'pipelines',    # Definitions for combinations of inputs, outputs, and processors
    ),
)

TokenDef = namedtuple(
    'TokenDef',
    TokenInitDef._fields + (
        'name',         # Human-friendly token name, taken from klass
        'schema',       # Schema of this token's dict representation, uses arg_schema
    ),
)

TokenInitDefs = frozenset({

    #### Concrete Tokens #######################################################

    TokenInitDef(
        klass=ci.Ingredient,
        keyword='INGR',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(ci.Ingredient,),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Tool,
        keyword='TOOL',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(ci.Tool,),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Vessel,
        keyword='VESS',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(ci.Vessel,),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Appliance,
        keyword='APPL',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(ci.Appliance,),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Environment,
        keyword='ENVR',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(ci.Environment,),
                process=None,
            ),
        ),
    ),

    #### Operational Tokens ####################################################

    TokenInitDef(
        klass=ci.Verb,
        keyword='VERB',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)',),
                outputs=('Has(Food)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Add,
        keyword='ADDI',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)', 'Has(Food)',),
                outputs=('Has(Food',),
                process=None,
            ),
            Pipeline(
                inputs=('Has(Vessel)', 'Has(Food)',),
                outputs=('Has(Food) + Has(Vessel)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.AddTo,
        keyword='ADDT',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)', 'Has(Food)',),
                outputs=('Has(Food)',),
                process=None,
            ),
            Pipeline(
                inputs=('Has(Food)', 'Has(Vessel)',),
                outputs=('Has(Food) + Has(Vessel)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Move,
        keyword='MOVE',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food) + Has(Vessel)', 'Has(Food)',),
                outputs=('Vessel', 'Has(Food)',),
                process=None,
            ),
            Pipeline(
                inputs=('Has(Food) + Has(Vessel)', 'Has(Vessel)',),
                outputs=('Vessel', 'Has(Food) + Has(Vessel)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.MoveFrom,
        keyword='MOVF',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)', 'Has(Food) + Has(Vessel)',),
                outputs=('Vessel', 'Has(Food)',),
                process=None,
            ),
            Pipeline(
                inputs=('Has(Vessel)', 'Has(Food) + Has(Vessel)',),
                outputs=('Vessel', 'Has(Food) + Has(Vessel)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Divide,
        keyword='DIVI',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)',),
                outputs=('Has(Food)', 'Food',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Reserve,
        keyword='RESV',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)',),
                outputs=('Has(Food)', 'Food',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Configure,
        keyword='CONF',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Has(Appliance)',),
                outputs=('Has(Appliance)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Meld,
        keyword='MELD',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Has(Vessel)', 'Tool',),
                outputs=('Has(Vessel)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Place,
        keyword='PLAC',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Environment)', 'Placeable',),
                outputs=('Process',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Remove,
        keyword='RMVE',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Process',),
                outputs=('Placeable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Bind,
        keyword='BIND',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Food)', 'Tool',),
                outputs=('Has(Food) + Has(Tool)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Discard,
        keyword='DISC',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Mixture)',),
                outputs=(),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Empty,
        keyword='EMPT',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Has(Mixture) + Has(Vessel)',),
                outputs=('Vessel',),
                process=None,
            ),
        ),
    ),
    # TODO: How does this work with multiple Tools?
    # TODO: Maybe have this work on two Verbs as input?
    TokenInitDef(
        klass=ci.Simultaneous,
        keyword='SIMU',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Has(Verb)',),
                outputs=('Has(Verb)',),
                process=None,
            ),
        ),
    ),

    #### Metadata Tokens #######################################################

    TokenInitDef(
        klass=ci.Condition,
        keyword='COND',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Has(Environment)',),
                outputs=('Has(Environment)',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Modifier,
        keyword='MODI',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Modifiable',),
                outputs=('Modifiable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Annotation,
        keyword='ANNO',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Annotatable',),
                outputs=('Annotatable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Photo,
        keyword='PHOT',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Photoable',),
                outputs=('Photoable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.LookupSet,
        keyword='LSET',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Lookupable',),
                outputs=('Lookupable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Fraction,
        keyword='FRAC',
        arg_schema=asc.FRACTION,
        pipelines=(
            Pipeline(
                inputs=('Divisor',),
                outputs=('Divisor',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Pseudoselect,
        keyword='PSEU',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=('Divisor',),
                outputs=('Divisor',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.QuantityMass,
        keyword='QMAS',
        arg_schema=asc.QUANTITY_MASS,
        pipelines=(
            Pipeline(
                inputs=('Quantifiable',),
                outputs=('Quantifiable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.QuantityVolume,
        keyword='QVOL',
        arg_schema=asc.QUANTITY_VOLUME,
        pipelines=(
            Pipeline(
                inputs=('Quantifiable',),
                outputs=('Quantifiable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.QuantityCount,
        keyword='QCNT',
        arg_schema=asc.QUANTITY_COUNT,
        pipelines=(
            Pipeline(
                inputs=('Quantifiable',),
                outputs=('Quantifiable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Time,
        keyword='TIME',
        arg_schema=asc.QUANTITY_TIME,
        pipelines=(
            Pipeline(
                inputs=('Timable',),
                outputs=('Timable',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.VariantTag,
        keyword='VTAG',
        arg_schema=asc.VARIANT_TAG_SET,
        pipelines=(
            Pipeline(
                inputs=('Group',),
                outputs=('Group',),
                process=None,
            ),
        ),
    ),

    #### Control Flow Tokens ###################################################

    TokenInitDef(
        klass=ci.Group,
        keyword='GRUP',
        arg_schema='tokenseq',
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=('Group',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Or,
        keyword='ORGR',
        arg_schema=asc.NONE,
        pipelines=(
            Pipeline(
                inputs=('Alternatable', 'Group'),
                outputs=('Alternatable'),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.Repeat,
        keyword='REPT',
        arg_schema=asc.POS_INT,
        pipelines=(
            Pipeline(
                inputs=('Group',),
                outputs=('Repetition',),
                process=None,
            ),
        ),
    ),
    TokenInitDef(
        klass=ci.LookupGet,
        keyword='LGET',
        arg_schema=asc.STRING,
        pipelines=(
            Pipeline(
                inputs=(),
                outputs=(),
                process=None,
            ),
        ),
    ),

})

def klass__init__(self, value):
    super().__init__()
    self.value = value

TokenDefs = frozenset({
    TokenDef(
        **tid._asdict(),
        name=tid.klass.__name__,
        schema=Schema({tid.keyword: tid.arg_schema}, required=True),
    ) for tid in TokenInitDefs
})

TokenNameToDef = {k.name: k for k in TokenDefs}
TokenKeywordToDef = {k.keyword: k for k in TokenDefs}
