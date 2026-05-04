# File: apps/hrms_custom/hrms_custom/api/pp.py
import frappe

@frappe.whitelist(allow_guest=True) # url:  http://hrms.locals:8000/api/method/hrms_custom.base_modul.doctype.dump_docs.api.pp.ping
def ping():
    """Endpoint publik: /api/ping"""
    return {"message": "PING!", "status": "success"}

@frappe.whitelist() # url:  http://hrms.locals:8000/api/method/hrms_custom.base_modul.doctype.dump_docs.api.pp.pong
def pong():
    """Endpoint butuh login: /api/pong"""
    return {
        "message": "PONG!",
        "status": "success",
        "user": frappe.session.user,
        "time": frappe.utils.now()
    }