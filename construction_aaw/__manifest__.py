# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Construction: ÄTA (Change Orders)',
    'version': '18.0.1.0.0',
    'summary': "Change order (ATA) handling for construction projects per AB04/ABT06.",
    'description': '''
ÄTA (Change Orders)
===================

    Change, Addition and Omission Works (ATA) per AB04/ABT06.

Features:

    - Full ATA life cycle: Draft -> Submitted -> Approved/Rejected ->
      In progress -> Done -> Invoiced.
    - Change order lines with quantities and prices.
    - Automatic invoicing of approved change orders.
    ''',
    'category': 'Construction',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-construction/construction_aaw',
    'license': 'AGPL-3',
    'maintainer': 'Vertel Sverige AB',
    "application": False,
    "auto-install": False,
    "installable": True,
    'depends': [
        'project',
        'contract',
        'account',
        'sale_management',
        'sign_oca',
        'mail',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/aaw_sequence.xml',
        'views/construction_aaw_views.xml',
        'views/construction_aaw_line_views.xml',
        'views/construction_aaw_surcharge_template_views.xml',
        'views/project_project_views.xml',
        'views/menu.xml',
    ],
}
