from app.db.database import SessionLocal
from app.db.models import Doctor, Slot

def seed_data():
    db = SessionLocal()

    # Clear existing data (optional but useful for testing)
    db.query(Slot).delete()
    db.query(Doctor).delete()
    db.commit()

    # Create doctors
    doctor1 = Doctor(name="Dr. Sharma", specialization="cardiologist")
    doctor2 = Doctor(name="Dr. Mehta", specialization="dermatologist")

    db.add_all([doctor1, doctor2])
    db.commit()

    # Create slots
    slots = [
        Slot(doctor_id=doctor1.id, time="10:00"),
        Slot(doctor_id=doctor1.id, time="11:00"),
        Slot(doctor_id=doctor2.id, time="12:00"),
    ]

    db.add_all(slots)
    db.commit()

    db.close()

    print("✅ Seed data inserted successfully!")

if __name__ == "__main__":
    seed_data()