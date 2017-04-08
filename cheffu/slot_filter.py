import typing
import functools
import operator

SlotFilter = typing.NewType('SlotFilter', int)
SlotIndex = typing.NewType('SlotIndex', int)
SlotSelection = typing.NewType('SlotSelection', int)

ALL_ZERO = SlotFilter(0)
ALL_ONES = SlotFilter(-1)

BLOCK_ALL = ALL_ZERO
ALLOW_ALL = ALL_ONES


def set_indices(*indices: SlotIndex) -> SlotFilter:
    """Given a list of non-negative integer indices, returns an integer with
    those bit position indices set to 1, and all other bits set to 0.

    Note that the LSB is considered to be index 0.
    """
    f: SlotFilter = ALL_ZERO
    for index in indices:
        f |= (1 << index)
    return f

make_white_list = set_indices


def make_black_list(*slots: SlotIndex) -> SlotFilter:
    """Given a list of non-negative integer indices, returns an integer with
    those bit position indices set to 0, and all other bits set to 1.

    Note that the LSB is considered to be index 0.
    """
    return ~(make_white_list(*slots))


def union(slot_filter_a: SlotFilter, slot_filter_b: SlotFilter) -> SlotFilter:
    return slot_filter_a | slot_filter_b


def intersection(slot_filter_a: SlotFilter, slot_filter_b: SlotFilter) -> SlotFilter:
    return slot_filter_a & slot_filter_b


def subtract(slot_filter_a: SlotFilter, slot_filter_b: SlotFilter) -> SlotFilter:
    return slot_filter_a & (~slot_filter_b)


def invert(slot_filter_a: SlotFilter) -> SlotFilter:
    return ~slot_filter_a


def any_pass(slot_filter: SlotFilter, slot_selection: SlotSelection) -> bool:
    return bool(slot_filter & slot_selection)


def all_pass(slot_filter: SlotFilter, slot_selection: SlotSelection) -> bool:
    return (slot_filter & slot_selection) == slot_selection


def is_white_list(slot_filter: SlotFilter) -> bool:
    return slot_filter >= 0


def is_black_list(slot_filter: SlotFilter) -> bool:
    return not is_white_list(slot_filter)


def _yield_bits(slot_filter: SlotFilter, stop_bit: bool) -> typing.Iterator[typing.Tuple[SlotIndex, bool]]:
    count = SlotIndex(0)
    mask = 0b1
    stop_val = ALL_ONES if stop_bit else ALL_ZERO
    while slot_filter != stop_val:
        bit = slot_filter & mask
        yield count, bool(bit)
        count += 1
        slot_filter >>= 1


def allowed_slots(slot_filter: SlotFilter) -> typing.Iterator[SlotIndex]:
    flag = True
    yield from (count for count, is_set in _yield_bits(slot_filter, not flag) if is_set == flag)


def blocked_slots(slot_filter: SlotFilter) -> typing.Iterator[SlotIndex]:
    flag = False
    yield from (count for count, is_set in _yield_bits(slot_filter, not flag) if is_set == flag)


def slot_n_allowed(slot_filter: SlotFilter, index: SlotIndex) -> bool:
    slots = set_indices(index)
    return all_pass(slot_filter, slots)


def pretty_string(slot_filter: SlotFilter) -> str:
    if slot_filter == ALLOW_ALL:
        return 'any'
    elif slot_filter == BLOCK_ALL:
        return 'none'
    else:
        is_white = is_white_list(slot_filter)
        slots = allowed_slots(slot_filter) if is_white else blocked_slots(slot_filter)

        slots_str = ', '.join(str(s) for s in slots)

        template = '{}' if is_white else '~({})'

        return template.format(slots_str)
