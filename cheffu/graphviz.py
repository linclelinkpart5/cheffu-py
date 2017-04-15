import collections
import typing as typ
import pydot
import uuid

import cheffu.parallel as cpa
import cheffu.slot_filter as sf


GraphvizId = typ.NewType('GraphvizId', str)
NoduleConverter = typ.Callable[[cpa.Nodule], GraphvizId]


def make_graph(*
               , start_nodule: cpa.Nodule
               , nodule_edge_map: cpa.NoduleEdgeMap
               , nodule_converter: NoduleConverter=str
               ) -> pydot.Graph:
    def pretty_string(slot_filter_stack_command: cpa.SlotFilterStackCommand) -> str:
        if slot_filter_stack_command is None:
            return ''
        else:
            return '{} {}'.format(slot_filter_stack_command.direction.value
                                  , sf.pretty_string(slot_filter_stack_command.slot_filter)
                                  )

    # Breadth-first search to find all nodes
    # Create and initialize data structures to help
    frontier: typ.Deque[cpa.Nodule] = collections.deque()
    frontier.appendleft(start_nodule)

    visited: typ.MutableSet[cpa.Nodule] = set()
    visited.add(start_nodule)

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
            # Draw a branch from current nodule to this child, adding elements as appropriate
            tokens = nodule_skewer.tokens
            command = nodule_skewer.command

            # Each token needs a GV node and edge
            for token in tokens:
                token_id: GraphvizId = str(uuid.uuid4())

                # Create GV node
                graph_nodes.append(pydot.Node(token_id, shape='circle', label=str(token)))

                # Create GV edge
                edge_label: str = pretty_string(command)
                graph_edges.append(pydot.Edge(last_node_id, token_id, arrowhead='none', label=edge_label))

                # Set command to None, since only the first segment of the skewer is to be labeled
                command = None

                # Update pointers for next iteration
                last_node_id = token_id

            # Close last edge of skewer
            child_nodule_id = nodule_converter(child_nodule)
            edge_label: str = pretty_string(command)
            graph_edges.append(pydot.Edge(last_node_id, child_nodule_id, label=edge_label, arrowsize=0.5))

            # Reset last node id
            last_node_id = nodule_converter(curr_nodule)

            if child_nodule not in visited:
                frontier.appendleft(child_nodule)
                visited.add(child_nodule)

    assert graph_nodes
    assert graph_edges

    # Create Graphviz object
    graph: pydot.Graph = pydot.Dot(graph_type='digraph', strict=False)

    # Add nodes and edges to graph
    for graph_node in graph_nodes:
        graph.add_node(graph_node)

    for graph_edge in graph_edges:
        graph.add_edge(graph_edge)

    return graph
