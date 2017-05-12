import typing as typ

import voluptuous

import cheffu.interfaces as ci
from cheffu.argument_schema import ArgumentSchemas as asc


# class Pipeline(typ.NamedTuple):
#     inputs: typ.Sequence[ci.Token]
#     # TODO: Should be more specific than Any.
#     process: typ.Any
#
#
# class TokenDef(typ.NamedTuple):
#     # Class used to represent this token (data and interface)
#     cls: typ.Type[ci.Token]
#     # Token keyword, used in JSON
#     keyword: str
#     pipelines: typ.Sequence[Pipeline]
#     json_arg_schema: voluptuous.Schema
#     # fl_arg_grammar: modgrammar.Grammar
#     # Character used as replacement for keyword
#     sigil: typ.Optional[str] = None
#
#     @property
#     def name(self) -> str:
#         return self.cls.__name__
#
#
# TokenDefs = frozenset({
#
#     # Concrete Tokens ##########################################################
#
#     TokenDef(
#         cls=ci.Ingredient,
#         keyword='INGR',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(ci.Ingredient,),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Tool,
#         keyword='TOOL',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(ci.Tool,),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Vessel,
#         keyword='VESS',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(ci.Vessel,),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Appliance,
#         keyword='APPL',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(ci.Appliance,),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Environment,
#         keyword='ENVR',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(ci.Environment,),
#                 process=None,
#             ),
#         ),
#     ),
#
#     #### Operational Tokens ####################################################
#
#     TokenDef(
#         cls=ci.Verb,
#         keyword='VERB',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff),),
#                 # outputs=(ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Add,
#         keyword='ADDI',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff), ci.Haz(ci.Foodstuff),),
#                 # outputs=(ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#             Pipeline(
#                 inputs=(ci.Haz(ci.Container), ci.Haz(ci.Foodstuff),),
#                 # outputs=('System',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.AddTo,
#         keyword='ADDT',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff), ci.Haz(ci.Foodstuff),),
#                 # outputs=(ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff), ci.Haz(ci.Container),),
#                 # outputs=('System',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Move,
#         keyword='MOVE',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=('System', ci.Haz(ci.Foodstuff),),
#                 # outputs=('Vessel', ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#             Pipeline(
#                 inputs=('System', ci.Haz(ci.Container),),
#                 # outputs=('Vessel', 'System',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.MoveFrom,
#         keyword='MOVF',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff), 'System',),
#                 # outputs=('Vessel', ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#             Pipeline(
#                 inputs=(ci.Haz(ci.Container), 'System',),
#                 # outputs=('Vessel', 'System',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Divide,
#         keyword='DIVI',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff),),
#                 # outputs=(ci.Haz(ci.Foodstuff), 'Food',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Reserve,
#         keyword='RESV',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff),),
#                 # outputs=(ci.Haz(ci.Foodstuff), 'Food',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Configure,
#         keyword='CONF',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Has(Appliance)',),
#                 # outputs=('Has(Appliance)',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Meld,
#         keyword='MELD',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Container), ci.Tool,),
#                 # outputs=(ci.Haz(ci.Container),),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Place,
#         keyword='PLAC',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=('Has(Environment)', 'Placeable',),
#                 # outputs=('Process',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Remove,
#         keyword='RMVE',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=('Process',),
#                 # outputs=('Placeable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Bind,
#         keyword='BIND',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=(ci.Haz(ci.Foodstuff), ci.Tool,),
#                 # outputs=(ci.Haz(ci.Foodstuff),),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Discard,
#         keyword='DISC',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=('Has(Mixture)',),
#                 # outputs=(),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Empty,
#         keyword='EMPT',
#         json_arg_schema=asc.NONE,
#         pipelines=(
#             Pipeline(
#                 inputs=('System',),
#                 # outputs=('Vessel',),
#                 process=None,
#             ),
#         ),
#     ),
#     # TODO: How does this work with multiple Tools?
#     # TODO: Maybe have this work on two Verbs as input?
#     TokenDef(
#         cls=ci.Simultaneous,
#         keyword='SIMU',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Has(Verb)',),
#                 # outputs=('Has(Verb)',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.LookupGet,
#         keyword='LGET',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=(),
#                 # outputs=(),
#                 process=None,
#             ),
#         ),
#     ),
#
#     #### Metadata Tokens #######################################################
#
#     TokenDef(
#         cls=ci.Condition,
#         keyword='COND',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Has(Environment)',),
#                 # outputs=('Has(Environment)',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Modifier,
#         keyword='MODI',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Modifiable',),
#                 # outputs=('Modifiable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Annotation,
#         keyword='ANNO',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Annotatable',),
#                 # outputs=('Annotatable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Photo,
#         keyword='PHOT',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Photoable',),
#                 # outputs=('Photoable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.LookupSet,
#         keyword='LSET',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Lookupable',),
#                 # outputs=('Lookupable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Fraction,
#         keyword='FRAC',
#         json_arg_schema=asc.FRACTION,
#         pipelines=(
#             Pipeline(
#                 inputs=('Divisor',),
#                 # outputs=('Divisor',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Pseudoselect,
#         keyword='PSEU',
#         json_arg_schema=asc.STRING,
#         pipelines=(
#             Pipeline(
#                 inputs=('Divisor',),
#                 # outputs=('Divisor',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.QuantityMass,
#         keyword='QMAS',
#         json_arg_schema=asc.QUANTITY_MASS,
#         pipelines=(
#             Pipeline(
#                 inputs=('Quantifiable',),
#                 # outputs=('Quantifiable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.QuantityVolume,
#         keyword='QVOL',
#         json_arg_schema=asc.QUANTITY_VOLUME,
#         pipelines=(
#             Pipeline(
#                 inputs=('Quantifiable',),
#                 # outputs=('Quantifiable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.QuantityCount,
#         keyword='QCNT',
#         json_arg_schema=asc.QUANTITY_COUNT,
#         pipelines=(
#             Pipeline(
#                 inputs=('Quantifiable',),
#                 # outputs=('Quantifiable',),
#                 process=None,
#             ),
#         ),
#     ),
#     TokenDef(
#         cls=ci.Time,
#         keyword='TIME',
#         json_arg_schema=asc.QUANTITY_TIME,
#         pipelines=(
#             Pipeline(
#                 inputs=('Timable',),
#                 # outputs=('Timable',),
#                 process=None,
#             ),
#         ),
#     ),
#
#     #### Generative Tokens #####################################################
#
#     # TokenDef(
#     #     cls=ci.Group,
#     #     keyword='GRUP',
#     #     json_arg_schema='tokenseq',
#     #     pipelines=(
#     #         Pipeline(
#     #             inputs=(),
#     #             # outputs=('Group',),
#     #             process=None,
#     #         ),
#     #     ),
#     # ),
#     # TokenDef(
#     #     cls=ci.VariantTag,
#     #     keyword='VTAG',
#     #     json_arg_schema=asc.VARIANT_TAG_SET,
#     #     pipelines=(
#     #         Pipeline(
#     #             inputs=('Group',),
#     #             # outputs=('Group',),
#     #             process=None,
#     #         ),
#     #     ),
#     # ),
#     # TokenDef(
#     #     cls=ci.Or,
#     #     keyword='ORGR',
#     #     json_arg_schema=asc.NONE,
#     #     pipelines=(
#     #         Pipeline(
#     #             inputs=('Alternatable', 'Group'),
#     #             # outputs=('Alternatable'),
#     #             process=None,
#     #         ),
#     #     ),
#     # ),
#     TokenDef(
#         cls=ci.Repeat,
#         keyword='REPT',
#         json_arg_schema=asc.POS_INT,
#         pipelines=(
#             Pipeline(
#                 inputs=('Group',),
#                 # outputs=('Repetition',),
#                 process=None,
#             ),
#         ),
#     ),
#
# })
#
# TokenNameToDef = {k.name: k for k in TokenDefs}
# TokenKeywordToDef = {k.keyword: k for k in TokenDefs}
