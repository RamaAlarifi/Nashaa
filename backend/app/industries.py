"""One industry catalogue for validation, discovery and matching.

Stable identifiers are persisted; labels are supplied to the UI by /industries.
Known old labels remain accepted for API compatibility. Unknown legacy values
may be retained unchanged, but cannot be introduced by new writes.
"""
from fastapi import HTTPException

CATALOG = (
    ("agriculture", "Agriculture and Food Production", ("Agriculture",)),
    ("food_beverage", "Food and Beverage", ("Food", "Food and beverage")),
    ("healthcare", "Healthcare and Life Sciences", ("Health", "Health tech", "Health-tech")),
    ("education", "Education and Training", ("Education", "Edtech")),
    ("logistics", "Logistics and Transportation", ("Logistics", "Transportation")),
    ("retail_ecommerce", "Retail and E-commerce", ("Retail", "E-commerce", "Retail tech")),
    ("software_it", "Software and Information Technology", ("Tech", "Technology", "Software", "SaaS", "IT")),
    ("financial_services", "Financial Services", ("Finance", "Fintech")),
    ("manufacturing_packaging", "Manufacturing and Packaging", ("Manufacturing", "Packaging", "Sustainable packaging")),
    ("energy_environment", "Energy and Environmental Services", ("Energy", "Sustainability", "Environment")),
    ("construction_property", "Construction and Real Estate", ("Construction", "Real estate")),
    ("tourism_hospitality", "Tourism and Hospitality", ("Tourism", "Hospitality")),
    ("professional_services", "Professional and Business Services", ("Consulting", "Professional services")),
    ("media_creative", "Media and Creative Industries", ("Media", "Creative industries")),
    ("other", "Other", ()),
)
ALIASES = {text.strip().casefold(): code for code, label, aliases in CATALOG for text in (code, label, *aliases)}
LABELS = {code: label for code, label, _ in CATALOG}


def canonical(value):
    return ALIASES.get(str(value or "").strip().casefold())


def industry_key(value):
    """Legacy unknown categories match only the same legacy text, never Other."""
    raw = str(value or "").strip().casefold()
    return canonical(raw) or ("legacy:" + raw if raw else "")


def validate_industry(value, existing=None, required=False):
    raw = str(value or "").strip()
    code = canonical(raw)
    if code:
        return code
    if not raw and not required:
        return ""
    if raw and existing is not None and raw == str(existing).strip():
        return raw
    raise HTTPException(422, "Choose an industry from the predefined categories.")


def label(value):
    return LABELS.get(canonical(value), str(value or "Not selected"))


def matches_filter(query, value):
    if not query:
        return True
    if canonical(query):
        return industry_key(query) == industry_key(value)
    return query.strip().casefold() in (str(value) + " " + label(value)).casefold()
