import unittest
import os
import uuid
from sqlalchemy import text
from app import app, db
from models import User, VendorProfile

class TestHomepageVisibility(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost' # Fix for url_for
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_mock_user(self, email="test@test.com"):
        user = User(username="user_" + uuid.uuid4().hex[:8], email=email, role="vendor", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        return user.id

    def test_homepage_with_status_active_and_pending(self):
        with app.app_context():
            uid1 = self.create_mock_user("vendor1@test.com")
            uid2 = self.create_mock_user("vendor2@test.com")
            
            # Active vendor
            v1 = VendorProfile(user_id=uid1, business_name="Active Business", status="active", description="Desc1")
            # Pending vendor
            v2 = VendorProfile(user_id=uid2, business_name="Pending Business", status="pending", description="Desc2")
            
            db.session.add_all([v1, v2])
            db.session.commit()

        with app.app_context():
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            html = response.data.decode('utf-8')
            
            # Test moderation behavior: active appears, pending does not
            self.assertIn("Active Business", html)
            self.assertNotIn("Pending Business", html)

    def test_homepage_with_null_description(self):
        with app.app_context():
            uid = self.create_mock_user("vendor_null@test.com")
            # Vendor with description None
            v1 = VendorProfile(user_id=uid, business_name="Null Desc Business", status="active", description=None)
            db.session.add(v1)
            db.session.commit()

        with app.app_context():
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            html = response.data.decode('utf-8')
            self.assertIn("Null Desc Business", html)
            self.assertIn("Description will", html)

    def test_homepage_missing_status_column(self):
        with app.app_context():
            # First insert data
            uid = self.create_mock_user("legacy@test.com")
            v1 = VendorProfile(user_id=uid, business_name="Legacy Business", status="active", description="Legacy")
            db.session.add(v1)
            db.session.commit()

            # Now manually drop the 'status' column to simulate legacy schema.
            with db.engine.connect() as conn:
                # SQLite trick to drop column if drop column not supported or to be safe
                conn.execute(text("CREATE TABLE vendor_profile_temp (id INTEGER PRIMARY KEY, user_id INTEGER, business_name VARCHAR, description TEXT, logo VARCHAR, banner VARCHAR, gst_number VARCHAR, msme_registration VARCHAR, seller_name VARCHAR, aadhar_number VARCHAR, family_background TEXT, registration_number VARCHAR)"))
                conn.execute(text("INSERT INTO vendor_profile_temp (id, user_id, business_name, description) VALUES (1, 1, 'Legacy Business', 'Legacy')"))
                conn.execute(text("DROP TABLE vendor_profile"))
                conn.execute(text("ALTER TABLE vendor_profile_temp RENAME TO vendor_profile"))
                conn.commit()

        with app.app_context():
            # Try to render the homepage
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            html = response.data.decode('utf-8')
            # Since fallback is to list all vendors when column is missing
            self.assertIn("Legacy Business", html)

if __name__ == '__main__':
    unittest.main()
