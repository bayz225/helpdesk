from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTimesheet(models.Model):
    _name = 'helpdesk.timesheet'
    _description = 'Ligne de temps HelpDesk'

    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Ticket', 
        required=True, 
        ondelete='cascade'
    )

    technician_id = fields.Many2one(
        comodel_name='res.users', 
        string='Technicien',  
        required=True
    )

    start_datetime = fields.Datetime(
        string='Début de session',
        required=True
    )

    end_datetime = fields.Datetime(
        string='Fin de session',
    )

    duration = fields.Float(
        string='Durée (heures)',
        compute='_compute_duration',
        store=True
    )

    @api.constrains("start_datetime", "end_datetime")
    def _check_session_dates(self):
        for record in self:
            if record.end_datetime and record.end_datetime < record.start_datetime:
                raise ValidationError(
                    "L'heure de fin d'une session doit être postérieure ou égale à l'heure de début."
                )

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                diff = record.end_datetime - record.start_datetime
                record.duration = diff.total_seconds() / 3600.0
            else:
                record.duration = 0.0