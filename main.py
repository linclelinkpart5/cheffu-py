import pprint
import typing as typ

import cheffu.parallel as par
import cheffu.slot_filter as sf
import cheffu.graphviz as gv

token_paths: typ.Sequence[par.TokenPath] = (
    (),
    (
        par.Token('A'),
        par.Token('B'),
        par.Token('C'),
        par.Token('D'),
        par.Token('E'),
    ),
    (
        par.Token('A'),
        par.Token('B'),
        (
            par.UnfilteredAlt(
                items=('C', 'D',),
            ),
            par.UnfilteredAlt(
                items=('C~', 'D~',),
            ),
        ),
        (
            par.UnfilteredAlt(
                items=('E', 'F',),
            ),
            par.UnfilteredAlt(
                items=('E~', 'F~',),
            ),
        ),
        par.Token('G'),
    ),
    (
        par.Token('O'),
        (
            par.FilteredAlt(
                items=(
                    (
                        par.FilteredAlt(
                            items=('P',),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredAlt(
                            items=('Q',),
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                    par.Token('R'),
                    (
                        par.FilteredAlt(
                            items=('S',),
                            slot_filter=sf.make_white_list(0),
                        ),
                    ),
                ),
                slot_filter=sf.make_white_list(0),
            ),
            par.FilteredAlt(
                items=(
                    (
                        par.FilteredAlt(
                            items=('P~',),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredAlt(
                            items=('Q~',),
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                    par.Token('R~'),
                    (
                        par.FilteredAlt(
                            items=('S~',),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredNull(
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                ),
                slot_filter=sf.make_white_list(2),
            ),
        ),
        par.Token('T'),
    ),
)

for i, token_path in enumerate(token_paths):
    nodule_edge_map, start_nodule, close_nodule = par.process(token_path)
    graph = gv.make_graph(start_nodule=start_nodule, nodule_edge_map=nodule_edge_map)

    graph.write_png(f'{i}.png')
