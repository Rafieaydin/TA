import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today
import time

class TestDepartmentAPI(IntegrationTestCase):
    
    def setUp(self):
        """Setup data test sebelum setiap test method"""
        frappe.set_user("Administrator")
        
        # Gunakan timestamp untuk nama unik setiap test
        self.timestamp = str(int(time.time()))
        self.test_department = f"Test Department IT {self.timestamp}"
        self.test_company = "Test Company"
        
        # Buat company test jika belum ada
        if not frappe.db.exists("Company", self.test_company):
            company = frappe.get_doc({
                "doctype": "Company",
                "company_name": self.test_company,
                "abbr": "TC",
                "default_currency": "IDR"
            }).insert()
            frappe.db.commit()
        
        # Bersihkan department dengan nama yang sama (jika ada)
        existing_dept = frappe.db.get_list('Department', 
            filters={'department_name': self.test_department},
            fields=['name'])
        for dept in existing_dept:
            frappe.delete_doc("Department", dept.name, force=True)
            frappe.db.commit()
    
    def tearDown(self):
        """Bersihkan data test setelah selesai"""
        frappe.set_user("Administrator")
        
        # Hapus department test berdasarkan department_name
        existing_dept = frappe.db.get_list('Department', 
            filters={'department_name': self.test_department},
            fields=['name'])
        for dept in existing_dept:
            frappe.delete_doc("Department", dept.name, force=True)
            frappe.db.commit()
    
    # ==================== TEST GET DEPARTMENT ====================
    def test_get_department_success(self):
        """Test get_department berhasil mengambil data"""
        from hrms_custom.hrms_custom.apis.department import get_department
        
        result = get_department()
        
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Data retrieved successfully")
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)
    
    # ==================== TEST FIND DEPARTMENT ====================
    def test_find_department_found(self):
        """Test find_department berhasil menemukan department"""
        from hrms_custom.hrms_custom.apis.department import create_department, find_department
        
        # Buat department
        create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments"
        )
        frappe.db.commit()
        
        # Karena API mencari berdasarkan 'name', kita cari dulu nama dokumennya
        dept_list = frappe.db.get_list('Department', 
            filters={'department_name': self.test_department},
            fields=['name'])
        
        if dept_list:
            # Panggil API dengan nama dokumen yang benar (bisa ada suffix - TC)
            result = find_department(dept_list[0]['name'])
            self.assertIsNotNone(result)
            self.assertEqual(result.get("department_name"), self.test_department)
        else:
            self.fail("Department tidak ditemukan")
    
    def test_find_department_not_found(self):
        """Test find_department mengembalikan None jika tidak ditemukan"""
        from hrms_custom.hrms_custom.apis.department import find_department
        
        result = find_department("Department Yang Tidak Ada 12345")
        
        self.assertIsNone(result)
    
    # ==================== TEST CREATE DEPARTMENT ====================
    def test_create_department_success(self):
        """Test create_department berhasil membuat department baru"""
        from hrms_custom.hrms_custom.apis.department import create_department
        
        result = create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments",
            is_group=False
        )
        
        self.assertEqual(result.get("message"), "Department created successfully")
        self.assertIn("department", result)
        
        # Verifikasi di database (cari berdasarkan department_name)
        dept_exists = frappe.db.exists("Department", {"department_name": self.test_department})
        self.assertTrue(dept_exists)
    
    def test_create_department_with_invalid_company(self):
        """Test create_department dengan company yang tidak valid"""
        from hrms_custom.hrms_custom.apis.department import create_department
        
        with self.assertRaises(frappe.ValidationError) as context:
            create_department(
                department="Test Dept",
                company="Company Tidak Ada",
                parent_department="All Departments"
            )
        
        self.assertIn("tidak ditemukan", str(context.exception))
    
    def test_create_department_as_group(self):
        """Test create_department dengan is_group=True"""
        from hrms_custom.hrms_custom.apis.department import create_department
        
        result = create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments",
            is_group=True
        )
        
        self.assertEqual(result.get("message"), "Department created successfully")
        
        # Verifikasi is_group
        dept_name_in_db = result["department"]["name"]
        dept_doc = frappe.get_doc("Department", dept_name_in_db)
        self.assertEqual(dept_doc.is_group, 1)
    
    def test_create_department_with_string_boolean(self):
        """Test create_department dengan is_group berupa string 'true'/'false'"""
        from hrms_custom.hrms_custom.apis.department import create_department
        
        result = create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments",
            is_group="true"
        )
        
        self.assertEqual(result.get("message"), "Department created successfully")
        
        # Verifikasi ter-convert ke boolean
        dept_name_in_db = result["department"]["name"]
        dept_doc = frappe.get_doc("Department", dept_name_in_db)
        self.assertEqual(dept_doc.is_group, 1)
    
    # ==================== TEST UPDATE DEPARTMENT ====================
    def test_update_department_success(self):
        """Test update_department berhasil mengubah data department"""
        from hrms_custom.hrms_custom.apis.department import create_department, update_department
        
        # Buat department
        create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments"
        )
        frappe.db.commit()
        
        dept_list = frappe.db.get_list('Department', 
            filters={'department_name': self.test_department},
            fields=['name'])
        
        if dept_list:
            # Update dengan nama dokumen yang benar
            result = update_department(
                department=dept_list[0]['name'],
                is_group=True
            )
            
            self.assertEqual(result.get("message"), "Department updated successfully")
            
            # Verifikasi perubahan
            dept_doc = frappe.get_doc("Department", dept_list[0]['name'])
            self.assertEqual(dept_doc.is_group, 1)
        else:
            self.fail("Department tidak ditemukan")
    
    def test_update_department_not_found(self):
        """Test update_department dengan department yang tidak ada"""
        from hrms_custom.hrms_custom.apis.department import update_department
        
        with self.assertRaises(frappe.ValidationError) as context:
            update_department(
                department="Department Tidak Ada 12345",
                is_group=True
            )
        
        self.assertIn("tidak ditemukan", str(context.exception))
    
    def test_update_department_with_invalid_company(self):
        """Test update_department dengan company yang tidak valid"""
        from hrms_custom.hrms_custom.apis.department import create_department, update_department
        
        # Buat department
        create_department(
            department=self.test_department,
            company=self.test_company,
            parent_department="All Departments"
        )
        frappe.db.commit()
        
        # Dapatkan nama dokumen yang benar
        dept_list = frappe.db.get_list('Department', 
            filters={'department_name': self.test_department},
            fields=['name'])
        
        if dept_list:
            with self.assertRaises(frappe.ValidationError) as context:
                update_department(
                    department=dept_list[0]['name'],
                    company="Company Invalid 12345"
                )
            
            self.assertIn("tidak ditemukan", str(context.exception))
    
    # ==================== TEST DELETE DEPARTMENT ====================
    def test_delete_department_success(self):
        """Test delete_department berhasil menghapus department"""
        from hrms_custom.hrms_custom.apis.department import create_department, delete_department
        
        # Buat department dengan nama unik
        temp_dept = f"Temp Department {self.timestamp}"
        
        result_create = create_department(
            department=temp_dept,
            company=self.test_company,
            parent_department="All Departments"
        )
        frappe.db.commit()
        
        dept_name_in_db = result_create["department"]["name"]
        
        # Delete department dengan nama dokumen yang benar
        result = delete_department(department=dept_name_in_db)
        
        self.assertEqual(result.get("message"), "Department deleted successfully")
        
        # Verifikasi sudah terhapus
        dept_exists = frappe.db.exists("Department", dept_name_in_db)
        self.assertFalse(dept_exists)
    
    def test_delete_department_not_found(self):
        """Test delete_department dengan department yang tidak ada"""
        from hrms_custom.hrms_custom.apis.department import delete_department
        
        with self.assertRaises(frappe.ValidationError) as context:
            delete_department(department="Department Tidak Ada 12345")
        
        self.assertIn("tidak ditemukan", str(context.exception))