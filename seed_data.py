#!/usr/bin/env python3
# seed_data.py
# Run this script to populate the database with sample test data
# Usage: python seed_data.py

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models
from auth import hash_password

# Create tables first
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    # Clear existing data
    db.query(models.Message).delete()
    db.query(models.HelpRequest).delete()
    db.query(models.User).delete()
    db.commit()
    print("🧹 Cleared existing data...")

    # ─── Create sample users ───
    users = [
        models.User(
            name="Margaret Johnson",
            email="margaret@example.com",
            hashed_password=hash_password("password123"),
            age=75,
            role="elder",
            contact="555-0101",
            location="Downtown, Springfield"
        ),
        models.User(
            name="Robert Williams",
            email="robert@example.com",
            hashed_password=hash_password("password123"),
            age=68,
            role="elder",
            contact="555-0102",
            location="Maple Street, Springfield"
        ),
        models.User(
            name="Alex Chen",
            email="alex@example.com",
            hashed_password=hash_password("password123"),
            age=24,
            role="volunteer",
            contact="555-0201",
            location="Downtown, Springfield"
        ),
        models.User(
            name="Priya Sharma",
            email="priya@example.com",
            hashed_password=hash_password("password123"),
            age=22,
            role="volunteer",
            contact="555-0202",
            location="Riverside, Springfield"
        ),
    ]
    for u in users:
        db.add(u)
    db.commit()
    for u in users:
        db.refresh(u)
    print(f"✅ Created {len(users)} users")

    margaret = users[0]
    robert   = users[1]
    alex     = users[2]

    # ─── Create sample requests ───
    requests = [
        models.HelpRequest(
            title="Grocery Shopping Needed",
            description="I need someone to pick up groceries from the supermarket. I have a list ready. Items include milk, bread, fruits, and vegetables. I am unable to walk long distances due to arthritis.",
            category="grocery",
            location="Downtown, Springfield",
            status="pending",
            elder_id=margaret.id,
        ),
        models.HelpRequest(
            title="Doctor Appointment Escort",
            description="I have a cardiology appointment at Springfield General Hospital on Friday at 10am. I need someone to accompany me and help me get back home safely.",
            category="hospital",
            location="Springfield General Hospital",
            status="accepted",
            elder_id=margaret.id,
            volunteer_id=alex.id,
        ),
        models.HelpRequest(
            title="Medicine Pickup from Pharmacy",
            description="My blood pressure medication is ready at City Pharmacy on Oak Street. I need someone to pick it up and drop it at my home. Cost will be reimbursed.",
            category="medicine",
            location="City Pharmacy, Oak Street",
            status="pending",
            elder_id=robert.id,
        ),
        models.HelpRequest(
            title="Help Reading Mail",
            description="I have accumulated several weeks of mail and need help sorting through it — especially checking for any important bills or notices.",
            category="other",
            location="Maple Street, Springfield",
            status="completed",
            elder_id=robert.id,
            volunteer_id=alex.id,
        ),
    ]
    for r in requests:
        db.add(r)
    db.commit()
    for r in requests:
        db.refresh(r)
    print(f"✅ Created {len(requests)} help requests")

    # ─── Create sample messages ───
    accepted_req = requests[1]
    messages = [
        models.Message(request_id=accepted_req.id, sender_id=margaret.id,
                       content="Hello Alex! Thank you for accepting. The appointment is at 10am Friday."),
        models.Message(request_id=accepted_req.id, sender_id=alex.id,
                       content="Hi Margaret! I will be there at 9:30am to pick you up. Please have your insurance card ready."),
    ]
    for m in messages:
        db.add(m)
    db.commit()
    print(f"✅ Created {len(messages)} messages")

    print("\n🎉 Database seeded successfully!")
    print("\n📋 Test Accounts:")
    print("  Elder:     margaret@example.com  / password123")
    print("  Elder:     robert@example.com    / password123")
    print("  Volunteer: alex@example.com      / password123")
    print("  Volunteer: priya@example.com     / password123")

db.close()
seed()
