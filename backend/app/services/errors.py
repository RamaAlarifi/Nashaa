"""Domain exceptions raised by the service layer.

Routers translate these into HTTP responses with clear, non-technical messages
(project rule 6: show useful error messages instead of technical error text).
"""

from __future__ import annotations


class ServiceError(Exception):
    """Base class for all service-layer errors."""


# Auth
class EmailAlreadyRegistered(ServiceError):
    pass


class InvalidCredentials(ServiceError):
    pass


class ResetTokenNotFound(ServiceError):
    pass


class ResetTokenExpired(ServiceError):
    pass


class ResetTokenUsed(ServiceError):
    pass


# Ideas
class IdeaNotFound(ServiceError):
    pass


class NotOwner(ServiceError):
    pass


class VisibilityBlocked(ServiceError):
    pass


# Assessments
class AssessmentInProgress(ServiceError):
    pass
