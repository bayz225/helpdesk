from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HelpdeskTicketFeedback(models.Model):
    _name = "helpdesk.ticket.feedback"
    _description = "Évaluation d'un ticket HelpDesk"
    _order = "create_date desc"

    _ticket_feedback_unique = models.Constraint(
        "UNIQUE(ticket_id)",
        "Un ticket ne peut recevoir qu'une seule évaluation.",
    )

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        string="Ticket",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="Demandeur",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )
    rating = fields.Selection(
        selection=[
            ("1", "1 - Très insatisfait"),
            ("2", "2 - Insatisfait"),
            ("3", "3 - Correct"),
            ("4", "4 - Satisfait"),
            ("5", "5 - Très satisfait"),
        ],
        string="Note",
        required=True,
    )
    comment = fields.Text(string="Commentaire")

    @api.model_create_multi
    def create(self, vals_list):
        submitted_ticket_ids = set()
        defaults = self.default_get(["ticket_id"])
        for vals in vals_list:
            ticket_id = vals.get("ticket_id") or defaults.get("ticket_id")
            ticket = self.env["helpdesk.ticket"].sudo().browse(
                ticket_id
            ).exists()
            if not ticket:
                raise ValidationError(_("Le ticket associé est introuvable."))
            if ticket.requester_id != self.env.user:
                raise UserError(
                    _("Seul le demandeur du ticket peut envoyer une évaluation.")
                )
            if ticket.state != "closed":
                raise UserError(
                    _("Une évaluation ne peut être envoyée que pour un ticket fermé.")
                )
            if vals.get("requester_id", self.env.user.id) != self.env.user.id:
                raise UserError(
                    _("L'évaluation doit être envoyée par le demandeur connecté.")
                )
            if (
                ticket.id in submitted_ticket_ids
                or self.sudo().search_count([("ticket_id", "=", ticket.id)])
            ):
                raise ValidationError(
                    _("Une évaluation a déjà été envoyée pour ce ticket.")
                )
            submitted_ticket_ids.add(ticket.id)
            vals["ticket_id"] = ticket.id
            vals["requester_id"] = self.env.user.id

        return super().create(vals_list)

    def action_submit(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window_close"}
