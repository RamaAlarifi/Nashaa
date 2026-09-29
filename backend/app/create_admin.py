"""Operator-only account provisioning: python -m app.create_admin."""
from getpass import getpass
from app.database import SessionLocal
from app.models.enums import Role
from app.schemas.auth import RegisterIn
from app.services.auth import create_user


def main():
    email = input("Administrator email: ").strip()
    name = input("Display name: ").strip()
    password = getpass("Password (at least 8 characters): ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match.")
    # Reuse public input validation, then assign the operator-only role.
    valid = RegisterIn(email=email, display_name=name, password=password)
    with SessionLocal() as db:
        create_user(db, email=valid.email, display_name=valid.display_name, password=valid.password, role=Role.ADMIN)
    print("Administrator account created.")


if __name__ == "__main__":
    main()
