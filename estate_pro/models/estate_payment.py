from odoo import models, fields, api
from datetime import date


class EstatePayment(models.Model):
    _name = 'estate.payment'
    _description = 'دفعة الإيجار'
    _order = 'payment_date desc'

    property_id = fields.Many2one('estate.property', string='العقار', required=True, ondelete='cascade')
    name = fields.Char(string='رقم الدفعة', readonly=True, default='جديد')
    amount = fields.Float(string='المبلغ', required=True)
    payment_date = fields.Date(string='تاريخ الدفع', default=fields.Date.today)
    due_date = fields.Date(string='تاريخ الاستحقاق')
    state = fields.Selection([
        ('pending', 'معلق'),
        ('paid', 'مدفوع'),
        ('late', 'متأخر'),
    ], string='الحالة', default='pending', tracking=True)
    payment_method = fields.Selection([
        ('cash', 'نقداً'),
        ('transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
    ], string='طريقة الدفع', default='cash')
    notes = fields.Text(string='ملاحظات')
    period = fields.Char(string='الفترة')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'جديد') == 'جديد':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.payment') or 'جديد'
        return super().create(vals_list)

    def action_mark_paid(self):
        self.state = 'paid'
        self.payment_date = date.today()

    def action_print_invoice(self):
        return self.env.ref('estate_pro.action_report_estate_invoice').report_action(self)

    def action_mark_late(self):
        self.state = 'late'

    @api.model
    def _check_late_payments(self):
        today = date.today()
        late = self.search([
            ('state', '=', 'pending'),
            ('due_date', '<', today),
        ])
        for payment in late:
            payment.state = 'late'
            payment.property_id.message_post(
                body=f'⛔ <b>تأخر في السداد!</b> الدفعة رقم {payment.name} للعقار <b>{payment.property_id.name}</b> متأخرة.<br/>المبلغ: <b>{payment.amount:,.2f} ر.س</b><br/>تاريخ الاستحقاق: {payment.due_date}',
                subject='تحذير: تأخر في سداد الإيجار',
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
