from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re
import unicodedata

class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Catégorie HelpDesk'
    
    _sql_constraints = [
        (
            "helpdesk_category_name_unique",
            "UNIQUE(name)",
            "Le nom de la catégorie doit être unique.",
        ),
    ]

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

    @api.constrains("name")
    def _check_unique_name(self):
        for category in self:
            normalized_name = self._normalize_category_name(
                category.name
            )

            duplicate = self.search([
                ("id", "!=", category.id),
            ]).filtered(
                lambda c: self._normalize_category_name(c.name)
                == normalized_name
            )

            if duplicate:
                raise ValidationError(
                    "Une catégorie portant ce nom existe déjà."
                )

    def _normalize_category_name(self, name):
        name = name.strip()
        name = re.sub(r"\s+", " ", name)
        name = unicodedata.normalize("NFKD", name)
        name = "".join(
            char for char in name
            if not unicodedata.combining(char)
        )
        return name.casefold()

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