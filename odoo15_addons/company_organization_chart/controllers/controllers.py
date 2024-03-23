from odoo import http
from odoo.http import request


class EmployeeHierarchyController(http.Controller):
    @http.route('/employee/hierarchy', type='http', auth='user', website=True)
    def employee_hierarchy(self):
        company_id = request.env.company.id
        root_employee = self.get_root_employee(company_id)
        employees = self.get_employees(company_id)
        return request.render('company_organization_chart.custom_company_hierarchy_node_template', {
            'root_employee': root_employee, 'employees': employees
        })

    def get_root_employee(self, company_id):
        root_employee = self.get_employees(company_id, limit=1)
        return root_employee

    @staticmethod
    def get_employees(company_id, domain=None, limit=None):
        company = request.env['res.company'].browse(company_id)
        employees = request.env['hr.employee'].search([('company_id', '=', company.id)] + (domain or []), limit=limit)
        return employees.sorted(key=lambda emp: emp.parent_id.id or 0)
