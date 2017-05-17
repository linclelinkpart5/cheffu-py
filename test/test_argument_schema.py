import itertools
import unittest

import voluptuous

import cheffu.argument_schema

class TestArgumentSchema(unittest.TestCase):
    VALID_STRINGS = (
        'onion',
        'egg',
        'mushroom',
        'chicken stock',
        'banana',
    )
    INVALID_STRINGS = (
        '',
    )

    VALID_POS_INTS = frozenset(range(1, 4))
    VALID_NON_NEG_INTS = frozenset(range(0, 3))
    VALID_NEG_INTS = frozenset(-n for n in VALID_POS_INTS)
    VALID_NON_POS_INTS = frozenset(-n for n in VALID_NON_NEG_INTS)
    INVALID_POS_INTS = VALID_NON_POS_INTS
    INVALID_NON_NEG_INTS = VALID_NEG_INTS

    VALID_VARIANT_TAG_SETS = (
        list(VALID_NON_NEG_INTS),
    )
    INVALID_VARIANT_TAG_SETS = (
        list(),
        list(VALID_NEG_INTS),
        list(VALID_NON_NEG_INTS) + list(VALID_NON_NEG_INTS),
    )

    VALID_FRACTIONS = tuple(
        {'keep': k, 'pass': p} for k, p in itertools.product(
            VALID_POS_INTS,
            repeat=2,
        ),
    )
    INVALID_FRACTIONS = (
        {},
        { 'keep': 1 },
        { 'pass': 1 },
        { 'keep': 0, 'pass': 1 },
        { 'keep': 1, 'pass': 0 },
        { 'keep': -1, 'pass': 1 },
        { 'keep': 1, 'pass': -1 },
    )

    VALID_QUANTITY_BASES = tuple(
        itertools.chain(
            (
                {
                    'base': b,
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for b, r, bd, rd, lo, mo in itertools.product(
                    VALID_POS_INTS,
                    VALID_NON_NEG_INTS,
                    VALID_POS_INTS,
                    VALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
            (
                { 'base': b } for b in VALID_POS_INTS
            ),
        )
    )
    INVALID_QUANTITY_BASES = tuple(
        itertools.chain(
            # Test empty dict
            (
                {}
            ),
            # Test missing base
            (
                {
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for r, bd, rd, lo, mo in itertools.product(
                    VALID_NON_NEG_INTS,
                    VALID_POS_INTS,
                    VALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
            # Test invalid base
            (
                {
                    'base': b,
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for b, r, bd, rd, lo, mo in itertools.product(
                    INVALID_POS_INTS,
                    VALID_NON_NEG_INTS,
                    VALID_POS_INTS,
                    VALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
            # Test invalid range
            (
                {
                    'base': b,
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for b, r, bd, rd, lo, mo in itertools.product(
                    VALID_POS_INTS,
                    INVALID_NON_NEG_INTS,
                    VALID_POS_INTS,
                    VALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
            # Test invalid base_den
            (
                {
                    'base': b,
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for b, r, bd, rd, lo, mo in itertools.product(
                    VALID_POS_INTS,
                    VALID_NON_NEG_INTS,
                    INVALID_POS_INTS,
                    VALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
            # Test invalid range_den
            (
                {
                    'base': b,
                    'range': r,
                    'base_den': bd,
                    'range_den': rd,
                    'less_ok': lo,
                    'more_ok': mo,
                } for b, r, bd, rd, lo, mo in itertools.product(
                    VALID_POS_INTS,
                    VALID_NON_NEG_INTS,
                    VALID_POS_INTS,
                    INVALID_POS_INTS,
                    (True, False),
                    (True, False),
                )
            ),
        ),
    )

    VALID_QUANTITY_MASSES = tuple(
        dict(d, units=u) for d, u in itertools.product(
            VALID_QUANTITY_BASES,
            argument_schema.ArgumentSchemas.MASS_UNITS
        ),
    )

    VALID_QUANTITY_VOLUMES = tuple(
        dict(d, units=u) for d, u in itertools.product(
            VALID_QUANTITY_BASES,
            argument_schema.ArgumentSchemas.VOLUME_UNITS
        ),
    )

    VALID_QUANTITY_COUNTS = tuple(
        dict(d, units=u) for d, u in itertools.product(
            VALID_QUANTITY_BASES,
            ('whole', 'count', 'sprig', 'unit',)
        ),
    )

    def test_string(self):
        sch = argument_schema.ArgumentSchemas.STRING

        for i in self.VALID_STRINGS:
            sch(i)

        for i in self.INVALID_STRINGS:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_pos_int(self):
        sch = argument_schema.ArgumentSchemas.POS_INT

        for i in self.VALID_POS_INTS:
            sch(i)

        for i in self.INVALID_POS_INTS:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_non_neg_int(self):
        sch = argument_schema.ArgumentSchemas.NON_NEG_INT

        for i in self.VALID_NON_NEG_INTS:
            sch(i)

        for i in self.INVALID_NON_NEG_INTS:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_variant_tag_set(self):
        sch = argument_schema.ArgumentSchemas.VARIANT_TAG_SET

        for i in self.VALID_VARIANT_TAG_SETS:
            sch(i)

        for i in self.INVALID_VARIANT_TAG_SETS:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_fraction(self):
        sch = argument_schema.ArgumentSchemas.FRACTION

        for i in self.VALID_FRACTIONS:
            sch(i)

        for i in self.INVALID_FRACTIONS:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_quantity_base(self):
        sch = argument_schema.ArgumentSchemas.QUANTITY_BASE

        for i in self.VALID_QUANTITY_BASES:
            sch(i)

        for i in self.INVALID_QUANTITY_BASES:
            with self.assertRaises(voluptuous.MultipleInvalid):
                sch(i)

    def test_quantity_mass(self):
        sch = argument_schema.ArgumentSchemas.QUANTITY_MASS

        for i in self.VALID_QUANTITY_MASSES:
            sch(i)

    def test_quantity_volume(self):
        sch = argument_schema.ArgumentSchemas.QUANTITY_VOLUME

        for i in self.VALID_QUANTITY_VOLUMES:
            sch(i)

    def test_quantity_count(self):
        sch = argument_schema.ArgumentSchemas.QUANTITY_COUNT

        for i in self.VALID_QUANTITY_COUNTS:
            sch(i)

if __name__ == '__main__':
    unittest.main()
