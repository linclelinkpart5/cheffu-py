import itertools
import typing as typ
import uuid

import collections
import enum
import functools

import cheffu.exceptions as chex
import cheffu.logging as clog
import cheffu.slot_filter as sf
import cheffu.types.common as ctpc
import cheffu.types.tokens as ctpt

logger = clog.get_logger(__name__)

# IDs for nodules, edges, and tokens.
Nodule = ctpc.UniqueId
EdgeId = ctpc.UniqueId


# Cheffu uses an edge-first system design, where edges represent directed connections between nodules.
# Edges contain most of the interesting information of the graph, including slot filters and tokens.
# It is possible for multiple edges between a pair of nodules, due to alts and variants.
class EdgeDef(typ.NamedTuple):
    id: EdgeId
    src_nodule: Nodule
    dst_nodule: Nodule
    token_seq: ctpt.TokenSequence
    start_cmd: 'StackCommand'
    close_cmd: 'StackCommand'

# Intermediate representation of a Cheffu variant choice.
# Variant choices allow for different sets (alts) of tokens to be included based on a slot filter.
AltSequence = typ.Sequence['FilteredAlt']

# An intermediate representation of a mixed sequence of tokens and alt sequences.
ProcedurePath = typ.Sequence[typ.Union[ctpt.Token, AltSequence]]


class FilteredAlt(typ.NamedTuple):
    items: ProcedurePath = ()
    slot_filter: sf.SlotFilter = sf.ALLOW_ALL

# A stack containing slot filters, used to determine what paths are legal to walk through.
SlotFilterStack = typ.Sequence[sf.SlotFilter]


# Symbolic representation of a stack push/pop.
class StackDirection(enum.Enum):
    PUSH = '+'
    POP = '-'


# Represents a push or pop operation on a slot filter stack.
# We need a separate command and slot filter (instead of just using a lambda)
# in order to make it easier to parse and view the command and slot filter.
class StackOperation(typ.NamedTuple):
    direction: StackDirection
    slot_filter: sf.SlotFilter

# If None, represents a no-op on the stack.
# Otherwise, pushes or pops (depending on the direction specified) the slot filter from a stack.
StackCommand = typ.Optional[StackOperation]


StackCommandSequence = typ.Sequence[StackCommand]


# Represents a move from a (implied) nodule along an edge to a new nodule.
class GraphHop(typ.NamedTuple):
    edge_id: EdgeId
    nodule: Nodule

# A walk along a completed graph, starting at a (implied) nodule, and then making zero or more hops to another nodule.
GraphHopSequence = typ.Sequence[GraphHop]


# Represents a full walk along a nodule graph.
class GraphWalk(typ.NamedTuple):
    start: Nodule
    hop_seq: GraphHopSequence


# Represents the possible change in a slot filter stack when traversing a nodule edge.
class StackHop(typ.NamedTuple):
    start_cmd: StackCommand
    close_cmd: StackCommand

# A sequence of stack hops.
StackHopSequence = typ.Sequence[StackHop]


class StackWalk(typ.NamedTuple):
    start: SlotFilterStack
    hop_seq: StackHopSequence

# Set of edge IDs outbound for a (implied) nodule.
OutEdgeIdSet = typ.AbstractSet[EdgeId]
MutOutEdgeIdSet = typ.MutableSet[EdgeId]

# Maps nodules to the IDs of edges travelling out from that nodule.
NoduleOutEdgeMap = typ.Mapping[Nodule, OutEdgeIdSet]
MutNoduleOutEdgeMap = typ.MutableMapping[Nodule, MutOutEdgeIdSet]

# Maps edge IDs to their edge definitions.
EdgeLookupMap = typ.Mapping[EdgeId, EdgeDef]
MutEdgeLookupMap = typ.MutableMapping[EdgeId, EdgeDef]

# Sequence indicating what consolidated slot filters are chosen at each branch for a particular walk of a graph.
SlotFilterChoiceSequence = typ.Sequence[typ.Sequence[sf.SlotFilter]]
MutSlotFilterChoiceSequence = typ.MutableSequence[typ.MutableSequence[sf.SlotFilter]]

PathDepth = typ.NewType('PathDepth', int)


def normalize_alt_sequence(alt_sequence: AltSequence) -> AltSequence:
    """Processes an alt sequence to remove multiple null alts, and to ensure that the union of all of its
    contained slot filters allows all slots (i.e. is an allow-all filter).
    """
    # Calculate the value of the else-filter, which contains all slots not explicitly allowed in the alt sequence.
    coverage_filter = functools.reduce(
        sf.union,
        (alt.slot_filter for alt in alt_sequence),
        sf.BLOCK_ALL,
    )
    else_filter = sf.invert(coverage_filter)

    # If else-filter is not block-all, append a null branch with the else-filter to filtered alts.
    # This provides an "escape hatch" for a case when a slot does not match any provided filter.
    if else_filter != sf.BLOCK_ALL:
        alt_sequence += (FilteredAlt(slot_filter=else_filter),)

    # From filtered alts, drop any that have a block-all filter.
    alt_sequence = tuple(filtered_alt for filtered_alt in alt_sequence if filtered_alt.slot_filter != sf.BLOCK_ALL)

    # Coalesce any null alts into a single null alt.
    # TODO: If possible, coalesce non-null branches as well, but much trickier
    null_alts = tuple(alt for alt in alt_sequence if not alt.items)
    alt_sequence = tuple(alt for alt in alt_sequence if alt.items)

    # Coalescing happens by union-ing the corresponding slot filters into one.
    if null_alts:
        null_filter = sf.BLOCK_ALL
        for null_alt in null_alts:
            null_filter = sf.union(null_filter, null_alt.slot_filter)

        alt_sequence += (FilteredAlt(slot_filter=null_filter),)

    # Sanity check: The alt sequence should not be empty.
    assert alt_sequence

    # Sanity check: There should be at most one null branch.
    assert sum(1 if not alt.items else 0 for alt in alt_sequence) <= 1

    # Sanity check: The union of all filters should equal an allow-all filter.
    assert functools.reduce(sf.union, (alt.slot_filter for alt in alt_sequence), sf.BLOCK_ALL) == sf.ALLOW_ALL

    return alt_sequence


def connect(*
            , edge_id_gen: ctpc.UniqueIdGen
            , src_nodule: Nodule
            , dst_nodule: Nodule
            , mut_nodule_out_edge_map: MutNoduleOutEdgeMap
            , mut_edge_lookup_map: MutEdgeLookupMap
            , encountered_tokens: typ.Sequence[ctpt.Token]
            , start_slot_filter_stack_command: StackCommand
            , close_slot_filter_stack_command: StackCommand
            ) -> None:
    """Connects two nodules together with an edge.
    This edge will contain information about the tokens present on it,
    as well as the stack commands on start and close.
    """
    logger.debug(f'Connecting nodule {src_nodule} to nodule {dst_nodule}, '
                 f'containing {len(encountered_tokens)} token(s)')

    # A new edge needs to be created.
    edge_id: EdgeId = edge_id_gen()
    edge_def: EdgeDef = EdgeDef(id=edge_id
                                , src_nodule=src_nodule
                                , dst_nodule=dst_nodule
                                , token_seq=encountered_tokens
                                , start_cmd=start_slot_filter_stack_command
                                , close_cmd=close_slot_filter_stack_command
                               )

    # Add edge ID to nodule out edge map.
    mut_nodule_out_edge_map[src_nodule].add(edge_id)

    # Add edge def and edge ID to edge lookup map.
    mut_edge_lookup_map[edge_id] = edge_def


def process_token_path(*
                       , procedure_path: ProcedurePath
                       , start_nodule: Nodule
                       , close_nodule: Nodule
                       , nodule_gen: ctpc.UniqueIdGen
                       , edge_id_gen: ctpc.UniqueIdGen
                       , tok_id_gen: ctpc.UniqueIdGen
                       , mut_nodule_out_edge_map: MutNoduleOutEdgeMap
                       , mut_edge_lookup_map: MutEdgeLookupMap
                       , start_slot_filter_stack_command: StackCommand
                       , close_slot_filter_stack_command: StackCommand
                       ) -> None:
    logger.debug(f'Starting processing of subprocedure path, with {len(procedure_path)} element(s)')

    # Keep track of the most recent parent nodule.
    curr_parent_nodule: Nodule = start_nodule

    # Collect tokens encountered directly on this path.
    encountered_tokens: typ.MutableSequence[ctpt.Token] = []

    # Process each path item.
    for path_item in procedure_path:
        # We need to check if this is an instance of token first, since it would match the check for tuple.
        if isinstance(path_item, ctpt.Token):
            token: ctpt.Token = typ.cast(ctpt.Token, path_item)

            # Add to the list of encountered tokens
            encountered_tokens.append(token)
        # TODO: See if there is a way to use type hint in subclass check.
        elif isinstance(path_item, tuple):
            # When an alt sequence is encountered:
            #     1) New start and close nodules (NSN, NCN) are generated for the to-be-processed alt sequence.
            #     2) The current skewer and list of encountered tokens is capped (use NSN).
            #     3) Process the alt sequence, using NSN and NCN.
            alt_sequence: AltSequence = typ.cast(AltSequence, path_item)

            # Create new start and close nodules for the to-be-processed alt sequence.
            alt_seq_start_nodule: Nodule = nodule_gen()
            alt_seq_close_nodule: Nodule = nodule_gen()

            # Capture current list of encountered tokens.
            # Close off the current path by connecting to the new start nodule.
            connect(edge_id_gen=edge_id_gen,
                    src_nodule=curr_parent_nodule,
                    dst_nodule=alt_seq_start_nodule,
                    mut_nodule_out_edge_map=mut_nodule_out_edge_map,
                    mut_edge_lookup_map=mut_edge_lookup_map,
                    encountered_tokens=tuple(encountered_tokens),
                    start_slot_filter_stack_command=start_slot_filter_stack_command,
                    close_slot_filter_stack_command=None,
                    )

            # We only want to put the stack command on the first out path of a branch, not on any further down.
            if start_slot_filter_stack_command is not None:
                start_slot_filter_stack_command = None

            # Reset list of encountered tokens.
            encountered_tokens = []

            # Process the alt sequence.
            process_alt_sequence(edge_id_gen=edge_id_gen,
                                 nodule_gen=nodule_gen,
                                 tok_id_gen=tok_id_gen,
                                 alt_sequence=alt_sequence,
                                 start_nodule=alt_seq_start_nodule,
                                 close_nodule=alt_seq_close_nodule,
                                 mut_nodule_out_edge_map=mut_nodule_out_edge_map,
                                 mut_edge_lookup_map=mut_edge_lookup_map,
                                 )

            # Update current parent nodule.
            curr_parent_nodule = alt_seq_close_nodule

    # Close the path by making an edge from the current parent nodule to the close nodule.
    # Note that the value of start slot filter stack command will be None if an alt sequence is processed before here.
    connect(edge_id_gen=edge_id_gen,
            src_nodule=curr_parent_nodule,
            dst_nodule=close_nodule,
            mut_nodule_out_edge_map=mut_nodule_out_edge_map,
            mut_edge_lookup_map=mut_edge_lookup_map,
            encountered_tokens=encountered_tokens,
            start_slot_filter_stack_command=start_slot_filter_stack_command,
            close_slot_filter_stack_command=close_slot_filter_stack_command,
            )

    # This creates an entry for the close nodule if it does not already exist.
    _ = mut_nodule_out_edge_map[close_nodule]

    logger.debug(f'Finished processing of subprocedure path')


def process_alt_sequence(*
                         , edge_id_gen: ctpc.UniqueIdGen
                         , nodule_gen: ctpc.UniqueIdGen
                         , tok_id_gen: ctpc.UniqueIdGen
                         , alt_sequence: AltSequence
                         , start_nodule: Nodule
                         , close_nodule: Nodule
                         , mut_nodule_out_edge_map: MutNoduleOutEdgeMap
                         , mut_edge_lookup_map: MutEdgeLookupMap
                         ):
    # Normalize alt sequence.
    alt_sequence = normalize_alt_sequence(alt_sequence)

    # For each alt in the alt sequence:
    #     1) Extract slot filter.
    #     2) Create slot filter stack commands for push and pop (SPSH, SPOP).
    #     3) Process token path contained in alt using SPSH and SPOP.
    for alt in alt_sequence:
        # Unpack alt into components.
        procedure_path: ProcedurePath = alt.items
        slot_filter: sf.SlotFilter = alt.slot_filter

        # Generate stack operations
        slot_filter_stack_push = StackOperation(direction=StackDirection.PUSH, slot_filter=slot_filter)
        slot_filter_stack_pop = StackOperation(direction=StackDirection.POP, slot_filter=slot_filter)

        # Process items as another token path.
        # Remember to add a push command!
        process_token_path(edge_id_gen=edge_id_gen,
                           nodule_gen=nodule_gen,
                           tok_id_gen=tok_id_gen,
                           procedure_path=procedure_path,
                           start_nodule=start_nodule,
                           close_nodule=close_nodule,
                           mut_nodule_out_edge_map=mut_nodule_out_edge_map,
                           mut_edge_lookup_map=mut_edge_lookup_map,
                           start_slot_filter_stack_command=slot_filter_stack_push,
                           close_slot_filter_stack_command=slot_filter_stack_pop,
                           )

DEFAULT_UNIQUE_ID_GEN = uuid.uuid4


def process(*
            , procedure_path: ProcedurePath
            , nodule_gen: ctpc.UniqueIdGen=None
            , edge_id_gen: ctpc.UniqueIdGen=None
            , tok_id_gen: ctpc.UniqueIdGen=None
            ) -> typ.Tuple[NoduleOutEdgeMap, EdgeLookupMap, Nodule, Nodule]:
    if nodule_gen is None:
        logger.info('Nodule generator not specified, using default generator')
        nodule_gen = DEFAULT_UNIQUE_ID_GEN
    if edge_id_gen is None:
        logger.info('Edge ID generator not specified, using default generator')
        edge_id_gen = DEFAULT_UNIQUE_ID_GEN
    if tok_id_gen is None:
        logger.info('Token ID generator not specified, using default generator')
        tok_id_gen = DEFAULT_UNIQUE_ID_GEN

    # Create start and close nodules.
    start_nodule = nodule_gen()
    logger.debug(f'Generated start nodule = {start_nodule}')
    close_nodule = nodule_gen()
    logger.debug(f'Generated close nodule = {close_nodule}')

    # Mappings to store edge information.
    mut_nodule_out_edge_map: MutNoduleOutEdgeMap = collections.defaultdict(set)
    mut_edge_lookup_map: MutEdgeLookupMap = {}

    # # Create top level push and pop commands.
    # slot_filter_stack_push = StackOperation(direction=StackDirection.PUSH, slot_filter=sf.ALLOW_ALL)
    # slot_filter_stack_pop = StackOperation(direction=StackDirection.POP, slot_filter=sf.ALLOW_ALL)

    logger.debug(f'Starting processing of main procedure path, with {len(procedure_path)} element(s)')

    process_token_path(edge_id_gen=edge_id_gen,
                       nodule_gen=nodule_gen,
                       tok_id_gen=tok_id_gen,
                       procedure_path=procedure_path,
                       start_nodule=start_nodule,
                       close_nodule=close_nodule,
                       mut_nodule_out_edge_map=mut_nodule_out_edge_map,
                       mut_edge_lookup_map=mut_edge_lookup_map,
                       start_slot_filter_stack_command=None,
                       close_slot_filter_stack_command=None,
                       )

    logger.debug(f'Finished processing of procedure path')

    return mut_nodule_out_edge_map, mut_edge_lookup_map, start_nodule, close_nodule


def process_stack(*
                  , stack: SlotFilterStack
                  , stack_cmd: StackCommand
                  ) -> SlotFilterStack:
    """Process a slot filter stack according to a stack command."""
    if stack_cmd is None:
        # A no-op, return the stack unchanged.
        return stack
    else:
        # Are we doing a push or pop?
        direction: StackDirection = stack_cmd.direction

        # What value of slot filter are we expecting?
        slot_filter: sf.SlotFilter = stack_cmd.slot_filter

        if direction == StackDirection.PUSH:
            # Append the slot filter to the end of the stack and return.
            return tuple(stack) + (slot_filter,)
        else:
            # Try and index the last slot filter in the stack.
            # If it matches, return a copy of the stack with that slot filter trimmed off.
            if not stack:
                raise chex.SlotFilterStackEmpty(f'Slot filter stack empty; expected = {slot_filter}')

            popped = stack[-1]

            if not popped == slot_filter:
                raise chex.SlotFilterStackResultMismatch(f'Unexpected value popped from slot filter stack; '
                                                         f'expected = {slot_filter}, found = {popped}')

            return stack[:-1]


def make_graph_hop_from_edge_id(*
                                , edge_id: EdgeId
                                , edge_lookup_map: EdgeLookupMap
                                ) -> GraphHop:
    """Helper to create a graph hop from an edge."""
    # Obtain the next nodule found by traversing this edge.
    edge_def: EdgeDef = edge_lookup_map[edge_id]
    dst_nodule: Nodule = edge_def.dst_nodule

    return GraphHop(edge_id=edge_id, dst_nodule=dst_nodule)


def make_stack_hop_from_edge_id(*
                                , edge_id: EdgeId
                                , edge_lookup_map: EdgeLookupMap
                                ) -> StackHop:
    """Helper to create a stack hop from an edge."""
    edge_def: EdgeDef = edge_lookup_map[edge_id]
    start_cmd: StackCommand = edge_def.start_cmd
    close_cmd: StackCommand = edge_def.close_cmd

    return StackHop(start_cmd=start_cmd, close_cmd=close_cmd)


def yield_all_hop_seqs(*
                       , nodule_out_edge_map: NoduleOutEdgeMap
                       , edge_lookup_map: EdgeLookupMap
                       , start_nodule: Nodule
                       , close_nodule: Nodule = None
                       ) -> typ.Iterable[typ.Tuple[GraphHopSequence, StackHopSequence]]:
    """Yields all hop sequences (graph and stack) of a constructed nodule out edge map/edge lookup map combo.
    """
    def helper(*
               , curr_nodule: Nodule
               , curr_graph_hop_seq: GraphHopSequence
               , curr_stack_hop_seq: StackHopSequence
               ) -> typ.Iterable[typ.Tuple[GraphHopSequence, StackHopSequence]]:
        out_edges: OutEdgeIdSet = nodule_out_edge_map[curr_nodule]
        if out_edges:
            for edge_id in out_edges:
                # Calculate the next addition to the graph walk.
                next_graph_hop: GraphHop = make_graph_hop_from_edge_id(edge_id=edge_id, edge_lookup_map=edge_lookup_map)
                next_graph_hop_seq: GraphHopSequence = (*curr_graph_hop_seq, next_graph_hop)

                # Calculate the next addition to the stack walk.
                next_stack_hop: StackHop = make_stack_hop_from_edge_id(edge_id=edge_id, edge_lookup_map=edge_lookup_map)
                next_stack_hop_seq: StackHopSequence = (*curr_stack_hop_seq, next_stack_hop)

                # Get the next nodule from this edge we traversed.
                next_nodule: Nodule = edge_lookup_map[edge_id].dst_nodule

                yield from helper(curr_nodule=next_nodule
                                  , curr_graph_hop_seq=next_graph_hop_seq
                                  , curr_stack_hop_seq=next_stack_hop_seq
                                  )
        # Base case, stop when this nodule is a dead end.
        else:
            if close_nodule is not None and curr_nodule != close_nodule:
                logger.warning(f'Found branch that does not end with expected close nodule, '
                               f'expected = {close_nodule}, found = {curr_nodule}')
                return

            yield curr_graph_hop_seq, curr_stack_hop_seq

    yield from helper(curr_nodule=start_nodule
                      , curr_graph_hop_seq=()
                      , curr_stack_hop_seq=()
                      )


def validate_stack_cmd_seq(*
                           , stack_cmd_seq: StackCommandSequence
                           ) -> typ.Tuple[bool, typ.Optional[SlotFilterChoiceSequence]]:
    """Given a stack command sequence, calculates if it is legal.
    If so, also returns its corresponding slot choice sequence.
    """
    # Keeps track of the current allowed slot filter for a given path depth.
    # In other words, if we're at path depth X, and a slot filter choice is encountered,
    # the Xth key of this is what is used to tell if we can go down that scope.
    # When a new scope is created, this gets set to the first slot filter encountered.
    # Within a scope, this gets used to test further encountered slot filters to see if there is a match.
    caches: typ.MutableMapping[PathDepth, sf.SlotFilter] = {}

    # This tracks the slot filter selected when a new scope is created.
    selections: typ.DefaultDict[PathDepth, typ.List[sf.SlotFilter]] = collections.defaultdict(list)

    curr_stack: SlotFilterStack = ()

    # Iterate over all stack commands in stack hop sequence.
    # This requires some unpacking.
    for stack_cmd in stack_cmd_seq:
        # Generate what the next stack would look like.
        next_stack = process_stack(stack=curr_stack, stack_cmd=stack_cmd)

        # Assert that one stack is a prefix of the other.
        for c, n in zip(curr_stack, next_stack):
            assert c == n

        # The path depth of a stack is equal to its length.
        curr_depth: PathDepth = len(curr_stack)
        next_depth: PathDepth = len(next_stack)

        # Direction indicates the direction of change in the stack.
        direction = next_depth - curr_depth

        # If direction is zero, no-op.
        if direction == 0:
            pass
        # Else if direction is positive, a push occurred.
        # Generalize, and allow any amount of pushed elements.
        elif direction > 0:
            for i in range(curr_depth, next_depth):
                if i not in caches:
                    new_sf: sf.SlotFilter = next_stack[i]
                    caches[i] = new_sf
                    selections[i].append(new_sf)

                # Test if this pushed slot filter is valid w.r.t. the known cached slot filter for this path depth.
                cached_sf: sf.SlotFilter = caches[i]
                tested_sf: sf.SlotFilter = next_stack[i]

                intersect = sf.intersection(cached_sf, tested_sf)
                if intersect == sf.BLOCK_ALL:
                    logger.debug(f'New and cached slot filters did not intersect; '
                                 f'new = {tested_sf}, cached = {cached_sf}')
                    return False, None

                # Update cache and stack with new intersected slot filter, since it may have been narrowed in scope.
                caches[i] = intersect
                selections[i][-1] = intersect
        # Else if direction is negative, a pop occurred.
        # Generalize, and allow any amount of popped elements.
        elif direction < 0:
            to_delete = set()
            for k in caches.keys():
                if k > next_depth:
                    to_delete.add(k)
            for k in to_delete:
                del caches[k]

        # Update current stack.
        curr_stack = next_stack

    # If stack hop sequence is valid, we should be once again left with an empty stack.
    if curr_stack:
        logger.debug(f'Final stack was not empty, contained {curr_stack}')
        return False, None

    # Convert stacks into proper choice sequence.
    tmp_list = []
    for key in sorted(selections.keys()):
        tmp_list.append(tuple(selections[key]))
    choice_sequence = tuple(tmp_list)

    return True, choice_sequence


def flatten_stack_hop_seq(*
                          , stack_hop_seq: StackHopSequence
                          ) -> StackCommandSequence:
    """Flattens a sequence of stack hops into a sequence of stack commands."""
    stack_cmd_seq: StackCommandSequence = tuple(itertools.chain.from_iterable(stack_hop_seq))
    return stack_cmd_seq


def yield_valid_hop_seqs(*
                         , nodule_out_edge_map: NoduleOutEdgeMap
                         , edge_lookup_map: EdgeLookupMap
                         , start_nodule: Nodule
                         , close_nodule: Nodule = None
                         ) -> typ.Iterable[typ.Tuple[GraphHopSequence, StackHopSequence, SlotFilterChoiceSequence]]:
    for graph_hop_seq, stack_hop_seq in yield_all_hop_seqs(nodule_out_edge_map=nodule_out_edge_map
                                                           , edge_lookup_map=edge_lookup_map
                                                           , start_nodule=start_nodule
                                                           , close_nodule=close_nodule
                                                           ):
        # Flatten the stack hop sequence, the validation function expects a flattened view.
        stack_cmd_seq = flatten_stack_hop_seq(stack_hop_seq=stack_hop_seq)
        is_valid, choice_seq = validate_stack_cmd_seq(stack_cmd_seq=stack_cmd_seq)
        if is_valid:
            yield graph_hop_seq, stack_hop_seq, choice_seq


def yield_tokens_from_graph_walk(*
                                 , nodule_out_edge_map: NoduleOutEdgeMap
                                 , edge_lookup_map: EdgeLookupMap
                                 , graph_walk: GraphWalk
                                 ) -> typ.Iterable[ctpt.Token]:
    curr_nodule = graph_walk.start
    graph_hop_seq = graph_walk.hop_seq

    for graph_hop in graph_hop_seq:
        # Get out edge IDs for the current nodule.
        # TODO: Handle exceptions!
        out_edge_ids: OutEdgeIdSet = nodule_out_edge_map[curr_nodule]

        desired_out_edge_id: EdgeId = graph_hop.edge_id
        desired_dst_nodule: Nodule = graph_hop.nodule

        assert desired_out_edge_id in out_edge_ids

        edge_def: EdgeDef = edge_lookup_map[desired_out_edge_id]

        assert edge_def.src_nodule == curr_nodule
        assert edge_def.dst_nodule == desired_out_edge_id

        yield from edge_def.token_seq

        curr_nodule = desired_dst_nodule


def stack_cmd_str(stack_cmd: StackCommand) -> str:
    if not stack_cmd:
        return 'NoOp'
    else:
        direction: StackDirection = stack_cmd.direction
        slot_filter: sf.SlotFilter = stack_cmd.slot_filter

        return f'{direction.name.title()}({slot_filter})'


def stack_cmd_label_str(stack_cmd: StackCommand) -> str:
    if not stack_cmd:
        return ''
    else:
        direction: StackDirection = stack_cmd.direction
        slot_filter: sf.SlotFilter = stack_cmd.slot_filter

        return f'{direction.value} {sf.pretty_string(slot_filter)}'


# TODO: Need a way to list all legal filtered paths through a recipe, as well as a way to address each unique path.
