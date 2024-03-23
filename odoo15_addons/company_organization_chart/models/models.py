# from odoo import models, api

# class Company(models.Model):
#     _inherit = 'res.company'
    
#     @api.model
#     def get_employees(self, company_id):
#         employees = self.env['hr.employee'].search([('company_id', '=', company_id)])
#         return employees