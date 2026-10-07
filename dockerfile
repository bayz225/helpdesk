ARG ODOO_VERSION
FROM odoo:${ODOO_VERSION}

USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt