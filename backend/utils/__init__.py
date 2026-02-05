"""
Utility module
"""
from .helpers import (
    calculate_average_price,
    safe_divide,
    round_to_half,
    get_item_dimensions,
    validate_dimensions,
    validate_weight,
    cm_to_inch,
    mm_to_inch,
    lbs_to_kg,
    determine_safety_status,
    get_safety_display,
    calculate_surface_area,
    calculate_volume,
    clamp
)

from .exceptions import (
    LumoPackError,
    ValidationError,
    InvalidDimensionsError,
    InvalidWeightError,
    NoProductsError,
    InvalidFluteTypeError,
    InvalidBoxTypeError,
    InvalidQuantityError,
    AIServiceError,
    AINotConfiguredError,
    AIResponseError,
    PricingError,
    MaterialNotFoundError
)

__all__ = [
    # Helpers
    'calculate_average_price',
    'safe_divide',
    'round_to_half',
    'get_item_dimensions',
    'validate_dimensions',
    'validate_weight',
    'cm_to_inch',
    'mm_to_inch',
    'lbs_to_kg',
    'determine_safety_status',
    'get_safety_display',
    'calculate_surface_area',
    'calculate_volume',
    'clamp',
    # Exceptions
    'LumoPackError',
    'ValidationError',
    'InvalidDimensionsError',
    'InvalidWeightError',
    'NoProductsError',
    'InvalidFluteTypeError',
    'InvalidBoxTypeError',
    'InvalidQuantityError',
    'AIServiceError',
    'AINotConfiguredError',
    'AIResponseError',
    'PricingError',
    'MaterialNotFoundError'
]
