"""Type hints that are not specific to any module."""

import typing as typ
import uuid

# Unique IDs for identifying graph components.
UniqueId = typ.NewType('UniqueId', uuid.UUID)

# Callable that generates new unique IDs.
UniqueIdGen = typ.Callable[[], UniqueId]
