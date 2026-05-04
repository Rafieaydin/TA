import frappe

# API untuk Department Management

@frappe.whitelist()
def get_department():
    """Get semua data department"""
    departments = frappe.db.get_list('Department', fields=['*'], limit=1000)
    return {
        "message": "Data retrieved successfully",
        "data": departments
    }

@frappe.whitelist()
def find_department(department_name):
    """Cari department berdasarkan nama"""
    department = frappe.db.get_list('Department', fields=['*'], filters={'name': department_name}, limit=1)
    return department[0] if department else None

@frappe.whitelist(methods=['POST'])
def create_department(department, company, parent_department="All Departments", is_group=False):
    """
    Buat department baru
    
    Parameters:
    - department: Nama department (wajib)
    - company: Nama company (wajib, akan divalidasi)
    - parent_department: Parent department (default: All Departments)
    - is_group: Boolean true/false (default: False)
    """
    if frappe.request.method != 'POST':
        frappe.throw("Invalid request method. Please use POST.")
    
    # Validasi company - cek apakah company ada di database
    company_exists = frappe.db.exists('Company', company)
    if not company_exists:
        frappe.throw(f"Company '{company}' tidak ditemukan! Silakan gunakan company yang valid.")
    
    # Validasi parent_department jika tidak "All Departments"
    if parent_department != "All Departments":
        parent_exists = frappe.db.exists('Department', parent_department)
        if not parent_exists:
            frappe.throw(f"Parent Department '{parent_department}' tidak ditemukan!")
    
    # Convert string "true"/"false" ke boolean jika diperlukan
    if isinstance(is_group, str):
        is_group = is_group.lower() == 'true'
    
    # Buat department
    new_department = frappe.get_doc({
        'doctype': 'Department',
        'department_name': department,
        'company': company,
        'parent_department': parent_department,
        'is_group': is_group
    })
    
    new_department.insert()
    
    return {
        "message": "Department created successfully",
        "department": new_department.as_dict()
    }

@frappe.whitelist(methods=['POST'])
def update_department(department, company=None, parent_department=None, is_group=None):
    """
    Update department berdasarkan nama department
    
    Parameters:
    - department: Nama department yang akan diupdate (wajib)
    - company: Company baru (optional)
    - parent_department: Parent department baru (optional)
    - is_group: Boolean true/false (optional)
    """
    if frappe.request.method != 'POST':
        frappe.throw("Invalid request method. Please use POST.")
    
    # Cari department
    dept = frappe.db.get_list('Department', fields=['name'], filters={'name': department}, limit=1)
    if not dept:
        frappe.throw(f"Department '{department}' tidak ditemukan!")
    
    # Update department
    dept_doc = frappe.get_doc('Department', dept[0]['name'])
    
    # Validasi company jika diupdate
    if company:
        company_exists = frappe.db.exists('Company', company)
        if not company_exists:
            frappe.throw(f"Company '{company}' tidak ditemukan!")
        dept_doc.company = company
    
    # Validasi parent_department jika diupdate
    if parent_department:
        if parent_department != "All Departments":
            parent_exists = frappe.db.exists('Department', parent_department)
            if not parent_exists:
                frappe.throw(f"Parent Department '{parent_department}' tidak ditemukan!")
        dept_doc.parent_department = parent_department
    
    # Update is_group jika dikirim
    if is_group is not None:
        if isinstance(is_group, str):
            is_group = is_group.lower() == 'true'
        dept_doc.is_group = is_group
    
    dept_doc.save()
    
    return {
        "message": "Department updated successfully",
        "department": dept_doc.as_dict()
    }

@frappe.whitelist(methods=['DELETE'])
def delete_department(department):
    """
    Delete department berdasarkan nama
    
    Parameters:
    - department: Nama department yang akan dihapus (wajib)
    """
    if frappe.request.method != 'DELETE':
        frappe.throw("Invalid request method. Please use DELETE.")
    
    # Cari department
    dept = frappe.db.get_list('Department', fields=['name'], filters={'name': department}, limit=1)
    if not dept:
        frappe.throw(f"Department '{department}' tidak ditemukan!")
    
    # Delete department
    dept_doc = frappe.get_doc('Department', dept[0]['name'])
    dept_doc.delete()
    
    return {"message": "Department deleted successfully"}
