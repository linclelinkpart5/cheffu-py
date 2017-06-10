"""Validates a Cheffu recipe branch. This logic is variant agnostic,
as this occurs after variants have been processed.

There are several main steps in validating a recipe branch:
* Constructing the token tree. This validates that the correct number of tokens was supplied.
* Processing the constructed token tree. This validates that the typing of tokens was correct.
"""

import typing as typ

import cheffu.interfaces as chin
import cheffu.exceptions as chex

import cheffu.types.tokens as ctpt

# from cheffu.interfaces import TokenType, OptTokenType, TokenTypeSequence, InputTypeSequence
#
# TokenData = typ.Any
#
# TNID = typ.NewType('TNID', int)
# TNIDGen = typ.Callable[[], TNID]
#
# TNIDSet = typ.AbstractSet[TNID]
#
# TNIDStack = typ.Sequence[TNID]
#
#
# class TokenNode(typ.NamedTuple):
#     id: TNID
#     type: TokenType
#     data: TokenData
#     input_ids: TNIDSet
#     # output_ids: TNIDSet
#
#
# TokenNodeMap = typ.Mapping[TNID, TokenNode]
# MutTokenNodeMap = typ.MutableMapping[TNID, TokenNode]
#
#
# class ValidatorException(chex.CheffuBaseException):
#     """Base class for all exceptions raised from the validation module."""
#
#
# class TNIDStackNotEnoughElements(ValidatorException):
#     """Raised when a TNID stack contains less than the expected number of elements."""
#
#
# class InvalidInputTypes(ValidatorException):
#     """Raised when the input types to a Cheffu operation do not match what is expected."""
#
#
# def split_stack(*
#                 , tnid_stack: TNIDStack
#                 , n: int
#                 ) -> typ.Tuple[TNIDStack, TNIDStack]:
#     """Helper to split a M-length stack in two. The first part contains the first (M - N)th items,
#     and the second contains the last Nth. This method avoids a naive slicing of the stack, which fails if N <= 0.
#     """
#     # If N is zero, we expect an empty stack to be sliced off.
#     if n <= 0:
#         return tnid_stack, ()
#
#     suffix = tnid_stack[-n:]
#     prefix = tnid_stack[:-n]
#
#     if len(suffix) != n:
#         raise TNIDStackNotEnoughElements()
#
#     return prefix, suffix
#
#
# # def check_types(*
# #                 , target_types: TokenTypeSequence
# #                 , actual_types: TokenTypeSequence
# #                 ) -> bool:
# #     """Determines if a sequence of token types is valid against a target sequence of token types.
# #     In order to be valid, both sequences must have the same length,
# #     and each type in the actual sequence must be a subclass of the corresponding type in the target sequence.
# #     """
# #     # If the sequence lengths are not equal, cannot be valid.
# #     if len(target_types) != len(actual_types):
# #         return False
# #
# #     # Check to see if the i-th actual type is a subclass of the i-th target type.
# #     for a, t in zip(actual_types, target_types):
# #         if not issubclass(a, t):
# #             return False
# #
# #     return True
#
#
# def test(*
#          , keyword: chin.TokenKeyword
#          ):
#     pass
#
#
# def connect_new_token(*
#                       , token_type: TokenType
#                       , token_data: TokenData
#                       , tnid_stack: TNIDStack
#                       , mut_tn_map: MutTokenNodeMap
#                       , tnid_gen: TNIDGen
#                       ) -> TNIDStack:
#     for pipeline in token_type.pipelines:
#         target_types: InputTypeSequence = pipeline.input_types
#         method: chin.PipelineMethod = pipeline.method
#
#         # See if the top contents of the stack match the expected input types.
#         num_target_types = len(target_types)
#         num_stack_elems = len(tnid_stack)
#
#         # If there are not enough elements in stack for this pipeline, skip it.
#         if num_target_types > num_stack_elems:
#             continue
#
#         remaining_stack, input_tnids = tnid_stack[(num_stack_elems - num_target_types):num_stack_elems]
#
#         # # Get the types of the TNIDs.
#         # # TODO: Check for exceptions!
#         # actual_types: chin.TokenTypeSequence = tuple(mut_tn_map[tnid].type for tnid in input_tnids)
#         #
#         # # If the types in this pipeline do not match the types on the stack, skip this pipeline.
#         # if not check_types(target_types=target_types, actual_types=actual_types):
#         #     continue
#
#         # Create a new token node.
#         tnid = tnid_gen()
#         token_node: TokenNode = TokenNode(id=tnid
#                                           , type=token_type
#                                           , data=token_data
#                                           , input_ids=input_tnids
#                                           )
#
#         # Add new token node to graph.
#         mut_tn_map[tnid] = token_node
#
#         # Append new TNID to remaining stack and return.
#         remaining_stack = (*remaining_stack, tnid)
#         return remaining_stack
#
#     # raise InvalidInputTypes()


def yield_processed_tokens(raw_tokens: typ.Iterable[ctpt.RawToken]) -> typ.Iterable[ctpt.Token]:
    for raw_token in raw_tokens:
        keyword = raw_token.keyword
        data = raw_token.data

        # Check if keyword is valid.
        # TODO: Check and raise exception if not found.
        token_spec = chin.KeywordToType[keyword]

        # Use spec to validate data/argument.
        token_spec.validate_arg(arg=data)
