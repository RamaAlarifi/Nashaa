"""Structured industries and optional business-plan details.

Known labels are normalised; unknown legacy text is preserved. Original owner
specialisations are retained in industry_detail. Back up before downgrade:
new plan details are removed, and canonical categories return to labels.
"""
import json
from alembic import op
import sqlalchemy as sa

revision = "0005_plan_industries"
down_revision = "0004_contact_context"
branch_labels = None
depends_on = None

CATALOG = (('agriculture', 'Agriculture and Food Production', ('Agriculture',)), ('food_beverage', 'Food and Beverage', ('Food', 'Food and beverage')), ('healthcare', 'Healthcare and Life Sciences', ('Health', 'Health tech', 'Health-tech')), ('education', 'Education and Training', ('Education', 'Edtech')), ('logistics', 'Logistics and Transportation', ('Logistics', 'Transportation')), ('retail_ecommerce', 'Retail and E-commerce', ('Retail', 'E-commerce', 'Retail tech')), ('software_it', 'Software and Information Technology', ('Tech', 'Technology', 'Software', 'SaaS', 'IT')), ('financial_services', 'Financial Services', ('Finance', 'Fintech')), ('manufacturing_packaging', 'Manufacturing and Packaging', ('Manufacturing', 'Packaging', 'Sustainable packaging')), ('energy_environment', 'Energy and Environmental Services', ('Energy', 'Sustainability', 'Environment')), ('construction_property', 'Construction and Real Estate', ('Construction', 'Real estate')), ('tourism_hospitality', 'Tourism and Hospitality', ('Tourism', 'Hospitality')), ('professional_services', 'Professional and Business Services', ('Consulting', 'Professional services')), ('media_creative', 'Media and Creative Industries', ('Media', 'Creative industries')), ('other', 'Other', ()))
FIELDS = ("industry_detail", "business_model", "value_proposition", "revenue_model", "market_opportunity", "competition", "cost_structure", "growth_strategy")
ALIASES = {s.strip().casefold(): code for code, label, aliases in CATALOG for s in (code, label, *aliases)}
LABELS = {code: label for code, label, _ in CATALOG}


def convert(value, reverse=False):
    if not isinstance(value, str):
        return value
    return LABELS.get(value, value) if reverse else ALIASES.get(value.strip().casefold(), value)


def normalise(reverse=False):
    conn = op.get_bind()
    for table in ("business_ideas", "challenges", "investment_history"):
        for row in conn.execute(sa.text(f"SELECT id,industry FROM {table}")).mappings().all():
            value=convert(row["industry"],reverse)
            if value != row["industry"]:
                if table == "business_ideas" and not reverse:
                    conn.execute(sa.text("UPDATE business_ideas SET industry_detail=:old WHERE id=:id AND industry_detail=''"), {"old":row["industry"],"id":row["id"]})
                conn.execute(sa.text(f"UPDATE {table} SET industry=:value WHERE id=:id"), {"value":value,"id":row["id"]})
    for row in conn.execute(sa.text("SELECT id,role_specific_info FROM profiles")).mappings().all():
        info=dict(row["role_specific_info"] or {})
        if "industry" not in info:
            continue
        old=info["industry"]; info["industry"]=convert(old,reverse)
        if not reverse and old != info["industry"]:
            info.setdefault("industry_detail",old)
        if reverse:
            info.pop("industry_detail",None)
        conn.execute(sa.text("UPDATE profiles SET role_specific_info=CAST(:info AS jsonb) WHERE id=:id"), {"info":json.dumps(info),"id":row["id"]})
    for row in conn.execute(sa.text("SELECT id,industries FROM investor_preferences")).mappings().all():
        values=list(dict.fromkeys(convert(v,reverse) for v in row["industries"]))
        conn.execute(sa.text("UPDATE investor_preferences SET industries=CAST(:values AS jsonb) WHERE id=:id"), {"values":json.dumps(values),"id":row["id"]})


def upgrade():
    for field in FIELDS:
        op.add_column("business_ideas", sa.Column(field,sa.Text(),nullable=False,server_default=""))
    normalise()


def downgrade():
    normalise(reverse=True)
    for field in reversed(FIELDS):
        op.drop_column("business_ideas",field)
