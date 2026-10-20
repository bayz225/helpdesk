from uuid import uuid4


# Helpers partagés pour créer les données de test.
class HelpdeskTestMixin:

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket_model = cls.env["helpdesk.ticket"]

    def create_user(self, name, group_xmlids=()):
        group_ids = [self.env.ref("base.group_user").id]
        group_ids.extend(self.env.ref(xmlid).id for xmlid in group_xmlids)
        login = f"{name.lower().replace(' ', '_')}_{uuid4().hex}"
        return self.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": name,
            "login": login,
            "email": f"{login}@example.com",
            "group_ids": [(6, 0, group_ids)],
        })

    def create_ticket(self, name="Test ticket", requester=None, **values):
        vals = {
            "name": name,
            "requester_id": (requester or self.env.user).id,
        }
        vals.update(values)
        return self.ticket_model.create(vals)