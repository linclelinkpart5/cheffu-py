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
        par.Token('E'),
        (
            par.FilteredAlt(
                items=('F', 'G',),
                slot_filter=sf.make_white_list(0),
            ),
            par.FilteredAlt(
                items=('F~',),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredAlt(
                items=('G~',),
                slot_filter=sf.make_white_list(0, 1),
            ),
        ),
        par.Token('H'),
        (
            par.UnfilteredAlt(
                items=('I',),
            ),
            par.UnfilteredNull(),
        ),
        par.Token('J'),
        (
            par.FilteredAlt(
                items=('K',),
                slot_filter=sf.make_white_list(0),
            ),
            par.FilteredAlt(
                items=('K~',),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredNull(
                slot_filter=sf.make_white_list(2),
            ),
        ),
        par.Token('L'),
        (
            par.FilteredAlt(
                items=('M', 'N', 'NN', 'NNN',),
                slot_filter=sf.make_white_list(0),
            ),
        ),
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
        (
            par.UnfilteredAlt(
                items=('U',),
            ),
            par.FilteredAlt(
                items=('V',),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredNull(
                slot_filter=sf.make_white_list(2),
            ),
        ),
    ),
)

for i, token_path in enumerate(token_paths):
    nodule_edge_map, start_nodule, close_nodule = par.process(token_path)
    graph = gv.make_graph(start_nodule=start_nodule, nodule_edge_map=nodule_edge_map)

    nodule_walks = []
    nodule_walks_set = set()

    for nodule_walk in par.yield_nodule_walks(nodule_edge_map=nodule_edge_map, start_nodule=start_nodule):
        print(nodule_walk)
        print('-' * 80)
        nodule_walks.append(nodule_walk)
        nodule_walks_set.add(nodule_walk)

    print(len(nodule_walks), len(nodule_walks_set))

    graph.write_png(f'{i}.png')
    print('=' * 80)
