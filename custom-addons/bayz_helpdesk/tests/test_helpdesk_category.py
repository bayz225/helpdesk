from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

from .common import HelpdeskTestMixin


class TestHelpdeskCategory(HelpdeskTestMixin, TransactionCase):

    def test_category_names_are_unique_after_normalization(self):
        self.env["helpdesk.category"].create({"name": "  Catégorie   Santé "})

        with self.assertRaises(ValidationError):
            self.env["helpdesk.category"].create({"name": "categorie sante"})

    def test_only_manager_can_modify_category(self):
        category = self.env["helpdesk.category"].create({"name": "Category"})
        manager = self.create_user(
            "Category manager", ["bayz_helpdesk.group_helpdesk_manager"]
        )

        with self.assertRaises(UserError):
            category.with_user(self.env.user).write({"name": "Renamed"})

        category.with_user(manager).write({"name": "Renamed"})
        self.assertEqual(category.name, "Renamed")

    def test_ticket_count_tracks_category_tickets(self):
        category = self.env["helpdesk.category"].create({"name": "Count category"})
        ticket = self.create_ticket(category_id=category.id)

        self.assertEqual(category.count_tickets, 1)

        ticket.unlink()
        self.assertEqual(category.count_tickets, 0)
