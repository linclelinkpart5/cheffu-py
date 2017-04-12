import collections
import itertools
import unittest

import cheffu.slot_filter as sf


class TestBitFilter(unittest.TestCase):
    MAX_SLOTS = 8

    VALID_SLOT_INDICES = tuple(range(MAX_SLOTS))
    INVALID_SLOT_INDICES = tuple(-1 - i for i in VALID_SLOT_INDICES)

    SLOT_INDEX_COMBINATIONS_MAP = {}
    for choose in range(MAX_SLOTS + 1):
        tmp_list = []
        for combo in itertools.combinations(VALID_SLOT_INDICES, choose):
            tmp_list.append(combo)
        SLOT_INDEX_COMBINATIONS_MAP[choose] = tuple(tmp_list)

    SLOT_INDEX_COMBINATIONS = tuple(itertools.chain.from_iterable(v for _, v in sorted(SLOT_INDEX_COMBINATIONS_MAP.items())))

    SINGLE_INDEX_SLOTS = tuple(1 << i for i in VALID_SLOT_INDICES)

    SAMPLE_FILTER_SLOTS = (
        *((i,) for i in VALID_SLOT_INDICES),
        VALID_SLOT_INDICES[::2],
        VALID_SLOT_INDICES[1::2],
        VALID_SLOT_INDICES[:MAX_SLOTS // 2],
        VALID_SLOT_INDICES[MAX_SLOTS // 2:],
        VALID_SLOT_INDICES,
        (),
    )

    SAMPLE_FILTERS = tuple(sf.make_white_list(*slots) for slots in SAMPLE_FILTER_SLOTS)

    def test_set_indices_args(self):
        for i in self.VALID_SLOT_INDICES:
            self.assertEqual(sf.make_white_list(i), self.SINGLE_INDEX_SLOTS[i])

        # Test that a zero-length filter blocks everything
        self.assertEqual(sf.make_white_list(), sf.BLOCK_ALL)

        # Negative bit shifts raise ValueError
        for i in self.INVALID_SLOT_INDICES:
            with self.assertRaises(ValueError):
                sf.make_white_list(i)

    def test_set_indices_multi(self):
        # Try all possible combinations (order does not matter)
        for choose in range(self.MAX_SLOTS + 1):
            for combo in itertools.combinations(self.VALID_SLOT_INDICES, choose):
                slots = sf.make_white_list(*combo)

                for i, slot in enumerate(self.SINGLE_INDEX_SLOTS):
                    if i in combo:
                        self.assertTrue(slots & slot)
                    else:
                        self.assertFalse(slots & slot)

    def test_any_pass(self):
        for indices, philter in zip(self.SAMPLE_FILTER_SLOTS, self.SAMPLE_FILTERS):
            indices_set = set(indices)
            for combo in self.SLOT_INDEX_COMBINATIONS:
                combo_set = set(combo)
                value = sf.make_white_list(*combo)
                if indices_set & combo_set:
                    # This should return true
                    self.assertTrue(sf.any_pass(philter, value))
                else:
                    # This should return false
                    self.assertFalse(sf.any_pass(philter, value))

    def test_all_pass(self):
        for indices, philter in zip(self.SAMPLE_FILTER_SLOTS, self.SAMPLE_FILTERS):
            indices_set = set(indices)
            for combo in self.SLOT_INDEX_COMBINATIONS:
                combo_set = set(combo)
                value = sf.make_white_list(*combo)
                if indices_set >= combo_set:
                    # This should return true
                    self.assertTrue(sf.all_pass(philter, value))
                else:
                    # This should return false
                    self.assertFalse(sf.all_pass(philter, value))

    def test_slot_n_allowed(self):
        for indices, philter in zip(self.SAMPLE_FILTER_SLOTS, self.SAMPLE_FILTERS):
            indices_set = set(indices)
            for combo in self.SLOT_INDEX_COMBINATIONS:
                for slot in combo:
                    if slot in indices_set:
                        # This should return true
                        self.assertTrue(sf.slot_n_allowed(philter, slot))
                    else:
                        # This should return false
                        self.assertFalse(sf.slot_n_allowed(philter, slot))

if __name__ == '__main__':
    unittest.main()
