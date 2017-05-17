import pprint
import typing as typ

import blessings
import colorama
import line_profiler

import cheffu.parallel as par
import cheffu.slot_filter as sf
import cheffu.graphviz as gv

colorama.init()

t = blessings.Terminal()

l_sf = sf.make_white_list(0, 1)
r_sf = sf.invert(l_sf)

sf_p_0_1 = sf.make_white_list(0, 1)

sample_slot_filters = {
    '0_1': sf.make_white_list(0, 1),
}

token_paths: typ.Mapping[str, par.TokenPath] = {
    # 'empty': (),
    # 'sequence': (
    #     par.Token('A'),
    #     par.Token('B'),
    #     par.Token('C'),
    #     par.Token('D'),
    #     par.Token('E'),
    # ),
    # 'simple_ub_split': (
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
    # 'kitchen_sink': (
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


def do_stuff():
    for token_path_key, token_path in token_paths.items():
        nodule_edge_map, start_nodule, close_nodule = par.process(token_path)
        graph = gv.make_graph(start_nodule=start_nodule, nodule_edge_map=nodule_edge_map)

        graph.write_png(f'{token_path_key}.png')

        count = 0
        choice_seqs: typ.List[par.SlotFilterChoiceSequence] = []
        for nodule_walk, stack_walk, choice_seq in par.yield_valid_nodule_walks(nodule_edge_map=nodule_edge_map
                                                                                , start_nodule=start_nodule
                                                                                , close_nodule=close_nodule
                                                                                ):
            choice_seqs.append(choice_seq)
            print(f'Choice Sequence: {str(choice_seq)}')
            # print(f'Allowed Slots: {str(allowed_slots)}')

            last_nodule: typ.Optional[par.Nodule] = None
            for nodule, slot_filter_stack in zip(nodule_walk, stack_walk):
                if last_nodule is not None:
                    tokens = nodule_edge_map[last_nodule][nodule].tokens
                    print(f'\tTokens: {str(tokens)}')

                last_nodule = nodule
                print('{:<8}{:<24}'.format(nodule, str(slot_filter_stack)))

            count += 1

            print(''.join(par.get_token_sequence(nodule_edge_map=nodule_edge_map, nodule_walk=nodule_walk)))

            print('-' * 80)

        unique_choice_sets = set(choice_seqs)
        print(f'Number of Choice Seqs: {len(choice_seqs)}')
        print(f'Number of Unique Choice Seqs: {len(unique_choice_sets)}')
        print(f'Unique Choice Sets:\n{pprint.pformat(sorted(unique_choice_sets))}')

        print(f'Number of Paths: {count}')

        print('=' * 80)

lp = line_profiler.LineProfiler()
lp_wrapper = lp(do_stuff)
lp_wrapper()
lp.print_stats()

# import cheffu.argument_schema
# import cheffu.defs
# import cheffu.grammars
# import cheffu.interfaces
# import cheffu.parallel
# import cheffu.slot_filter
# import cheffu.interfaces as chi
# import cheffu.sample_recipes as samples
# import pprint
#
# import voluptuous as vp
#
# recipe = samples.SampleRecipes['Magic Mushroom Powder']
# procedure = recipe['procedure']
#
# pprint.pprint(procedure)
# pprint.pprint(chi.process(procedure))
