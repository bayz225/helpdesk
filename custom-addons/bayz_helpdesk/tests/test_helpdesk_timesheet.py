from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from .common import HelpdeskTestMixin


class TestHelpdeskTimesheet(HelpdeskTestMixin, TransactionCase):

    def setUp(self):
        super().setUp()
        self.technician = self.create_user(
            "Timesheet technician", ["bayz_helpdesk.group_helpdesk_technician"]
        )
        self.category = self.env["helpdesk.category"].create({
            "name": "Timesheet category",
        })

    def _create_timesheet(self, ticket, start, end):
        return self.env["helpdesk.timesheet"].create({
            "ticket_id": ticket.id,
            "technician_id": self.technician.id,
            "start_datetime": start,
            "end_datetime": end,
        })

    def test_duration_is_computed_in_hours(self):
        ticket = self.create_ticket(category_id=self.category.id)
        line = self._create_timesheet(
            ticket,
            datetime(2025, 1, 1, 9, 0),
            datetime(2025, 1, 1, 10, 30),
        )

        self.assertAlmostEqual(line.duration, 1.5)

    def test_end_before_start_is_rejected(self):
        ticket = self.create_ticket(category_id=self.category.id)

        with self.assertRaises(ValidationError):
            self._create_timesheet(
                ticket,
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 9, 0),
            )

    def test_open_session_has_zero_duration(self):
        ticket = self.create_ticket(category_id=self.category.id)
        line = self.env["helpdesk.timesheet"].create({
            "ticket_id": ticket.id,
            "technician_id": self.technician.id,
            "start_datetime": datetime(2025, 1, 1, 9, 0),
        })

        self.assertEqual(line.duration, 0.0)

    def test_ticket_time_totals_are_computed(self):
        ticket = self.create_ticket(
            category_id=self.category.id,
            technician_id=self.technician.id,
        )
        self._create_timesheet(
            ticket,
            datetime(2025, 1, 1, 9, 0),
            datetime(2025, 1, 1, 10, 0),
        )
        self._create_timesheet(
            ticket,
            datetime(2025, 1, 1, 10, 0),
            datetime(2025, 1, 1, 12, 0),
        )

        self.assertAlmostEqual(ticket.total_time, 3.0)
        self.assertAlmostEqual(ticket.times_by_technician, 3.0)
        self.assertAlmostEqual(ticket.time_by_category, 3.0)

    def test_technician_statistics_group_by_ticket(self):
        first_ticket = self.create_ticket(category_id=self.category.id)
        second_ticket = self.create_ticket(category_id=self.category.id)
        self._create_timesheet(
            first_ticket,
            datetime(2025, 1, 1, 9, 0),
            datetime(2025, 1, 1, 10, 0),
        )
        self._create_timesheet(
            second_ticket,
            datetime(2025, 1, 1, 10, 0),
            datetime(2025, 1, 1, 12, 0),
        )

        statistics = self.env["helpdesk.timesheet"].get_technician_stats([
            ("ticket_id", "in", [first_ticket.id, second_ticket.id]),
        ])

        self.assertEqual(len(statistics), 1)
        self.assertEqual(statistics[0]["technician_name"], self.technician.name)
        self.assertEqual(statistics[0]["ticket_count"], 2)
        self.assertAlmostEqual(statistics[0]["total_time"], 3.0)
        self.assertAlmostEqual(statistics[0]["average_time"], 1.5)
