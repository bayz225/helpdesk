from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.bayz_helpdesk.models.helpdesk_ticket import HelpdeskTicket

from .common import HelpdeskTestMixin


# Transitions, permissions et sessions déclenchées par le workflow.
class TestHelpdeskWorkflow(HelpdeskTestMixin, TransactionCase):

    def setUp(self):
        super().setUp()
        self.manager = self.create_user(
            "Workflow manager", ["bayz_helpdesk.group_helpdesk_manager"]
        )
        self.technician = self.create_user(
            "Assigned technician", ["bayz_helpdesk.group_helpdesk_technician"]
        )
        self.other_technician = self.create_user(
            "Other technician", ["bayz_helpdesk.group_helpdesk_technician"]
        )

    def _assign_ticket(self, ticket):
        # L'affectation déclenche une notification, inutile pour ces tests.
        with patch.object(HelpdeskTicket, "_send_state_notification"):
            ticket.with_user(self.manager).write({
                "technician_id": self.technician.id,
            })

    def test_manager_assignment_moves_new_ticket_to_assigned(self):
        ticket = self.create_ticket()

        self._assign_ticket(ticket)

        self.assertEqual(ticket.state, "assigned")
        self.assertEqual(ticket.technician_id, self.technician)

    def test_direct_state_write_is_rejected(self):
        ticket = self.create_ticket()

        with self.assertRaises(UserError):
            ticket.write({"state": "closed"})

    def test_invalid_transition_is_rejected(self):
        ticket = self.create_ticket()

        with self.assertRaises(UserError):
            ticket.with_user(self.manager)._change_state("closed")

    def test_only_assigned_technician_can_start_ticket(self):
        ticket = self.create_ticket()
        self._assign_ticket(ticket)

        with self.assertRaises(UserError):
            ticket.with_user(self.other_technician)._change_state("in_progress")

    def test_starting_and_pausing_work_creates_and_closes_session(self):
        ticket = self.create_ticket()
        self._assign_ticket(ticket)

        with patch.object(HelpdeskTicket, "_send_state_notification"):
            technician_ticket = ticket.with_user(self.technician)
            technician_ticket._change_state("in_progress")
            technician_ticket._start_work_session()
            sessions = ticket.timesheet_ids

            self.assertEqual(len(sessions), 1)
            self.assertFalse(sessions.end_datetime)

            technician_ticket._change_state("pending")

        self.assertTrue(sessions.end_datetime)
        self.assertGreaterEqual(sessions.duration, 0.0)

    def test_requester_cannot_be_changed(self):
        ticket = self.create_ticket()
        another_user = self.create_user("Another requester")

        with self.assertRaises(UserError):
            ticket.write({"requester_id": another_user.id})

    def test_requester_can_only_see_own_tickets(self):
        first_requester = self.create_user(
            "First requester", ["bayz_helpdesk.group_helpdesk_user"]
        )
        second_requester = self.create_user(
            "Second requester", ["bayz_helpdesk.group_helpdesk_user"]
        )
        first_ticket = self.create_ticket(requester=first_requester)
        self.create_ticket(requester=second_requester)

        visible_tickets = self.ticket_model.with_user(first_requester).search([])

        self.assertEqual(visible_tickets, first_ticket)
