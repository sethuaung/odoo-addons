# -*- encoding: utf-8 -*-
{
    'name': "Attendances Checkin Location",
    'version': '15.0.1.2',
    'summary': 'A product of Bac Ha Software allows employees to check-in from many different working locations such as: The company, home or other places such as outdoor locations.',
    'category': 'Human Resources/Attendances',
    'description': """A product of Bac Ha Software allows employees to check-in from many different working locations such as: The company, home or other places such as outdoor locations.""",
    "depends": ['web', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_location.xml',
        'data/attendance_location_data.xml',
    ],
    "assets": {
        'web.assets_backend': [
            '/bhs_checkin_location/static/src/scss/my_attendances.scss',
            '/bhs_checkin_location/static/src/js/my_attendances.js',
        ],
        'web.assets_qweb': {
            '/bhs_checkin_location/static/src/xml/my_attendances.xml',
        },
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    # Author
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}
