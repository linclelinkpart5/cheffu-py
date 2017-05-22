import typing as typ
import re

import modgrammar as mg

import cheffu.interfaces as chin
import cheffu.slot_filter as sf


# # This sorts keys first by character length (longest to shortest), and then subsorts lexicographically ascending (A-Z).
# AllKeywordsSorted = sorted(chin.KeywordToType.keys(), key=lambda s: (-len(s), s))
# AllKeywordsRegexPattern = '({substrs})'.format(substrs='|'.join(re.escape(s) for s in AllKeywordsSorted))
# AllKeywordsRegex = re.compile(AllKeywordsRegexPattern)


# def process(lines: typ.Iterable[str]) -> typ.Iterable[typ.Tuple[str, str]]:
#     count = 0
#     for line in lines:
#         count += 1
#
#         tokens = AllKeywordsRegex.split(line)
#
#         arg_field_tokens = tokens[0::2]
#         keyword_tokens = tokens[1::2]
#
#         # First arg field should consist of only whitespace
#         assert not arg_field_tokens[0].strip()
#
#         # Trim off first arg field
#         arg_field_tokens = arg_field_tokens[1:]
#
#         assert len(arg_field_tokens) == len(keyword_tokens)
#
#         for keyword, arg_field in zip(keyword_tokens, arg_field_tokens):
#             arg_field = arg_field.strip()
#             yield keyword, arg_field


class TokenGroup(list):
    def __init__(self, *args, slot_filter=sf.ALLOW_ALL, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot_filter = slot_filter


def get_keyword_from_td(token_dict):
    assert isinstance(token_dict, dict)
    assert len(token_dict) == 1
    keyword = next(token_dict.keys())
    assert keyword in chin.KeywordToType
    return keyword


def pre_process_groups(procedure: typ.Sequence[typ.Union[typ.Mapping, typ.Sequence]]):
    target_priority = chin.Priority.GRAPH_GEN

    stack = []

    for item in procedure:
        if isinstance(item, list):
            group = item
            item = {chin.Group.keyword: group}

        if isinstance(item, dict):
            token_dict = item
            keyword = get_keyword_from_td(token_dict)
            priority = chin.KeywordToType[keyword].priority

            if target_priority == priority:
                pass


def pre_process_json(procedure: typ.Sequence[typ.Union[typ.Mapping, typ.Sequence]]):
    for item in procedure:
        if isinstance(item, typ.Sequence):
            # Process the sequence/group
            pass
