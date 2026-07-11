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
    'summary': 'ÄTA-hantering för bygg- och entreprenadprojekt enligt AB04/ABT06',
    'description': """
        Hantera Ändrings-, Tilläggs- och Avgående arbeten (ÄTA) enligt AB04/ABT06.
        
        Funktioner:
        - Fullständig ÄTA-livscykel: Utkast → Inskickad → Godkänd/Avvisad → Pågående → Klar → Fakturerad → Avslutad
        - ÄTA-nummer per projekt (ÄTA 001, ÄTA 002, ...)
        - Orderrader med kvantitet, pris, påslag
        - Påslagsmallar som kan överstyra individuella rad-påslag
        - Digital signering via sign.mixin
        - Integration med projekt och kontrakt
    """,
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
