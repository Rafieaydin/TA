import frappe
from frappe.tests import IntegrationTestCase
import time

class TestOrganizationalChart(IntegrationTestCase):
    
    def setUp(self):
        """Setup data test sebelum setiap test"""
        frappe.set_user("Administrator")
        
        # Data test dengan timestamp UNIK
        self.timestamp = str(int(time.time()))
        self.test_company = f"Test Company {self.timestamp}"
        self.test_department = f"Test Dept {self.timestamp}"
        self.sub_department = f"Sub Dept {self.timestamp}"
        
        # Buat company test dengan abbreviation UNIK
        company = frappe.get_doc({
            "doctype": "Company",
            "company_name": self.test_company,
            "abbr": f"TC{self.timestamp}",  # ← UNIK!
            "default_currency": "IDR"
        }).insert()
        frappe.db.commit()
        self.test_company_name = company.name
        
        # Buat department utama
        dept = frappe.get_doc({
            "doctype": "Department",
            "department_name": self.test_department,
            "company": self.test_company_name,
            "parent_department": "All Departments",
            "is_group": 1
        }).insert()
        frappe.db.commit()
        self.test_dept_id = dept.name
        
        # Buat sub department
        sub_dept = frappe.get_doc({
            "doctype": "Department",
            "department_name": self.sub_department,
            "company": self.test_company_name,
            "parent_department": self.test_dept_id,
            "is_group": 0
        }).insert()
        frappe.db.commit()
        self.sub_dept_id = sub_dept.name
        
        # Buat employee test
        self.test_employee = f"TEST-EMP-{self.timestamp}"
        emp = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": f"Test Employee {self.timestamp}",
            "first_name": "Test",
            "last_name": "Employee",
            "company": self.test_company_name,
            "department": self.sub_dept_id,
            "status": "Active",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2024-01-01"
        }).insert()
        frappe.db.commit()
        self.test_emp_id = emp.name
    
    def tearDown(self):
        """Bersihkan data test"""
        frappe.set_user("Administrator")
        
        # Hapus employee
        if frappe.db.exists("Employee", self.test_emp_id):
            frappe.delete_doc("Employee", self.test_emp_id, force=True)
        
        # Hapus sub department
        if frappe.db.exists("Department", self.sub_dept_id):
            frappe.delete_doc("Department", self.sub_dept_id, force=True)
        
        # Hapus department utama
        if frappe.db.exists("Department", self.test_dept_id):
            frappe.delete_doc("Department", self.test_dept_id, force=True)
        
        # Hapus company
        if frappe.db.exists("Company", self.test_company_name):
            frappe.delete_doc("Company", self.test_company_name, force=True)
        
        frappe.db.commit()
    
    # ==================== TEST DEPARTMENT CHILDREN ====================
    
    def test_01_get_department_children_all_roots(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        result = get_department_children(
            parent=None,
            company=self.test_company_name,
            department=None,
            doctype="Department"
        )
        
        self.assertIsInstance(result, list)
    
    def test_02_get_department_children_with_parent(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        result = get_department_children(
            parent=self.test_dept_id,
            company=self.test_company_name,
            department=None,
            doctype="Department"
        )
        
        self.assertIsInstance(result, list)
        found = any(node.get("id") == self.sub_dept_id for node in result)
        self.assertTrue(found)
    
    def test_03_get_department_children_filter_by_department(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        result = get_department_children(
            parent=None,
            company=self.test_company_name,
            department=self.test_dept_id,
            doctype="Department"
        )
        
        self.assertIsInstance(result, list)
    
    def test_04_get_department_children_no_company(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        result = get_department_children(
            parent=None,
            company=None,
            department=None,
            doctype="Department"
        )
        
        self.assertEqual(result, [])
    
    def test_05_get_department_children_with_json_company(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        import json
        
        company_json = json.dumps([self.test_company_name, self.test_department])
        
        result = get_department_children(
            parent=None,
            company=company_json,
            department=None,
            doctype="Department"
        )
        
        self.assertIsInstance(result, list)
    
    # ==================== TEST ALL DEPARTMENT NODES ====================
    
    def test_06_get_all_department_nodes(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_all_department_nodes
        
        result = get_all_department_nodes(company=self.test_company_name)
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)
    
    def test_07_get_all_department_nodes_no_company(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_all_department_nodes
        
        result = get_all_department_nodes(company=None)
        
        self.assertIsInstance(result, list)
    
    # ==================== TEST EMPLOYEE CHILDREN ====================
    
    def test_08_get_employee_children_root(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        import json
        
        company_with_dept = json.dumps([self.test_company_name, self.sub_dept_id])
        
        result = get_employee_children(
            parent=None,
            company=company_with_dept,
            exclude_node=None
        )
        
        self.assertIsInstance(result, list)
    
    def test_09_get_employee_children_with_parent(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        import json
        
        company_with_dept = json.dumps([self.test_company_name, self.sub_dept_id])
        
        result = get_employee_children(
            parent=self.test_emp_id,
            company=company_with_dept,
            exclude_node=None
        )
        
        self.assertIsInstance(result, list)
    
    def test_10_get_employee_children_exclude_node(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        import json
        
        company_with_dept = json.dumps([self.test_company_name, self.sub_dept_id])
        
        result = get_employee_children(
            parent=None,
            company=company_with_dept,
            exclude_node=self.test_emp_id
        )
        
        self.assertIsInstance(result, list)
        
        for node in result:
            self.assertNotEqual(node.get("id"), self.test_emp_id)
    
    def test_11_get_employee_children_no_department_filter(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        
        result = get_employee_children(
            parent=None,
            company=self.test_company_name,
            exclude_node=None
        )
        
        self.assertIsInstance(result, list)
    
    def test_12_get_employee_children_empty_company(self):
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        
        result = get_employee_children(
            parent=None,
            company=None,
            exclude_node=None
        )
        
        self.assertIsInstance(result, list)


    def test_13_invalid_json_parsing(self):
        """Test untuk memicu blok except JSONDecodeError"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        # Kirim string yang diawali '[' tapi bukan JSON yang valid
        result = get_department_children(
            parent=None,
            company="[Invalid JSON String", 
            department=None
        )
        self.assertIsInstance(result, list)

    def test_14_department_descendants(self):
        """Test untuk memicu blok get_all_descendants di dalam get_department_children"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        # Kirim parent dan department secara bersamaan
        result = get_department_children(
            parent=self.test_dept_id,
            company=self.test_company_name,
            department=self.test_dept_id,
            doctype="Department"
        )
        self.assertIsInstance(result, list)

    def test_15_employee_with_designation(self):
        """Test untuk memicu blok if current_title and dept_name"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        
        # Update employee agar punya designation
        frappe.db.set_value("Employee", self.test_emp_id, "designation", "Software Engineer")
        frappe.db.commit()
        
        result = get_employee_children(
            parent=None,
            company=self.test_company_name
        )
        
        self.assertIsInstance(result, list)
        # Pastikan title tergabung dengan benar
        found_emp = next((node for node in result if node.id == self.test_emp_id), None)
        if found_emp:
            self.assertTrue("Software Engineer" in found_emp.title)

    def test_16_get_department_show_self(self):
        """Test parameter show_self=1"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children
        
        result = get_department_children(
            parent=None,
            company=self.test_company_name,
            department=self.test_dept_id,
            show_self=1
        )
        self.assertIsInstance(result, list)

    def test_17_company_all_companies(self):
        """Memicu kondisi if company == 'All Companies'"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children, get_all_department_nodes
        
        res1 = get_department_children(company="All Companies")
        res2 = get_all_department_nodes(company="All Companies")
        
        self.assertIsInstance(res1, list)
        self.assertIsInstance(res2, list)

    def test_18_json_array_single_element(self):
        """Memicu blok elif len(parsed) == 1 di parsing JSON"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_department_children, get_employee_children
        import json
        
        company_json = json.dumps([self.test_company_name])
        
        get_department_children(company=company_json)
        get_employee_children(company=company_json)


    def test_20_empty_root_ids_and_multiple_depts(self):
        """Memicu departments.split(',') dan else: return [] saat root_ids kosong"""
        from hrms_custom.hrms_custom.apis.organizational_chart import get_employee_children
        import json
        
        # 1. Test split koma dengan departemen fiktif yang tidak punya karyawan
        fake_dept_1 = f"Fake1 {self.timestamp}"
        fake_dept_2 = f"Fake2 {self.timestamp}"
        
        # Format string dengan koma
        company_json = json.dumps([self.test_company_name, f"{fake_dept_1}, {fake_dept_2}"])
        
        res = get_employee_children(parent=None, company=company_json)
        
        # Pastikan mengembalikan array kosong karena departemen tersebut tidak punya employee
        self.assertEqual(res, [])