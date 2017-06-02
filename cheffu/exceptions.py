class CheffuBaseException(Exception):
    """Base class for all Cheffu exceptions and errors."""


class LeftoverSlotFilters(CheffuBaseException):
    """Raised when no more slot filters are expected, but one or more remain."""


class NoMoreSlotFilters(CheffuBaseException):
    """Raised when slot filters are requested, but no more are available."""


class InvalidSlotFilterPath(CheffuBaseException):
    """Raised when an attempt is made to traverse a Cheffu graph path with an incorrect slot filter."""


class SlotFilterStackException(CheffuBaseException):
    """Base class for all exception raised from slot filter stack manipulation."""


class SlotFilterStackEmpty(SlotFilterStackException):
    """Raised when a pop is performed on a slot filter stack, but it is empty."""


class SlotFilterStackResultMismatch(SlotFilterStackException):
    """Raised when the value popped from a slot filter stack does not match the expected value."""
