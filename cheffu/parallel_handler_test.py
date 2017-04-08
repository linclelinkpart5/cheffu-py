import collections
import typing as typ
import itertools
import functools
import pprint
import uuid
import pydot

# TODO: Only for __main__ testing, remove when done!
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import cheffu.slot_filter as sf

# Each nodule is represented by a UUID
Nodule = typ.NewType('Nodule', uuid.UUID)
NoduleSegment = typ.Tuple[Nodule, Nodule]
NoduleGen = typ.Callable[[], Nodule]

Token = typ.NewType('Token', str)
AltSequence = typ.Sequence['FilteredAlt']
PathItem = typ.Union[Token, AltSequence]
TokenPath = typ.Sequence[PathItem]

FilteredAlt = typ.NamedTuple('FilteredAlt', [('items', TokenPath), ('slot_filter', sf.SlotFilter)])
UnfilteredAlt = functools.partial(FilteredAlt, slot_filter=sf.ALLOW_ALL)
FilteredNull = functools.partial(FilteredAlt, items=())
UnfilteredNull = functools.partial(UnfilteredAlt, items=())

SlotFilterStack = typ.List[sf.SlotFilter]

SlotFilterStackCommand = typ.Callable[[SlotFilterStack], None]


def push_slot_filter_cmd(slot_filter: sf.SlotFilter) -> SlotFilterStackCommand:
    def inner(slot_filter_stack: SlotFilterStack) -> None:
        slot_filter_stack.append(slot_filter)

    return inner


def pop_slot_filter_cmd() -> SlotFilterStackCommand:
    def inner(slot_filter_stack: SlotFilterStack) -> None:
        slot_filter_stack.pop()

    return inner


def no_op_slot_filter_cmd() -> SlotFilterStackCommand:
    def inner(_: SlotFilterStack) -> None:
        pass

    return inner

NoduleSkewer = typ.Tuple[
    typ.MutableSequence[Token],
    SlotFilterStackCommand,
]

NoduleSkewerSequence = typ.MutableSequence[
    NoduleSkewer
]

NoduleEdgeMap = typ.MutableMapping[
    NoduleSegment,
    NoduleSkewerSequence,
]

TOKEN_LIST: TokenPath = (
    Token('A'),
    Token('B'),
    (
        UnfilteredAlt(
            items=('C', 'D',),
        ),
        UnfilteredAlt(
            items=('C~', 'D~',),
        ),
    ),
    Token('E'),
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
    Token('H'),
    (
        UnfilteredAlt(
            items=('I',),
        ),
        UnfilteredNull(),
    ),
    Token('J'),
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
    Token('L'),
    (
        FilteredAlt(
            items=('M', 'N', 'NN', 'NNN',),
            slot_filter=sf.make_white_list(0),
        ),
    ),
    Token('O'),
    (
        FilteredAlt(
            items=(
                (
                    FilteredAlt(
                        items=('P',),
                        slot_filter=sf.make_white_list(0),
                    ),
                    FilteredAlt(
                        items=('Q',),
                        slot_filter=sf.make_white_list(1),
                    ),
                ),
                Token('R'),
                (
                    FilteredAlt(
                        items=('S',),
                        slot_filter=sf.make_white_list(0),
                    ),
                ),
            ),
            slot_filter=sf.make_white_list(0),
        ),
        FilteredAlt(
            items=(
                (
                    FilteredAlt(
                        items=('P~',),
                        slot_filter=sf.make_white_list(0),
                    ),
                    FilteredAlt(
                        items=('Q~',),
                        slot_filter=sf.make_white_list(1),
                    ),
                ),
                Token('R~'),
                (
                    FilteredAlt(
                        items=('S~',),
                        slot_filter=sf.make_white_list(0),
                    ),
                    FilteredNull(
                        slot_filter=sf.make_white_list(1),
                    ),
                ),
            ),
            slot_filter=sf.make_white_list(2),
        ),
    ),
    Token('T'),
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


def normalize_alt_sequence(alt_sequence: AltSequence) -> AltSequence:
    # Calculate the value of the else-filter
    coverage_filter = functools.reduce(
        sf.union,
        (alt.slot_filter for alt in alt_sequence),
        sf.BLOCK_ALL,
    )
    else_filter = sf.invert(coverage_filter)

    # If else-filter is not block-all, append a null branch with the else-filter to filtered alts
    if else_filter != sf.BLOCK_ALL:
        alt_sequence += (FilteredAlt(slot_filter=else_filter),)

    # From filtered alts, drop any that have a block-all filter
    alt_sequence = tuple(filtered_alt for filtered_alt in alt_sequence if filtered_alt.slot_filter != sf.BLOCK_ALL)

    # Coalesce null branches into a single one
    # TODO: If possible, coalesce non-null branches as well, but much trickier
    null_alts = tuple(alt for alt in alt_sequence if not alt.items)
    alt_sequence = tuple(alt for alt in alt_sequence if alt.items)

    # Coalescing happens by combining the filters into one
    if null_alts:
        null_filter = sf.BLOCK_ALL
        for null_alt in null_alts:
            null_filter = sf.union(null_filter, null_alt.slot_filter)

        alt_sequence += (FilteredNull(slot_filter=null_filter),)

    # Sanity checks
    # There should be at most one null branch
    assert(sum(1 if not alt.items else 0 for alt in alt_sequence) <= 1)
    # The union of all filters should equal an allow-all filter
    assert(functools.reduce(sf.union, (alt.slot_filter for alt in alt_sequence), sf.BLOCK_ALL) == sf.ALLOW_ALL)

    return alt_sequence


def process(token_path: TokenPath, start_nodule: Nodule, nodule_gen: NoduleGen=uuid.uuid4):
    slot_filter_stack: SlotFilterStack = []

    # Create return data structure
    nodule_edge_map: NoduleEdgeMap = collections.defaultdict(list)

    # We will always have at least one other nodule, to make one segment
    curr_nodule: Nodule = nodule_gen()

    # Make that segment now
    curr_segment: NoduleSegment = (start_nodule, curr_nodule)

    curr_skewer: NoduleSkewer = ([], no_op_slot_filter_cmd())

    for path_item in token_path:
        if isinstance(path_item, Token):
            # Thread onto the current skewer
            token = path_item
            curr_skewer[0].append(token)
        elif isinstance(path_item, FilteredAlt):
            pass


# UUID_TO_TOKEN_MAP = {}
# PARENT_UUID_TO_CHILD_UUIDS_MAP = collections.defaultdict(set)
# ADJACENCY_LOOKUP_MAP = collections.defaultdict(
#     lambda: collections.defaultdict(
#         lambda: sf.ALLOW_ALL
#     )
# )
# ADJACENCY_HISTORY_LOOKUP_MAP = collections.defaultdict(
#     lambda: collections.defaultdict(list)
# ),]


# def new_nodule() -> Nodule:
#     return Nodule(uuid.uuid4())
#
#
# def process(token_path: TokenPath) -> typ.Tuple[Nodule, Nodule, NoduleEdgeStateMap]:
#     # Starting and closing nodule UUIDs for the entire path
#     start_uuid = new_nodule()
#     close_uuid = new_nodule()
#
#     # Nodule edge state map, represented as a dict mapping nodules to dicts, which map nodules to nodule edge states
#     nodule_edge_state_map = collections.defaultdict(dict)
#
#     # This holds the current 'attach to' nodule
#     current_anchor_nodule = start_uuid
#
#     for item in token_path:
#         if isinstance(item, tuple):
#             # This is an alt tuple
#             alt_sequence = item
#
#             # Normalize
#             alt_sequence = normalize_alt_sequence()
#         else:
#             # Assume we have a token
#             pass
#
#     def process_token_path(token_path: TokenPath, parent_uuids: typ.Sequence=tuple()) -> typ.Tuple[uuid.UUID, uuid.UUID]:
#         most_recent_parent_uuid = None
#
#         # Iterate over all items in this path
#         for item in token_path:
#             # Check if item is a tuple or token
#             if isinstance(item, tuple):
#                 # This is a tuple of filtered alts
#                 alt_sequence = item
#                 process_alt_sequence(alt_sequence)
#             else:
#                 # This is a token
#                 # Make a new UUID for it
#                 new_uuid = uuid.uuid4()
#
#                 if most_recent_parent_uuid:
#                     # There is a new edge, add it to the adjacency edge filter map
#                     adj_edge_filter_map[most_recent_parent_uuid][new_uuid] = make_slot_filter_state()
#
#         return sub_start_uuid, sub_close_uuid
#
#     def process_alt_sequence(alt_sequence: AltSequence):
#         for alt in alt_sequence:
#             items = alt.items
#             slot_filter = alt.slot_filter
#             # TODO: CONTINUE HERE
#
#     return start_uuid, close_uuid, adj_edge_filter_map

# def process_alt_set(filtered_alts, parent_uuids):
#     ret = []
#
#     # Normalize the filtered alts
#     filtered_alts = normalize_alt_sequence(filtered_alts)
#     # print(filtered_alts)
#
#     for filtered_alt in filtered_alts:
#         items = filtered_alt.items
#         slot_filter = filtered_alt.slot_filter
#
#         new_parent_uuids = organize(items, parent_uuids, incoming_slot_filter=slot_filter)
#         ret.append(new_parent_uuids)
#
#     # For each branch, return the most recent parent UUID list
#     # TODO: This needs to return a:
#     #       1) start-item UUIDs, if available
#     #       2) close-item UUIDs, if available
#     #       3) start-edge slot filter, if available
#     #       4) close-edge slot filter, if available
#     return tuple(itertools.chain.from_iterable(ret))
#
# def organize(tokens, parent_uuids, incoming_slot_filter=sf.ALLOW_ALL, incoming_slot_filter_history=()):
#     # Keep track of the outgoing slot filter and history
#     outgoing_slot_filter = incoming_slot_filter
#     outgoing_slot_filter_history = incoming_slot_filter_history
#
#     for token in tokens:
#         if not isinstance(token, tuple):
#             # Generate a new UUID for this token, and add it to the lookup map
#             new_uuid = uuid.uuid4()
#             UUID_TO_TOKEN_MAP[new_uuid] = token
#
#             for parent_uuid in parent_uuids:
#                 ADJACENCY_LOOKUP_MAP[parent_uuid][new_uuid] = incoming_slot_filter
#
#             # # The gate has been set, reset the filter
#             # if current_filter != sf.ALLOW_ALL:
#             #     current_filter = sf.ALLOW_ALL
#
#             # The outgoing slot filter and history stays the same
#
#             # The parent UUIDs get updated
#             parent_uuids = (new_uuid,)
#         else:
#             # These are actually filtered alts
#             filtered_alts = token
#
#             # Perform organization of each split branch
#             for filtered_alt in filtered_alts:
#                 # At this point, we need the UUIDs of the last items before this filtered alt set
#                 start_item_uuids, close_item_uuids, start_edge_slot_filter, close_edge_slot_filter = process_alt_set(filtered_alt, parent_uuids)
#             # The new list of parent UUIDs will be the last UUID of each branch
#             parent_uuids = process_alt_set(filtered_alts, parent_uuids) # TODO: This needs to return a filter and filter history
#
#     # TODO: Add an 'outgoing_slot_filter' return value
#     return parent_uuids








# def process_alt_set(filtered_alts, parent_uuids):
#     ret = []
#
#     # Normalize the filtered alts
#     filtered_alts = normalize_alt_sequence(filtered_alts)
#     print(filtered_alts)
#
#     for i, filtered_alt in enumerate(filtered_alts):
#         items = filtered_alt.items
#         slot_filter = filtered_alt.slot_filter
#
#         new_parent_uuids = organize(items, parent_uuids, current_filter=slot_filter)
#         ret.append(new_parent_uuids)
#
#     # TODO: Need to finish the branch with the right slot filter as well
#
#     # For each branch, return the most recent parent UUID list
#     return tuple(itertools.chain.from_iterable(ret))
#
# # TODO: Add an 'incoming_slot_filter' argument
# # TODO: Add an 'incoming_slot_filter_history' argument
# def organize(tokens, parent_uuids, current_filter=sf.ALLOW_ALL):
#     for token in tokens:
#         if not isinstance(token, tuple):
#             # Generate a new UUID for this token, and add it to the lookup map
#             new_uuid = uuid.uuid4()
#             UUID_TO_TOKEN_MAP[new_uuid] = token
#
#             for parent_uuid in parent_uuids:
#                 ADJACENCY_LOOKUP_MAP[parent_uuid][new_uuid] = current_filter
#
#             # # The gate has been set, reset the filter
#             # if current_filter != sf.ALLOW_ALL:
#             #     current_filter = sf.ALLOW_ALL
#
#             parent_uuids = (new_uuid,)
#         else:
#             # These are actually filtered alts
#             filtered_alts = token
#
#             # Perform organization of each split branch
#             # The new list of parent UUIDs will be the last UUID of each branch
#             parent_uuids = process_alt_set(filtered_alts, parent_uuids)
#
#     # TODO: Add an 'outgoing_slot_filter' return value
#     return parent_uuids

# UUID_TO_TOKEN_MAP[START_UUID] = '{start}'
# UUID_TO_TOKEN_MAP[CLOSE_UUID] = '{close}'
# last_parents = organize(TOKEN_LIST, {START_UUID})
# for last_parent in last_parents:
#     ADJACENCY_LOOKUP_MAP[last_parent][CLOSE_UUID] = sf.ALLOW_ALL
#
# # Sanity checks
# edge_pairs = [(a, b) for a, av in ADJACENCY_LOOKUP_MAP.items() for b in av.keys()]
# edge_pairs_set = set(edge_pairs)
# assert len(edge_pairs) == len(edge_pairs_set)
#
# UUID_TO_GV_NODE = {}
# UUID_PAIR_TO_GV_EDGE = collections.defaultdict(dict)
# GRAPH = pydot.Dot(graph_type='digraph', strict=False)
#
# GRAPH_NODES = []
# GRAPH_EDGES = []
#
# frontier = collections.deque()
# visited = set()
#
# frontier.appendleft(START_UUID)
# visited.add(START_UUID)
#
# while frontier:
#     curr_uuid = frontier.pop()
#
#     curr_token = UUID_TO_TOKEN_MAP[curr_uuid]
#
#     # Make a GV node for this UUID
#     GRAPH_NODES.append(pydot.Node(str(curr_uuid), label=curr_token))
#
#     adjacency_gates = ADJACENCY_LOOKUP_MAP[curr_uuid]
#     for succ_uuid, slot_filter in adjacency_gates.items():
#         # Make a GV edge for this successor UUID
#         GRAPH_EDGES.append(pydot.Edge(str(curr_uuid), str(succ_uuid), label=sf.pretty_string(slot_filter)))
#
#         if succ_uuid not in visited:
#             frontier.appendleft(succ_uuid)
#             visited.add(succ_uuid)
#
# assert GRAPH_NODES
# assert GRAPH_EDGES
#
# for node in GRAPH_NODES:
#     GRAPH.add_node(node)
#
# for edge in GRAPH_EDGES:
#     GRAPH.add_edge(edge)
#
# GRAPH.write_png('out.png')
