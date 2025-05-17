import os
import sys
from app import create_app
from app.extensions import db
from app.core.models import Volunteer

app = create_app()

with app.app_context():
    email = input("Volunteer email: ").strip()
    user = Volunteer.query.filter_by(email=email).first()

    if not user:
        print("❌ Volunteer not found.")
        sys.exit(1)

    new_pw = input("New password: ").strip()
    user.set_password(new_pw)
    db.session.commit()
    print(f"✅ Password set for {user.name}")
