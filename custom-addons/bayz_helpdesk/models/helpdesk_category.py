from odoo import models, fields, api
from odoo.exceptions import UserError

class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Catégorie HelpDesk'

    name = fields.Char(string='Nom de la catégorie', required=True)
    active = fields.Boolean(string='Actif', default=True)
    ticket_ids = fields.One2many(
        comodel_name='helpdesk.ticket', 
        inverse_name='category_id', 
        string='Tickets'
    )
    count_tickets = fields.Integer(
        string='Nombre de tickets',
        compute='_compute_count_tickets',
        store=True
    )
    is_manager = fields.Boolean(
        string='Est un manager',
        compute='_compute_is_manager',
    )

    @api.depends('ticket_ids')
    def _compute_count_tickets(self):
        for category in self:
            category.count_tickets = len(category.ticket_ids)

    @api.depends_context("uid")
    def _compute_is_manager(self):
        for category in self:
            category.is_manager = self.env.user.has_group('bayz_helpdesk.group_helpdesk_manager')

    def write(self, vals):
        is_manager = self.env.user.has_group(
            "bayz_helpdesk.group_helpdesk_manager"
        )

        if not is_manager and {"name", "active"} & set(vals):
            raise UserError(
                "Seul le responsable peut modifier une catégorie."
            )

        return super().write(vals)