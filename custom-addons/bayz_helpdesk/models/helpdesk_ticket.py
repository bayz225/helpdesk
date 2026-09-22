from datetime import timedelta

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Ticket HelpDesk"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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