from collections import namedtuple
from types import new_class

import interfaces as ci

from argument_schema import ArgumentSchemas

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
        'inputs',
        'outputs',
        'process',
    ),
)

# TODO: Combine inputs and outputs into a ioseqs field; needed to simpify overloaded inputs to actions
TokenInitDef = namedtuple(
    'TokenInitDef',
    (
        'name',         # Human-friendly token name
        #'klass',        # Class to use to represent this token (data and interface)
        'keyword',      # Token keyword, used in JSON
        'arg_schema',   # Schema that argument needs to validate against
        'inputs',       # Expected inputs, to be popped from stack
        'outputs',      # Expected outputs, to be pushed onto stack
        'ioseqs',
        'interfaces',   # Interfaces token is to support
    ),
)

TokenDef = namedtuple(
    'TokenDef',
    TokenInitDef._fields + (
        'klass',        # Type for this token
        'schema',       # Schema this token's dict representation
    ),
)

TokenInitDefs = frozenset({

    #### Concrete Tokens #######################################################

    TokenInitDef(
        name='Ingredient',
        keyword='INGR',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=('Ingredient',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Ingredient',),),
        ),
        interfaces=(
            ci.Foodstuff,
            ci.Measurable,
            ci.Placable,
        ),
    ),
    TokenInitDef(
        name='Tool',
        keyword='TOOL',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=('Tool',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Tool',),),
        ),
        interfaces=(
            ci.Equipment,
            ci.Placable,
        ),
    ),
    TokenInitDef(
        name='Vessel',
        keyword='VESS',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=('Vessel',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Vessel',),),
        ),
        interfaces=(
            ci.Container,
            ci.Placable,
        ),
    ),
    TokenInitDef(
        name='Appliance',
        keyword='APPL',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=('Appliance',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Appliance',),),
        ),
        interfaces=(
            ci.Container,
            ci.Placable,
        ),
    ),
    TokenInitDef(
        name='Environment',
        keyword='ENVR',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=('Environment',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Environment',),),
        ),
        interfaces=(
            ci.Equipment,
        ),
    ),

    #### Operational Tokens ####################################################

    TokenInitDef(
        name='Verb',
        keyword='VERB',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Has(Food)',),
        outputs=('Has(Food)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food)',), output_seq=('Has(Food)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Add',
        keyword='ADDI',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food) | Has(Vessel)', 'Has(Food)',),
        outputs=('Has(Food) | Has(Food) + Has(Vessel)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food) | Has(Vessel)', 'Has(Food)',), output_seq=('Has(Food) | Has(Food) + Has(Vessel)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='AddTo',
        keyword='ADDT',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food)', 'Has(Food) | Has(Vessel)',),
        outputs=('Has(Food) | Has(Food) + Has(Vessel)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food)', 'Has(Food) | Has(Vessel)',), output_seq=('Has(Food) | Has(Food) + Has(Vessel)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Move',
        keyword='MOVE',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food) + Has(Vessel)', 'Has(Food) | Has(Vessel)',),
        outputs=('Vessel', 'Has(Food) | Has(Food) + Has(Vessel)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food) + Has(Vessel)', 'Has(Food) | Has(Vessel)',), output_seq=('Vessel', 'Has(Food) | Has(Food) + Has(Vessel)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='MoveFrom',
        keyword='MOVF',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food) | Has(Vessel)', 'Has(Food) + Has(Vessel)',),
        outputs=('Vessel', 'Has(Food) | Has(Food) + Has(Vessel)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food) | Has(Vessel)', 'Has(Food) + Has(Vessel)',), output_seq=('Vessel', 'Has(Food) | Has(Food) + Has(Vessel)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    # Take, Leave, Push, Pull, Yield, Quash, Separate, Reserve, Divide
    TokenInitDef(
        name='Divide',
        keyword='DIVI',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food)',),
        outputs=('Has(Food)', 'Food',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food)',), output_seq=('Has(Food)', 'Food',),),
        ),
        interfaces=(
            ci.Action,
            ci.Photoable,
            ci.Annotatable,
            ci.Partitionable,
        ),
    ),
    TokenInitDef(
        name='Reserve',
        keyword='RESV',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food)',),
        outputs=('Has(Food)', 'Food',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food)',), output_seq=('Has(Food)', 'Food',),),
        ),
        interfaces=(
            ci.Action,
            ci.Photoable,
            ci.Annotatable,
            ci.Partitionable,
        ),
    ),
    TokenInitDef(
        name='Configure',
        keyword='CONF',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Has(Appliance)',),
        outputs=('Has(Appliance)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Appliance)',), output_seq=('Has(Appliance)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Meld',
        keyword='MELD',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Has(Vessel)', 'Tool',),
        outputs=('Has(Vessel)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Vessel)', 'Tool',), output_seq=('Has(Vessel)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Place',
        keyword='PLAC',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Environment)', 'Placeable',),
        outputs=('Process',),
        ioseqs=(
            IOSeq(input_seq=('Has(Environment)', 'Placeable',), output_seq=('Process',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Remove',
        keyword='RMVE',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Process',),
        outputs=('Placeable',),
        ioseqs=(
            IOSeq(input_seq=('Process',), output_seq=('Placeable',),),
        ),
        interfaces=(
            ci.Action,
            ci.Modifiable,
            ci.Annotatable,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Bind',
        keyword='BIND',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Food)', 'Tool',),
        outputs=('Has(Food) + Has(Tool)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Food)', 'Tool',), output_seq=('Has(Food) + Has(Tool)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Passthru,
        ),
    ),
    TokenInitDef(
        name='Discard',
        keyword='DISC',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Mixture)',),
        outputs=(),
        ioseqs=(
            IOSeq(input_seq=('Has(Mixture)',), output_seq=(),),
        ),
        interfaces=(
            ci.Action,
            ci.Photoable,
        ),
    ),
    TokenInitDef(
        name='Empty',
        keyword='EMPT',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Has(Mixture) + Has(Vessel)',),
        outputs=('Vessel',),
        ioseqs=(
            IOSeq(input_seq=('Has(Mixture) + Has(Vessel)',), output_seq=('Vessel',),),
        ),
        interfaces=(
            ci.Action,
            ci.Photoable,
        ),
    ),
    # TODO: How does this work with multiple Tools?
    # TODO: Maybe have this work on two Verbs as input?
    TokenInitDef(
        name='Simultaneous',
        keyword='SIMU',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Has(Verb)',),
        outputs=('Has(Verb)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Verb)',), output_seq=('Has(Verb)',),),
        ),
        interfaces=(
            ci.Action,
            ci.Passthru,
        ),
    ),

    #### Metadata Tokens #######################################################

    TokenInitDef(
        name='Condition',
        keyword='COND',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Has(Environment)',),
        outputs=('Has(Environment)',),
        ioseqs=(
            IOSeq(input_seq=('Has(Environment)',), output_seq=('Has(Environment)',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='Modifier',
        keyword='MODI',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Modifiable',),
        outputs=('Modifiable',),
        ioseqs=(
            IOSeq(input_seq=('Modifiable',), output_seq=('Modifiable',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='Annotation',
        keyword='ANNO',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Annotatable',),
        outputs=('Annotatable',),
        ioseqs=(
            IOSeq(input_seq=('Annotatable',), output_seq=('Annotatable',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='Photo',
        keyword='PHOT',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Photoable',),
        outputs=('Photoable',),
        ioseqs=(
            IOSeq(input_seq=('Photoable',), output_seq=('Photoable',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='LookupSet',
        keyword='LSET',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Lookupable',),
        outputs=('Lookupable',),
        ioseqs=(
            IOSeq(input_seq=('Lookupable',), output_seq=('Lookupable',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='Fraction',
        keyword='FRAC',
        arg_schema=ArgumentSchemas.FRACTION,
        inputs=('Divisor',),
        outputs=('Divisor',),
        ioseqs=(
            IOSeq(input_seq=('Divisor',), output_seq=('Divisor',),),
        ),
        interfaces=(
            ci.Partition,
        ),
    ),
    TokenInitDef(
        name='Pseudoselect',
        keyword='PSEU',
        arg_schema=ArgumentSchemas.STRING,
        inputs=('Divisor',),
        outputs=('Divisor',),
        ioseqs=(
            IOSeq(input_seq=('Divisor',), output_seq=('Divisor',),),
        ),
        interfaces=(
            ci.Partition,
        ),
    ),
    TokenInitDef(
        name='QuantityMass',
        keyword='QMAS',
        arg_schema=ArgumentSchemas.QUANTITY_MASS,
        inputs=('Quantifiable',),
        outputs=('Quantifiable',),
        ioseqs=(
            IOSeq(input_seq=('Quantifiable',), output_seq=('Quantifiable',),),
        ),
        interfaces=(
            ci.Quantity,
        ),
    ),
    TokenInitDef(
        name='QuantityVolume',
        keyword='QVOL',
        arg_schema=ArgumentSchemas.QUANTITY_VOLUME,
        inputs=('Quantifiable',),
        outputs=('Quantifiable',),
        ioseqs=(
            IOSeq(input_seq=('Quantifiable',), output_seq=('Quantifiable',),),
        ),
        interfaces=(
            ci.Quantity,
        ),
    ),
    TokenInitDef(
        name='QuantityCount',
        keyword='QCNT',
        arg_schema=ArgumentSchemas.QUANTITY_COUNT,
        inputs=('Quantifiable',),
        outputs=('Quantifiable',),
        ioseqs=(
            IOSeq(input_seq=('Quantifiable',), output_seq=('Quantifiable',),),
        ),
        interfaces=(
            ci.Quantity,
        ),
    ),
    TokenInitDef(
        name='Time',
        keyword='TIME',
        arg_schema=ArgumentSchemas.QUANTITY_TIME,
        inputs=('Timable',),
        outputs=('Timable',),
        ioseqs=(
            IOSeq(input_seq=('Timable',), output_seq=('Timable',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),
    TokenInitDef(
        name='VariantTag',
        keyword='VTAG',
        arg_schema=ArgumentSchemas.VARIANT_TAG_SET,
        inputs=('Group',),
        outputs=('Group',),
        ioseqs=(
            IOSeq(input_seq=('Group',), output_seq=('Group',),),
        ),
        interfaces=(
            ci.Meta,
        ),
    ),

    #### Control Flow Tokens ###################################################

    TokenInitDef(
        name='Group',
        keyword='GRUP',
        arg_schema='tokenseq',
        inputs=(),
        outputs=('Group',),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=('Group',),),
        ),
        interfaces=(
            ci.ControlFlow,
        ),
    ),
    TokenInitDef(
        name='Or',
        keyword='ORGR',
        arg_schema=ArgumentSchemas.NONE,
        inputs=('Alternatable', 'Group'),
        outputs=('Alternatable'),
        ioseqs=(
            IOSeq(input_seq=('Alternatable', 'Group'), output_seq=('Alternatable'),),
        ),
        interfaces=(
            ci.ControlFlow,
        ),
    ),
    TokenInitDef(
        name='Repeat',
        keyword='REPT',
        arg_schema=ArgumentSchemas.POS_INT,
        inputs=('Group',),
        outputs=('Repetition',),
        ioseqs=(
            IOSeq(input_seq=('Group',), output_seq=('Repetition',),),
        ),
        interfaces=(
            ci.ControlFlow,
        ),
    ),
    TokenInitDef(
        name='LookupGet',
        keyword='LGET',
        arg_schema=ArgumentSchemas.STRING,
        inputs=(),
        outputs=(),
        ioseqs=(
            IOSeq(input_seq=(), output_seq=(),),
        ),
        interfaces=(
            ci.ControlFlow,
        ),
    ),

})

def klass__init__(self, value):
    super().__init__()
    self.value = value

TokenDefs = frozenset({
    TokenDef(
        **tid._asdict(),
        klass=new_class(
            tid.name,
            bases=tid.interfaces,
            exec_body=lambda ns: ns.update({'__init__': klass__init__}),
        ),
        schema=Schema({tid.keyword: tid.arg_schema}, required=True),
    ) for tid in TokenInitDefs
})

TokenNameToDef = {k.name: k for k in TokenDefs}
TokenKeywordToDef = {k.keyword: k for k in TokenDefs}
