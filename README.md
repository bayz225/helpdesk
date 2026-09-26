# HelpDesk Bayz

Résumé : Gestion professionnelle des tickets de support
Module de HelpDesk pour la gestion des incidents internes.

## 🚀 Fonctionnalités principales

Gestion des tickets : Création et assignation de tickets.
Suivi des SLA : Gestion des dates limites en fonction du niveau de priorité.
Feuilles de temps : Intégration pour le suivi du temps passé sur chaque intervention.
Sécurité et Droits : Gestion des accès basée sur l'héritage des groupes natifs d'Odoo.

## 📂 Architecture du module

Le code source est structuré de la manière suivante :

```text
custom-addons/
└── helpdesk/
    ├── __init__.py                
    ├── __manifest__.py           
    ├── models/
    │   ├── __init__.py            
    │   ├── helpdesk_category.py
    │   ├── helpdesk_ticket.py
    │   └── helpdesk_timesheet.py
    ├── security/
    │   ├── helpdesk_security.xml 
    │   └── ir.model.access.csv    
    └── views/
        └── helpdesk_ticket_views.xml
```

## 🛠️ Commandes Utiles

🐳 Gestion des conteneurs Docker

```bash
# Télécharger ou mettre à jour l'image Odoo 19.0
docker pull odoo:19.0

# Démarrer les conteneurs en arrière-plan
docker compose up -d

# Démarrer en forçant la suppression des conteneurs orphelins (utile après modif du docker-compose)
docker compose up -d --remove-orphans

# Redémarrer les conteneurs actifs
docker compose restart

# Arrêter proprement les conteneurs (sans les supprimer)
docker compose stop

# Arrêter ET supprimer les conteneurs et les réseaux
docker compose down
```
