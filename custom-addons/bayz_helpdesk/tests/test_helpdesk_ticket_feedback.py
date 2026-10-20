from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase

from .common import HelpdeskTestMixin


class TestHelpdeskTicketFeedback(HelpdeskTestMixin, TransactionCase):

    def setUp(self):
        super().setUp()
        self.requester = self.create_user(
            "Feedback requester", ["bayz_helpdesk.group_helpdesk_user"]
        )
        self.other_user = self.create_user(
            "Other feedback user", ["bayz_helpdesk.group_helpdesk_user"]
        )
        self.ticket = self.create_ticket(requester=self.requester)
        self.ticket.with_context(allow_state_change=True).write({
            "state": "closed",
        })

    def _submit_feedback(self, user=None, **values):
        vals = {
            "ticket_id": self.ticket.id,
            "rating": "5",
        }
        vals.update(values)
        return self.env["helpdesk.ticket.feedback"].with_user(
            user or self.requester
        ).create(vals)

    def test_requester_can_submit_feedback_once(self):
        feedback = self._submit_feedback(comment="Très bonne prise en charge.")

        self.assertEqual(feedback.requester_id, self.requester)
        self.assertEqual(feedback.ticket_id, self.ticket)
        self.assertEqual(feedback.rating, "5")
        self.assertEqual(feedback.comment, "Très bonne prise en charge.")

    def test_ticket_is_loaded_from_form_default_context(self):
        feedback = self.env["helpdesk.ticket.feedback"].with_user(
            self.requester
        ).with_context(
            default_ticket_id=self.ticket.id,
            default_requester_id=self.requester.id,
        ).create({"rating": "4"})

        self.assertEqual(feedback.ticket_id, self.ticket)
        self.assertEqual(feedback.requester_id, self.requester)

    def test_feedback_is_rejected_before_ticket_is_closed(self):
        self.ticket.with_context(allow_state_change=True).write({
            "state": "resolved",
        })

        with self.assertRaises(UserError):
            self._submit_feedback()

    def test_feedback_is_rejected_for_non_requester(self):
        with self.assertRaises(UserError):
            self._submit_feedback(user=self.other_user)

    def test_feedback_is_rejected_if_requester_is_spoofed(self):
        with self.assertRaises(UserError):
            self._submit_feedback(requester_id=self.other_user.id)

    def test_duplicate_feedback_is_rejected(self):
        self._submit_feedback()

        with self.assertRaises(ValidationError):
            self._submit_feedback()

    def test_duplicate_feedback_in_same_batch_is_rejected(self):
        vals = {"ticket_id": self.ticket.id, "rating": "5"}

        with self.assertRaises(ValidationError):
            self.env["helpdesk.ticket.feedback"].with_user(
                self.requester
            ).create([vals.copy(), vals.copy()])

    def test_feedback_cannot_be_changed_or_deleted(self):
        feedback = self._submit_feedback()

        with self.assertRaises(AccessError):
            feedback.with_user(self.requester).write({"comment": "Changed"})

        with self.assertRaises(AccessError):
            feedback.with_user(self.requester).unlink()

    def test_only_requester_can_open_feedback_form(self):
        action = self.ticket.with_user(self.requester).action_submit_feedback()

        self.assertEqual(action["res_model"], "helpdesk.ticket.feedback")
        self.assertEqual(action["target"], "new")

        with self.assertRaises(UserError):
            self.ticket.with_user(self.other_user).action_submit_feedback()
