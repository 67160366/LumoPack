"""
ข้อมูลราคากล่องและวัสดุ

ราคาพื้นฐานสำหรับกล่องขนาดมาตรฐาน 10x10x10 ซม.
จะถูกคูณด้วย factor ตามขนาดจริง
"""
from typing import Dict, Any
from dataclasses import dataclass


# ==================== PRICE DATA STRUCTURES ====================
@dataclass
class PriceRange:
    """ช่วงราคา min-max"""
    min: float
    max: float
    
    @property
    def average(self) -> float:
        """คำนวณราคาเฉลี่ย"""
        return (self.min + self.max) / 2


# ==================== BOX BASE PRICES ====================
# ราคาเป็นบาท สำหรับกล่องขนาด 10x10x10 ซม.
BASE_BOX_PRICES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "RSC": {
        "ลูกฟูก": {
            "cost": 3.378,
            "paper_cost": 22,
            "description": "กล่องลูกฟูกมาตรฐาน"
        },
        "คราฟท์": {
            "cost": 1.596,
            "paper_cost": 30,
            "description": "กล่องกระดาษคราฟท์"
        },
    },
    "Die-cut": {
        "ลูกฟูก": {
            "cost": 3.57,
            "paper_cost": 22,
            "description": "กล่องไดคัทลูกฟูก"
        },
        "จั่วปัง": {
            "cost": 8.6,
            "paper_cost": 40,
            "description": "กล่องจั่วปัง พรีเมียม"
        },
        "อาร์ต": {
            "cost": 6.67,
            "paper_cost": 200,
            "description": "กล่องกระดาษอาร์ต พิมพ์สี่สี"
        },
        "กล่องแป้ง": {
            "cost": 1.93,
            "paper_cost": 40,
            "description": "กล่องแป้ง Food-grade"
        },
    }
}


# ==================== INNER PRICES ====================
# ราคาเป็นบาท/กก. + น้ำหนักต่อกล่องมาตรฐาน
INNER_PRICES: Dict[str, Dict[str, Any]] = {
    "กระดาษฝอย": {
        "min": 120,
        "max": 170,
        "weight_per_box": 0.02,
        "description": "กระดาษฝอยรอง กันกระแทก"
    },
    "บับเบิ้ล": {
        "min": 60,
        "max": 90,
        "weight_per_box": 0.015,
        "description": "แผ่นบับเบิ้ลกันกระแทก"
    },
    "ถุงลม": {
        "min": 120,
        "max": 200,
        "weight_per_box": 0.01,
        "description": "ถุงลมกันกระแทก"
    },
    "โฟม": {
        "min": 80,
        "max": 150,
        "weight_per_box": 0.025,
        "description": "โฟมกันกระแทก"
    },
    "กระดาษลูกฟูก": {
        "min": 50,
        "max": 80,
        "weight_per_box": 0.03,
        "description": "แผ่นกระดาษลูกฟูกรอง"
    }
}


# ==================== COATING PRICES ====================
# ราคาเป็นบาท/กล่องมาตรฐาน
COATING_PRICES: Dict[str, Dict[str, Any]] = {
    # กันชื้น (Moisture Resistant)
    "AQ Coating": {
        "min": 0.48,
        "max": 1.2,
        "type": "moisture",
        "description": "Acrylic polymer - ต้นทุนต่ำ"
    },
    "PE Coating": {
        "min": 1.2,
        "max": 3.6,
        "type": "moisture",
        "description": "Polyethylene - กันชื้นดี"
    },
    "Wax Coating": {
        "min": 1.2,
        "max": 3.0,
        "type": "moisture",
        "description": "Paraffin wax - กันชื้นดี"
    },
    
    # Food-grade
    "Food-grade Water-based": {
        "min": 0.8,
        "max": 1.5,
        "type": "food",
        "description": "เคลือบ Food-grade น้ำ"
    },
    "Food-grade PE": {
        "min": 1.2,
        "max": 2.0,
        "type": "food",
        "description": "เคลือบ Food-grade PE"
    },
    
    # เคลือบเงา (Gloss)
    "Gloss AQ": {
        "min": 0.6,
        "max": 1.2,
        "type": "gloss",
        "description": "เคลือบเงา AQ"
    },
    "UV Gloss": {
        "min": 1.2,
        "max": 2.4,
        "type": "gloss",
        "description": "เคลือบเงา UV"
    },
    
    # เคลือบด้าน (Matte)
    "UV Matte": {
        "min": 4.0,
        "max": 8.0,
        "type": "matte",
        "description": "เคลือบด้าน UV"
    },
    "Laminate Matte": {
        "min": 6.0,
        "max": 12.0,
        "type": "matte",
        "description": "ลามิเนตด้าน"
    }
}


# ==================== EMBOSS PRICES ====================
EMBOSS_PRICES: Dict[str, Any] = {
    "block": {
        "min": 800,
        "max": 1500,
        "unit": "บาท/บล็อก"
    },
    "per_box": 2.0  # บาท/กล่อง
}


# ==================== FOIL PRICES ====================
FOIL_PRICES: Dict[str, Dict[str, Any]] = {
    "block": {
        "standard": {"min": 1000, "max": 2000},
        "detailed": {"min": 2000, "max": 3500},
        "emboss_foil": {"min": 2500, "max": 5000}
    },
    "per_box": {
        "1_color": {"min": 2, "max": 5},
        "large": {"min": 5, "max": 10},
        "emboss_foil": {"min": 6, "max": 12}
    }
}

# Foil type keywords for categorization
FOIL_TYPE_KEYWORDS = {
    "emboss": ["นูน"],
    "detailed": ["ละเอียด", "ใหญ่"]
}


# ==================== FLUTE PRICE MULTIPLIER ====================
# ตัวคูณราคาตามลอน (ลอนหนากว่า = แพงกว่า)
FLUTE_PRICE_MULTIPLIER: Dict[str, float] = {
    "E": 0.9,
    "B": 1.0,
    "C": 1.1,
    "A": 1.2,
    "EB": 1.3,
    "BC": 1.5
}

# Default multiplier for unknown flute types
DEFAULT_FLUTE_MULTIPLIER = 1.0


# ==================== HELPER FUNCTIONS ====================
def get_base_price(box_type: str, material: str) -> float:
    """
    ดึงราคาพื้นฐานของกล่อง
    
    Args:
        box_type: ประเภทกล่อง (RSC/Die-cut)
        material: วัสดุ
    
    Returns:
        ราคาพื้นฐาน (บาท)
    """
    box_prices = BASE_BOX_PRICES.get(box_type, BASE_BOX_PRICES["RSC"])
    material_data = box_prices.get(material)
    
    if material_data:
        return material_data["cost"]
    
    # Fallback: หา material แรกที่มี
    first_material = next(iter(box_prices.values()), {"cost": 3.5})
    return first_material["cost"]


def get_flute_multiplier(flute_type: str) -> float:
    """ดึงตัวคูณราคาตามลอน"""
    return FLUTE_PRICE_MULTIPLIER.get(flute_type, DEFAULT_FLUTE_MULTIPLIER)


def get_inner_price_data(inner_type: str) -> Dict[str, Any]:
    """ดึงข้อมูลราคา Inner"""
    return INNER_PRICES.get(inner_type, {})


def get_coating_price_data(coating_type: str) -> Dict[str, Any]:
    """ดึงข้อมูลราคาเคลือบ"""
    return COATING_PRICES.get(coating_type, {})


def categorize_foil_type(foil_type: str) -> str:
    """
    จำแนกประเภทฟอยล์จากชื่อ
    
    Returns:
        "emboss_foil" | "detailed" | "standard"
    """
    if not foil_type:
        return "standard"
    
    for category, keywords in FOIL_TYPE_KEYWORDS.items():
        if any(keyword in foil_type for keyword in keywords):
            return "emboss_foil" if category == "emboss" else "detailed"
    
    return "standard"
