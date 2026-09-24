from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Ticket HelpDesk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    # Workflow de l'etat d'un ticket
    ALLOWED_TRANSITIONS = {
        "new": ["assigned", "cancelled"],
        "assigned": ["in_progress", "cancelled"],
        "in_progress": ["pending", "resolved"],
        "pending": ["in_progress", "resolved"],
        "resolved": ["closed", "reopened"],
        "closed": ["reopened"],
        "reopened": ["assigned"],
        "cancelled": [],
    }
    
    ALLOWED_TRANS_ROLES = {
        ("new", "assigned"): ["manager"],
        ("new", "cancelled"): ["manager"],
        ("assigned", "in_progress"): ["manager", "technician"],
        ("assigned", "cancelled"): ["manager"],
        ("in_progress", "pending"): ["manager", "technician"],
        ("in_progress", "resolved"): ["manager", "technician"],
        ("pending", "in_progress"): ["manager", "technician"],
        ("pending", "resolved"): ["manager", "technician"],
        ("resolved", "closed"): ["manager"],
        ("resolved", "reopened"): ["manager"],
        ("closed", "reopened"): ["manager"],
        ("reopened", "assigned"): ["manager"],
    }

    # Informations générales
    name = fields.Char(
        string="Titre",
        required=True,
        tracking=True,
    )

    description = fields.Html(
        string="Description",
    )

    # Utilisateurs
    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="Demandeur",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    technician_id = fields.Many2one(
        comodel_name="res.users",
        string="Technicien assigné",
        tracking=True,
    )

    category_id = fields.Many2one(
        comodel_name="helpdesk.category",
        string="Catégorie",
        tracking=True,
    )

    # États
    state = fields.Selection(
        selection=[
            ("new", "Nouveau"),
            ("assigned", "Assigné"),
            ("in_progress", "En cours"),
            ("pending", "En attente"),
            ("resolved", "Résolu"),
            ("closed", "Fermé"),
            ("reopened", "Réouvert"),
            ("cancelled", "Annulé"),
        ],
        string="État",
        default="new",
        tracking=True,
    )

    priority = fields.Selection(
        selection=[
            ("0", "Faible"),
            ("1", "Moyenne"),
            ("2", "Haute"),
            ("3", "Urgent"),
        ],
        string="Priorité",
        default="0",
        tracking=True,
    )

    # Dates et temps
    deadline = fields.Datetime(
        string="Date limite",
        compute="_compute_deadline",
        store=True,
    )

    timesheet_ids = fields.One2many(
        comodel_name="helpdesk.timesheet",
        inverse_name="ticket_id",
        string="Feuilles de temps",
    )

    total_time = fields.Float(
        string="Temps total (heures)",
        compute="_compute_total_time",
        store=True,
    )

    # Utilisateurs disponibles dans le champ Technicien
    technician_domain_ids = fields.Many2many(
        comodel_name="res.users",
        string="Techniciens autorisés",
        compute="_compute_technician_domain_ids",
    )

    @api.depends_context("uid")
    def _compute_technician_domain_ids(self):
        technician_group = self.env.ref(
            "bayz_helpdesk.group_helpdesk_technician",
            raise_if_not_found=False,
        )
        manager_group = self.env.ref(
            "bayz_helpdesk.group_helpdesk_manager",
            raise_if_not_found=False,
        )

        groups = technician_group | manager_group
        users = groups.mapped("user_ids")

        for ticket in self:
            ticket.technician_domain_ids = users

    @api.depends("priority", "create_date")
    def _compute_deadline(self):
        for ticket in self:
            base_date = ticket.create_date or fields.Datetime.now()

            if ticket.priority == "3":
                ticket.deadline = base_date + timedelta(hours=6)
            elif ticket.priority == "2":
                ticket.deadline = base_date + timedelta(hours=24)
            elif ticket.priority == "1":
                ticket.deadline = base_date + timedelta(days=3)
            else:
                ticket.deadline = base_date + timedelta(days=7)

    @api.depends("timesheet_ids.duration")
    def _compute_total_time(self):
        for ticket in self:
            ticket.total_time = sum(
                ticket.timesheet_ids.mapped("duration")
            )

    def _change_state(self, new_state):
        is_manager = self.env.user.has_group(
            "bayz_helpdesk.group_helpdesk_manager"
        )
        is_technician = self.env.user.has_group(
            "bayz_helpdesk.group_helpdesk_technician"
        )

        for ticket in self:
            current_state = ticket.state
            transition = (current_state, new_state)

            if new_state not in self.ALLOWED_TRANSITIONS[current_state]:
                raise UserError(
                    "Cette transition n'est pas autorisée."
                )

            if transition not in self.ALLOWED_TRANS_ROLES:
                raise UserError(
                    "Aucune règle de permission n'est définie pour cette transition."
                )

            allowed_roles = self.ALLOWED_TRANS_ROLES[transition]

            can_change_state = (
                (is_manager and "manager" in allowed_roles)
                or
                (
                    is_technician
                    and "technician" in allowed_roles
                    and ticket.technician_id == self.env.user
                )
            )

            if not can_change_state:
                raise UserError(
                    "Vous n'avez pas les droits nécessaires pour effectuer cette transition."
                )

            ticket.with_context(
                allow_state_change=True
            ).write({
                "state": new_state
            })

    def action_assign(self):
        for ticket in self:
            if not ticket.technician_id:
                raise UserError(
                    "Veuillez sélectionner un Technicien."
                )

        self._change_state("assigned")

    def action_start(self):
        self._change_state("in_progress")

    def action_pending(self):
        self._change_state("pending")

    def action_resume(self):
        self._change_state("in_progress")

    def action_resolve(self):
        self._change_state("resolved")

    def action_close(self):
        self._change_state("closed")

    def action_reopen(self):
        self._change_state("reopened")

    def action_cancel(self):
        self._change_state("cancelled")

    def write(self, vals):
        if "state" in vals:
            if not self.env.context.get("allow_state_change"):
                raise UserError(
                    "L'état d'un ticket ne peut être modifié que par une action du workflow."
                )

        return super().write(vals)