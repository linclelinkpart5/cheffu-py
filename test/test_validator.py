# import itertools as it
# import unittest
# import typing as typ
#
# import cheffu.validator as chv
#
#
# class TestValidator(unittest.TestCase):
#     VALID_TNIDS: typ.AbstractSet[chv.TNID] = frozenset(range(6))
#
#     VALID_TNID_STACKS: typ.Collection[chv.TNIDStack] = frozenset({
#         (),
#         *it.chain(
#             (tuple(p) for p in it.product(VALID_TNIDS, repeat=1)),
#             (tuple(p) for p in it.product(VALID_TNIDS, repeat=2)),
#             (tuple(p) for p in it.product(VALID_TNIDS, repeat=3)),
#             (tuple(p) for p in it.product(VALID_TNIDS, repeat=4)),
#         ),
#     })
#
#     def test_split_stack(self):
#         for tnid_stack in self.VALID_TNID_STACKS:
#             length = len(tnid_stack)
#
#             for n in range(length + 1):
#                 prefix, suffix = chv.split_stack(tnid_stack=tnid_stack, n=n)
#
#                 self.assertEqual(tnid_stack, (*prefix, *suffix))
#                 self.assertEqual(len(suffix), n)
#
#             # Test fail case
#             with self.assertRaises(chv.TNIDStackNotEnoughElements):
#                 _, _ = chv.split_stack(tnid_stack=tnid_stack, n=(length + 1))
#
#
# if __name__ == '__main__':
#     unittest.main()
