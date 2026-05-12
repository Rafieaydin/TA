import frappe
import requests

# API untuk Employee Management 
@frappe.whitelist()
def get_employee(methods=['GET']):
    return {
        "message": "Data retrieved successfully",
        "data": frappe.db.get_list('Employee',
                                   fields=['*'],
            limit=1000
        )
    }

@frappe.whitelist()
def find_employee_by_name(name):
    employee = frappe.db.get_list('Employee',fields=['*'], filters={'employee_name': name}, limit=1)
    if employee:
        return employee[0]
    else:
        return None

@frappe.whitelist(methods=['POST'])
def create_employee(nippos, company, status, first_name=None, middle_name=None, 
                   last_name=None, gender=None, date_of_birth=None, salutation=None, date_of_joining=None):  
                   
    # cek apakah request nya sudah post // kalau mau di test matiin aja dulu
    # if frappe.request.method != 'POST':
    #     frappe.throw("Invalid request method. Please use POST.")
    
    # Set default values jika tidak dikirim
    if not first_name:
        first_name = "Employee"
    
    new_employee = frappe.get_doc({
        'doctype': 'Employee',
        'name': "NIPPOS-"+nippos,  # contoh penentuan nama dokumen berdasarkan NIPPOS
        'custom_nippos': nippos,
        'employee_name': first_name + " " + (middle_name or "") + " " + (last_name or ""),
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'company': company, 
        'status': status,
        'gender': gender or 'Male',
        'date_of_birth': date_of_birth,
        'salutation': salutation,
        'date_of_joining': date_of_joining
    })
    
    new_employee.insert()

    return {
        "message": "Employee created successfully",
        "employee": new_employee.as_dict()
    }

@frappe.whitelist(methods=['POST'])
def update_employee(nippos, status):
    """Update status employee berdasarkan nippos"""
    # if frappe.request.method != 'POST':
    #     frappe.throw("Invalid request method. Please use POST.")
    
    # Filter berdasarkan nippos (custom_nippos field)
    employee = frappe.db.get_list('Employee', fields=['name'], filters={'custom_nippos': nippos}, limit=1)
    if not employee:
        frappe.throw(f"Employee dengan NIPPOS {nippos} tidak ditemukan!")
    
    # Update status
    emp_doc = frappe.get_doc('Employee', employee[0]['name'])
    emp_doc.status = status
    emp_doc.save()
    
    return {
        "message": "Employee updated successfully",
        "employee": emp_doc.as_dict()
    }

@frappe.whitelist(methods=['DELETE'])
def delete_employee(nippos):
    """Delete employee berdasarkan nippos"""
    # if frappe.request.method != 'DELETE':
    #     frappe.throw("Invalid request method. Please use DELETE.")
    
    # Cari employee berdasarkan nippos
    employee = frappe.db.get_list('Employee', fields=['name'], filters={'custom_nippos': nippos}, limit=1)
    if not employee:
        frappe.throw(f"Employee dengan NIPPOS {nippos} tidak ditemukan!")
    
    # Delete employee
    emp_doc = frappe.get_doc('Employee', employee[0]['name'])
    emp_doc.delete()
    
    return {"message": "Employee deleted successfully"}