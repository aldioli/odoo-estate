FROM odoo:17.0

COPY ./estate_pro /mnt/extra-addons/estate_pro
COPY ./odoo.conf /etc/odoo/odoo.conf

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/ && \
    chown odoo:odoo /etc/odoo/odoo.conf
USER odoo

EXPOSE 8069
CMD ["odoo", "--config=/etc/odoo/odoo.conf"]
```
اضغط **Commit changes** ✅

---

### الملف الثاني — **odoo.conf**
1. اضغط على ملف **odoo.conf**
2. اضغط أيقونة القلم ✏️
3. احذف كل شيء والصق هذا:
```
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = %(HOST)s
db_port = 5432
db_user = %(USER)s
db_password = %(PASSWORD)s
db_name = %(DATABASE)s
http_port = 8069
proxy_mode = True
