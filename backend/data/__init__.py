"""
Data module - ข้อมูลลอน ราคา และวัสดุ
"""
from .flute_specs import (
    FLUTE_SPECS,
    DEFAULT_FLUTE,
    STRONGEST_FLUTE,
    get_flute_spec,
    get_stronger_flute,
    get_weaker_flute,
    is_valid_flute,
    get_all_flute_codes
)

from .pricing import (
    BASE_BOX_PRICES,
    INNER_PRICES,
    COATING_PRICES,
    EMBOSS_PRICES,
    FOIL_PRICES,
    FLUTE_PRICE_MULTIPLIER,
    get_base_price,
    get_flute_multiplier,
    get_inner_price_data,
    get_coating_price_data,
    categorize_foil_type
)

from .materials import (
    PRODUCT_TYPE_MATERIALS,
    WEIGHT_FLUTE_THRESHOLDS,
    get_material_for_product,
    get_material_recommendation,
    get_flute_by_weight,
    get_inner_recommendation,
    is_valid_product_type,
    get_all_product_types
)

__all__ = [
    # Flute specs
    'FLUTE_SPECS',
    'DEFAULT_FLUTE',
    'STRONGEST_FLUTE',
    'get_flute_spec',
    'get_stronger_flute',
    'get_weaker_flute',
    'is_valid_flute',
    'get_all_flute_codes',
    
    # Pricing
    'BASE_BOX_PRICES',
    'INNER_PRICES',
    'COATING_PRICES',
    'EMBOSS_PRICES',
    'FOIL_PRICES',
    'FLUTE_PRICE_MULTIPLIER',
    'get_base_price',
    'get_flute_multiplier',
    'get_inner_price_data',
    'get_coating_price_data',
    'categorize_foil_type',
    
    # Materials
    'PRODUCT_TYPE_MATERIALS',
    'WEIGHT_FLUTE_THRESHOLDS',
    'get_material_for_product',
    'get_material_recommendation',
    'get_flute_by_weight',
    'get_inner_recommendation',
    'is_valid_product_type',
    'get_all_product_types'
]
