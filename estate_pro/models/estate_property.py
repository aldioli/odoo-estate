from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'العقار'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ═══════════════════════════════════════
    # المعلومات الأساسية
    # ═══════════════════════════════════════
    name = fields.Char(string='اسم العقار', required=True, tracking=True)
    ref = fields.Char(string='رقم العقار', readonly=True, copy=False, default='جديد')
    description = fields.Text(string='الوصف')
    image = fields.Binary(string='صورة العقار')

    property_type = fields.Selection([
        ('apartment', 'شقة'),
        ('villa', 'فيلا'),
        ('office', 'مكتب'),
        ('shop', 'محل تجاري'),
        ('land', 'أرض'),
        ('building', 'مبنى'),
        ('warehouse', 'مستودع'),
    ], string='نوع العقار', required=True, default='apartment', tracking=True)

    status = fields.Selection([
        ('available', 'متاح'),
        ('rented', 'مؤجر'),
        ('sold', 'مباع'),
        ('maintenance', 'تحت الصيانة'),
        ('expired', 'منتهي العقد'),
    ], string='الحالة', default='available', tracking=True)

    listing_type = fields.Selection([
        ('rent', 'للإيجار'),
        ('sale', 'للبيع'),
        ('both', 'للإيجار والبيع'),
    ], string='نوع العرض', default='rent', tracking=True)

    # ═══════════════════════════════════════
    # الألوان
    # ═══════════════════════════════════════
    color = fields.Integer(string='اللون', compute='_compute_color', store=True)

    @api.depends('status', 'days_to_expire')
    def _compute_color(self):
        for rec in self:
            if rec.status == 'available':
                rec.color = 10  # أخضر
            elif rec.status == 'rented':
                if rec.days_to_expire and rec.days_to_expire <= 30:
                    rec.color = 2  # أحمر - قرب الانتهاء
                elif rec.days_to_expire and rec.days_to_expire <= 60:
                    rec.color = 3  # أصفر - تحذير
                else:
                    rec.color = 4  # أصفر عادي
            elif rec.status == 'expired':
                rec.color = 1  # أحمر
            elif rec.status == 'maintenance':
                rec.color = 7  # رمادي
            elif rec.status == 'sold':
                rec.color = 11  # بنفسجي
            else:
                rec.color = 0

    # ═══════════════════════════════════════
    # تفاصيل العقار
    # ═══════════════════════════════════════
    price = fields.Float(string='سعر البيع / الإيجار السنوي', tracking=True)
    monthly_rent = fields.Float(string='الإيجار الشهري', compute='_compute_monthly_rent', store=True)
    area = fields.Float(string='المساحة (م²)')
    bedrooms = fields.Integer(string='غرف النوم')
    bathrooms = fields.Integer(string='دورات المياه')
    floor = fields.Integer(string='الطابق')

    @api.depends('price', 'listing_type')
    def _compute_monthly_rent(self):
        for rec in self:
            if rec.listing_type in ('rent', 'both') and rec.price:
                rec.monthly_rent = rec.price / 12
            else:
                rec.monthly_rent = 0

    # ═══════════════════════════════════════
    # الموقع
    # ═══════════════════════════════════════
    city = fields.Char(string='المدينة')
    district = fields.Char(string='الحي')
    street = fields.Char(string='الشارع')
    address = fields.Char(string='العنوان الكامل', compute='_compute_address', store=True)

    @api.depends('city', 'district', 'street')
    def _compute_address(self):
        for rec in self:
            parts = [rec.street, rec.district, rec.city]
            rec.address = ' - '.join([p for p in parts if p])

    # ═══════════════════════════════════════
    # بيانات المالك
    # ═══════════════════════════════════════
    owner_name = fields.Char(string='اسم المالك', tracking=True)
    owner_phone = fields.Char(string='هاتف المالك')
    owner_email = fields.Char(string='بريد المالك')
    owner_id = fields.Char(string='هوية المالك')

    # ═══════════════════════════════════════
    # بيانات المستأجر والعقد
    # ═══════════════════════════════════════
    tenant_name = fields.Char(string='اسم المستأجر', tracking=True)
    tenant_phone = fields.Char(string='هاتف المستأجر')
    tenant_email = fields.Char(string='بريد المستأجر')
    tenant_id = fields.Char(string='هوية المستأجر')

    contract_start = fields.Date(string='بداية العقد', tracking=True)
    contract_end = fields.Date(string='نهاية العقد', tracking=True)
    contract_duration = fields.Integer(string='مدة العقد (شهر)', compute='_compute_duration', store=True)

    days_to_expire = fields.Integer(string='أيام حتى الانتهاء', compute='_compute_days_to_expire', store=True)
    contract_status = fields.Selection([
        ('active', 'نشط'),
        ('expiring_soon', 'ينتهي قريباً'),
        ('expired', 'منتهي'),
        ('no_contract', 'لا يوجد عقد'),
    ], string='حالة العقد', compute='_compute_contract_status', store=True)

    # ═══════════════════════════════════════
    # المدفوعات
    # ═══════════════════════════════════════
    payment_day = fields.Integer(string='يوم السداد الشهري', default=1,
                                  help='اليوم من الشهر المحدد لسداد الإيجار')
    next_payment_date = fields.Date(string='موعد الدفعة القادمة', compute='_compute_next_payment', store=True)
    days_to_payment = fields.Integer(string='أيام حتى الدفعة', compute='_compute_next_payment', store=True)
    total_paid = fields.Float(string='إجمالي المدفوع', compute='_compute_payments', store=True)
    total_remaining = fields.Float(string='المبلغ المتبقي', compute='_compute_payments', store=True)
    payment_ids = fields.One2many('estate.payment', 'property_id', string='المدفوعات')

    # ═══════════════════════════════════════
    # المرافق
    # ═══════════════════════════════════════
    has_parking = fields.Boolean(string='موقف سيارات')
    has_elevator = fields.Boolean(string='مصعد')
    has_pool = fields.Boolean(string='مسبح')
    has_gym = fields.Boolean(string='صالة رياضية')
    has_security = fields.Boolean(string='حراسة أمنية')
    has_ac = fields.Boolean(string='تكييف مركزي')

    notes = fields.Text(string='ملاحظات')
    active = fields.Boolean(default=True)

    # ═══════════════════════════════════════
    # الحسابات
    # ═══════════════════════════════════════
    @api.depends('contract_start', 'contract_end')
    def _compute_duration(self):
        for rec in self:
            if rec.contract_start and rec.contract_end:
                delta = rec.contract_end - rec.contract_start
                rec.contract_duration = int(delta.days / 30)
            else:
                rec.contract_duration = 0

    @api.depends('contract_end')
    def _compute_days_to_expire(self):
        today = date.today()
        for rec in self:
            if rec.contract_end:
                delta = rec.contract_end - today
                rec.days_to_expire = delta.days
            else:
                rec.days_to_expire = 0

    @api.depends('days_to_expire', 'contract_end', 'status')
    def _compute_contract_status(self):
        for rec in self:
            if not rec.contract_end:
                rec.contract_status = 'no_contract'
            elif rec.days_to_expire < 0:
                rec.contract_status = 'expired'
            elif rec.days_to_expire <= 30:
                rec.contract_status = 'expiring_soon'
            else:
                rec.contract_status = 'active'

    @api.depends('payment_day', 'contract_end')
    def _compute_next_payment(self):
        today = date.today()
        for rec in self:
            if rec.payment_day and rec.status == 'rented':
                # حساب موعد الدفعة القادمة
                if today.day <= rec.payment_day:
                    next_payment = today.replace(day=rec.payment_day)
                else:
                    if today.month == 12:
                        next_payment = today.replace(year=today.year + 1, month=1, day=rec.payment_day)
                    else:
                        next_payment = today.replace(month=today.month + 1, day=rec.payment_day)
                rec.next_payment_date = next_payment
                rec.days_to_payment = (next_payment - today).days
            else:
                rec.next_payment_date = False
                rec.days_to_payment = 0

    @api.depends('payment_ids', 'payment_ids.amount', 'payment_ids.state')
    def _compute_payments(self):
        for rec in self:
            paid = sum(rec.payment_ids.filtered(lambda p: p.state == 'paid').mapped('amount'))
            rec.total_paid = paid
            if rec.price and rec.contract_duration:
                total = rec.monthly_rent * rec.contract_duration
                rec.total_remaining = total - paid
            else:
                rec.total_remaining = 0

    # ═══════════════════════════════════════
    # الإجراءات
    # ═══════════════════════════════════════
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'جديد') == 'جديد':
                vals['ref'] = self.env['ir.sequence'].next_by_code('estate.property') or 'جديد'
        return super().create(vals_list)

    def action_set_rented(self):
        self.status = 'rented'

    def action_set_available(self):
        self.status = 'available'
        self.tenant_name = False
        self.tenant_phone = False
        self.contract_start = False
        self.contract_end = False

    def action_set_maintenance(self):
        self.status = 'maintenance'

    # ═══════════════════════════════════════
    # التنبيهات التلقائية
    # ═══════════════════════════════════════
    @api.model
    def _send_expiry_notifications(self):
        """إرسال تنبيهات انتهاء العقود"""
        today = date.today()

        # عقود تنتهي خلال 30 يوم
        expiring_30 = self.search([
            ('status', '=', 'rented'),
            ('contract_end', '=', today + timedelta(days=30)),
        ])
        for prop in expiring_30:
            prop.message_post(
                body=f'⚠️ <b>تنبيه:</b> عقد العقار <b>{prop.name}</b> سينتهي خلال <b>30 يوماً</b> بتاريخ {prop.contract_end}<br/>المستأجر: {prop.tenant_name or "غير محدد"}<br/>يرجى التواصل مع المستأجر لتجديد العقد.',
                subject='تنبيه: عقد ينتهي خلال 30 يوماً',
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

        # عقود تنتهي خلال 7 أيام
        expiring_7 = self.search([
            ('status', '=', 'rented'),
            ('contract_end', '=', today + timedelta(days=7)),
        ])
        for prop in expiring_7:
            prop.message_post(
                body=f'🚨 <b>تنبيه عاجل:</b> عقد العقار <b>{prop.name}</b> سينتهي خلال <b>7 أيام</b> بتاريخ {prop.contract_end}<br/>المستأجر: {prop.tenant_name or "غير محدد"}',
                subject='تنبيه عاجل: عقد ينتهي خلال 7 أيام',
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

        # عقود منتهية - تحديث الحالة
        expired = self.search([
            ('status', '=', 'rented'),
            ('contract_end', '<', today),
        ])
        for prop in expired:
            prop.status = 'expired'
            prop.message_post(
                body=f'🔴 <b>انتهى عقد</b> العقار <b>{prop.name}</b>. يرجى مراجعة الوضع.',
                subject='انتهاء عقد الإيجار',
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

    @api.model
    def _send_payment_notifications(self):
        """إرسال تنبيهات مواعيد السداد"""
        today = date.today()

        # تنبيه قبل 3 أيام من موعد السداد
        properties = self.search([('status', '=', 'rented')])
        for prop in properties:
            if prop.next_payment_date and prop.days_to_payment == 3:
                prop.message_post(
                    body=f'💰 <b>تذكير:</b> موعد سداد إيجار العقار <b>{prop.name}</b> بعد <b>3 أيام</b> بتاريخ {prop.next_payment_date}<br/>المستأجر: {prop.tenant_name or "غير محدد"}<br/>المبلغ المستحق: <b>{prop.monthly_rent:,.2f} ر.س</b>',
                    subject='تذكير: موعد سداد الإيجار',
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
