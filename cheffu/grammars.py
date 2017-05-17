import modgrammar as mg
import modgrammar.extras as mgex
import fractions
import itertools

import cheffu.slot_filter as sf

ALPHA_CHARS = "A-Za-z"
NZ_DIGIT_CHARS = "1-9"
DIGIT_CHARS = "0" + NZ_DIGIT_CHARS
PHRASE_CHARS = "-' \"" + ALPHA_CHARS
STRING_CHARS = PHRASE_CHARS + DIGIT_CHARS + "[]#."

PARTITION_A_PORTION_FLAG = '+'
PARTITION_B_PORTION_FLAG = '-'

MIXED_NUM_SEPARATOR = '_'
FRACTION_SEPARATOR = '/'
DECIMAL_SEPARATOR = '.'

QUANTITY_RANGE_SEPARATOR = '~'
QUANTITY_RANGE_APPROX_FLAG = '~'

SEQUENCE_ITEM_SEPARATOR = ','
RANGE_SEPARATOR = '...'

SLOT_FILTER_ALLOW_ALL_KEYWORD = 'ANY'
SLOT_FILTER_BLOCK_ALL_KEYWORD = 'NONE'

VARIANT_SLOT_SIGIL = '#'
VARIANT_SLOT_INVERT_SIGIL = '!'

grammar_whitespace_mode = 'optional'

# Primitives

class NonNegInteger(mg.Grammar):
    grammar = mg.WORD(DIGIT_CHARS)

    def value(self):
        return int(self.string)


class PosInteger(mg.Grammar):
    grammar = mg.WORD(NZ_DIGIT_CHARS, DIGIT_CHARS)

    def value(self):
        return int(self.string)


class NonNegFraction(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (NonNegInteger, FRACTION_SEPARATOR, PosInteger)

    def value(self):
        return fractions.Fraction(self[0].value(), self[2].value())


class PosFraction(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (PosInteger, FRACTION_SEPARATOR, PosInteger)

    def value(self):
        return fractions.Fraction(self[0].value(), self[2].value())


class NonNegMixedNum(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (NonNegInteger, MIXED_NUM_SEPARATOR, NonNegFraction)

    def value(self):
        return self[0].value() + self[2].value()


class PosMixedNum(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = mg.OR(
        (PosInteger, MIXED_NUM_SEPARATOR, NonNegFraction),
        (NonNegInteger, MIXED_NUM_SEPARATOR, PosFraction),
    )

    def value(self):
        return self[0][0].value() + self[0][2].value()


class NonNegDecimal(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (NonNegInteger, DECIMAL_SEPARATOR, NonNegInteger)

    def value(self):
        return fractions.Fraction(self.string)


class PosDecimal(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = mg.OR(
        (NonNegInteger, DECIMAL_SEPARATOR, PosInteger),
        (PosInteger, DECIMAL_SEPARATOR, NonNegInteger),
    )

    def value(self):
        return fractions.Fraction(self.string)


class NonNegNumber(mg.Grammar):
    grammar = mg.OR(NonNegMixedNum, NonNegFraction, NonNegDecimal, NonNegInteger)

    def value(self):
        return self[0].value()


class PosNumber(mg.Grammar):
    grammar = mg.OR(PosMixedNum, PosFraction, PosDecimal, PosInteger)

    def value(self):
        return self[0].value()


class Partition(mg.Grammar):
    grammar_whitespace_mode = 'explicit'

    grammar = (mg.ONE_OR_MORE(PARTITION_A_PORTION_FLAG), mg.ONE_OR_MORE(PARTITION_B_PORTION_FLAG))

    def value(self):
        num = len(self[0].string)
        den = len(self.string)
        return fractions.Fraction(num, den)


# Slot Filters

class SlotIndex(mg.Grammar):
    grammar = NonNegInteger

    def value(self):
        return self[0].value()

    def yield_value(self):
        yield self.value()


class SlotIndexRange(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (
        SlotIndex,
        RANGE_SEPARATOR,
        SlotIndex,
    )

    def value(self):
        return frozenset(range(self[0].value(), self[2].value() + 1))

    def yield_value(self):
        yield from self.value()


class SlotIndexSet(mg.Grammar):
    grammar = mg.LIST_OF(mg.OR(SlotIndex, SlotIndexRange), sep=SEQUENCE_ITEM_SEPARATOR, min=1)

    def value(self):
        return frozenset(self.yield_value())

    def yield_value(self):
        yield from itertools.chain.from_iterable(
            s.yield_value() for s in self[0] if s.string != SEQUENCE_ITEM_SEPARATOR
        )


class SlotFilterAllowAll(mg.Grammar):
    grammar = SLOT_FILTER_ALLOW_ALL_KEYWORD

    @staticmethod
    def value():
        return sf.ALLOW_ALL


class SlotFilterBlockAll(mg.Grammar):
    grammar = SLOT_FILTER_BLOCK_ALL_KEYWORD

    @staticmethod
    def value():
        return sf.BLOCK_ALL


class SlotFilterCustom(mg.Grammar):
    grammar = (mg.OPTIONAL(VARIANT_SLOT_INVERT_SIGIL), SlotIndexSet)

    def value(self):
        if self[0]:
            sf_gen = sf.make_black_list
        else:
            sf_gen = sf.make_white_list

        return sf_gen(*self[1].yield_value())


class VariantSlotFilter(mg.Grammar):
    grammar = (
        VARIANT_SLOT_SIGIL,
        mg.OR(
            SlotFilterAllowAll,
            SlotFilterBlockAll,
            SlotFilterCustom,
        ),
    )

    def value(self):
        return self[1].value()


class Phrase(mg.Grammar):
    grammar = mgex.QuotedString

    def value(self):
        return self.string.strip()


class String(mg.Grammar):
    grammar = mgex.QuotedString

    def value(self):
        return self.string.strip()


class Quantity(mg.Grammar):
    # TODO: Stub for now, make this work.
    grammar = (
                  mg.ANY
              )

    def value(self):
        return self[0].string


class Time(mg.Grammar):
    grammar_whitespace_mode = 'explicit'

    unit_lookup = {
        's': 'sec',
        'sec': 'sec',
        'm': 'min',
        'min': 'min',
        'h': 'hour',
        'hour': 'hour',
    }

    grammar = (
        mg.OPTIONAL(QUANTITY_RANGE_APPROX_FLAG),
        PosNumber,
        mg.OPTIONAL(
                      mg.GRAMMAR(
                          QUANTITY_RANGE_SEPARATOR,
                          PosNumber,
                      ),
                  ),
        mg.OPTIONAL(QUANTITY_RANGE_APPROX_FLAG),
        mg.WHITESPACE,
        mg.OR(
                      *unit_lookup.keys()
                  ),
              )

    def value(self):
        return {
            'less_ok': True if self[0] else False,
            'base': self[1].value().numerator,
            'base_den': self[1].value().denominator,
            'range': self[2][1].value().numerator if self[2] else 0,
            'range_den': self[2][1].value().denominator if self[2] else 1,
            'units': self.unit_lookup[self[5].string],
        }
