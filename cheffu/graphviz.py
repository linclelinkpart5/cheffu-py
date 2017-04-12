import collections
import typing as typ

import pydot

import cheffu.parallel as cpa
import cheffu.slot_filter as sf


GraphvizId = typ.NewType('GraphvizId', str)
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
    graph: pydot.Graph = pydot.Dot(graph_type='digraph', strict=False)

    graph_nodes: typ.MutableSequence[pydot.Node] = []
    graph_edges: typ.MutableSequence[pydot.Edge] = []

    while frontier:
        curr_nodule: cpa.Nodule = frontier.pop()

        # Create graph object for nodule
        last_node_id = nodule_converter(curr_nodule)
        graph_nodes.append(pydot.Node(last_node_id, shape='point', width=0.125, height=0.125))

        # Find all children of this nodule
        outbound_edges = nodule_edge_map[curr_nodule]

        for child_nodule, nodule_skewer in outbound_edges.items():
            # Draw a branch from current nodule to this child
            # Add elements as appropriate
            tokens = nodule_skewer.tokens
            command = nodule_skewer.command

            stack_direction: cpa.StackDirection = None
            slot_filter: sf.SlotFilter = None

            # TODO: Actually use the stack for drawing slot filters
            if command is not None:
                stack_direction, slot_filter = command

            # Each token needs a GV node and edge
            command_already_set = False
            for token in tokens:
                # TODO: Need a more robust way of handling ids for tokens!
                token_id: GraphvizId = str(token)

                # Create GV node
                graph_nodes.append(pydot.Node(token_id, shape='circle'))

                # Create GV edge
                edge_label: str = '' if (command is None or command_already_set) else '{} {}'.format(stack_direction, sf.pretty_string(slot_filter))
                command_already_set = True
                graph_edges.append(pydot.Edge(last_node_id, token_id, arrowhead='none', label=edge_label))

                # Update pointers for next iteration
                last_node_id = token_id

            # Close last edge of skewer
            child_nodule_id = nodule_converter(child_nodule)
            edge_label: str = '' if (command is None or command_already_set) else '{} {}'.format(stack_direction, sf.pretty_string(slot_filter))
            command_already_set = True
            graph_edges.append(pydot.Edge(last_node_id, child_nodule_id, label=edge_label))

            # Reset last node id
            last_node_id = nodule_converter(curr_nodule)

            if child_nodule not in visited:
                frontier.appendleft(child_nodule)
                visited.add(child_nodule)

    assert graph_nodes
    assert graph_edges

    # Add nodes and edges to graph
    for graph_node in graph_nodes:
        graph.add_node(graph_node)

    for graph_edge in graph_edges:
        graph.add_edge(graph_edge)

    return graph
