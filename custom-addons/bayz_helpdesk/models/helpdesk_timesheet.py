from odoo import models, fields

class HelpdeskTimesheet(models.Model):
    _name = 'helpdesk.timesheet'
    _description = 'Ligne de temps HelpDesk'

    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Ticket', 
        required=True, 
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string='Technicien', 
        default=lambda self: self.env.user, 
        required=True
    )
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    description = fields.Char(string='Description de l\'intervention', required=True)
    duration = fields.Float(string='Durée (Heures)', required=True)