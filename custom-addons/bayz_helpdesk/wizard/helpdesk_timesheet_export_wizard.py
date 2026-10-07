import base64
import io
from datetime import datetime, time

import pytz
from openpyxl import Workbook
from openpyxl.styles import Font

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTimesheetExportWizard(models.TransientModel):
    _name = "helpdesk.timesheet.export.wizard"
    _description = "Export des statistiques du temps"

    date_from = fields.Date(
        string="Du",
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        string="Au",
        default=fields.Date.context_today,
    )
    technician_ids = fields.Many2many(
        comodel_name="res.users",
        relation="helpdesk_export_wizard_technician_rel",
        column1="wizard_id",
        column2="user_id",
        string="Techniciens",
        domain=lambda self: [("id", "in", self._get_technician_user_ids())],
    )
    category_ids = fields.Many2many(
        comodel_name="helpdesk.category",
        relation="helpdesk_export_wizard_category_rel",
        column1="wizard_id",
        column2="category_id",
        string="Catégories",
    )
    file_data = fields.Binary(string="Fichier", readonly=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)

    @api.model
    def _get_technician_user_ids(self):
        """Utilisateurs des groupes technicien et responsable."""
        groups = self.env["res.groups"]
        for xmlid in (
            "bayz_helpdesk.group_helpdesk_technician",
            "bayz_helpdesk.group_helpdesk_manager",
        ):
            groups |= self.env.ref(xmlid, raise_if_not_found=False) or self.env["res.groups"]
        return groups.mapped("user_ids").ids

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")

    def _local_to_utc(self, day, at):
        """Date locale (fuseau de l'utilisateur) -> datetime UTC naïf."""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_dt = tz.localize(datetime.combine(day, at))
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    def _get_domain(self):
        # On ignore les sessions encore en cours (sans fin)
        domain = [("end_datetime", "!=", False)]
        if self.date_from:
            domain.append(("start_datetime", ">=", self._local_to_utc(self.date_from, time.min)))
        if self.date_to:
            domain.append(("start_datetime", "<=", self._local_to_utc(self.date_to, time.max)))
        if self.technician_ids:
            domain.append(("technician_id", "in", self.technician_ids.ids))
        if self.category_ids:
            domain.append(("category_id", "in", self.category_ids.ids))
        return domain

    def action_export_excel(self):
        self.ensure_one()
        stats = self.env["helpdesk.timesheet"].get_technician_stats(self._get_domain())

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Statistiques"

        sheet.append([
            "Technicien",
            "Nombre de tickets",
            "Temps total (h)",
            "Temps moyen / ticket (h)",
        ])
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for stat in stats:
            sheet.append([
                stat["technician_name"],
                stat["ticket_count"],
                round(stat["total_time"], 2),
                round(stat["average_time"], 2),
            ])

        for column, width in zip("ABCD", (30, 20, 18, 26)):
            sheet.column_dimensions[column].width = width

        buffer = io.BytesIO()
        workbook.save(buffer)

        suffix = "_".join(
            d.strftime("%Y%m%d") for d in (self.date_from, self.date_to) if d
        )
        self.write({
            "file_data": base64.b64encode(buffer.getvalue()),
            "file_name": f"statistiques_techniciens{'_' + suffix if suffix else ''}.xlsx",
        })

        return {
            "type": "ir.actions.act_url",
            "url": (
                f"/web/content/{self._name}/{self.id}/file_data"
                f"?download=true&filename={self.file_name}"
            ),
            "target": "self",
        }