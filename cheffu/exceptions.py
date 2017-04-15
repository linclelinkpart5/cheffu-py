class CheffuBaseException(Exception):
    """Base class for all Cheffu exceptions and errors."""


class LeftoverSlotFilters(CheffuBaseException):
    """Raised when no more slot filters are expected, but one or more remain."""


class NoMoreSlotFilters(CheffuBaseException):
    """Raised when slot filters are requested, but no more are available."""
