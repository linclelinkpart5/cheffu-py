import collections
import typing as typ
import itertools
import functools
import uuid
import enum

import cheffu.slot_filter as sf
import cheffu.exceptions as chex

# Nodule = typ.NewType('Nodule', uuid.UUID)
Nodule = typ.NewType('Nodule', int)
NoduleGen = typ.Callable[[], Nodule]

Token = typ.NewType('Token', str)
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
SlotFilterStackOperation = typ.NamedTuple('SlotFilterStackOperation'
                                          , (('direction', StackDirection), ('slot_filter', sf.SlotFilter), ('id', int))
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

SlotFilterHierarchy = typ.Mapping[sf.SlotFilter, 'SlotFilterHierarchy']


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
        id_ = next(id_gen)
        slot_filter_stack_push = SlotFilterStackOperation(direction=StackDirection.PUSH, slot_filter=slot_filter, id=id_)
        slot_filter_stack_pop = SlotFilterStackOperation(direction=StackDirection.POP, slot_filter=slot_filter, id=id_)

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


class Multiplexer:
    @staticmethod
    def next(_):
        raise NotImplemented

    @staticmethod
    def empty_or_raise():
        raise NotImplemented


MultiplexerCFD = typ.Type[Multiplexer]


def choice_sequence_multiplexer(slot_filter_choice_sequence: typ.Optional[SlotFilterChoiceSequence]) -> MultiplexerCFD:
    if slot_filter_choice_sequence is None:
        class Dummy(Multiplexer):
            @staticmethod
            def next(_):
                return sf.ALLOW_ALL

            @staticmethod
            def empty_or_raise():
                pass

        return Dummy

    # Return a callable that, given an integer index, gets the next item in that index's choice sequence
    plexer = [iter(slot_filter_choices) for slot_filter_choices in slot_filter_choice_sequence]

    class Return(Multiplexer):
        @staticmethod
        def next(i):
            try:
                return next(plexer[i])
            except StopIteration:
                raise chex.NoMoreSlotFilters()

        @staticmethod
        def empty_or_raise():
            for plex in plexer:
                try:
                    next(plex)
                    raise chex.LeftoverSlotFilters()
                except StopIteration:
                    continue

    return Return


def ensure_memory(*
                  , multiplexer: MultiplexerCFD
                  , target_path_degree: PathDegree
                  , memory: typ.MutableSequence[sf.SlotFilter]
                  ) -> None:
    if target_path_degree < 0:
        raise ValueError()

    while len(memory) <= target_path_degree:
        new_index = len(memory)
        new_item = multiplexer.next(new_index)
        memory.append(new_item)

    if len(memory) > target_path_degree + 1:
        del memory[target_path_degree + 1:]


def yield_nodule_walks(*
                       , nodule_edge_map: NoduleEdgeMap
                       , start_nodule: Nodule
                       , slot_filter_choice_sequence: SlotFilterChoiceSequence=None
                       ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterStackWalk]]:
    """Yields walks (start-to-end traversals) of a nodule edge map, as well as the slot filter stack at each step.
    """
    # Counts the number of times a specific scope is opened
    # Needed to check which index in slot filter choice sequence to look up
    scope_instantiations: typ.Counter[PathDegree] = collections.Counter()

    # This can grow and shrink with respect to the current scope depth
    # When a split on a i-th degree path is encountered, the i-th element in this is chosen as the slot filter to use
    # If this element does not exist, it is queried and popped from the slot filter choice sequence
    chosen_slot_filters: typ.List[sf.SlotFilter] = []

    multiplexer = choice_sequence_multiplexer(slot_filter_choice_sequence)

    # def ensure(i: int):
    #     while len(chosen_slot_filters) <= i:
    #         chosen_slot_filters.append(sf.ALLOW_ALL)
    #
    #     if len(chosen_slot_filters) >

    def helper(*
               , curr_nodule: Nodule
               , curr_walk: NoduleWalk
               , curr_slot_filter_stack: SlotFilterStack
               , curr_slot_filter_stack_walk: SlotFilterStackWalk
               ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterStackWalk]]:

        # The scope degree at a nodule is equal to the length of the stack at that nodule
        curr_path_degree: PathDegree = len(curr_slot_filter_stack)

        # if curr_scope_index not in path_memory:
        #

        if nodule_edge_map[curr_nodule]:
            for next_nodule, next_skewer in nodule_edge_map[curr_nodule].items():
                next_graph_walk: NoduleWalk = tuple(curr_walk) + (next_nodule,)
                command = next_skewer.command

                next_slot_filter_stack = process_stack(curr_slot_filter_stack, command)
                next_slot_filter_stack_walk = tuple(curr_slot_filter_stack_walk) + (next_slot_filter_stack,)

                next_path_degree: PathDegree = len(next_slot_filter_stack)

                # TODO: Code for checking stack deltas here
                delta = len(next_slot_filter_stack) - len(curr_slot_filter_stack)
                # If delta is 1) negative, an item was popped
                #             2) positive, an item was pushed
                #             3) zero, no-op

                yield from helper(curr_nodule=next_nodule
                                  , curr_walk=next_graph_walk
                                  , curr_slot_filter_stack=next_slot_filter_stack
                                  , curr_slot_filter_stack_walk=next_slot_filter_stack_walk
                                  )
        else:
            yield curr_walk, curr_slot_filter_stack_walk

    yield from helper(curr_nodule=start_nodule
                      , curr_walk=(start_nodule,)
                      , curr_slot_filter_stack=()
                      , curr_slot_filter_stack_walk=((),)
                      )


def eval_choice_sequence(*
                         , sf_stack_walk: SlotFilterStackWalk
                         , sf_choice_sequence: SlotFilterChoiceSequence
                         ):
    """Yields all nodule walks that satisfy a given slot filter choice sequence.
    """
    # Create a list version of choice sequence for easier mutation
    sf_choice_stacks = [[s_f for s_f in sf_choices] for sf_choices in sf_choice_sequence]

    # Indexes into choice stacks and composite SFs
    curr_degree: int = 0

    # This can grow and shrink with respect to the current scope depth
    current_composite_sfs: typ.List[sf.SlotFilter] = []

    def ensure(i: int):
        while len(current_composite_sfs) <= i:
            current_composite_sfs.append(sf.ALLOW_ALL)

    for sf_stack in sf_stack_walk:
        curr_degree = len(sf_stack)

# def yield_nodule_walks_choices(*
#                                , nodule_edge_map: NoduleEdgeMap
#                                , start_nodule: Nodule
#                                ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterChoiceSequence]]:
#
#     def flatten(stack_walk: SlotFilterStackWalk) -> SlotFilterChoiceSequence:
#         slot_filter_buckets: typ.MutableMapping[int, typ.MutableMapping[int, sf.SlotFilter]] = collections.defaultdict(lambda: collections.defaultdict(sf.ALLOW_ALL))
#
#         # Whenever the length of the slot filter stack increases from the previous iteration, add any new elements
#         # to the respective buckets
#
#         for slot_filter_stack in stack_walk:
#             for i, slot_filter in enumerate(slot_filter_stack):
#                 slot_filter_buckets[i] = sf.intersection(result[i], slot_filter)
#
#         return tuple(result)
#
#     for nodule_walk, slot_filter_stack_walk in yield_nodule_walks(nodule_edge_map=nodule_edge_map
#                                                                   , start_nodule=start_nodule
#                                                                   ):
#             yield nodule_walk, flatten(slot_filter_stack_walk)

# def yield_nodule_walks_flattened(*
#                                  , nodule_edge_map: NoduleEdgeMap
#                                  , start_nodule: Nodule
#                                  ) -> typ.Iterable[typ.Tuple[NoduleWalk, SlotFilterChoiceSequence]]:
#     def flatten(stack_walk: SlotFilterStackWalk) -> SlotFilterChoiceSequence:
#         result = []
#         for slot_filter_stack in stack_walk:
#             for i, slot_filter in enumerate(slot_filter_stack):
#                 if len(result) <= i:
#                     result.append(slot_filter)
#                     assert len(result) == i + 1
#
#                 result[i] = sf.intersection(result[i], slot_filter)
#
#         return tuple(result)
#
#     for nodule_walk, slot_filter_stack_walk in yield_nodule_walks(nodule_edge_map=nodule_edge_map, start_nodule=start_nodule):
#         yield nodule_walk, flatten(slot_filter_stack_walk)
