# ⚙️ Commandes Odoo (CLI)

Note : Les commandes de mise à jour utilisent le paramètre `-d odoo` (à remplacer par le nom exact de votre base de données si différent) et le nom technique du module `-u helpdesk` (ou `bayz_helpdesk` selon votre `__manifest__.py`).

```bash
# Créer l'architecture de base d'un nouveau module directement dans le dossier monté
docker compose exec odoo odoo scaffold nom_du_module /mnt/extra-addons

# Mettre à jour le module directement depuis le terminal via le conteneur en cours d'exécution
# -p 0 désactive le port HTTP pour éviter les conflits si le conteneur tourne déjà
docker exec -it odoo-v19-helpdesk odoo -c //etc/odoo/odoo.conf -d odoo -p 0 -u bayz_helpdesk --stop-after-init

# Alternative : Vider le cache et mettre à jour le module en lançant un conteneur éphémère (--rm)
docker compose run --rm odoo odoo -c //etc/odoo/odoo.conf -d odoo -u bayz_helpdesk --stop-after-init

docker compose exec odoo odoo -d NOM_DE_TA_BASE -u bayz_helpdesk --stop-after-init
```

Entrer dans le conteneur Odoo
Depuis PowerShell :

```bash
docker compose exec -it <nom_du_conteneur_odoo> bash

odoo shell -d <nom_de_ta_base>
```
