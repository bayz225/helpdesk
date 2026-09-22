```bash
# Demarrer le conteneur
docker compose up -d

# Arret normal
docker compose stop
# Arret et supession des conteneurs
docker compose down

docker compose restart

# M
docker compose up -d --remove-orphans

docker pull odoo:19.0

odoo scaffold clinique /mnt/extra-addons

Vider le cache
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -u om_hospital --stop-after-init

odoo -c /etc/odoo/odoo.conf -d odoo -p 0 -u om_hospital --stop-after-init

# mettre à jour le module directement depuis ton terminal sans passer par l'interface web
docker exec -it odoo-v19-projectname odoo -c /etc/odoo/odoo.conf -u om_hospital --stop-after-init


```
