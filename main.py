import pprint
import typing as typ

import blessings
import colorama
import line_profiler

import cheffu.parallel as par
import cheffu.slot_filter as sf
import cheffu.graphviz as gv
import cheffu.logging as clog
import cheffu.types.common as ctpc
import cheffu.types.tokens as ctpt

logger = clog.get_logger(__name__)

colorama.init()

t = blessings.Terminal()

l_sf = sf.make_white_list(0, 1)
r_sf = sf.invert(l_sf)

sf_p_0_1 = sf.make_white_list(0, 1)

sample_slot_filters = {
    '0_1': sf.make_white_list(0, 1),
}


def token(x: str) -> ctpt.Token:
    return ctpt.Token(id=par.DEFAULT_UNIQUE_ID_GEN(), type_def=None, data=x)


token_paths: typ.Mapping[str, par.ProcedurePath] = {
    'empty': (),
    'sequence': (
        token('A'),
        token('B'),
        token('C'),
        token('D'),
        token('E'),
    ),
    'simple_ub_split': (
        token('A'),
        token('B'),
        (
            par.FilteredAlt(
                items=(token('C'), token('D'),),
            ),
            par.FilteredAlt(
                items=(token('C~'), token('D~'),),
            ),
        ),
        (
            par.FilteredAlt(
                items=(token('E'), token('F'),),
            ),
            par.FilteredAlt(
                items=(token('E~'), token('F~'),),
            ),
        ),
        token('G'),
    ),
    'singleton_ub_split': (
        (
            par.FilteredAlt(items=(token('A'), token('B'))),
            par.FilteredAlt(items=(token('A~'), token('B~'))),
        ),
    ),
    'kitchen_sink': (
        token('A'),
        token('B'),
        (
            par.FilteredAlt(
                items=(
                    token('C'),
                    token('D'),
                ),
            ),
            par.FilteredAlt(
                items=(
                    token('C~'),
                    token('D~'),
                ),
            ),
        ),
        token('E'),
        (
            par.FilteredAlt(
                items=(
                    token('F'),
                    token('G'),
                ),
                slot_filter=sf.make_white_list(0),
            ),
            par.FilteredAlt(
                items=(
                    token('F~'),
                ),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredAlt(
                items=(
                    token('G~'),
                ),
                slot_filter=sf.make_white_list(0, 1),
            ),
        ),
        token('H'),
        (
            par.FilteredAlt(
                items=(
                    token('I'),
                ),
            ),
            par.FilteredAlt(),
        ),
        token('J'),
        (
            par.FilteredAlt(
                items=(
                    token('K'),
                ),
                slot_filter=sf.make_white_list(0),
            ),
            par.FilteredAlt(
                items=(
                    token('K~'),
                ),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredAlt(
                slot_filter=sf.make_white_list(2),
            ),
        ),
        token('L'),
        (
            par.FilteredAlt(
                items=(
                    token('M'),
                    token('N'),
                    token('NN'),
                    token('NNN'),
                ),
                slot_filter=sf.make_white_list(0),
            ),
        ),
        token('O'),
        (
            par.FilteredAlt(
                items=(
                    (
                        par.FilteredAlt(
                            items=(
                                token('P'),
                            ),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredAlt(
                            items=(
                                token('Q'),
                            ),
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                    token('R'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('S'),
                            ),
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
                            items=(
                                token('P~'),
                            ),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredAlt(
                            items=(
                                token('Q~'),
                            ),
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                    token('R~'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('S~'),
                            ),
                            slot_filter=sf.make_white_list(0),
                        ),
                        par.FilteredAlt(
                            slot_filter=sf.make_white_list(1),
                        ),
                    ),
                ),
                slot_filter=sf.make_white_list(2),
            ),
        ),
        token('T'),
        (
            par.FilteredAlt(
                items=(
                    token('U'),
                ),
            ),
            par.FilteredAlt(
                items=(
                    token('V'),
                ),
                slot_filter=sf.make_white_list(1),
            ),
            par.FilteredAlt(
                slot_filter=sf.make_white_list(2),
            ),
        ),
        token('W'),
    ),
    'symmetric_depth_2': (
        token('A'),
        (
            par.FilteredAlt(
                items=(
                    token('B'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('D'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('E'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('H'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('J'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('K'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('N'),
                ),
                slot_filter=l_sf,
            ),
            par.FilteredAlt(
                items=(
                    token('C'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('F'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('G'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('I'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('L'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('M'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('O'),
                ),
                slot_filter=r_sf,
            ),
        ),
        token('P'),
        (
            par.FilteredAlt(
                items=(
                    token('Q'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('S'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('T'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('W'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('Y'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('Z'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('2'),
                ),
                slot_filter=l_sf,
            ),
            par.FilteredAlt(
                items=(
                    token('R'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('U'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('V'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('X'),
                    (
                        par.FilteredAlt(
                            items=(
                                token('0'),
                            ),
                            slot_filter=l_sf,
                        ),
                        par.FilteredAlt(
                            items=(
                                token('1'),
                            ),
                            slot_filter=r_sf,
                        ),
                    ),
                    token('3'),
                ),
                slot_filter=r_sf,
            ),
        ),
        token('4'),
    ),
}


def do_stuff():
    for token_path_key, token_path in token_paths.items():
        logger.info(f"Starting processing for token path '{token_path_key}'")
        nodule_out_edge_map, edge_lookup_map, start_nodule, close_nodule = par.process(procedure_path=token_path)

        gv_graph = gv.make_graph(nodule_out_edge_map=nodule_out_edge_map, edge_lookup_map=edge_lookup_map)

        gv_graph.write_png(f'{token_path_key}.png')

lp = line_profiler.LineProfiler()
lp_wrapper = lp(do_stuff)
lp_wrapper()
lp.print_stats()

import cheffu.argument_schema
import cheffu.defs
import cheffu.grammars
import cheffu.interfaces
import cheffu.parallel
import cheffu.slot_filter
import cheffu.interfaces as chi
import cheffu.sample_recipes as samples
import cheffu.defs
