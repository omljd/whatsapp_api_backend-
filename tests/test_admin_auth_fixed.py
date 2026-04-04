import requests
import unittest
import uuid

BASE_URL = "http://localhost:8000/api"

class TestAdminAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Admin Credentials as per task
        cls.credentials = {
            "email": "adminlogin6631@gmail.com",
            "password": "Admin@6631"
        }
        cls.token = None
        cls.admin_id = None

    def test_01_admin_login(self):
        """Test admin login with seeded credentials"""
        print("\nTesting Admin Login...")
        response = requests.post(f"{BASE_URL}/admin/login", json=self.credentials)
        self.assertEqual(response.status_code, 200, f"Login failed: {response.text}")
        
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "admin")
        self.__class__.token = data["access_token"]
        print("✅ Login successful")

    def test_02_get_profile(self):
        """Test getting admin profile using JWT"""
        if not self.token: self.skipTest("No token available")
        
        print("\nTesting Get Admin Profile...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/admin/profile", headers=headers)
        self.assertEqual(response.status_code, 200, f"Profile fetch failed: {response.text}")
        
        data = response.json()
        self.assertEqual(data["email"], self.credentials["email"])
        self.assertEqual(data["role"], "Super Admin")
        print(f"✅ Profile fetched: {data['name']} ({data['email']})")

    def test_03_protect_stats(self):
        """Test that stats endpoint is protected"""
        print("\nTesting Protected Stats Endpoint...")
        # No token should fail
        response = requests.get(f"{BASE_URL}/admin/stats")
        self.assertEqual(response.status_code, 401)
        
        # Valid token should work
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        print("✅ Stats protection verified")

    def test_04_delete_user_authorization(self):
        """Test delete user authorization (ensuring no 'role' attribute error)"""
        if not self.token: self.skipTest("No token available")
        
        print("\nTesting Delete User Authorization...")
        # We'll try to delete a non-existent user just to trigger the auth check
        random_id = str(uuid.uuid4())
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{BASE_URL}/admin/users/{random_id}", headers=headers)
        
        # If the fix works, it should NOT return 500 (AttributeError) 
        # It should return 404 (Not Found) since the user ID is random.
        # This confirms current_admin was authenticated and the .role check didn't crash.
        self.assertEqual(response.status_code, 404, f"Expected 404 but got {response.status_code}: {response.text}")
        print("✅ Delete authorization logic verified (No AttributeError)")

if __name__ == "__main__":
    unittest.main()
