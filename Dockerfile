FROM odoo:17.0

COPY ./estate_pro /mnt/extra-addons/estate_pro

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/
USER odoo

EXPOSE 8069

CMD odoo \
    --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons \
    --db_host=$DB_HOST \
    --db_port=5432 \
    --db_user=$DB_USER \
    --db_password=$DB_PASS \
    --database=$DB_NAME \
    --http-port=8069 \
    --proxy-mode
