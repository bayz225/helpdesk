# Bayz HelpDesk

Module Odoo 19 pour gérer les demandes de support internes, leur traitement par
les techniciens et le temps passé sur chaque intervention.

## Fonctionnalités disponibles

### Gestion des tickets

- Création de tickets avec une référence générée automatiquement au format
  `HD/AAAA/00001`.
- Suivi du demandeur, du technicien assigné, de la catégorie, de la priorité,
  de la description et de l’échéance.
- Workflow contrôlé : Nouveau, Assigné, En cours, En attente, Résolu, Fermé,
  Réouvert et Annulé. Les transitions et les actions autorisées dépendent du
  rôle de l’utilisateur; la modification directe de l’état est bloquée.
- Le responsable affecte les tickets et gère leur annulation, fermeture et
  réouverture. Seul le technicien affecté (ou un responsable) peut démarrer,
  mettre en attente, reprendre ou résoudre un ticket.
- Vues liste, formulaire et Kanban, avec recherche, filtres et déplacement des
  tickets entre les colonnes du Kanban.
- Vue Graphique pour analyser le volume des tickets par état et par priorité.
- Historique des échanges et activités dans le chatter Odoo.

### SLA et suivi du temps

- Échéance calculée selon la priorité :

  | Priorité | Délai |
  |----------|-------|
  | Faible | 7 jours |
  | Moyenne | 3 jours |
  | Haute | 24 heures |
  | Urgent | 6 heures |

- À la réouverture, le délai est recalculé à partir de la date de réouverture.
- Indicateur et filtre de recherche pour les tickets en retard; les tickets
  résolus, fermés ou annulés ne sont pas considérés en retard.
- Une session de temps est démarrée lors du passage à « En cours » et arrêtée
  lorsque le ticket quitte cet état. La durée est calculée en heures.
- Analyse des durées par technicien et catégorie avec les vues Pivot et
  Graphique.
- Export Excel des statistiques par technicien (nombre de tickets, temps total
  et temps moyen par ticket), filtrable par période, technicien et catégorie.

### Catégories et notifications

- Gestion des catégories et affichage du nombre de tickets associés.
- Les noms de catégories sont uniques sans tenir compte de la casse, des
  accents ou des espaces en trop.
- Envoi d’un courriel au demandeur lors d’un changement d’état. Le demandeur
  doit avoir une adresse électronique et le serveur de courrier sortant d’Odoo
  doit être configuré.
- Après la fermeture d’un ticket, son demandeur peut envoyer une seule
  évaluation (note de 1 à 5 et commentaire facultatif). L’évaluation est
  immuable après envoi; les techniciens des tickets concernés et les
  responsables peuvent la consulter selon leurs règles d’accès.
- Des données de démonstration peuvent être chargées si l’installation est
  effectuée avec l’option de données de démonstration d’Odoo.

## Accès et rôles

Les groupes sont définis dans `security/helpdesk_security.xml`. Ils héritent
les uns des autres : Technicien inclut Utilisateur, et Responsable inclut
Technicien.

| Groupe | Accès aux tickets | Accès complémentaire |
|--------|-------------------|----------------------|
| **HelpDesk : Utilisateur** | Créer, lire et modifier ses propres tickets de demandeur; pas de suppression. | Lire les catégories et les lignes de temps rattachées à ses tickets. |
| **HelpDesk : Technicien** | Créer, lire et modifier les tickets dont il est demandeur ou technicien affecté; pas de suppression. | Accéder aux paramètres de catégories et au modèle d’export des temps. |
| **HelpDesk : Responsable** | Accès en lecture, création, modification et suppression à tous les tickets. | Accéder à tous les temps, aux rapports et à la gestion des catégories. |

Les règles d’enregistrement limitent aussi la visibilité des feuilles de temps
et des évaluations :
un utilisateur voit les temps associés à ses tickets, un technicien ceux de ses
tickets demandés ou affectés, et un responsable tous les temps. Un utilisateur
ne peut évaluer que son propre ticket fermé; un technicien peut consulter les
évaluations des tickets qui lui sont affectés ou qu’il a demandés, et un
responsable toutes les évaluations. Les utilisateurs internes ont un accès en
lecture seule aux feuilles de temps; leur création et leur clôture sont
réalisées automatiquement par le workflow du ticket.

Les catégories ont des droits d’accès CRUD pour les utilisateurs internes.
Toutefois, la modification du nom ou de l’état actif d’une catégorie est
réservée au responsable HelpDesk.

### Attribuer un rôle

1. Installer le module (voir la section suivante).
2. Dans Odoo, ouvrir **Paramètres → Utilisateurs et sociétés → Utilisateurs**,
   puis sélectionner l’utilisateur.
3. Dans ses droits d’accès / groupes, attribuer **HelpDesk : Utilisateur**,
   **HelpDesk : Technicien** ou **HelpDesk : Responsable**.
4. Enregistrer l’utilisateur. L’héritage des groupes donne automatiquement les
   droits du niveau inférieur.

Les utilisateurs qui ne sont pas membres d’un groupe HelpDesk n’ont pas accès
aux menus des tickets du module.

## Installation

### Prérequis

- Odoo 19.
- Modules Odoo `base` et `mail` (dépendances déclarées).
- La bibliothèque Python `openpyxl`, nécessaire à l’export Excel.
- Le répertoire `custom-addons` doit être inclus dans les chemins d’addons
  d’Odoo.

### Installer le module

1. Copier ou monter `custom-addons/bayz_helpdesk` dans un répertoire d’addons
   reconnu par Odoo.
2. Installer `openpyxl` dans l’environnement Python du serveur Odoo si ce
   n’est pas déjà fait.
3. Redémarrer Odoo, mettre à jour la liste des applications, rechercher
   **HelpDesk Bayz**, puis installer le module.

Pour mettre à jour le module depuis le conteneur Docker du projet :

```bash
docker compose exec odoo odoo -d NOM_DE_LA_BASE -u bayz_helpdesk --stop-after-init
```

Remplacer `NOM_DE_LA_BASE` par le nom de la base Odoo utilisée.

## Menus

- **HelpDesk → Tickets** : tickets (visible aux membres du groupe Utilisateur
  HelpDesk).
- **HelpDesk → Paramètres → Catégories** : catégories (menu visible aux
  Techniciens et Responsables).
- **HelpDesk → Reporting → Analyse du temps** : analyse Pivot et Graphique
  (menu réservé aux Responsables).

## Tests

Les tests du module sont dans `tests/` et couvrent notamment le workflow et ses
permissions, les échéances SLA, les évaluations, les catégories, les feuilles
de temps et l’export Excel. Depuis l’environnement Docker du projet :

```bash
docker compose exec odoo odoo -d NOM_DE_LA_BASE -u bayz_helpdesk --test-enable --stop-after-init --http-port=8070
```
