"""
Utility functions ที่ใช้ร่วมกันทั้งโปรเจค
"""
from typing import Dict, Any, Optional, Tuple
import math

from config import (
    BoxConfig, 
    UnitConversion, 
    SafetyConfig,
    PricingConfig,
    SafetyStatus
)


# ==================== PRICE HELPERS ====================
def calculate_average_price(price_data: Dict[str, float]) -> float:
    """
    คำนวณราคาเฉลี่ยจาก min-max
    
    Args:
        price_data: {"min": float, "max": float}
    
    Returns:
        ราคาเฉลี่ย
    """
    min_price = price_data.get("min", 0)
    max_price = price_data.get("max", 0)
    return (min_price + max_price) / 2


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    หารอย่างปลอดภัย ป้องกัน division by zero
    
    Args:
        numerator: ตัวตั้ง
        denominator: ตัวหาร
        default: ค่า default ถ้าหารไม่ได้
    
    Returns:
        ผลหาร หรือ default
    """
    if denominator == 0:
        return default
    return numerator / denominator


# ==================== DIMENSION HELPERS ====================
def round_to_half(value: float) -> float:
    """
    ปัดเลขให้เป็นทวีคูณของ 0.5
    
    Args:
        value: ค่าที่ต้องการปัด
    
    Returns:
        ค่าที่ปัดแล้ว
    
    Example:
        round_to_half(3.3) -> 3.5
        round_to_half(3.7) -> 4.0
    """
    return math.ceil(value * 2) / 2


def get_item_dimensions(
    item: Dict[str, Any]
) -> Tuple[float, float, float, float, int]:
    """
    ดึงข้อมูล dimensions จาก item dict อย่างปลอดภัย
    
    Args:
        item: dict ข้อมูลสินค้า
    
    Returns:
        (width, length, height, weight, quantity)
    """
    return (
        item.get("width", BoxConfig.DEFAULT_WIDTH),
        item.get("length", BoxConfig.DEFAULT_LENGTH),
        item.get("height", BoxConfig.DEFAULT_HEIGHT),
        item.get("weight", 0.0),
        item.get("quantity", 1)
    )


def validate_dimensions(
    width: float, 
    length: float, 
    height: float
) -> bool:
    """
    ตรวจสอบว่า dimensions ถูกต้องหรือไม่
    
    Args:
        width, length, height: ขนาด (cm)
    
    Returns:
        True ถ้าถูกต้อง
    """
    return all(d > 0 for d in [width, length, height])


def validate_weight(weight: float) -> bool:
    """ตรวจสอบว่าน้ำหนักถูกต้องหรือไม่"""
    return weight >= 0


# ==================== UNIT CONVERSION HELPERS ====================
def cm_to_inch(cm: float) -> float:
    """แปลง centimeter เป็น inch"""
    return cm * UnitConversion.CM_TO_INCH


def mm_to_inch(mm: float) -> float:
    """แปลง millimeter เป็น inch"""
    return mm * UnitConversion.MM_TO_INCH


def lbs_to_kg(lbs: float) -> float:
    """แปลง pounds เป็น kilograms"""
    return lbs * UnitConversion.LBS_TO_KG


def kg_to_lbs(kg: float) -> float:
    """แปลง kilograms เป็น pounds"""
    return kg * UnitConversion.KG_TO_LBS


# ==================== SAFETY STATUS HELPERS ====================
def determine_safety_status(safety_score: float) -> SafetyStatus:
    """
    กำหนดสถานะความปลอดภัยจาก safety score
    
    Args:
        safety_score: คะแนนความปลอดภัย
    
    Returns:
        SafetyStatus enum
    """
    if safety_score < SafetyConfig.DANGER_THRESHOLD:
        return SafetyStatus.DANGER
    elif safety_score < SafetyConfig.WARNING_THRESHOLD:
        return SafetyStatus.WARNING
    return SafetyStatus.SAFE


def get_safety_display(status: SafetyStatus) -> Dict[str, str]:
    """
    ดึงข้อมูลการแสดงผลตาม safety status
    
    Args:
        status: SafetyStatus enum
    
    Returns:
        {"thai": str, "color": str, "emoji": str}
    """
    status_display = {
        SafetyStatus.SAFE: {
            "thai": "ปลอดภัย",
            "color": "green",
            "emoji": "✅"
        },
        SafetyStatus.WARNING: {
            "thai": "ควรระวัง",
            "color": "yellow", 
            "emoji": "⚠️"
        },
        SafetyStatus.DANGER: {
            "thai": "อันตราย",
            "color": "red",
            "emoji": "❌"
        }
    }
    return status_display.get(status, status_display[SafetyStatus.DANGER])


# ==================== CALCULATION HELPERS ====================
def calculate_surface_area(
    width: float, 
    length: float, 
    height: float
) -> float:
    """
    คำนวณพื้นที่ผิวกล่อง 6 ด้าน
    
    Formula: 2 * (WL + WH + LH)
    
    Args:
        width, length, height: ขนาดกล่อง (cm)
    
    Returns:
        พื้นที่ผิว (cm²)
    """
    return 2 * ((width * length) + (width * height) + (length * height))


def calculate_volume(
    width: float, 
    length: float, 
    height: float
) -> float:
    """คำนวณปริมาตร (cm³)"""
    return width * length * height


def clamp(value: float, min_val: float, max_val: float) -> float:
    """จำกัดค่าให้อยู่ในช่วง [min_val, max_val]"""
    return max(min_val, min(max_val, value))
