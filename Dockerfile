FROM odoo:17.0

# نسخ وحدة العقارات
COPY ./estate_pro /mnt/extra-addons/estate_pro

# صلاحيات المجلد
USER root
RUN chown -R odoo:odoo /mnt/extra-addons/
USER odoo

