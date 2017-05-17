import fractions
import decimal
import unittest
import itertools
import collections

import cheffu.grammars as gr
import cheffu.slot_filter as sf


SFRange = collections.namedtuple('SFRange', ('a', 'b'))


class TestGrammars(unittest.TestCase):
    VALID_POS_INTEGERS = frozenset(range(1, 6))
    VALID_NON_NEG_INTEGERS = VALID_POS_INTEGERS | frozenset((0,))

    VALID_POS_FRACTION_DOUBLES = frozenset(
        (i, j) for i, j in itertools.product(VALID_POS_INTEGERS, VALID_POS_INTEGERS)
    )
    VALID_NON_NEG_FRACTION_DOUBLES = frozenset(
        (i, j) for i, j in itertools.product(VALID_NON_NEG_INTEGERS, VALID_POS_INTEGERS)
    )

    VALID_POS_MIXED_NUM_TRIPLES = frozenset(itertools.chain(
        ((i, j, k) for i, (j, k) in itertools.product(VALID_NON_NEG_INTEGERS, VALID_POS_FRACTION_DOUBLES)),
        ((i, j, k) for i, (j, k) in itertools.product(VALID_POS_INTEGERS, VALID_NON_NEG_FRACTION_DOUBLES)),
    ))
    VALID_NON_NEG_MIXED_NUM_TRIPLES = frozenset(
        (i, j, k) for i, (j, k) in itertools.product(VALID_NON_NEG_INTEGERS, VALID_NON_NEG_FRACTION_DOUBLES)
    )

    VALID_POS_DECIMAL_DOUBLES = frozenset(itertools.chain(
        ((i, j) for i, j in itertools.product(VALID_NON_NEG_INTEGERS, VALID_POS_INTEGERS)),
        ((i, j) for i, j in itertools.product(VALID_POS_INTEGERS, VALID_NON_NEG_INTEGERS)),
    ))
    VALID_NON_NEG_DECIMAL_DOUBLES = frozenset(
        (i, j) for i, j in itertools.product(VALID_NON_NEG_INTEGERS, VALID_NON_NEG_INTEGERS)
    )

    VALID_PARTITION_DOUBLES = frozenset(
        (i, j) for i, j in itertools.product(VALID_POS_INTEGERS, VALID_POS_INTEGERS)
    )

    VALID_SLOT_INDICES = VALID_NON_NEG_INTEGERS

    VALID_SLOT_INDEX_RANGES = frozenset(
        (i, j) for i, j in itertools.product(VALID_SLOT_INDICES, VALID_SLOT_INDICES)
    )

    VALID_POS_INTEGER_CONVS = {
        str(i): i for i in VALID_POS_INTEGERS
    }
    VALID_NON_NEG_INTEGER_CONVS = {
        str(i): i for i in VALID_NON_NEG_INTEGERS
    }

    VALID_POS_FRACTION_CONVS = {
        '{}{}{}'.format(i, gr.FRACTION_SEPARATOR, j): fractions.Fraction(i, j) for i, j in VALID_POS_FRACTION_DOUBLES
    }
    VALID_NON_NEG_FRACTION_CONVS = {
        '{}{}{}'.format(i, gr.FRACTION_SEPARATOR, j): fractions.Fraction(i, j) for i, j in VALID_NON_NEG_FRACTION_DOUBLES
    }

    VALID_POS_MIXED_NUM_CONVS = {
        '{}{}{}{}{}'.format(i, gr.MIXED_NUM_SEPARATOR, j, gr.FRACTION_SEPARATOR, k): i + fractions.Fraction(j, k) for i, j, k in VALID_POS_MIXED_NUM_TRIPLES
    }
    VALID_NON_NEG_MIXED_NUM_CONVS = {
        '{}{}{}{}{}'.format(i, gr.MIXED_NUM_SEPARATOR, j, gr.FRACTION_SEPARATOR, k): i + fractions.Fraction(j, k) for i, j, k in VALID_NON_NEG_MIXED_NUM_TRIPLES
    }

    VALID_POS_DECIMAL_CONVS = {
        s: decimal.Decimal(s) for s in ('{}{}{}'.format(i, gr.DECIMAL_SEPARATOR, j) for i, j in VALID_POS_DECIMAL_DOUBLES)
    }
    VALID_NON_NEG_DECIMAL_CONVS = {
        s: decimal.Decimal(s) for s in ('{}{}{}'.format(i, gr.DECIMAL_SEPARATOR, j) for i, j in VALID_NON_NEG_DECIMAL_DOUBLES)
    }

    VALID_NON_NEG_NUMBER_CONVS = {
        **VALID_NON_NEG_MIXED_NUM_CONVS,
        **VALID_NON_NEG_FRACTION_CONVS,
        **VALID_NON_NEG_DECIMAL_CONVS,
        **VALID_NON_NEG_INTEGER_CONVS,
    }
    VALID_POS_NUMBER_CONVS = {
        **VALID_POS_MIXED_NUM_CONVS,
        **VALID_POS_FRACTION_CONVS,
        **VALID_POS_DECIMAL_CONVS,
        **VALID_POS_INTEGER_CONVS,
    }

    VALID_PARTITION_CONVS = {
        '{}{}'.format(i * gr.PARTITION_A_PORTION_FLAG, j * gr.PARTITION_B_PORTION_FLAG): fractions.Fraction(i, i + j) for i, j in VALID_PARTITION_DOUBLES
    }

    VALID_SLOT_INDEX_CONVS = {
        str(i): i for i in VALID_SLOT_INDICES
    }

    VALID_SLOT_INDEX_RANGE_CONVS = {
        '{}{}{}'.format(i, gr.RANGE_SEPARATOR, j): frozenset(range(i, j + 1)) for i, j in VALID_SLOT_INDEX_RANGES
    }

    VALID_SLOT_INDEX_SET_CONVS = {
        '0{sep} 1{sep} 4{rng}7{sep}3'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset({0, 1, 3, 4, 5, 6, 7}),
        '1{rng}5{sep}4{rng}7'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset({1, 2, 3, 4, 5, 6, 7}),
        '0 {sep} 1  {sep}2   {sep}7'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset({0, 1, 2, 7}),
        ' 27'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset({27}),
        ' 0{rng}99'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset(range(0, 100)),
        '99{rng}0'.format(sep=gr.SEQUENCE_ITEM_SEPARATOR, rng=gr.RANGE_SEPARATOR):
            frozenset(),
    }

    VALID_SLOT_FILTER_ALLOW_ALL_CONVS = {
        gr.SLOT_FILTER_ALLOW_ALL_KEYWORD: sf.ALLOW_ALL,
    }

    VALID_SLOT_FILTER_BLOCK_ALL_CONVS = {
        gr.SLOT_FILTER_BLOCK_ALL_KEYWORD: sf.BLOCK_ALL,
    }

    def test_non_neg_integer(self):
        p = gr.NonNegInteger.parser()

        for k, ve in self.VALID_NON_NEG_INTEGER_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_pos_integer(self):
        p = gr.PosInteger.parser()

        for k, ve in self.VALID_POS_INTEGER_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_non_neg_fraction(self):
        p = gr.NonNegFraction.parser()

        for k, ve in self.VALID_NON_NEG_FRACTION_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_pos_fraction(self):
        p = gr.PosFraction.parser()

        for k, ve in self.VALID_POS_FRACTION_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_non_neg_mixed_num(self):
        p = gr.NonNegMixedNum.parser()

        for k, ve in self.VALID_NON_NEG_MIXED_NUM_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_pos_mixed_num(self):
        p = gr.PosMixedNum.parser()

        for k, ve in self.VALID_POS_MIXED_NUM_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_non_neg_decimal(self):
        p = gr.NonNegDecimal.parser()

        for k, ve in self.VALID_NON_NEG_DECIMAL_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_pos_decimal(self):
        p = gr.PosDecimal.parser()

        for k, ve in self.VALID_POS_DECIMAL_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_non_neg_number(self):
        p = gr.NonNegNumber.parser()

        for k, ve in self.VALID_NON_NEG_NUMBER_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_pos_number(self):
        p = gr.PosNumber.parser()

        for k, ve in self.VALID_POS_NUMBER_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_partition(self):
        p = gr.Partition.parser()

        for k, ve in self.VALID_PARTITION_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_slot_index(self):
        p = gr.SlotIndex.parser()

        for k, ve in self.VALID_SLOT_INDEX_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_slot_index_range(self):
        p = gr.SlotIndexRange.parser()

        for k, ve in self.VALID_SLOT_INDEX_RANGE_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_slot_index_set(self):
        p = gr.SlotIndexSet.parser()

        for k, ve in self.VALID_SLOT_INDEX_SET_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_slot_filter_allow_all(self):
        p = gr.SlotFilterAllowAll.parser()

        for k, ve in self.VALID_SLOT_FILTER_ALLOW_ALL_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

    def test_slot_filter_block_all(self):
        p = gr.SlotFilterBlockAll.parser()

        for k, ve in self.VALID_SLOT_FILTER_BLOCK_ALL_CONVS.items():
            va = p.parse_string(k).value()
            self.assertEqual(va, ve)

if __name__ == '__main__':
    unittest.main()
