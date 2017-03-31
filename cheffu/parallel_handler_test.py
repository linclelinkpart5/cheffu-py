from collections import namedtuple
from collections import defaultdict
from functools import partial, reduce
import typing
import itertools

import slot_filter as sf

FilteredAlt = namedtuple('FilteredAlt', ('items', 'slot_filter'))
UnfilteredAlt = partial(FilteredAlt, slot_filter=sf.ALLOW_ALL)
FilteredNull = partial(FilteredAlt, items=())
UnfilteredNull = partial(UnfilteredAlt, items=())

# A
# B
# [ C D | C' D' ]
# E
# [ F G #1 | F' #2 | G' #1,2 ]
# H
# [ I | ]
# J
# [ K #1 | K' #2 | #3 ]
# L
# [ M N #1 ]
# O
# [
#    [ P #1 | Q #2 ]
#    R
#    [ S #1 ]
# #1
# |
#    [ P' #1 | Q' #2 ]
#    R'
#    [ S' #1 | #2 ]
# #3
# ]
# T
# [ U | V #2 | #3 ]

TOKEN_LIST = (
    'A',
    'B',
    (
        UnfilteredAlt(
            items=('C', 'D',),
        ),
        UnfilteredAlt(
            items=('C~', 'D~',),
        ),
    ),
    # 'E',
    (
        FilteredAlt(
            items=('F', 'G',),
            slot_filter=sf.make_white_list(0),
        ),
        FilteredAlt(
            items=('F~',),
            slot_filter=sf.make_white_list(1),
        ),
        FilteredAlt(
            items=('G~',),
            slot_filter=sf.make_white_list(0, 1),
        ),
    ),
    'H',
    (
        UnfilteredAlt(
            items=('I',),
        ),
        UnfilteredNull(),
    ),
    'J',
    (
        FilteredAlt(
            items=('K',),
            slot_filter=sf.make_white_list(0),
        ),
        FilteredAlt(
            items=('K~',),
            slot_filter=sf.make_white_list(1),
        ),
        FilteredNull(
            slot_filter=sf.make_white_list(2),
        ),
    ),
    'L',
    (
        FilteredAlt(
            items=('M', 'N',),
            slot_filter=sf.make_white_list(0),
        ),
    ),
    'O',
    # (
    #     FilteredAlt(
    #         items=(
    #             (
    #                 FilteredAlt(
    #                     items=('P',),
    #                     slot_filter=sf.make_white_list(0),
    #                 ),
    #                 FilteredAlt(
    #                     items=('Q',),
    #                     slot_filter=sf.make_white_list(1),
    #                 ),
    #             ),
    #             'R',
    #             (
    #                 FilteredAlt(
    #                     items=('S',),
    #                     slot_filter=sf.make_white_list(0),
    #                 ),
    #             ),
    #         ),
    #         slot_filter=sf.make_white_list(0),
    #     ),
    #     FilteredAlt(
    #         items=(
    #             (
    #                 FilteredAlt(
    #                     items=('P~',),
    #                     slot_filter=sf.make_white_list(0),
    #                 ),
    #                 FilteredAlt(
    #                     items=('Q~',),
    #                     slot_filter=sf.make_white_list(1),
    #                 ),
    #             ),
    #             'R~',
    #             (
    #                 FilteredAlt(
    #                     items=('S~',),
    #                     slot_filter=sf.make_white_list(0),
    #                 ),
    #                 FilteredNull(
    #                     slot_filter=sf.make_white_list(1),
    #                 ),
    #             ),
    #         ),
    #         slot_filter=sf.make_white_list(2),
    #     ),
    # ),
    'T',
    (
        UnfilteredAlt(
            items=('U',),
        ),
        FilteredAlt(
            items=('V',),
            slot_filter=sf.make_white_list(1),
        ),
        FilteredNull(
            slot_filter=sf.make_white_list(2),
        ),
    ),
)

# from pydot import (
#     Dot,
#     Node,
#     Edge,
# )

# // let s be the source node
# frontier = new Queue()
# mark root visited (set root.distance = 0)
# frontier.push(root)
# while frontier not empty {
#     Vertex v = frontier.pop()
#     for each successor v' of v {
# 	if v' unvisited {
# 	    frontier.push(v')
# 	    mark v' visited (v'.distance = v.distance + 1)
# 	}
#     }
# }

import uuid
import collections

UUID_TO_TOKEN_MAP = {}
PARENT_UUID_TO_CHILD_UUIDS_MAP = collections.defaultdict(set)
UUID_ADJACENCY_GATES = defaultdict(lambda: defaultdict(lambda: sf.ALLOW_ALL))

START_UUID = uuid.uuid4()
CLOSE_UUID = uuid.uuid4()

frontier = collections.deque()
visited = set()

def treeify(items, parent_uuids):
    # Loop over each item in list
    for item in items:
        if isinstance(item, FilteredAlt):
            # The item is a tagged alt, containing subitems
            tagged_alt = item

            # Obtain the list of subitems and the slot_filter
            subitems, slot_filter = tagged_alt.items, tagged_alt.slot_filter

            # Each item in this tagged_alt may be a token or another tagged_alt

        # elif isinstance(item, str):
        else:
            # The item is an actual token
            token = item

            # Generate a new UUID to tag this token with
            new_uuid = uuid.uuid4()
            UUID_TO_TOKEN_MAP[new_uuid] = token

            # For each parent UUID
            for parent_uuid in parent_uuids:
                # Make an edge from the parent to this new child
                PARENT_UUID_TO_CHILD_UUIDS_MAP[parent_uuid].add(new_uuid)

            # Set the parent UUIDs for next iteration to be this one
            parent_uuids = (new_uuid,)




# def sub_branch(token_alts, parent_uuids):
#     ret = []
#
#     # Check if each token_alt is tagged, if so, need a short-circuit
#     total_filter = reduce(sf.union, (ta.slot_filter for ta in token_alts), sf.BLOCK_ALL)
#     if total_filter != sf.ALLOW_ALL:
#         else_clause = (FilteredNull(slot_filter=sf.invert(total_filter),),)
#         print('Need else clause', token_alts, else_clause)
#         token_alts = token_alts + else_clause
#
#     for i, token_alt in enumerate(token_alts):
#         token_list = token_alt.tokens
#         token_slot_filter = token_alt.slot_filter
#
#         new_parent_uuids = organize(token_list, parent_uuids, current_filter=token_slot_filter)
#         ret.append(new_parent_uuids)
#
#     # For each branch, return the most recent parent UUID list
#     return tuple(itertools.chain.from_iterable(ret))
#
# def organize(tokens, parent_uuids, current_filter=sf.ALLOW_ALL):
#     for token in tokens:
#         if not isinstance(token, tuple):
#             # Generate a new UUID for this token, and add it to the lookup map
#             new_uuid = uuid4()
#             UUID_TO_TOKEN_MAP[new_uuid] = token
#
#             print('Bare token', token, current_filter)
#
#             for parent_uuid in parent_uuids:
#                 UUID_ADJACENCY_GATES[parent_uuid][new_uuid] = current_filter
#
#             # The gate has been set, reset the filter
#             if current_filter != sf.ALLOW_ALL:
#                 current_filter = sf.ALLOW_ALL
#
#             parent_uuids = (new_uuid,)
#         else:
#             # These are actually token alts
#             token_alts = token
#
#             print('Token alts', token_alts, current_filter)
#
#             # Perform organization of each split branch
#             # The new list of parent UUIDs will be the last UUID of each branch
#             parent_uuids = sub_branch(token_alts, parent_uuids)
#
#     return parent_uuids
#
# UUID_TO_TOKEN_MAP[START_UUID] = '{start}'
# UUID_TO_TOKEN_MAP[CLOSE_UUID] = '{close}'
# last_parents = organize(TOKEN_LIST, {START_UUID})
# for last_parent in last_parents:
#     UUID_ADJACENCY_GATES[last_parent][CLOSE_UUID] = sf.ALLOW_ALL
#
# from pprint import pprint
#
# plain_edges = []
# for a_uuid, d in UUID_ADJACENCY_GATES.items():
#     for b_uuid, slot_filter in d.items():
#         plain_edges.append((UUID_TO_TOKEN_MAP[a_uuid], UUID_TO_TOKEN_MAP[b_uuid], slot_filter))
# plain_edges.sort()
#
# pprint(plain_edges)
# pprint(UUID_ADJACENCY_GATES)

# UUID_TO_GV_NODE = {}
# GRAPH = Dot(graph_type='digraph', strict=True)
#
# def dump(frontier, previous_uuid=None):
#     if frontier:
#         for uuid in frontier:
#             token = UUID_TO_TOKEN_MAP[uuid]
#
#             if uuid not in UUID_TO_GV_NODE:
#                 UUID_TO_GV_NODE[uuid] = Node(str(uuid), label=token)
#                 GRAPH.add_node(UUID_TO_GV_NODE[uuid])
#             node = UUID_TO_GV_NODE[uuid]
#
#             if previous_uuid:
#                 # Make edges
#                 previous_node = UUID_TO_GV_NODE[previous_uuid]
#                 philter = UUID_ADJACENCY_GATES[previous_uuid][uuid]
#                 edge = Edge(previous_node, node, label=str(philter))
#                 GRAPH.add_edge(edge)
#
#             new_frontier = set(UUID_ADJACENCY_GATES[uuid].keys())
#             dump(new_frontier, previous_uuid=uuid)
#
# dump(UUID_ADJACENCY_GATES[START_UUID])
# GRAPH.write_png('out.png')
