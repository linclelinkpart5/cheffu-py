import collections
import typing as typ

import pydot

import cheffu.parallel as cpa


GraphvizId = typ.NewType('GVID', str)
NoduleConverter = typ.Callable[[cpa.Nodule], GraphvizId]


def make_graph(*
               , start_nodule: cpa.Nodule
               , nodule_edge_map: cpa.NoduleEdgeMap
               , nodule_converter: NoduleConverter=str
               ) -> pydot.Graph:
    # Breadth-first search to find all nodes
    # Create and initialize data structures to help
    frontier: typ.Deque[cpa.Nodule] = collections.deque()
    frontier.appendleft(start_nodule)

    visited: typ.MutableSet[cpa.Nodule] = set()
    visited.add(start_nodule)

    # Create Graphviz object
    graph = pydot.Dot(graph_type='digraph', strict=False)

    graph_nodes: typ.MutableSequence[pydot.Node] = []
    graph_edges: typ.MutableSequence[pydot.Edge] = []

    while frontier:
        curr_nodule: cpa.Nodule = frontier.pop()

        # Create graph object for nodule
        last_node_id = nodule_converter(curr_nodule)
        graph_nodes.append(pydot.Node(last_node_id))

        # Find all children of this nodule
        outbound_edges = nodule_edge_map[curr_nodule]

        for child_nodule, nodule_skewer in outbound_edges.items():
            # Draw a branch from current nodule to this child
            # Add elements as appropriate
            tokens = nodule_skewer.tokens
            command = nodule_skewer.command

            # Each token needs a GV node and edge
            for token in tokens:
                # TODO: Need a more robust way of handling ids for tokens!
                token_id: GraphvizId = str(token)

                # Create GV node
                graph_nodes.append(pydot.Node(token_id))

                # Create GV edge
                graph_edges.append(pydot.Edge(last_node_id, token_id, label='$'))

                # Update pointers for next iteration
                last_node_id = token_id

            # Close last edge of skewer
            child_nodule_id = nodule_converter(child_nodule)
            graph_edges.append(pydot.Edge(last_node_id, child_nodule_id, label='X'))

            if child_nodule not in visited:
                frontier.appendleft(child_nodule)
                visited.add(child_nodule)

    # TODO: Continue here! Need to add nodes and edges to graph

    return graph

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
