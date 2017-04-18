import pprint
import typing as typ
import blessings
import colorama

import cheffu.parallel as par
import cheffu.slot_filter as sf
import cheffu.graphviz as gv

colorama.init()

t = blessings.Terminal()

l_sf = sf.make_white_list(0, 1)
r_sf = sf.invert(l_sf)

token_paths: typ.Mapping[str, par.TokenPath] = {
    # (),
    # (
    #     par.Token('A'),
    #     par.Token('B'),
    #     par.Token('C'),
    #     par.Token('D'),
    #     par.Token('E'),
    # ),
    # (
    #     par.Token('A'),
    #     par.Token('B'),
    #     (
    #         par.UnfilteredAlt(
    #             items=('C', 'D',),
    #         ),
    #         par.UnfilteredAlt(
    #             items=('C~', 'D~',),
    #         ),
    #     ),
    #     (
    #         par.UnfilteredAlt(
    #             items=('E', 'F',),
    #         ),
    #         par.UnfilteredAlt(
    #             items=('E~', 'F~',),
    #         ),
    #     ),
    #     par.Token('G'),
    # ),
    # (
    #     par.Token('O'),
    #     (
    #         par.FilteredAlt(
    #             items=(
    #                 (
    #                     par.FilteredAlt(
    #                         items=('P',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredAlt(
    #                         items=('Q',),
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #                 par.Token('R'),
    #                 (
    #                     par.FilteredAlt(
    #                         items=('S',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                 ),
    #             ),
    #             slot_filter=sf.make_white_list(0),
    #         ),
    #         par.FilteredAlt(
    #             items=(
    #                 (
    #                     par.FilteredAlt(
    #                         items=('P~',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredAlt(
    #                         items=('Q~',),
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #                 par.Token('R~'),
    #                 (
    #                     par.FilteredAlt(
    #                         items=('S~',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredNull(
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #             ),
    #             slot_filter=sf.make_white_list(2),
    #         ),
    #     ),
    #     par.Token('T'),
    # ),
    # (
    #     par.Token('A'),
    #     par.Token('B'),
    #     (
    #         par.UnfilteredAlt(
    #             items=('C', 'D',),
    #         ),
    #         par.UnfilteredAlt(
    #             items=('C~', 'D~',),
    #         ),
    #     ),
    #     par.Token('E'),
    #     (
    #         par.FilteredAlt(
    #             items=('F', 'G',),
    #             slot_filter=sf.make_white_list(0),
    #         ),
    #         par.FilteredAlt(
    #             items=('F~',),
    #             slot_filter=sf.make_white_list(1),
    #         ),
    #         par.FilteredAlt(
    #             items=('G~',),
    #             slot_filter=sf.make_white_list(0, 1),
    #         ),
    #     ),
    #     par.Token('H'),
    #     (
    #         par.UnfilteredAlt(
    #             items=('I',),
    #         ),
    #         par.UnfilteredNull(),
    #     ),
    #     par.Token('J'),
    #     (
    #         par.FilteredAlt(
    #             items=('K',),
    #             slot_filter=sf.make_white_list(0),
    #         ),
    #         par.FilteredAlt(
    #             items=('K~',),
    #             slot_filter=sf.make_white_list(1),
    #         ),
    #         par.FilteredNull(
    #             slot_filter=sf.make_white_list(2),
    #         ),
    #     ),
    #     par.Token('L'),
    #     (
    #         par.FilteredAlt(
    #             items=('M', 'N', 'NN', 'NNN',),
    #             slot_filter=sf.make_white_list(0),
    #         ),
    #     ),
    #     par.Token('O'),
    #     (
    #         par.FilteredAlt(
    #             items=(
    #                 (
    #                     par.FilteredAlt(
    #                         items=('P',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredAlt(
    #                         items=('Q',),
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #                 par.Token('R'),
    #                 (
    #                     par.FilteredAlt(
    #                         items=('S',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                 ),
    #             ),
    #             slot_filter=sf.make_white_list(0),
    #         ),
    #         par.FilteredAlt(
    #             items=(
    #                 (
    #                     par.FilteredAlt(
    #                         items=('P~',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredAlt(
    #                         items=('Q~',),
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #                 par.Token('R~'),
    #                 (
    #                     par.FilteredAlt(
    #                         items=('S~',),
    #                         slot_filter=sf.make_white_list(0),
    #                     ),
    #                     par.FilteredNull(
    #                         slot_filter=sf.make_white_list(1),
    #                     ),
    #                 ),
    #             ),
    #             slot_filter=sf.make_white_list(2),
    #         ),
    #     ),
    #     par.Token('T'),
    #     (
    #         par.UnfilteredAlt(
    #             items=('U',),
    #         ),
    #         par.FilteredAlt(
    #             items=('V',),
    #             slot_filter=sf.make_white_list(1),
    #         ),
    #         par.FilteredNull(
    #             slot_filter=sf.make_white_list(2),
    #         ),
    #     ),
    #     par.Token('W'),
    # ),
    'symmetric_depth_2': (
        par.Token('A'),
        (
            par.FilteredAlt(
                items=(
                    par.Token('B'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('D'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('E'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('H'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('J'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('K'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('N'),
                ),
                slot_filter=l_sf,
            ),
            par.FilteredAlt(
                items=(
                    par.Token('C'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('F'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('G'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('I'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('L'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('M'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('O'),
                ),
                slot_filter=r_sf,
            ),
        ),
        par.Token('P'),
        (
            par.FilteredAlt(
                items=(
                    par.Token('Q'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('S'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('T'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('W'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('Y'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('Z'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('2'),
                ),
                slot_filter=l_sf,
            ),
            par.FilteredAlt(
                items=(
                    par.Token('R'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('U'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('V'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('X'),
                    (
                        par.FilteredAlt(
                            items=(
                                par.Token('0'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                par.Token('1'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    par.Token('3'),
                ),
                slot_filter=r_sf,
            ),
        ),
        par.Token('4'),
    ),
}

# from line_profiler import LineProfiler
#
#
# def do_stuff():
#     slot_filter_choice_sequence: par.SlotFilterChoiceSequence = ((1,), (4, 5), (6,))
#
#     multiplexer = par.choice_sequence_multiplexer(slot_filter_choice_sequence)
#
#     print(multiplexer.next(0))
#     print(multiplexer.next(1))
#     print(multiplexer.next(1))
#     print(multiplexer.next(2))
#     multiplexer.empty_or_raise()
#
#     multiplexer = par.choice_sequence_multiplexer(slot_filter_choice_sequence)
#
#     memory = []
#     par.ensure_memory(multiplexer=multiplexer, target_path_degree=0, memory=memory)
#     print(memory)
#     par.ensure_memory(multiplexer=multiplexer, target_path_degree=2, memory=memory)
#     print(memory)
#     par.ensure_memory(multiplexer=multiplexer, target_path_degree=0, memory=memory)
#     print(memory)
#     par.ensure_memory(multiplexer=multiplexer, target_path_degree=1, memory=memory)
#     print(memory)
#     multiplexer.empty_or_raise()
#
# lp = LineProfiler()
# lp_wrapper = lp(do_stuff)
# lp_wrapper()
# lp.print_stats()


choices: par.SlotFilterChoiceSequence = (
    (sf.make_white_list(1),),
    (sf.make_white_list(0), sf.make_white_list(2)),
)

for token_path_key, token_path in token_paths.items():
    nodule_edge_map, start_nodule, close_nodule = par.process(token_path)
    graph = gv.make_graph(start_nodule=start_nodule, nodule_edge_map=nodule_edge_map)

    graph.write_png(f'{token_path_key}.png')

    # pprint.pprint(nodule_edge_map)

    for nodule_walk, slot_filter_stack_walk in par.yield_nodule_walks(nodule_edge_map=nodule_edge_map
                                                                      , start_nodule=start_nodule
                                                                      ):

        is_valid = par.is_legal_slot_filter_stack_walk(slot_filter_stack_walk=slot_filter_stack_walk)

        is_valid_str = t.green(str(is_valid)) if is_valid else t.red(str(is_valid))
        print(f'Is Valid? {is_valid_str}')

        if is_valid:
            for nodule, slot_filter_stack in zip(nodule_walk, slot_filter_stack_walk):
                print('{:<8}{}'.format(nodule, str(slot_filter_stack)))

        print('-' * 80)

    print('=' * 80)
