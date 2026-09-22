from odoo import models, fields

class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Catégorie HelpDesk'

    name = fields.Char(string='Nom de la catégorie', required=True)
    active = fields.Boolean(string='Actif', default=True)