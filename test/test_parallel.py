import unittest
import typing as typ
import itertools
import functools as ft

import cheffu.parallel as par
import cheffu.slot_filter as sf
import cheffu.exceptions as chex
import cheffu.helpers as chlp


def yield_valid_stack_cmd_seqs(length: int) -> typ.Iterable[par.StackCommandSequence]:
    """Lazily yields valid stack command sequences with increasing slot filter values.

    Valid stack command sequences are properly nested and balanced, and follow Cheffu slot/scope rules.
    """
    # Using black lists because they have an infinite intersection set.
    # An intersection between any two black lists is always guaranteed to have some allowed slots.
    # This enables following Cheffu slot/scope rules.
    sf_count = itertools.count(start=sf.ALLOW_ALL, step=-1)

    def helper(n: int) -> typ.Iterable[par.StackCommandSequence]:
        if n <= 0:
            # Exactly one sequence of length 0.
            yield ()
            return

        # Generate sequences of NoOp + Subcombinations(n - 1).
        subcombinations = helper(n - 1)
        for subcombination in subcombinations:
            yield (None, *subcombination)

        # Generate sequences of the form Push(x) + Subcombinations(a) + Pop(x) + Subcombinations(b),
        # where a >= 0, b >= 0, and a + b = (length - 2).
        if n >= 2:
            for a, b in chlp.yield_sum_splits(n - 2):
                a_sub = helper(a)
                b_sub = helper(b)

                # Use itertools.product when using yield, nested for loops would omit some outputs, strangely.
                for a_part, b_part in itertools.product(a_sub, b_sub):
                    i = next(sf_count)
                    pu_op: par.StackOperation = par.StackOperation(direction=par.StackDirection.PUSH, slot_filter=i)
                    po_op: par.StackOperation = par.StackOperation(direction=par.StackDirection.POP, slot_filter=i)
                    yield (pu_op, *a_part, po_op, *b_part)

    yield from helper(length)


class TestParallel(unittest.TestCase):
    # VALID_SLOT_FILTER_MAP: typ.Mapping[str, sf.SlotFilter] = {
    #     'allow_all': sf.ALLOW_ALL,
    #     'block_all': sf.BLOCK_ALL,
    #     '0': sf.make_white_list(0),
    #     '1': sf.make_white_list(1),
    #     '2': sf.make_white_list(2),
    #     '0,1': sf.make_white_list(0, 1),
    #     '0,2': sf.make_white_list(0, 2),
    #     '1,2': sf.make_white_list(1, 2),
    #     '0,1,2': sf.make_white_list(0, 1, 2),
    #     '!0': sf.make_black_list(0),
    #     '!1': sf.make_black_list(1),
    #     '!2': sf.make_black_list(2),
    #     '!0,1': sf.make_black_list(0, 1),
    #     '!0,2': sf.make_black_list(0, 2),
    #     '!1,2': sf.make_black_list(1, 2),
    #     '!0,1,2': sf.make_black_list(0, 1, 2),
    # }

    # VALID_TOKEN_PATH_MAP: typ.Mapping[str, par.TokenPath] = {
    #     'empty': (),
    #     'sequence': (
    #         par.Token('A'),
    #         par.Token('B'),
    #         par.Token('C'),
    #         par.Token('D'),
    #         par.Token('E'),
    #     ),
    #     'simple_ub_split': (
    #         par.Token('A'),
    #         par.Token('B'),
    #         (
    #             par.FilteredAlt(
    #                 items=('C', 'D',),
    #             ),
    #             par.FilteredAlt(
    #                 items=('C~', 'D~',),
    #             ),
    #         ),
    #         (
    #             par.FilteredAlt(
    #                 items=('E', 'F',),
    #             ),
    #             par.FilteredAlt(
    #                 items=('E~', 'F~',),
    #             ),
    #         ),
    #         par.Token('G'),
    #     ),
    #     'kitchen_sink': (
    #         par.Token('A'),
    #         par.Token('B'),
    #         (
    #             par.FilteredAlt(
    #                 items=('C', 'D',),
    #             ),
    #             par.FilteredAlt(
    #                 items=('C~', 'D~',),
    #             ),
    #         ),
    #         par.Token('E'),
    #         (
    #             par.FilteredAlt(
    #                 items=('F', 'G',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #             par.FilteredAlt(
    #                 items=('F~',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #             ),
    #             par.FilteredAlt(
    #                 items=('G~',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0,1'],
    #             ),
    #         ),
    #         par.Token('H'),
    #         (
    #             par.FilteredAlt(
    #                 items=('I',),
    #             ),
    #             par.FilteredAlt(),
    #         ),
    #         par.Token('J'),
    #         (
    #             par.FilteredAlt(
    #                 items=('K',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #             par.FilteredAlt(
    #                 items=('K~',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #             ),
    #             par.FilteredAlt(
    #                 slot_filter=VALID_SLOT_FILTER_MAP['2'],
    #             ),
    #         ),
    #         par.Token('L'),
    #         (
    #             par.FilteredAlt(
    #                 items=('M', 'N', 'NN', 'NNN',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #         ),
    #         par.Token('O'),
    #         (
    #             par.FilteredAlt(
    #                 items=(
    #                     (
    #                         par.FilteredAlt(
    #                             items=('P',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=('Q',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #                         ),
    #                     ),
    #                     par.Token('R'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=('S',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                     ),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #             par.FilteredAlt(
    #                 items=(
    #                     (
    #                         par.FilteredAlt(
    #                             items=('P~',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=('Q~',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #                         ),
    #                     ),
    #                     par.Token('R~'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=('S~',),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #                         ),
    #                     ),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['2'],
    #             ),
    #         ),
    #         par.Token('T'),
    #         (
    #             par.FilteredAlt(
    #                 items=('U',),
    #             ),
    #             par.FilteredAlt(
    #                 items=('V',),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['1'],
    #             ),
    #             par.FilteredAlt(
    #                 slot_filter=VALID_SLOT_FILTER_MAP['2'],
    #             ),
    #         ),
    #         par.Token('W'),
    #     ),
    #     'symmetric_depth_2': (
    #         par.Token('A'),
    #         (
    #             par.FilteredAlt(
    #                 items=(
    #                     par.Token('B'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('D'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('E'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('H'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('J'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('K'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('N'),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #             par.FilteredAlt(
    #                 items=(
    #                     par.Token('C'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('F'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('G'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('I'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('L'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('M'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('O'),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #             ),
    #         ),
    #         par.Token('P'),
    #         (
    #             par.FilteredAlt(
    #                 items=(
    #                     par.Token('Q'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('S'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('T'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('W'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('Y'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('Z'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('2'),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #             ),
    #             par.FilteredAlt(
    #                 items=(
    #                     par.Token('R'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('U'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('V'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('X'),
    #                     (
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('0'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['0'],
    #                         ),
    #                         par.FilteredAlt(
    #                             items=(
    #                                 par.Token('1'),
    #                             ),
    #                             slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #                         ),
    #                     ),
    #                     par.Token('3'),
    #                 ),
    #                 slot_filter=VALID_SLOT_FILTER_MAP['!0'],
    #             ),
    #         ),
    #         par.Token('4'),
    #     ),
    #     'singleton_ub_split': (
    #         (
    #             par.FilteredAlt(
    #                 items=('A', 'B'),
    #             ),
    #             par.FilteredAlt(
    #                 items=('A~', 'B~'),
    #             ),
    #         ),
    #     ),
    # }

    VALID_SLOT_SETS = frozenset({
        (),
        (0,),
        (1,),
        (2,),
        (0, 1),
        (0, 2),
        (1, 2),
        (0, 1, 2),
    })

    VALID_WHITE_LIST_SLOT_FILTERS = frozenset({
        sf.make_white_list(*t) for t in VALID_SLOT_SETS
    })

    VALID_BLACK_LIST_SLOT_FILTERS = frozenset({
        sf.make_black_list(*t) for t in VALID_SLOT_SETS
    })

    VALID_SLOT_FILTERS = VALID_WHITE_LIST_SLOT_FILTERS | VALID_BLACK_LIST_SLOT_FILTERS

    VALID_STACKS = frozenset({
        *itertools.chain(
            (tuple(it) for it in itertools.product(VALID_SLOT_FILTERS, repeat=1)),
            (tuple(it) for it in itertools.product(VALID_SLOT_FILTERS, repeat=2)),
            (tuple(it) for it in itertools.product(VALID_SLOT_FILTERS, repeat=3)),
        ),
        (),
    })

    VALID_STACK_COMMANDS = frozenset({
        None,
        *(
            par.StackOperation(direction=d, slot_filter=sf)
            for d, sf in itertools.product(par.StackDirection.__members__.values()
                                           , VALID_SLOT_FILTERS
                                           )
        ),
    })

    VALID_STACK_CMD_SEQS = tuple(
        itertools.chain.from_iterable(yield_valid_stack_cmd_seqs(i) for i in range(6))
    )

    def test_process_stack(self):
        for v_stack, v_stack_cmd in itertools.product(self.VALID_STACKS, self.VALID_STACK_COMMANDS):
            # By default, use an empty context manager for later.
            # Set to an assertRaises if we expect an error condition.
            ctx_manager = chlp.empty_context

            if v_stack_cmd is None:
                expected_stack = v_stack
            else:
                direction = v_stack_cmd.direction
                slot_filter = v_stack_cmd.slot_filter

                if direction == par.StackDirection.PUSH:
                    expected_stack = v_stack + (slot_filter,)
                elif direction == par.StackDirection.POP:
                    expected_stack = v_stack[:-1]
                    if not v_stack:
                        # Popping from an empty stack, we expect an exception.
                        ctx_manager = ft.partial(self.assertRaises
                                                 , expected_exception=chex.SlotFilterStackEmpty
                                                 )
                    elif v_stack[-1] != slot_filter:
                        # Popped slot filter would not match what we expect, we expect an exception.
                        ctx_manager = ft.partial(self.assertRaises
                                                 , expected_exception=chex.SlotFilterStackResultMismatch
                                                 )
                else:
                    self.fail(f'Unknown stack direction = {direction}')

            with ctx_manager():
                actual_stack = par.process_stack(stack=v_stack, stack_cmd=v_stack_cmd)
                self.assertEqual(expected_stack, actual_stack)

    def test_validate_stack_cmd_seq_a(self):
        for stack_cmd_seq in self.VALID_STACK_CMD_SEQS:
            is_valid, _ = par.validate_stack_cmd_seq(stack_cmd_seq=stack_cmd_seq)
            self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()
