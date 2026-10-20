/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

const VISIBLE_STATES = [
    "assigned",
    "in_progress",
    "pending",
    "resolved",
    "closed",
];

export class HelpdeskKanbanController extends KanbanController {
}


export class HelpdeskKanbanRenderer extends KanbanRenderer {

    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    getGroupsOrRecords() {
        const groupsOrRecords = super.getGroupsOrRecords();

        if (!this.props.list.isGrouped) {
            return groupsOrRecords;
        }

        return groupsOrRecords
            .filter(({ group }) => VISIBLE_STATES.includes(group.value))
            .sort(
                (a, b) =>
                    VISIBLE_STATES.indexOf(a.group.value) -
                    VISIBLE_STATES.indexOf(b.group.value)
            );
    }

    async sortRecordDrop(dataRecordId, dataGroupId, params) {
        const targetGroupId = params.parent?.dataset.id;

        // Déplacement dans la même colonne :
        // on conserve le comportement standard d'Odoo.
        if (dataGroupId === targetGroupId) {
            return super.sortRecordDrop(
                dataRecordId,
                dataGroupId,
                params
            );
        }

        // Récupération du ticket déplacé
        const record = this.props.list.records.find(
            (record) => record.id === dataRecordId
        );

        // Récupération de la colonne cible
        const targetGroup = this.props.list.groups.find(
            (group) => group.id === targetGroupId
        );

        // Sécurité frontend minimale
        if (!record || !targetGroup) {
            return;
        }

        const ticketId = record.resId;
        const newState = targetGroup.value;

        // Appel du workflow métier côté serveur
        await this.orm.call(
            "helpdesk.ticket",
            "action_kanban_change_state",
            [[ticketId], newState]
        );

        // Rechargement du Kanban après le changement
        await this.props.list.load();
    }
}


export const helpdeskKanbanView = {
    ...kanbanView,
    Controller: HelpdeskKanbanController,
    Renderer: HelpdeskKanbanRenderer,
};


registry.category("views").add(
    "helpdesk_kanban",
    helpdeskKanbanView
);