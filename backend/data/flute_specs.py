"""
ข้อมูลลอนกระดาษ (Flute Specifications)

Flute Types:
- E: Micro flute - บาง พิมพ์สวย สินค้าเบา
- B: Fine flute - กันกระแทกดี ใช้งานทั่วไป  
- C: Medium flute - มาตรฐาน แข็งแรง
- A: Coarse flute - หนา กันกระแทกดีมาก
- BC: Double wall - 2 ชั้น แข็งแรงสูงสุด
- EB: Double wall - 2 ชั้น พิมพ์ได้ดี
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from config import FLUTE_STRENGTH_ORDER


@dataclass(frozen=True)
class FluteSpec:
    """ข้อมูลลอนกระดาษ"""
    code: str
    name: str
    name_en: str
    ect: float  # Edge Crush Test (kN/m)
    thickness_mm: float
    max_weight_kg: float
    description: str
    use_cases: List[str]
    pros: List[str]
    cons: List[str]
    flutes_per_meter: Optional[int] = None


# ==================== FLUTE SPECIFICATIONS ====================
FLUTE_SPECS: Dict[str, Dict] = {
    "E": {
        "name": "ลอน E (Micro Flute)",
        "name_en": "E-Flute (Micro)",
        "ect": 3.0,
        "thickness": 1.5,
        "flutes_per_meter": 290,
        "description": "บาง เรียบ พิมพ์สวย เหมาะกับสินค้าเบา",
        "max_weight": 3,
        "use_case": "เครื่องสำอาง, อาหารเบา, ของขวัญ, กล่องแสดงสินค้า",
        "pros": ["พิมพ์ได้คมชัด", "ผิวเรียบ", "ประหยัดพื้นที่"],
        "cons": ["กันกระแทกน้อย", "รับน้ำหนักได้จำกัด"]
    },
    "B": {
        "name": "ลอน B",
        "name_en": "B-Flute",
        "ect": 4.0,
        "thickness": 2.5,
        "flutes_per_meter": 150,
        "description": "กันกระแทกดี พิมพ์ได้ ใช้งานทั่วไป",
        "max_weight": 10,
        "use_case": "อาหาร, สินค้าทั่วไป, อิเล็กทรอนิกส์เบา",
        "pros": ["สมดุลระหว่างความแข็งแรงและพิมพ์ได้", "กันกระแทกดี"],
        "cons": ["หนากว่าลอน E"]
    },
    "C": {
        "name": "ลอน C",
        "name_en": "C-Flute",
        "ect": 4.2,
        "thickness": 3.6,
        "flutes_per_meter": 130,
        "description": "มาตรฐานทั่วไป แข็งแรง กันกระแทกดี",
        "max_weight": 20,
        "use_case": "สินค้าทั่วไป, ของใช้ในบ้าน, เฟอร์นิเจอร์เล็ก",
        "pros": ["แข็งแรงมาตรฐาน", "ใช้งานได้หลากหลาย", "ราคาเหมาะสม"],
        "cons": ["พิมพ์ได้แต่ไม่คมเท่าลอน E/B"]
    },
    "A": {
        "name": "ลอน A",
        "name_en": "A-Flute",
        "ect": 5.0,
        "thickness": 4.5,
        "flutes_per_meter": 105,
        "description": "หนา กันกระแทกดีมาก เหมาะกับสินค้าหนัก",
        "max_weight": 30,
        "use_case": "สินค้าหนัก, เครื่องใช้ไฟฟ้า, อุปกรณ์",
        "pros": ["กันกระแทกดีมาก", "รับน้ำหนักได้มาก"],
        "cons": ["หนา ใช้พื้นที่มาก", "พิมพ์ไม่คม"]
    },
    "BC": {
        "name": "ลอน BC (Double Wall)",
        "name_en": "BC-Flute (Double Wall)",
        "ect": 6.5,
        "thickness": 6.0,
        "flutes_per_meter": None,
        "description": "2 ชั้น (B+C) แข็งแรงสูงสุด",
        "max_weight": 50,
        "use_case": "สินค้าหนักมาก, เครื่องจักร, ส่งออก, สินค้าแตกง่าย",
        "pros": ["แข็งแรงสูงสุด", "กันกระแทกดีเยี่ยม", "ซ้อนได้หลายชั้น"],
        "cons": ["หนามาก", "ราคาสูง"]
    },
    "EB": {
        "name": "ลอน EB (Double Wall)",
        "name_en": "EB-Flute (Double Wall)",
        "ect": 5.5,
        "thickness": 4.0,
        "flutes_per_meter": None,
        "description": "2 ชั้น (E+B) แข็งแรงและพิมพ์ได้",
        "max_weight": 25,
        "use_case": "สินค้าหนักปานกลาง ต้องการพิมพ์สวย",
        "pros": ["พิมพ์ได้ดีกว่า BC", "แข็งแรงพอสมควร"],
        "cons": ["แข็งแรงน้อยกว่า BC"]
    }
}

# Default flute for fallback
DEFAULT_FLUTE = "C"
STRONGEST_FLUTE = "BC"


# ==================== HELPER FUNCTIONS ====================
def get_flute_spec(flute_code: str) -> Dict:
    """
    ดึงข้อมูล spec ของลอน
    
    Args:
        flute_code: รหัสลอน (E/B/C/A/BC/EB)
    
    Returns:
        dict ข้อมูลลอน (fallback เป็น C ถ้าไม่พบ)
    """
    return FLUTE_SPECS.get(flute_code, FLUTE_SPECS[DEFAULT_FLUTE])


def get_stronger_flute(current_flute: str) -> str:
    """
    หาลอนที่แข็งแรงกว่า 1 ระดับ
    
    Args:
        current_flute: ลอนปัจจุบัน
    
    Returns:
        รหัสลอนที่แข็งแรงกว่า
    """
    try:
        current_index = FLUTE_STRENGTH_ORDER.index(current_flute)
        next_index = min(current_index + 1, len(FLUTE_STRENGTH_ORDER) - 1)
        return FLUTE_STRENGTH_ORDER[next_index]
    except ValueError:
        return STRONGEST_FLUTE


def get_weaker_flute(current_flute: str) -> str:
    """
    หาลอนที่บางกว่า 1 ระดับ
    
    Args:
        current_flute: ลอนปัจจุบัน
    
    Returns:
        รหัสลอนที่บางกว่า
    """
    try:
        current_index = FLUTE_STRENGTH_ORDER.index(current_flute)
        prev_index = max(current_index - 1, 0)
        return FLUTE_STRENGTH_ORDER[prev_index]
    except ValueError:
        return FLUTE_STRENGTH_ORDER[0]


def is_valid_flute(flute_code: str) -> bool:
    """ตรวจสอบว่าเป็นรหัสลอนที่ถูกต้องหรือไม่"""
    return flute_code in FLUTE_SPECS


def get_all_flute_codes() -> List[str]:
    """ดึงรหัสลอนทั้งหมดเรียงตามความแข็งแรง"""
    return FLUTE_STRENGTH_ORDER.copy()
