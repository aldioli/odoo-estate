FROM odoo:17.0

COPY ./estate_pro /mnt/extra-addons/estate_pro
COPY ./odoo.conf /etc/odoo/odoo.conf

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/ && \
    chown odoo:odoo /etc/odoo/odoo.conf
USER odoo

EXPOSE 8069

CMD odoo \
    --config=/etc/odoo/odoo.conf \
    --db_host=$PGHOST \
    --db_port=5432 \
    --db_user=$PGUSER \
    --db_password=$PGPASSWORD \
    --database=aldioli
