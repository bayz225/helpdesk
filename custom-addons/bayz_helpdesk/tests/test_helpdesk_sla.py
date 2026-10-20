from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


# Échéances SLA, réouverture et recherche des tickets en retard.
class TestHelpdeskSLA(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket_model = cls.env["helpdesk.ticket"]

    def _create_ticket(self, priority="0"):
        return self.ticket_model.create({
            "name": "Test SLA",
            "requester_id": self.env.user.id,
            "priority": priority,
        })

    def test_deadline_matches_each_priority(self):
        deadlines = {
            "0": timedelta(days=7),
            "1": timedelta(days=3),
            "2": timedelta(hours=24),
            "3": timedelta(hours=6),
        }

        for priority, delay in deadlines.items():
            with self.subTest(priority=priority):
                ticket = self._create_ticket(priority=priority)
                self.assertEqual(ticket.deadline, ticket.create_date + delay)

    def test_deadline_is_recomputed_when_priority_changes(self):
        manager_group = self.env.ref("bayz_helpdesk.group_helpdesk_manager")
        manager = self.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "SLA Manager",
            "login": "sla_manager_test",
            "email": "sla_manager_test@example.com",
            "group_ids": [(6, 0, [
                self.env.ref("base.group_user").id,
                manager_group.id,
            ])],
        })
        ticket = self._create_ticket(priority="0")
        create_date = ticket.create_date

        ticket.with_user(manager).write({"priority": "3"})

        self.assertEqual(ticket.deadline, create_date + timedelta(hours=6))

    def test_deadline_restarts_when_ticket_is_reopened(self):
        manager_group = self.env.ref("bayz_helpdesk.group_helpdesk_manager")
        manager = self.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "SLA Reopen Manager",
            "login": "sla_reopen_manager_test",
            "email": "sla_reopen_manager_test@example.com",
            "group_ids": [(6, 0, [
                self.env.ref("base.group_user").id,
                manager_group.id,
            ])],
        })
        ticket = self._create_ticket(priority="3")

        from unittest.mock import patch
        from odoo.addons.bayz_helpdesk.models.helpdesk_ticket import HelpdeskTicket

        # Isole le workflow de l'envoi réel d'e-mails.
        with patch.object(HelpdeskTicket, "_send_state_notification"):
            ticket.with_user(manager).write({"technician_id": self.env.user.id})
            ticket.with_user(manager)._change_state("in_progress")
            ticket.with_user(manager)._change_state("resolved")
            ticket.with_user(manager)._change_state("reopened")

        self.assertEqual(ticket.state, "reopened")
        self.assertTrue(ticket.reopened_date)
        self.assertEqual(
            ticket.deadline,
            ticket.reopened_date + timedelta(hours=6),
        )

    def test_overdue_search_rejects_unsupported_operator(self):
        ticket = self._create_ticket()

        with self.assertRaises(UserError):
            ticket._search_is_overdue(">", True)

    def test_overdue_search_returns_deadline_and_active_states(self):
        ticket = self._create_ticket()
        domain = ticket._search_is_overdue("=", True)

        self.assertEqual(domain[0][:2], ("deadline", "<"))
        self.assertIn(("state", "not in", ["resolved", "closed", "cancelled"]), domain)

    def test_overdue_search_supports_negation(self):
        ticket = self._create_ticket()

        self.assertEqual(ticket._search_is_overdue("=", False)[0], "!")
        self.assertEqual(ticket._search_is_overdue("!=", True)[0], "!")

    def test_overdue_flag_excludes_resolved_tickets(self):
        ticket = self._create_ticket()
        old_reopened_date = fields.Datetime.now() - timedelta(days=10)
        ticket.with_context(allow_reopen_date_change=True).write({
            "reopened_date": old_reopened_date,
        })

        self.assertTrue(ticket.is_overdue)

        ticket.with_context(allow_state_change=True).write({"state": "resolved"})

        self.assertFalse(ticket.is_overdue)
