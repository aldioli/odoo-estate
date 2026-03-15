{
    'name': 'العقارات الاحترافية',
    'version': '17.0.2.0.0',
    'category': 'Real Estate',
    'summary': 'نظام إدارة العقارات الاحترافي مع التنبيهات والمحاسبة',
    'description': 'نظام متكامل لإدارة العقارات مع تنبيهات انتهاء العقود وسداد الإيجار',
    'author': 'Custom',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_invoice_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
