from voluptuous import Schema, All, Length, Unique, Range, Required, In

class ArgumentSchemas:
    MASS_UNITS              = frozenset({'g', 'kg', 'lb', 'oz',})
    VOLUME_UNITS            = frozenset({'L', 'mL', 'cup', 'floz', 'Tbsp', 'tsp', 'qt', 'gal'})
    TIME_UNITS              = frozenset({'sec', 'min', 'hr', 'day', 'week'})
    LENGTH_UNITS            = frozenset({'cm', 'm', 'mm', 'in', 'ft',})

    STRING                  = Schema(All(str, Length(min=1)))
    POS_INT                 = Schema(All(int, Range(min=1)))
    NON_NEG_INT             = Schema(All(int, Range(min=0)))
    VARIANT_TAG_SET         = Schema(All(Unique(), Length(min=1), [NON_NEG_INT]))
    FRACTION                = Schema({
                                Required('keep'): POS_INT,
                                Required('pass'): POS_INT,
                            })
    QUANTITY_BASE           = Schema({
                                Required('base'): POS_INT,
                                Required('range', default=0): NON_NEG_INT,
                                Required('base_den', default=1): POS_INT,
                                Required('range_den', default=1): POS_INT,
                                Required('less_ok', default=True): bool,
                                Required('more_ok', default=True): bool,
                            })
    QUANTITY_MASS           = QUANTITY_BASE.extend({
                                Required('units'): All(str, In(MASS_UNITS)),
                            })
    QUANTITY_VOLUME         = QUANTITY_BASE.extend({
                                Required('units'): All(str, In(VOLUME_UNITS)),
                            })
    QUANTITY_COUNT          = QUANTITY_BASE.extend({
                                Required('units'): STRING,
                            })
    QUANTITY_TIME           = QUANTITY_BASE.extend({
                                Required('units'): All(str, In(TIME_UNITS)),
                            })
    NONE                    = Schema(None)
    # TOKEN_SEQUENCE          = None
