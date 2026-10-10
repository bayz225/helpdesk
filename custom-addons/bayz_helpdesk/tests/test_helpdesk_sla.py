from datetime import timedelta

from odoo.tests.common import TransactionCase


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

    def test_deadline_urgent_priority(self):
        ticket = self._create_ticket(priority="3")

        expected_deadline = (
            ticket.create_date + timedelta(hours=6)
        )

        self.assertEqual(
            ticket.deadline,
            expected_deadline,
            "Un ticket urgent doit avoir un délai de 6 heures.",
        )

    def test_deadline_high_priority(self):
        ticket = self._create_ticket(priority="2")
        
        expected_deadline = (
            ticket.create_date + timedelta(hours=24)
        )
        
        self.assertEqual(
            ticket.deadline,
            expected_deadline,
            "Un ticket acev une Haute priorité doit avoir un délai de 24 heures.",
        )

    def test_deadline_medium_priority(self): 
        ticket = self._create_ticket(priority="1")
        
        expected_deadline = ( 
            ticket.create_date + timedelta(days=3) 
        )
        
        self.assertEqual( 
            ticket.deadline,
            expected_deadline,
            "Un ticket de priorité moyenne doit avoir un délai de 3 jours.",
        )

    def test_deadline_low_priority(self): 
        ticket = self._create_ticket(priority="0")
        
        expected_deadline = (
            ticket.create_date + timedelta(days=7)
        ) 
        
        self.assertEqual(
            ticket.deadline,
            expected_deadline,
            "Un ticket de priorité faible doit avoir un délai de 7 jours.",
        )

    def test_deadline_recomputed_when_priority_changes(self):
        manager_group = self.env.ref(
            "bayz_helpdesk.group_helpdesk_manager"
        )

        manager = self.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "Manager Test SLA",
            "login": "manager_test_sla",
            "email": "manager_test_sla@example.com",
            "group_ids": [
                (6, 0, [
                    self.env.ref("base.group_user").id,
                    manager_group.id,
                ])
            ],
        })
        
        ticket = self._create_ticket(priority="0")
        
        create_date = ticket.create_date
        
        initial_deadline = ticket.deadline
        
        self.assertEqual(
            initial_deadline,
            create_date + timedelta(days=7),
            "Le délai initial d'un ticket de priorité faible doit avoir un délai de 7 jours.",
        )
        
        ticket.with_user(manager).write({
            "priority": "3"
        })
        
        expected_deadline = (
            create_date + timedelta(hours=6)
        )
        
        self.assertEqual(
            ticket.deadline,
            expected_deadline,
            "Un ticket dont la priorité devient urgent doit avoir un délai de 6 heures.",
        )

    def test_deadline_recomputed_when_ticket_is_reopened(self):
        manager_group = self.env.ref(
            "bayz_helpdesk.group_helpdesk_manager"
        )

        manager = self.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "Manager Test SLA",
            "login": "manager_test_sla",
            "email": "manager_test_sla@example.com",
            "group_ids": [
                (6, 0, [
                    self.env.ref("base.group_user").id,
                    manager_group.id,
                ])
            ],
        })

        ticket = self._create_ticket(priority="3")
        
        # Affecter un technicien avant l'assignation
        ticket.with_user(manager).write({
            "technician_id": self.env.user.id,
        })

        # Suivre le workflow autorisé
        ticket.with_user(manager)._change_state("in_progress")
        ticket.with_user(manager)._change_state("resolved")

        # Réouverture par le manager
        ticket.with_user(manager)._change_state("reopened")

        self.assertEqual(ticket.state, "reopened")
        self.assertTrue(ticket.reopened_date)

        expected_deadline = (
            ticket.reopened_date + timedelta(hours=6)
        )

        self.assertEqual(
            ticket.deadline,
            expected_deadline,
            "À la réouverture, le SLA urgent doit repartir de reopened_date.",
        )

