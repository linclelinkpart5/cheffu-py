import itertools
import typing as typ
import pydot

import cheffu.parallel as par
import cheffu.logging as clog

logger = clog.get_logger(__name__)

GraphvizId = typ.NewType('GraphvizId', str)
UniqueIdConverter = typ.Callable[[par.UniqueId], GraphvizId]
TokenConverter = typ.Callable[[par.Token], str]


def make_graph(*
               , nodule_out_edge_map: par.NoduleOutEdgeMap
               , edge_lookup_map: par.EdgeLookupMap
               , unique_id_conv: UniqueIdConverter=None
               , token_conv: TokenConverter=None
               ) -> pydot.Graph:
    # If ID converter is not specified, use the default.
    if unique_id_conv is None:
        logger.info('Unique ID converter not specified, using default converter')

        def unique_id_conv(x):
            return str(x)

    # If token converter is not specified, use the default.
    if token_conv is None:
        logger.info('Token converter not specified, using default converter')

        def token_conv(t: par.Token) -> str:
            token_data: par.TokenData = t.data
            return str(token_data)

    # Storage for Graphviz nodes and edges.
    gv_node_map: typ.MutableMapping[par.UniqueId, pydot.Node] = {}
    gv_edges: typ.MutableSequence[pydot.Edge] = []

    # Create Graphviz nodes from nodules.
    nodule_count = 0
    for nodule in nodule_out_edge_map:
        nodule_gv_node = pydot.Node(name=unique_id_conv(nodule)
                                    , shape='point'
                                    , width=0.125
                                    , height=0.125
                                    )

        gv_node_map[nodule] = nodule_gv_node
        nodule_count += 1

    logger.info(f'Created {nodule_count} Graphviz node(s) from nodules')

    # Create Graphviz nodes from tokens.
    token_count = 0
    for token in itertools.chain.from_iterable(edge_def.token_seq for edge_def in edge_lookup_map.values()):
        token_id: par.TokenId = token.id

        token_gv_node = pydot.Node(name=unique_id_conv(token_id)
                                   , shape='circle'
                                   , label=token_conv(token)
                                   )

        gv_node_map[token_id] = token_gv_node
        token_count += 1

    logger.info(f'Created {token_count} Graphviz node(s) from tokens')

    # Creating Graphviz edges are more complicated.
    # An edge needs to be drawn between nodules and tokens, not just from nodule to nodule.
    # In addition, only edges directly entering a nodule should have arrowheads.
    # Start with each edge definition.
    virtual_edge_count = 0
    for edge_id, edge_def in edge_lookup_map.items():
        src_nodule: par.Nodule = edge_def.src_nodule
        dst_nodule: par.Nodule = edge_def.dst_nodule
        token_seq: par.TokenSequence = edge_def.token_seq

        # For this edge definition, this stores the newest node ID to connect a Graphviz edge from.
        curr_anchor_node_id: par.UniqueId = src_nodule
        tail_label: str = par.stack_cmd_label_str(edge_def.start_cmd)
        head_label: str = par.stack_cmd_label_str(edge_def.close_cmd)

        for token in token_seq:
            token_id: par.TokenId = token.id

            # Draw a Graphviz edge (without arrowhead) from the current anchor node to this token.
            gv_edge = pydot.Edge(gv_node_map[curr_anchor_node_id]
                                 , gv_node_map[token_id]
                                 , arrowhead='none'
                                 , headlabel=''
                                 , taillabel=tail_label
                                 )

            tail_label = ''

            gv_edges.append(gv_edge)

            # Update the current anchor node ID.
            curr_anchor_node_id = token_id

        # Draw a Graphviz edge from the current anchor node to the destination nodule.
        # This edge will have an arrowhead.
        gv_edge = pydot.Edge(gv_node_map[curr_anchor_node_id]
                             , gv_node_map[dst_nodule]
                             , arrowhead='vee'
                             , headlabel=head_label
                             , taillabel=tail_label
                             )

        gv_edges.append(gv_edge)
        virtual_edge_count += 1

    actual_edge_count = len(gv_edges)

    logger.info(f'Created {actual_edge_count} Graphviz edge(s) from {virtual_edge_count} virtual edge(s)')

    # Create Graphviz graph, and add nodes and edges to it.
    graph: pydot.Graph = pydot.Dot(graph_type='digraph'
                                   , strict=False
                                   , overlap=False
                                   , splines=True
                                   )

    for gv_node in gv_node_map.values():
        graph.add_node(gv_node)

    for gv_edge in gv_edges:
        graph.add_edge(gv_edge)

    return graph
