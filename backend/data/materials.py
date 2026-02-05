"""
ข้อมูลการเลือกวัสดุตามประเภทสินค้า

จับคู่ระหว่าง:
- ประเภทสินค้า → วัสดุที่เหมาะสม
- น้ำหนักสินค้า → ลอนที่แนะนำ
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ==================== DATA STRUCTURES ====================
@dataclass
class MaterialRecommendation:
    """คำแนะนำวัสดุ"""
    material: str
    recommended_flutes: List[str]
    inner_options: Optional[List[str]]
    coating_options: Optional[List[str]]
    reason: str


# ==================== PRODUCT TYPE -> MATERIALS ====================
PRODUCT_TYPE_MATERIALS: Dict[str, Dict[str, Any]] = {
    "สินค้าทั่วไป": {
        "RSC": "ลูกฟูก",
        "Die-cut": "ลูกฟูก",
        "recommended_flute": ["B", "C"],
        "inner": None,
        "coating": None,
        "reason": "ประหยัด แข็งแรง เหมาะกับการขนส่งทั่วไป"
    },
    "Non-food": {
        "RSC": "ลูกฟูก",
        "Die-cut": "ลูกฟูก",
        "recommended_flute": ["B", "C"],
        "inner": ["บับเบิ้ล", "โฟม"],
        "coating": None,
        "reason": "เน้นการปกป้องสินค้า"
    },
    "Food-grade": {
        "RSC": "ลูกฟูก",
        "Die-cut": "กล่องแป้ง",
        "recommended_flute": ["E", "B"],
        "inner": ["กระดาษรองอาหาร"],
        "coating": ["Food-grade Water-based", "Food-grade PE"],
        "reason": "ปลอดภัยสำหรับอาหาร ผ่านมาตรฐาน FDA"
    },
    "เครื่องสำอาง": {
        "RSC": "คราฟท์",
        "Die-cut": "อาร์ต",
        "recommended_flute": ["E"],
        "inner": ["โฟม", "กระดาษฝอย"],
        "coating": ["UV Gloss", "Laminate Matte"],
        "reason": "เน้นความสวยงาม พรีเมียม"
    },
    "อิเล็กทรอนิกส์": {
        "RSC": "ลูกฟูก",
        "Die-cut": "ลูกฟูก",
        "recommended_flute": ["B", "C", "BC"],
        "inner": ["โฟม", "บับเบิ้ล"],
        "coating": None,
        "reason": "กันกระแทกดี ป้องกันความเสียหาย"
    },
    "แตกง่าย": {
        "RSC": "ลูกฟูก",
        "Die-cut": "ลูกฟูก",
        "recommended_flute": ["C", "A", "BC"],
        "inner": ["โฟม", "บับเบิ้ล", "ถุงลม"],
        "coating": None,
        "reason": "เน้นการกันกระแทกสูงสุด"
    }
}

# Default product type for fallback
DEFAULT_PRODUCT_TYPE = "สินค้าทั่วไป"


# ==================== WEIGHT -> FLUTE RECOMMENDATION ====================
WEIGHT_FLUTE_THRESHOLDS = [
    {"max_weight_kg": 1, "flute": "E", "reason": "สินค้าเบามาก"},
    {"max_weight_kg": 3, "flute": "E", "reason": "สินค้าเบา"},
    {"max_weight_kg": 10, "flute": "B", "reason": "สินค้าน้ำหนักปานกลาง"},
    {"max_weight_kg": 20, "flute": "C", "reason": "สินค้าน้ำหนักปานกลาง-หนัก"},
    {"max_weight_kg": 30, "flute": "A", "reason": "สินค้าหนัก"},
    {"max_weight_kg": float('inf'), "flute": "BC", "reason": "สินค้าหนักมาก"}
]


# ==================== INNER RECOMMENDATIONS ====================
INNER_RECOMMENDATIONS = {
    "fragile": "บับเบิ้ล หรือ โฟม",
    "food": "กระดาษรองอาหาร (Food-grade)",
    "electronics": "โฟมกันกระแทก",
    "cosmetics": "กระดาษฝอยสี หรือ โฟม"
}


# ==================== HELPER FUNCTIONS ====================
def get_material_for_product(
    product_type: str, 
    box_type: str = "RSC"
) -> str:
    """
    ดึงวัสดุที่แนะนำตามประเภทสินค้า
    
    Args:
        product_type: ประเภทสินค้า
        box_type: ประเภทกล่อง (RSC/Die-cut)
    
    Returns:
        ชื่อวัสดุที่แนะนำ
    """
    product_info = PRODUCT_TYPE_MATERIALS.get(
        product_type, 
        PRODUCT_TYPE_MATERIALS[DEFAULT_PRODUCT_TYPE]
    )
    return product_info.get(box_type, "ลูกฟูก")


def get_material_recommendation(
    product_type: str, 
    box_type: str = "RSC"
) -> Dict[str, Any]:
    """
    ดึงคำแนะนำวัสดุทั้งหมดตามประเภทสินค้า
    
    Args:
        product_type: ประเภทสินค้า
        box_type: ประเภทกล่อง
    
    Returns:
        dict คำแนะนำทั้งหมด
    """
    product_info = PRODUCT_TYPE_MATERIALS.get(
        product_type, 
        PRODUCT_TYPE_MATERIALS[DEFAULT_PRODUCT_TYPE]
    )
    
    return {
        "material": product_info.get(box_type, "ลูกฟูก"),
        "recommended_flute": product_info.get("recommended_flute", ["C"]),
        "inner": product_info.get("inner"),
        "coating": product_info.get("coating"),
        "reason": product_info.get("reason", "วัสดุมาตรฐาน")
    }


def get_flute_by_weight(weight_kg: float) -> Dict[str, str]:
    """
    หาลอนที่แนะนำจากน้ำหนัก
    
    Args:
        weight_kg: น้ำหนักสินค้า (kg)
    
    Returns:
        {"flute": str, "reason": str}
    """
    for threshold in WEIGHT_FLUTE_THRESHOLDS:
        if weight_kg <= threshold["max_weight_kg"]:
            return {
                "flute": threshold["flute"],
                "reason": threshold["reason"]
            }
    
    # Fallback (shouldn't reach here due to inf)
    return {"flute": "BC", "reason": "สินค้าหนักมาก"}


def get_inner_recommendation(
    is_fragile: bool = False, 
    is_food: bool = False
) -> Optional[str]:
    """
    ดึงคำแนะนำ Inner ตามคุณสมบัติสินค้า
    
    Args:
        is_fragile: สินค้าแตกง่ายหรือไม่
        is_food: เป็นอาหารหรือไม่
    
    Returns:
        คำแนะนำ Inner หรือ None
    """
    if is_fragile:
        return INNER_RECOMMENDATIONS["fragile"]
    elif is_food:
        return INNER_RECOMMENDATIONS["food"]
    return None


def is_valid_product_type(product_type: str) -> bool:
    """ตรวจสอบว่าเป็นประเภทสินค้าที่รองรับหรือไม่"""
    return product_type in PRODUCT_TYPE_MATERIALS


def get_all_product_types() -> List[str]:
    """ดึงประเภทสินค้าทั้งหมด"""
    return list(PRODUCT_TYPE_MATERIALS.keys())
