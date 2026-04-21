from app import app, db
from models import User, VendorProfile, Product
from werkzeug.security import generate_password_hash

def seed_db():
    with app.app_context():
        # Drop and re-create database for schema updates
        db.drop_all()
        db.create_all()

        # Admin User
        admin = User(
            username='admin', 
            email='admin@bizzora.in', 
            role='admin', 
            password_hash=generate_password_hash('admin123'),
            phone_number='9876543210',
            address='Bizzora HQ, Mumbai, Maharashtra 400001'
        )
        db.session.add(admin)

        # Vendors
        vendor1 = User(
            username='ramesh_electronics', 
            email='ramesh@example.in', 
            role='vendor', 
            password_hash=generate_password_hash('vendor123'),
            phone_number='9123456780',
            address='12, MG Road, Bengaluru, Karnataka 560001'
        )
        vendor2 = User(
            username='sita_fashion', 
            email='sita@example.in', 
            role='vendor', 
            password_hash=generate_password_hash('vendor123'),
            phone_number='9988776655',
            address='Shop 45, Connaught Place, New Delhi 110001'
        )
        
        db.session.add(vendor1)
        db.session.add(vendor2)
        db.session.commit()

        vp1 = VendorProfile(
            user_id=vendor1.id, 
            business_name='Ramesh Electronics & Mobiles', 
            description='Authentic electronics, smartphones, and accessories dealer.',
            gst_number='29ABCDE1234F1Z5',
            status='active'
        )
        vp2 = VendorProfile(
            user_id=vendor2.id, 
            business_name='Sita Fashion & Ethnics', 
            description='Premium traditional wear, sarees, and kurtis.',
            gst_number='07FGHIJ5678K1Z9',
            status='pending'
        )
        
        db.session.add(vp1)
        db.session.add(vp2)
        db.session.commit()

        # Products
        products = [
            Product(name='Samsung Galaxy M34 5G', description='120Hz sAMOLED display, 50MP No Shake Cam', price=17999.0, vendor_id=vp1.id),
            Product(name='boAt Airdopes 141', description='Bluetooth TWS earbuds with 42H playtime', price=1299.0, vendor_id=vp1.id),
            Product(name='Milton Thermosteel Flask', description='1000ml vacuum insulated water bottle', price=899.0, vendor_id=vp1.id),
            Product(name='Banarasi Silk Saree', description='Beautiful handwoven Banarasi Silk Saree with Blouse Piece', price=3499.0, vendor_id=vp2.id),
            Product(name='Biba Cotton Kurta Set', description='Womens pure cotton printed straight Kurta with Palazzo', price=1599.0, vendor_id=vp2.id),
            Product(name='Men\'s Cotton Kurta', description='Festive wear, solid color mens kurta', price=899.0, vendor_id=vp2.id),
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        
        # Test Customer
        customer = User(
            username='arjun_kumar', 
            email='arjun@example.in', 
            role='customer', 
            password_hash=generate_password_hash('customer123'),
            phone_number='9898989898',
            address='A-102, Sunrise Apartments, Pune, Maharashtra'
        )
        db.session.add(customer)
        db.session.commit()
        
        print("Database seeded with Indian demo data successfully!")

if __name__ == '__main__':
    seed_db()
