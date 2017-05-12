import collections
import typing as typ
import itertools
import functools
import uuid
import enum
import copy

import cheffu.slot_filter as sf
import cheffu.logging as clog
import cheffu.helpers as chlp
import cheffu.exceptions as chex

logger = clog.get_logger(__name__)

# Nodule = typ.NewType('Nodule', uuid.UUID)
Nodule = typ.NewType('Nodule', int)
NoduleGen = typ.Callable[[], Nodule]

Token = typ.NewType('Token', dict)
AltSequence = typ.Sequence['FilteredAlt']
PathItem = typ.Union[Token, AltSequence]
TokenPath = typ.Sequence[PathItem]

FilteredAlt = typ.NamedTuple('FilteredAlt', (('items', TokenPath), ('slot_filter', sf.SlotFilter)))
UnfilteredAlt = functools.partial(FilteredAlt, slot_filter=sf.ALLOW_ALL)
FilteredNull = functools.partial(FilteredAlt, items=())
UnfilteredNull = functools.partial(UnfilteredAlt, items=())

SlotFilterStack = typ.Sequence[sf.SlotFilter]


class StackDirection(enum.Enum):
    PUSH = '+'
    POP = '-'

# Need to separate slot filter in order to parse and view
id_gen = itertools.count()
SlotFilterStackOperation = typ.NamedTuple('SlotFilterStackOperation',
                                          (('direction', StackDirection), ('slot_filter', sf.SlotFilter))
                                          )
SlotFilterStackCommand = typ.Optional[SlotFilterStackOperation]

NoduleSkewer = typ.NamedTuple('NoduleSkewer', (('tokens', typ.Sequence[Token]), ('command', SlotFilterStackCommand)))

NoduleEdgeMap = typ.MutableMapping[
    Nodule,
    typ.MutableMapping[
        Nodule,
        NoduleSkewer,
    ],
]


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


AllowedSlotIndices = typ.AbstractSet[sf.SlotIndex]


def generate_allowed_slot_indices_from_alt(*
                                           , alt_sequence: AltSequence
                                           ) -> AllowedSlotIndices:
    interesting_slot_indices: typ.Set[sf.SlotIndex] = set()
    for alt in alt_sequence:
        slot_filter: sf.SlotFilter = alt.slot_filter

        if sf.is_white_list(slot_filter):
            interesting_slot_indices.update(sf.allowed_slots(slot_filter))
        else:
            interesting_slot_indices.update(sf.blocked_slots(slot_filter))

    if interesting_slot_indices:
        sorted_slot_indices: typ.List[sf.SlotIndex] = sorted(interesting_slot_indices)

        if all(map(lambda t: sf.SlotIndex(t[0]) == t[1], enumerate(sorted_slot_indices))):
            # All slot indices less than the largest selected are also selected.
            # Select the lowest index not selected, which is equal to the length of the collection.
            interesting_slot_indices.add(len(sorted_slot_indices))
        else:
            # At least one slot index less than the largest selected is not selected.
            # Select all slot indices in [0...<largest index>], inclusive.
            interesting_slot_indices.update(range(0, sorted_slot_indices[-1]))

    return frozenset(interesting_slot_indices)


def connect(*,
            start_nodule: Nodule,
            close_nodule: Nodule,
            nodule_edge_map: NoduleEdgeMap,
            encountered_tokens: typ.Sequence[Token],
            slot_filter_stack_command: SlotFilterStackCommand
            ) -> None:
    logger.debug(f'Connecting nodule {start_nodule} to nodule {close_nodule}, '
                 f'containing {len(encountered_tokens)} token(s)')
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

            # We only want to put the stack command on the first skewer of a branch
            if slot_filter_stack_command:
                slot_filter_stack_command = None

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
        slot_filter_stack_push = SlotFilterStackOperation(direction=StackDirection.PUSH, slot_filter=slot_filter)
        slot_filter_stack_pop = SlotFilterStackOperation(direction=StackDirection.POP, slot_filter=slot_filter)

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
        logger.debug('Nodule generator not specified, using default generator')
        counter = itertools.count()

        def nodule_gen():
            return next(counter)

    # Create start and close nodules
    start_nodule = nodule_gen()
    logger.debug(f'Generated start nodule = {start_nodule}')
    close_nodule = nodule_gen()
    logger.debug(f'Generated close nodule = {close_nodule}')

    # Mapping to store edge information
    nodule_edge_map: NoduleEdgeMap = collections.defaultdict(dict)

    process_token_path(token_path=token_path,
                       start_nodule=start_nodule,
                       close_nodule=close_nodule,
                       nodule_gen=nodule_gen,
                       nodule_edge_map=nodule_edge_map,
                       slot_filter_stack_command=None,
                       )

    # Sanity checks
    edge_pairs = [(a, b) for a, av in nodule_edge_map.items() for b in av.keys()]
    edge_pairs_set = set(edge_pairs)
    assert len(edge_pairs) == len(edge_pairs_set)

    return nodule_edge_map, start_nodule, close_nodule


def process_stack(slot_filter_stack: SlotFilterStack, slot_filter_stack_command: SlotFilterStackCommand):
    if slot_filter_stack_command is None:
        return slot_filter_stack
    else:
        direction: StackDirection = slot_filter_stack_command.direction
        slot_filter: sf.SlotFilter = slot_filter_stack_command.slot_filter

        if direction == StackDirection.PUSH:
            return tuple(slot_filter_stack) + (slot_filter,)
        else:
            popped = slot_filter_stack[-1]
            assert popped == slot_filter
            return slot_filter_stack[:-1]


NoduleWalk = typ.Sequence[Nodule]
SlotFilterStackWalk = typ.Sequence[SlotFilterStack]
# Sequence indicating what consolidated slot filters are chosen at each branch for a particular walk of a graph
SlotFilterChoiceSequence = typ.Sequence[typ.Sequence[sf.SlotFilter]]

PathDegree = typ.NewType('PathDegree', int)


def yield_all_nodule_walks(*
                           , nodule_edge_map: NoduleEdgeMap
                           , start_nodule: Nodule
                           , close_nodule: Nodule=None
                           ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterStackWalk]]:
    """Yields walks (start-to-end traversals) of a nodule edge map, as well as the slot filter stack at each step.
    """
    def helper(*
               , curr_nodule: Nodule
               , curr_walk: NoduleWalk
               , curr_slot_filter_stack: SlotFilterStack
               , curr_slot_filter_stack_walk: SlotFilterStackWalk
               ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterStackWalk]]:
        if nodule_edge_map[curr_nodule]:
            for next_nodule, next_skewer in nodule_edge_map[curr_nodule].items():
                next_graph_walk: NoduleWalk = tuple(curr_walk) + (next_nodule,)
                command = next_skewer.command

                next_slot_filter_stack = process_stack(curr_slot_filter_stack, command)
                next_slot_filter_stack_walk = tuple(curr_slot_filter_stack_walk) + (next_slot_filter_stack,)

                yield from helper(curr_nodule=next_nodule
                                  , curr_walk=next_graph_walk
                                  , curr_slot_filter_stack=next_slot_filter_stack
                                  , curr_slot_filter_stack_walk=next_slot_filter_stack_walk
                                  # , curr_caches=caches
                                  # , curr_stacks=stacks
                                  )
        else:
            if close_nodule is not None and curr_nodule != close_nodule:
                logger.warning(f'Found branch that does not end with expected close nodule, '
                               f'expected = {close_nodule}, found = {curr_nodule}')
                return

            yield curr_walk, curr_slot_filter_stack_walk

    yield from helper(curr_nodule=start_nodule
                      , curr_walk=(start_nodule,)
                      , curr_slot_filter_stack=()
                      , curr_slot_filter_stack_walk=((),)
                      )


def yield_valid_nodule_walks(*
                             , nodule_edge_map: NoduleEdgeMap
                             , start_nodule: Nodule
                             , close_nodule: Nodule=None
                             ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterStackWalk, SlotFilterChoiceSequence]]:
    for nodule_walk, slot_filter_stack_walk in yield_all_nodule_walks(nodule_edge_map=nodule_edge_map
                                                                      , start_nodule=start_nodule
                                                                      , close_nodule=close_nodule
                                                                      ):
        is_valid, choice_sequence = validate_slot_filter_stack_walk(slot_filter_stack_walk=slot_filter_stack_walk)
        if is_valid:
            yield nodule_walk, slot_filter_stack_walk, choice_sequence


def validate_slot_filter_stack_walk(*
                                    , slot_filter_stack_walk: SlotFilterStackWalk
                                    ) -> typ.Tuple[bool, typ.Optional[SlotFilterChoiceSequence]]:
    caches: typ.MutableMapping[PathDegree, sf.SlotFilter] = {}
    stacks: typ.DefaultDict[PathDegree, typ.List[sf.SlotFilter]] = collections.defaultdict(list)

    for prev_slot_filter_stack, curr_slot_filter_stack in chlp.pairwise(slot_filter_stack_walk):
        # Assert that one stack is a prefix of the other
        for p, c in zip(prev_slot_filter_stack, curr_slot_filter_stack):
            assert p == c

        prev_degree: PathDegree = len(prev_slot_filter_stack)
        curr_degree: PathDegree = len(curr_slot_filter_stack)

        direction = curr_degree - prev_degree

        # At this point, one stack should be a prefix of the other
        if direction == 0:
            pass
        elif direction > 0:
            for i in range(prev_degree, curr_degree):
                if i not in caches:
                    caches[i] = curr_slot_filter_stack[i]
                    stacks[i].append(curr_slot_filter_stack[i])

                cached_slot_filter = caches[i]
                tested_slot_filter = curr_slot_filter_stack[i]

                intersect = sf.intersection(cached_slot_filter, tested_slot_filter)
                if intersect == sf.BLOCK_ALL:
                    return False, None

                caches[i] = intersect
                stacks[i][-1] = intersect
        elif direction < 0:
            to_delete = set()
            for k in caches.keys():
                if k > curr_degree:
                    to_delete.add(k)
            for k in to_delete:
                del caches[k]

    # Convert stacks into proper choice sequence
    tmp_list = []
    for key in sorted(stacks.keys()):
        tmp_list.append(tuple(stacks[key]))
    choice_sequence = tuple(tmp_list)

    return True, choice_sequence


def is_valid_stack_walk(*,
                        slot_filter_stack_walk: SlotFilterStackWalk
                        ) -> bool:
    result, _ = validate_slot_filter_stack_walk(slot_filter_stack_walk=slot_filter_stack_walk)
    return result


def get_token_sequence(*
                       , nodule_edge_map: NoduleEdgeMap
                       , nodule_walk: NoduleWalk
                       ) -> typ.Iterable[Token]:
    return itertools.chain.from_iterable(nodule_edge_map[nodule_a][nodule_b].tokens
                                         for nodule_a, nodule_b in chlp.pairwise(nodule_walk)
                                         )


AllowedSlotMap = typ.MutableMapping[
    Nodule,
    typ.MutableMapping[
        sf.SlotIndex,
        Nodule,
    ],
]


# TODO: Need a way to list all legal filtered paths through a recipe, as well as a way to address each unique path.


# def generate_allowed_slot_map(*
#                               , nodule_edge_map: NoduleEdgeMap
#                               , start_nodule: Nodule
#                               , close_nodule: Nodule=None
#                               ):
#     allowed_slot_map: AllowedSlotMap = collections.defaultdict(dict)
#
#     for _, stack_walk, _ in yield_valid_nodule_walks(nodule_edge_map=nodule_edge_map
#                                                                         , start_nodule=start_nodule
#                                                                         , close_nodule=close_nodule
#                                                                         ):
#         for stack in stack_walk:

