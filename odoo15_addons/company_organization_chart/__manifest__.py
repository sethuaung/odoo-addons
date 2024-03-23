# -*- coding: utf-8 -*-
{
    'name': "company_organization_chart",

    'summary': """
        Simple Company Organization Chart""",

    'description': """
        This is just a simple addons that shows company org chart based on your employees data
    """,

    'author': "Codesev",
    'website': "https://codesev.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',

        # 'data/demo.xml',
    ],
    'css': [
        'static/src/css/organization_chart_styles.css',
    ],
    'currency': 'usd',
    'price': 0,
    'license': 'LGPL-3',
    'images': [
        'static/description/icon.png',
    ],
}
