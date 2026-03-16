FROM odoo:17.0

COPY ./estate_pro /mnt/extra-addons/estate_pro

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/
USER odoo

EXPOSE 8069

CMD ["odoo", \
    "--addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons", \
    "--db_host=$(HOST)", \
    "--db_port=5432", \
    "--db_user=$(USER)", \
    "--db_password=$(PASSWORD)", \
    "--db_name=$(DATABASE)", \
    "--http-port=8069", \
    "--proxy-mode"]
