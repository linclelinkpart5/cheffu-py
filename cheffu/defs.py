import typing as typ

import cheffu.interfaces as chin
import cheffu.grammars as chgr
from cheffu.types.tokens import TokenTypeDef, TokenInterfaceSequence, Pipeline


# TODO:
# * Handling of Systems/Vessels nested within other Systems/Vessels.
#   * Directives to place a System/Vessel inside another System/Vessel.
#   * Indexing nested Systems/Vessels (e.g. to put water inside a bain-marie, but not in the ramekins).
# * Handling multiple Placables inside of a single Environment.
#   * Removing a specific Placable and not another.
# * Handling of With/Using being specified more than once for a given Action.
# * Handling interaction between lazily-evaluated bundles ans LookupSet/Get.
#   * Need to ensure that a Concrete internal to the bundle is not yanked out.
# * Prohibiting stupid Discards.
#   * Prohibit putting an Ingredient into a Vessel, and then immediately Discarding.
# * More flexibility with Verbs and Systems using an Appliance.
#   * Directives to perform a Verb on such a System without using Appliance function (e.g. scrape down in a blender).
# * Numerical ranges in other areas.
#   * Numerical ranges in Ingredient Modifiers (e.g. 75-85% dark chocolate).
# * Enabling batch operations on many identical outputs.
#   * Specify a repeated Verb/Action to perform on a number of Vessels/Systems (e.g. sprinkle each cupcake with sugar).
# * Handling cases where an Ingredient is processed, but leaves a remainder needing Discarding or further processing.
#   * Examples include using the juice & zest of a lemon and cracking eggs and using only the yolks.
# * Prohibiting multiple non-stackable Meta tokens on a single target.
#   * Examples include multiple Partitions on a Divide or Reserve operation.

TokenTypeDefs = (
    TokenTypeDef(
        interface=chin.Ingredient,
        keyword='INGR',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=(chin.Ingredient,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Tool,
        keyword='TOOL',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=(chin.Tool,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Container,
        keyword='CONT',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=(chin.Container,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Appliance,
        keyword='APPL',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=(chin.Appliance,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Environment,
        keyword='ENVR',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=(chin.Environment,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Verb,
        keyword='VERB',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Foodstuff,), output_types=(chin.Mixture,)),
            Pipeline(input_types=(chin.System,), output_types=(chin.System,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Add,
        keyword='ADDI',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Vessel, chin.Foodstuff), output_types=(chin.System,)),
            Pipeline(input_types=(chin.Foodstuff, chin.Foodstuff), output_types=(chin.Mixture,)),
            Pipeline(input_types=(chin.System, chin.Foodstuff), output_types=(chin.System,)),
            Pipeline(input_types=(chin.Vessel, chin.System), output_types=(chin.System,)),
            Pipeline(input_types=(chin.Foodstuff, chin.System), output_types=(chin.Mixture,)),
            Pipeline(input_types=(chin.System, chin.System), output_types=(chin.System,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.AddTo,
        keyword='ADDT',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Foodstuff, chin.Vessel), output_types=(chin.System,)),
            Pipeline(input_types=(chin.Foodstuff, chin.Foodstuff), output_types=(chin.Mixture,)),
            Pipeline(input_types=(chin.Foodstuff, chin.System), output_types=(chin.System,)),
            Pipeline(input_types=(chin.System, chin.Vessel), output_types=(chin.System,)),
            Pipeline(input_types=(chin.System, chin.Foodstuff), output_types=(chin.Mixture,)),
            Pipeline(input_types=(chin.System, chin.System), output_types=(chin.System,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Move,
        keyword='MOVE',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.System, chin.Vessel), output_types=(chin.Vessel, chin.System,)),
            Pipeline(input_types=(chin.System, chin.Foodstuff), output_types=(chin.Vessel, chin.Mixture,)),
            Pipeline(input_types=(chin.System, chin.System), output_types=(chin.Vessel, chin.System,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.MoveFrom,
        keyword='MOVF',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Vessel, chin.System), output_types=(chin.Vessel, chin.System,)),
            Pipeline(input_types=(chin.Foodstuff, chin.System), output_types=(chin.Vessel, chin.Mixture,)),
            Pipeline(input_types=(chin.System, chin.System), output_types=(chin.Vessel, chin.System,)),
        ),
    ),
    # TODO: Should Divide and Reserve be parameterized by a Verb? Many ways to use a Verb to split a Mixture or
    #       Ingredient into two parts.
    TokenTypeDef(
        interface=chin.Divide,
        keyword='DIVI',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Foodstuff,), output_types=(chin.Mixture, chin.Mixture,)),
            Pipeline(input_types=(chin.System,), output_types=(chin.System, chin.Mixture,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Reserve,
        keyword='RESV',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Foodstuff,), output_types=(chin.Mixture, chin.Mixture,)),
            Pipeline(input_types=(chin.System,), output_types=(chin.System, chin.Mixture,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Configure,
        keyword='CONF',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Configurable,), output_types=(chin.Configurable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Meld,
        keyword='MELD',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Vessel, chin.Tool), output_types=(chin.Vessel,)),
            Pipeline(input_types=(chin.System, chin.Tool), output_types=(chin.System,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Place,
        keyword='PLAC',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Environment, chin.Placable), output_types=(chin.Process,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Remove,
        keyword='REMO',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Process,), output_types=(chin.Placable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.With,
        keyword='WITH',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Action, chin.Tool), output_types=(chin.Action,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Using,
        keyword='USIN',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Action,), output_types=(chin.Action,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Discard,
        keyword='DISC',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Mixture,), output_types=()),
            Pipeline(input_types=(chin.System,), output_types=()),
        ),
    ),
    TokenTypeDef(
        interface=chin.Empty,
        keyword='EMPT',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.System,), output_types=(chin.Vessel,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Simultaneous,
        keyword='SIMU',
        arg_conv=None,
        pipelines=(
            Pipeline(input_types=(chin.Action, chin.Verb), output_types=(chin.Action,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Precondition,
        keyword='PREC',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Environment,), output_types=(chin.Environment,)),
            Pipeline(input_types=(chin.Appliance,), output_types=(chin.Appliance,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Modifier,
        keyword='MODI',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Modifiable,), output_types=(chin.Modifiable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Annotation,
        keyword='ANNO',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Annotatable,), output_types=(chin.Annotatable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Photo,
        keyword='PHOT',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Photoable,), output_types=(chin.Photoable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.LookupSet,
        keyword='LSET',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Taggable,), output_types=(chin.Taggable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.LookupGet,
        keyword='LGET',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(), output_types=()),
        ),
    ),
    TokenTypeDef(
        interface=chin.Fraction,
        keyword='FRAC',
        arg_conv=chgr.Partition,
        pipelines=(
            Pipeline(input_types=(chin.Partitionable,), output_types=(chin.Partitionable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Pseudoselect,
        keyword='PSEU',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Partitionable,), output_types=(chin.Partitionable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.QuantityMass,
        keyword='QMAS',
        arg_conv=chgr.Quantity,
        pipelines=(
            Pipeline(input_types=(chin.Measurable,), output_types=(chin.Measurable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.QuantityVolume,
        keyword='QVOL',
        arg_conv=chgr.Quantity,
        pipelines=(
            Pipeline(input_types=(chin.Measurable,), output_types=(chin.Measurable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.QuantityCount,
        keyword='QCNT',
        arg_conv=chgr.Quantity,
        pipelines=(
            Pipeline(input_types=(chin.Measurable,), output_types=(chin.Measurable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Time,
        keyword='TIME',
        arg_conv=chgr.Time,
        pipelines=(
            Pipeline(input_types=(chin.Timeable,), output_types=(chin.Timeable,)),
        ),
    ),
    TokenTypeDef(
        interface=chin.Until,
        keyword='UNTL',
        arg_conv=chgr.String,
        pipelines=(
            Pipeline(input_types=(chin.Timeable,), output_types=(chin.Timeable,)),
        ),
    ),
)


TokenNameToDef = {k.name: k for k in TokenTypeDefs}
TokenKeywordToDef = {k.keyword: k for k in TokenTypeDefs}
