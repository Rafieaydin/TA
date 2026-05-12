import frappe
import requests
from frappe.tests import IntegrationTestCase
from frappe.utils import today

# Import fungsi yang akan di-test
from hrms_custom.hrms_custom.apis.employee import (
    get_employee,
    find_employee_by_name,
    create_employee,
    update_employee,
    delete_employee
)
 
class TestEmployeeAPI(IntegrationTestCase):
    
    def setUp(self):
        """Setup data test sebelum setiap test method dijalankan"""
        frappe.set_user("Administrator")
        
        # Data test
        self.test_nippos = "123456789012345678"
        self.test_employee_name = f"Test Employee"
        self.base_url = "http://hrms-test.local:8000"
        
        # Buat employee test jika belum ada
        if not frappe.db.exists("Employee", {"custom_nippos": self.test_nippos}):
            self.test_employee = frappe.get_doc({
                "doctype": "Employee",
                "custom_nippos": self.test_nippos,
                "employee_name": self.test_employee_name,
                "first_name": "Test",
                "last_name": "Employee",
                "company": "test",  # Sesuaikan dengan company yang ada
                "status": "Active",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": today()
            }).insert()
        else:
            self.test_employee = frappe.get_doc("Employee", {"custom_nippos": self.test_nippos})
    
    def tearDown(self):
        """Bersihkan data test setelah selesai"""
        frappe.set_user("Administrator")
        if frappe.db.exists("Employee", {"custom_nippos": self.test_nippos}):
            emp = frappe.get_doc("Employee", {"custom_nippos": self.test_nippos})
            emp.delete()
    
    # ==================== TEST GET EMPLOYEE ====================
    def test_get_employee_function(self):
        """Test get_employee function langsung"""
        result = get_employee()
        
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Data retrieved successfully")
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)
    
    def test_get_employee_via_api(self):
        """Test endpoint get_employee via HTTP request"""
        # Endpoint yang benar sesuai dengan struktur Frappe
        url = f"{self.base_url}/api/method/hrms_custom.hrms_custom.apis.employee.get_employee"
        
        # Atau jika endpoint-nya seperti yang kamu sebutkan
        # url = f"{self.base_url}/api/v1/method/get_employee"
        
        # Untuk akses API, perlu authentication
        # Method 1: Menggunakan API Key (jika sudah di setup)
        headers = {}
        
        # Method 2: Menggunakan session login (lebih mudah untuk test)
        # Login terlebih dahulu
        session = requests.Session()
        login_url = f"{self.base_url}/api/method/login"
        
        # Gunakan credentials Administrator (pastikan passwordnya benar)
        login_data = {
            "usr": "Administrator",
            "pwd": "root"  # Ganti dengan password Administrator site kamu
        }
        
        # Login dulu
        session.post(login_url, data=login_data)
        
        # Panggil API setelah login
        response = session.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("message"))
        
        # Atau jika endpoint-nya langsung bisa diakses (allow_guest=True)
        # response = requests.get(url)
        # self.assertEqual(response.status_code, 200)
    
#     # ==================== TEST FIND EMPLOYEE BY NAME ====================
    def test_find_employee_by_name_found(self):
        """Test find_employee_by_name berhasil menemukan employee"""
        result = find_employee_by_name(self.test_employee_name)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["custom_nippos"], self.test_nippos)
        self.assertEqual(result["employee_name"], self.test_employee_name)
    
    def test_find_employee_by_name_not_found(self):
        """Test find_employee_by_name returns None ketika tidak ditemukan"""
        result = find_employee_by_name("Nama Yang Tidak Ada 12345")
        
        self.assertIsNone(result)
    
    def test_find_employee_by_name_via_api(self):
        """Test find_employee_by_name via HTTP GET"""
        session = requests.Session()
        
        # Login dulu
        login_url = f"{self.base_url}/api/method/login"
        session.post(login_url, data={"usr": "Administrator", "pwd": "root"})
        
        # Panggil API
        url = f"{self.base_url}/api/method/hrms_custom.hrms_custom.apis.employee.find_employee_by_name"
        params = {"name": self.test_employee_name}
        
        response = session.get(url, params=params)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("message"))
    
    # ==================== TEST CREATE EMPLOYEE ====================
    def test_create_employee_success(self):
        """Test create_employee berhasil membuat employee baru"""
        new_nippos = "999999999999999999"
        
        result = create_employee(
            nippos=new_nippos,
            company="test",
            status="Active",
            first_name="New",
            last_name="Employee",
            gender="Female",
            date_of_birth="1995-05-05",
            date_of_joining=today()
        )
        
        self.assertEqual(result["message"], "Employee created successfully")
        self.assertIn("employee", result)
        
        # Verifikasi di database
        employee_exists = frappe.db.exists("Employee", {"custom_nippos": new_nippos})
        self.assertTrue(employee_exists)
        
        # Cleanup
        if employee_exists:
            emp = frappe.get_doc("Employee", {"custom_nippos": new_nippos})
            emp.delete()
    
    
    def test_create_employee_via_api(self):
        """Test create_employee via HTTP POST"""
         # Commit semua transaksi sebelumnya
        frappe.db.commit()
    
        # Reload employee dari database fresh
        self.test_employee.reload()
        session = requests.Session()
        
        # Login
        login_url = f"{self.base_url}/api/method/login"
        session.post(login_url, data={"usr": "Administrator", "pwd": "root"})
        
        new_nippos = "777777"
        
        # POST data
        url = f"{self.base_url}/api/method/hrms_custom.hrms_custom.apis.employee.create_employee"
        payload = {
            "nippos": new_nippos,
            "company": "test",
            "status": "Active",
            "first_name": "API",
            "last_name": "Test",
            "gender": "Male",
            "date_of_birth": "1992-02-02",
            "date_of_joining": today()
        }
        
        response = session.post(url, data=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("message")['message'], "Employee created successfully")
        
        # Cleanup
        if frappe.db.exists("Employee", {"custom_nippos": new_nippos}):
            emp = frappe.get_doc("Employee", {"custom_nippos": new_nippos})
            emp.delete()
    
    # ==================== TEST UPDATE EMPLOYEE ====================
    def test_update_employee_success(self):
        """Test update_employee berhasil mengubah status"""
        from hrms_custom.hrms_custom.apis.employee import update_employee
        
        new_status = "Inactive"
        
        result = update_employee(
            nippos=self.test_nippos,
            status=new_status
        )
        
        # Assertions
        self.assertEqual(result.get("message"), "Employee updated successfully")
        self.assertEqual(result.get("employee", {}).get("status"), new_status)
        
        # Verifikasi di database
        frappe.db.set_value("Employee", self.test_employee.name, "status", "Active")
        frappe.db.commit()
        
        # Reload object biar sinkron
        self.test_employee.reload()
    
    def test_update_employee_not_found(self):
        """Test update_employee dengan nippos yang tidak ada"""
        with self.assertRaises(frappe.ValidationError) as context:
            update_employee(
                nippos="000000000000000000",
                status="Active"
            )
        
        self.assertIn("tidak ditemukan", str(context.exception))
    
    def test_update_employee_via_api(self):
        """Test update_employee via HTTP POST"""
        frappe.db.commit()
    
        # Reload employee dari database fresh
        self.test_employee.reload()
        session = requests.Session()
        
        # Login
        login_url = f"{self.base_url}/api/method/login"
        session.post(login_url, data={"usr": "Administrator", "pwd": "root"})
        
        # Update status
        url = f"{self.base_url}/api/method/hrms_custom.hrms_custom.apis.employee.update_employee"
        payload = {
            "nippos": self.test_nippos,
            "status": "Inactive"
        }
        
        response = session.post(url, data=payload)

        # self.assertEqual(response, 200)
        data = response.json()
        if isinstance(data.get("message"), dict):
            # Jika response nested, ambil dari dalam
            self.assertEqual(data["message"].get("message"), "Employee updated successfully")
        else:
        # Jika response langsung
            self.assertEqual(data.get("message"), "Employee updated successfully")
    
        
        # Verifikasi di database
        frappe.db.set_value("Employee", self.test_employee.name, "status", "Active")
        frappe.db.commit()
        
        # Reload object biar sinkron
        self.test_employee.reload()
    
#     # ==================== TEST DELETE EMPLOYEE ====================
    def test_delete_employee_success(self):
        """Test delete_employee berhasil menghapus"""
        # Buat employee temporary
        temp_nippos = "6666666666"
        temp_employee = frappe.get_doc({
            "doctype": "Employee",
            "custom_nippos": temp_nippos,
            "employee_name": "Temp Employee",
            "first_name": "Temp",
            "company": "test",
            "status": "Active",
            "date_of_birth": "1990-01-01",
            "date_of_joining": today(),
            "gender": "Male"
        }).insert()
        
        # Delete
        result = delete_employee(nippos=temp_nippos)
        
        self.assertEqual(result.get("message"), "Employee deleted successfully")
        
        # Verifikasi sudah terhapus
        employee_exists = frappe.db.exists("Employee", {"custom_nippos": temp_nippos})
        self.assertFalse(employee_exists)
    
    def test_delete_employee_not_found(self):
        """Test delete_employee dengan nippos yang tidak ada"""
        with self.assertRaises(frappe.ValidationError) as context:
            delete_employee(nippos="000000000000000000")
        
        self.assertIn("tidak ditemukan", str(context.exception))


# ==================== TEST UNTUK PATH YANG KAMU SEBUTKAN ====================
class TestEmployeeAPIImport(IntegrationTestCase):
    """Test untuk memastikan import dari path yang benar"""
    
    def test_import_from_correct_path(self):
        """Test import fungsi dari path yang benar"""
        # Ini akan sukses jika path-nya benar
        from hrms_custom.hrms_custom.tests.test_employee import find_employee_by_name
        
        # Seharusnya ini adalah fungsi yang kamu buat, bukan dari folder tests
        # Saran: Jangan simpan fungsi API di folder tests
        # Pindahkan fungsi API ke hrms_custom/hrms_custom/api/employee_api.py
        
        self.assertTrue(callable(find_employee_by_name))
    
    def test_api_endpoint_url(self):
        """Test format URL endpoint"""
        base_url = "http://hrms-test.local:8000"
        
        # Format endpoint yang benar untuk Frappe
        endpoint1 = f"{base_url}/api/method/get_employee"
        endpoint2 = f"{base_url}/api/v1/method/get_employee"  # Yang kamu sebutkan
        
        # Keduanya bisa jalan tergantung konfigurasi route
        print(f"Endpoint 1: {endpoint1}")
        print(f"Endpoint 2: {endpoint2}")
        
        # Test endpoint availability (optional)
        # response = requests.get(endpoint2)
        # print(f"Status: {response.status_code}")