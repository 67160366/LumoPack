"""
ข้อมูลการเลือกวัสดุตามประเภทสินค้า
"""

# ==================== วัสดุที่แนะนำตามประเภทสินค้า ====================
PRODUCT_TYPE_MATERIALS = {
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

# ==================== แนะนำลอนตามน้ำหนัก ====================
WEIGHT_FLUTE_RECOMMENDATION = [
    {"max_weight": 1, "flute": "E", "reason": "สินค้าเบามาก"},
    {"max_weight": 3, "flute": "E", "reason": "สินค้าเบา"},
    {"max_weight": 10, "flute": "B", "reason": "สินค้าน้ำหนักปานกลาง"},
    {"max_weight": 20, "flute": "C", "reason": "สินค้าน้ำหนักปานกลาง-หนัก"},
    {"max_weight": 30, "flute": "A", "reason": "สินค้าหนัก"},
    {"max_weight": float('inf'), "flute": "BC", "reason": "สินค้าหนักมาก"}
]

def get_recommended_flute_by_weight(weight_kg: float) -> dict:
    """หาลอนที่แนะนำจากน้ำหนัก"""
    for rec in WEIGHT_FLUTE_RECOMMENDATION:
        if weight_kg <= rec["max_weight"]:
            return {"flute": rec["flute"], "reason": rec["reason"]}
    return {"flute": "BC", "reason": "สินค้าหนักมาก"}

def get_material_recommendation(product_type: str, box_type: str = "RSC") -> dict:
    """หาวัสดุที่แนะนำตามประเภทสินค้า"""
    if product_type in PRODUCT_TYPE_MATERIALS:
        info = PRODUCT_TYPE_MATERIALS[product_type]
        return {
            "material": info.get(box_type, "ลูกฟูก"),
            "recommended_flute": info.get("recommended_flute", ["C"]),
            "inner": info.get("inner"),
            "coating": info.get("coating"),
            "reason": info.get("reason")
        }
    return {
        "material": "ลูกฟูก",
        "recommended_flute": ["C"],
        "inner": None,
        "coating": None,
        "reason": "วัสดุมาตรฐาน"
    }
