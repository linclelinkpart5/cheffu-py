import collections
import typing as typ
import itertools
import functools
import uuid
import pydot

import cheffu.slot_filter as sf

# Nodule = typ.NewType('Nodule', uuid.UUID)
Nodule = typ.NewType('Nodule', int)
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

StackDirection = typ.NewType('StackDirection', bool)

STACK_PUSH = StackDirection(True)
STACK_POP = StackDirection(False)

# Need to separate slot filter in order to parse and view
SlotFilterStackCommand = typ.Optional[typ.Tuple[StackDirection, sf.SlotFilter]]


# def push_slot_filter_cmd(slot_filter: sf.SlotFilter) -> SlotFilterStackCommand:
#     def inner(slot_filter_stack: SlotFilterStack) -> None:
#         slot_filter_stack.append(slot_filter)
#
#     return inner
#
#
# def pop_slot_filter_cmd(expected_slot_filter: sf.SlotFilter) -> SlotFilterStackCommand:
#     def inner(slot_filter_stack: SlotFilterStack) -> None:
#         value = slot_filter_stack.pop()
#         if value != expected_slot_filter:
#             raise Exception()
#
#     return inner
#
#
# def no_op_slot_filter_cmd() -> SlotFilterStackCommand:
#     def inner(_: SlotFilterStack) -> None:
#         pass
#
#     return inner

NoduleSkewer = typ.NamedTuple('NoduleSkewer', [('tokens', typ.Sequence[Token]), ('command', SlotFilterStackCommand)])

NoduleEdgeMap = typ.MutableMapping[
    Nodule,
    typ.MutableMapping[
        Nodule,
        NoduleSkewer,
    ],
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
        alt_sequence += (FilteredNull(slot_filter=else_filter),)

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


def connect(*
            , start_nodule: Nodule
            , close_nodule: Nodule
            , nodule_edge_map: NoduleEdgeMap
            , encountered_tokens: typ.Sequence[Token]
            , slot_filter_stack_command: SlotFilterStackCommand
            ) -> None:
    nodule_skewer: NoduleSkewer = NoduleSkewer(tokens=encountered_tokens, command=slot_filter_stack_command)
    nodule_edge_map[start_nodule][close_nodule] = nodule_skewer


def process_token_path(*
                       , token_path: TokenPath
                       , start_nodule: Nodule
                       , close_nodule: Nodule
                       , nodule_gen: NoduleGen
                       , nodule_edge_map: NoduleEdgeMap
                       , slot_filter_stack_command: SlotFilterStackCommand
                       ) -> None:
    # Keep track of the most recent parent nodule
    curr_parent_nodule: Nodule = start_nodule

    # Tokens encountered directly on this path
    encountered_tokens: typ.MutableSequence[Token] = []

    # Process each path item
    for path_item in token_path:
        if isinstance(path_item, tuple):
            alt_sequence: AltSequence = typ.cast(AltSequence, path_item)

            # Create a new nodule, and close current skewer
            new_nodule: Nodule = nodule_gen()
            connect(start_nodule=curr_parent_nodule,
                    close_nodule=new_nodule,
                    nodule_edge_map=nodule_edge_map,
                    encountered_tokens=encountered_tokens,
                    slot_filter_stack_command=slot_filter_stack_command,
                    )

            # Reset encountered tokens
            encountered_tokens = []

            # Update current parent nodule
            curr_parent_nodule = new_nodule

            # Generate new close nodule for alts
            alt_sequence_close_nodule: Nodule = nodule_gen()

            # Process the alt sequence
            process_alt_sequence(alt_sequence=alt_sequence,
                                 start_nodule=curr_parent_nodule,
                                 close_nodule=alt_sequence_close_nodule,
                                 nodule_gen=nodule_gen,
                                 nodule_edge_map=nodule_edge_map,
                                 )

            # Update current parent nodule
            curr_parent_nodule = alt_sequence_close_nodule
        elif isinstance(path_item, str):
            token: Token = typ.cast(Token, path_item)

            # Add to the list of encountered tokens
            encountered_tokens.append(token)

    # Close the path by making an edge from the current parent nodule to the close nodule
    connect(start_nodule=curr_parent_nodule,
            close_nodule=close_nodule,
            nodule_edge_map=nodule_edge_map,
            encountered_tokens=encountered_tokens,
            slot_filter_stack_command=slot_filter_stack_command,
            )


def process_alt_sequence(*
                         , alt_sequence: AltSequence
                         , start_nodule: Nodule
                         , close_nodule: Nodule
                         , nodule_gen: NoduleGen
                         , nodule_edge_map: NoduleEdgeMap
                         ):
    # Normalize alt sequence
    alt_sequence = normalize_alt_sequence(alt_sequence)
    assert alt_sequence, 'Alt sequence is empty'

    # Process each alt
    for alt in alt_sequence:
        # Generate a new intermediate nodule
        inter_nodule = nodule_gen()

        # Unpack alt
        token_path: TokenPath = alt.items
        slot_filter: sf.SlotFilter = alt.slot_filter

        # Generate stack operations
        slot_filter_stack_push: SlotFilterStackCommand = (STACK_PUSH, slot_filter)
        slot_filter_stack_pop: SlotFilterStackCommand = (STACK_POP, slot_filter)

        # Process items as another token path, connecting them to intermediate nodule
        # Remember to add a push command
        process_token_path(token_path=token_path,
                           start_nodule=start_nodule,
                           close_nodule=inter_nodule,  # NOTE!
                           nodule_gen=nodule_gen,
                           nodule_edge_map=nodule_edge_map,
                           slot_filter_stack_command=slot_filter_stack_push,
                           )

        # Connect intermediate nodule to close nodule
        # This section will never contain tokens, but will have a pop command
        connect(start_nodule=inter_nodule,
                close_nodule=close_nodule,
                nodule_edge_map=nodule_edge_map,
                encountered_tokens=[],
                slot_filter_stack_command=slot_filter_stack_pop,
                )


def process(token_path: TokenPath, nodule_gen: NoduleGen=None):
    if nodule_gen is None:
        counter = itertools.count()

        def nodule_gen():
            return next(counter)

    # Create start and close nodules
    start_nodule = nodule_gen()
    close_nodule = nodule_gen()

    # Mapping to store edge information
    nodule_edge_map: NoduleEdgeMap = collections.defaultdict(dict)

    process_token_path(token_path=token_path,
                       start_nodule=start_nodule,
                       close_nodule=close_nodule,
                       nodule_gen=nodule_gen,
                       nodule_edge_map=nodule_edge_map,
                       slot_filter_stack_command=None,
                       )
    return nodule_edge_map, start_nodule, close_nodule


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
