import modgrammar as mg
import fractions

ALPHA_CHARS = "A-Za-z"
NZ_DIGIT_CHARS = "1-9"
DIGIT_CHARS = "0" + NZ_DIGIT_CHARS
PHRASE_CHARS = "-' \"" + ALPHA_CHARS
STRING_CHARS = PHRASE_CHARS + DIGIT_CHARS + "[]#."

PARTITION_A_PORTION_FLAG = '+'
PARTITION_B_PORTION_FLAG = '-'

MIXED_NUM_SEPERATOR = '_'
FRACTION_SEPARATOR = '/'
DECIMAL_SEPARATOR = '.'

QUANTITY_RANGE_SEPARATOR = '~'
QUANTITY_RANGE_APPROX_FLAG = '~'

grammar_whitespace_mode = 'optional'


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
    grammar = (NonNegInteger, MIXED_NUM_SEPERATOR, NonNegFraction)

    def value(self):
        return self[0].value() + self[2].value()


class PosMixedNum(mg.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = mg.OR(
        (PosInteger, MIXED_NUM_SEPERATOR, NonNegFraction),
        (NonNegInteger, MIXED_NUM_SEPERATOR, PosFraction),
    )

    def value(self):
        return self[0].value() + self[2].value()


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


class Phrase(mg.Grammar):
    grammar = mg.WORD(PHRASE_CHARS)

    def value(self):
        return self.string.strip()


class String(mg.Grammar):
    grammar = (
                  mg.WORD(STRING_CHARS),
              )

    def value(self):
        return self.string.strip()


class Partition(mg.Grammar):
    grammar_whitespace_mode = 'explicit'

    grammar = (
                  mg.ONE_OR_MORE(PARTITION_A_PORTION_FLAG),
                  mg.ONE_OR_MORE(PARTITION_B_PORTION_FLAG),
              )

    def value(self):
        num = len(self[0].string)
        den = len(self.string)
        return fractions.Fraction(num, den)


class PosQuantity(mg.Grammar):
    grammar = (
                  mg.OR(
                      PosFraction,
                      PosDecimal,
                      PosInteger,
                  ),
              )

    def value(self):
        return self[0].value()


class NonNegIntegerSeq(mg.Grammar):
    grammar = (
                  mg.LIST_OF(NonNegInteger)
              )

    def value(self):
        return set(s.value() for s in self[0])


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
                  PosQuantity,
                  mg.OPTIONAL(
                      mg.GRAMMAR(
                          QUANTITY_RANGE_SEPARATOR,
                          PosQuantity,
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
