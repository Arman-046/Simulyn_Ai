# Compatibility re-export layer.
# Centralizes all schema imports from backend.schemas.pydantic_schemas
# so existing code using `from .models import X` continues to work.

from .schemas.pydantic_schemas import *
