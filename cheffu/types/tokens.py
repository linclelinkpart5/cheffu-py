"""Type hints for tokens and their direct use cases."""

import collections
import typing as typ
import enum

from cheffu.interfaces import TokenSpec

from cheffu.types.common import UniqueId

# Tokens, representing the pieces of data in Cheffu recipes.
TokenId = UniqueId

# Keyword used to uniquely & uniformly identify token types.
# Also used in the Cheffu text representations.
TokenKeyword = typ.NewType('TokenKeyword', str)

# Raw string argument to a token, before conversion and processing.
TokenArg = str


class RawToken(typ.NamedTuple):
    """A raw token, containing just a keyword and data."""
    keyword: TokenKeyword
    arg: TokenArg

RawTokenSequence = typ.Sequence[RawToken]

# TokenNodeId = typ.NewType('TokenNodeId', int)
# TokenNodeIdSequence = typ.Sequence[TokenNodeId]
#
#
# class TokenNode(typ.NamedTuple):
#     id: TokenNodeId
#     token: Token
#     input_ids: TokenNodeIdSequence

# Result from converting/processing of a token string argument.
TokenData = typ.Any

# Callable that converts/processes a raw token argument into token data.
TokenArgConverter = typ.Callable[[TokenArg], TokenData]

# Token interface, used to determine which interfaces are subclasses of which other interfaces.
TokenInterface = typ.Type[TokenSpec]


class TokenTypeDef(typ.NamedTuple):
    interface: TokenInterface
    keyword: TokenKeyword
    arg_conv: TokenArgConverter
    sigil: TokenKeyword = None

    @property
    def name(self) -> str:
        return self.interface.__name__


class Token(typ.NamedTuple):
    id: TokenId
    type_def: TokenTypeDef
    data: TokenData

TokenSequence = typ.Sequence[Token]
