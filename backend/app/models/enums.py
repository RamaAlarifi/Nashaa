"""Enumerations shared across models.

Stored as VARCHAR (``native_enum=False``) to keep schema changes simple
and migration-friendly across the three sprints.
"""

from __future__ import annotations

import enum


class Role(str, enum.Enum):
    BUSINESS_OWNER = "business_owner"
    INNOVATOR = "innovator"
    INVESTOR = "investor"
    ADMIN = "admin"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class VerificationStatus(str, enum.Enum):
    # Sprint 1 keeps this as a stored field; verification flow is Sprint 2.
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class BusinessStage(str, enum.Enum):
    IDEA = "idea"
    VALIDATION = "validation"
    EARLY = "early"
    OPERATING = "operating"
    SCALING = "scaling"


class IdeaVisibility(str, enum.Enum):
    # Sprint 1 minimum visibility choices (US08).
    PRIVATE = "private"            # owner only
    REGISTERED = "registered"      # signed-in users see permitted summary


class ProfileVisibility(str, enum.Enum):
    PUBLIC = "public"
    REGISTERED = "registered"
    PRIVATE = "private"


class ContactPreference(str, enum.Enum):
    DIRECT_MESSAGE = "direct_message"
    CONTACT_REQUEST = "contact_request"


class AssessmentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
