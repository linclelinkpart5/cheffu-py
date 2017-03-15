from collections import namedtuple

TokenDef = namedtuple(
    'TokenDef',
    [
        'name',
        'keyword',
        'inputs',
        'arguments',
        'outputs',
    ],
)

# Key:
#   !Token:         exactly Token
#   Token:          anything that IS-A Token, including Token itself
#   @Token:         Contains(Token)
#   &Token:         CanHold(Token)
# These can all be combined with + and -

def has_food(token):
    return True

def has_vessel(token):
    return True

TokenDefs = frozenset({

#### Concrete Tokens ###########################################################################################################

    TokenDef(
        name='Ingredient',
        keyword='INGR',
        inputs=(),
        arguments=(str,),
        outputs=('Ingredient',),
    ),
    TokenDef(
        name='Tool',
        keyword='TOOL',
        inputs=(),
        arguments=(str,),
        outputs=('Tool',),
    ),
    TokenDef(
        name='Vessel',
        keyword='VESS',
        inputs=(),
        arguments=(str,),
        outputs=('Vessel',),
    ),
    TokenDef(
        name='Appliance',
        keyword='APPL',
        inputs=(),
        arguments=(str,),
        outputs=('Appliance',),
    ),
    TokenDef(
        name='Environment',
        keyword='ENVR',
        inputs=(),
        arguments=(str,),
        outputs=('Environment',),
    ),

#### Operational Tokens ########################################################################################################

    TokenDef(
        name='Verb',
        keyword='VERB',
        inputs=('Has(Food)',),
        arguments=(str,),
        outputs=('Has(Food)',),
    ),
    TokenDef(
        name='Add',
        keyword='ADDI',
        inputs=('Has(Food) | Has(Vessel)', 'Has(Food)',),
        arguments=(),
        outputs=('Has(Food) | Has(Food) + Has(Vessel)',),
    ),
    TokenDef(
        name='Move',
        keyword='MOVE',
        inputs=('Has(Food) + Has(Vessel)', 'Has(Food) | Has(Vessel)',),
        arguments=(),
        outputs=('Vessel', 'Has(Food) | Has(Food) + Has(Vessel)',),
    ),
    # Take, Leave, Push, Pull, Yield, Quash, Separate, Reserve, Divide
    TokenDef(
        name='Divide',
        keyword='DIVI',
        inputs=('Has(Food)',),
        arguments=(),
        outputs=('Has(Food)', 'Food',),
    ),
    TokenDef(
        name='Reserve',
        keyword='RESV',
        inputs=('Has(Food)',),
        arguments=(),
        outputs=('Has(Food)', 'Food',),
    ),
    TokenDef(
        name='Configure',
        keyword='CONF',
        inputs=('Has(Appliance)',),
        arguments=(str,),
        outputs=('Has(Appliance)',),
    ),
    TokenDef(
        name='Meld',
        keyword='MELD',
        inputs=('Has(Vessel)', 'Tool',),
        arguments=(str,),
        outputs=('Has(Vessel)',),
    ),
    TokenDef(
        name='Place',
        keyword='PLAC',
        inputs=('Has(Environment)', 'Placeable',),
        arguments=(),
        outputs=('Process',),
    ),
    TokenDef(
        name='Remove',
        keyword='RMVE',
        inputs=('Process',),
        arguments=(),
        outputs=('Placeable',),
    ),
    TokenDef(
        name='Bind',
        keyword='BIND',
        inputs=('Has(Food)', 'Tool',),
        arguments=(),
        outputs=('Has(Food) + Has(Tool)',),
    ),
    TokenDef(
        name='Discard',
        keyword='DISC',
        inputs=('Has(Mixture)',),
        arguments=(),
        outputs=(),
    ),
    TokenDef(
        name='Empty',
        keyword='EMPT',
        inputs=('Has(Mixture) + Has(Vessel)',),
        arguments=(),
        outputs=('Vessel',),
    ),
    TokenDef(
        name='Simultaneous',
        keyword='SIMU',
        inputs=('Has(Verb)',),
        arguments=(str,),
        outputs=('Has(Verb)',),
    ),

#### Metadata Tokens ###########################################################################################################

    TokenDef(
        name='Condition',
        keyword='COND',
        inputs=('Has(Environment)',),
        arguments=(str,),
        outputs=('Has(Environment)',),
    ),
    TokenDef(
        name='Modifier',
        keyword='MODI',
        inputs=('Modifiable',),
        arguments=(str,),
        outputs=('Modifiable',),
    ),
    TokenDef(
        name='Annotation',
        keyword='ANNO',
        inputs=('Annotatable',),
        arguments=(str,),
        outputs=('Annotatable',),
    ),
    TokenDef(
        name='Photo',
        keyword='PHOT',
        inputs=('Photoable',),
        arguments=(str,),
        outputs=('Photoable',),
    ),
    TokenDef(
        name='LookupSet',
        keyword='LSET',
        inputs=('Lookupable',),
        arguments=(str,),
        outputs=('Lookupable',),
    ),
    TokenDef(
        name='Partition',
        keyword='PART',
        inputs=('Divisor',),
        arguments=('Fraction'),
        outputs=('Divisor',),
    ),
    TokenDef(
        name='QuantityMass',
        keyword='QMAS',
        inputs=('Quantifiable',),
        arguments=('quantitym',),
        outputs=('Quantifiable',),
    ),
    TokenDef(
        name='QuantityVolume',
        keyword='QVOL',
        inputs=('Quantifiable',),
        arguments=('quantityv',),
        outputs=('Quantifiable',),
    ),
    TokenDef(
        name='QuantityCount',
        keyword='QCNT',
        inputs=('Quantifiable',),
        arguments=('quantityc',),
        outputs=('Quantifiable',),
    ),
    TokenDef(
        name='Time',
        keyword='TIME',
        inputs=('Timable',),
        arguments=('time',),
        outputs=('Timable',),
    ),
    TokenDef(
        name='VariantTag',
        keyword='VTAG',
        inputs=('Group',),
        arguments=('posintset',),
        outputs=('Group',),
    ),

#### Control Flow Tokens #######################################################################################################

    TokenDef(
        name='Group',
        keyword='GRUP',
        inputs=(),
        arguments=('tokenseq',),
        outputs=('Group',),
    ),
    TokenDef(
        name='Or',
        keyword='ORGR',
        inputs=('Alternatable', 'Group'),
        arguments=(),
        outputs=('Alternatable'),
    ),
    TokenDef(
        name='Repeat',
        keyword='REPT',
        inputs='Group',
        arguments=(int,),
        outputs=('Repetition',),
    ),
    TokenDef(
        name='LookupGet',
        keyword='LGET',
        inputs=(),
        arguments=(str,),
        outputs=(),
    ),

})

TokenNameToDef = {k.name: k for k in TokenDefs}
TokenKeywordToDef = {k.keyword: k for k in TokenDefs}
