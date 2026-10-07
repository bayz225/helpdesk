{
    'name': 'HelpDesk Bayz',
    'version': '19.0.1',
    'sequence': -99,
    'category': 'Service',
    'summary': 'Gestion professionnelle des tickets de support',
    'description': """
        Module de HelpDesk Bayz pour la gestion des incidents internes.
        Fonctionnalités :
        - Création et assignation de tickets
        - Suivi des SLA (Date limite selon priorité)
        - Feuilles de temps intégrées
        - Sécurité basée sur l'héritage de groupes Odoo
    """,
    'author': 'Bayz225',
    'depends': [
        'base', 
        'mail' # Requis pour le chatter et les activités
    ],
    'data': [
        # 1. Sécurité
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        
        "data/ir_sequence.xml",
        
        # 2. Vues de l'interface
        'views/menu.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_category_views.xml',
        'views/helpdesk_timesheet_views.xml',
        
        # 3. Wizard
        'wizard/helpdesk_timesheet_export_wizard_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "bayz_helpdesk/static/src/js/helpdesk_kanban.js",
        ],
    },
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True, # Permet au module d'apparaître dans l'écran principal des Apps
    'license': 'LGPL-3',
}

