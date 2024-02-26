# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from . import test_fsm_order


class TestFsmCategory(test_fsm_order.TestFSMOrder):
    def setUp(self):
        super().setUp()
        fsm_category = self.env["fsm.category"]
        self.fsm_category_a = fsm_category.create({"name": "Category A"})
        self.fsm_category_b = fsm_category.create(
            {"name": "Category B", "parent_id": self.fsm_category_a.id}
        )
        self.fsm_category_c = fsm_category.create(
            {"name": "Category C", "parent_id": self.fsm_category_b.id}
        )

    def test_fsm_order_category(self):
        self.assertEqual(self.fsm_category_a.full_name, self.fsm_category_a.name)
        self.assertEqual(
            self.fsm_category_b.full_name,
            "%s / %s" % (self.fsm_category_a.name, self.fsm_category_b.name),
        )

    def test_fsm_category_recursion(self):
        self.assertTrue(self.fsm_category_c._check_recursion())
        with self.assertRaises(UserError):
            self.fsm_category_a.write({"parent_id": self.fsm_category_c.id})
