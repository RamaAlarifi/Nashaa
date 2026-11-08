"""Upgrade actual Sprint 1 records and inspect schema compatibility."""
from pathlib import Path
from uuid import uuid4
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text
from app.models.base import Base
from quality.conftest import _BASE_URL


def test_existing_sprint1_data_survives_upgrade():
    name = "nashaa_s2upgrade_" + uuid4().hex
    admin = create_engine(f"{_BASE_URL}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"CREATE DATABASE {name}"))
    engine = create_engine(f"{_BASE_URL}/{name}")
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    config.attributes["database_url"] = f"{_BASE_URL}/{name}"
    uid, pid, iid = uuid4(), uuid4(), uuid4()
    try:
        command.upgrade(config, "0002_sprint1_only")
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO users (id,email,password_hash) VALUES (:id,'upgrade@example.com','fictional-hash')"), {"id": uid})
            conn.execute(text("INSERT INTO profiles (id,user_id,display_name) VALUES (:id,:user,'Fictional retained profile')"), {"id": pid, "user": uid})
            conn.execute(text("INSERT INTO business_ideas (id,owner_id,name,industry) VALUES (:id,:owner,'Retained Sprint 1 idea','Sustainable packaging')"), {"id": iid, "owner": uid})
            conn.execute(text("UPDATE profiles SET role_specific_info=CAST(:info AS jsonb) WHERE id=:id"), {"info":'{"industry":"Packaging"}',"id":pid})
        command.upgrade(config, "head")
        with engine.connect() as conn:
            assert conn.execute(text("SELECT name FROM business_ideas WHERE id=:id"), {"id": iid}).scalar() == "Retained Sprint 1 idea"
            assert conn.execute(text("SELECT verification_status FROM users WHERE id=:id"), {"id": uid}).scalar() == "unverified"
            assert conn.execute(text("SELECT contact_preference FROM profiles WHERE id=:id"), {"id": pid}).scalar() == "contact_request"
            assert conn.execute(text("SELECT industry FROM business_ideas WHERE id=:id"), {"id": iid}).scalar() == "manufacturing_packaging"
            assert conn.execute(text("SELECT industry_detail FROM business_ideas WHERE id=:id"), {"id": iid}).scalar() == "Sustainable packaging"
            assert conn.execute(text("SELECT role_specific_info->>'industry' FROM profiles WHERE id=:id"), {"id": pid}).scalar() == "manufacturing_packaging"
            assert compare_metadata(MigrationContext.configure(conn), Base.metadata) == []
        command.downgrade(config, "0002_sprint1_only")
        command.upgrade(config, "head")
        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM business_ideas")).scalar() == 1
    finally:
        engine.dispose()
        assert name.startswith("nashaa_s2upgrade_")
        with admin.connect() as conn:
            conn.execute(text(f"DROP DATABASE {name}"))
        admin.dispose()
