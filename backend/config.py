"""
Configuration settings for LumoPack Backend
รวม constants ทั้งหมดไว้ที่เดียว
"""
import os
from enum import Enum
from typing import List


# ==================== API KEYS ====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


# ==================== LLM SETTINGS ====================
class LLMConfig:
    MODEL = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    BASE_URL = "https://api.groq.com/openai/v1"


# ==================== BOX SETTINGS ====================
class BoxConfig:
    DEFAULT_BUFFER_CM = 1.0
    MIN_ORDER_QUANTITY = 500
    STACK_LAYERS = 4
    
    # Default dimensions (cm)
    DEFAULT_WIDTH = 10.0
    DEFAULT_LENGTH = 10.0
    DEFAULT_HEIGHT = 5.0
    
    # Rounding precision
    DIMENSION_PRECISION = 0.5  # ปัดเป็นทวีคูณของ 0.5


# ==================== SAFETY THRESHOLDS ====================
class SafetyConfig:
    DANGER_THRESHOLD = 1.5
    WARNING_THRESHOLD = 3.0
    MIN_ACCEPTABLE_SCORE = 2.0
    MAX_SAFETY_SCORE = 100.0


# ==================== UNIT CONVERSION ====================
class UnitConversion:
    """ค่าคงที่สำหรับแปลงหน่วย"""
    CM_TO_INCH = 0.3937007874
    MM_TO_INCH = 0.03937007874
    LBS_TO_KG = 0.45359237
    KG_TO_LBS = 2.20462262


# ==================== MCKEE FORMULA ====================
class McKeeConfig:
    """ค่าคงที่สำหรับสูตร McKee"""
    COEFFICIENT = 5.87  # McKee constant
    
    # Heatmap grid settings
    GRID_SIZE = 3
    CENTER_RISK_FACTOR = 1.0
    EDGE_RISK_FACTOR = 0.8
    CORNER_RISK_FACTOR = 0.6
    RISK_DIVISOR = 5.0


# ==================== PRICING ====================
class PricingConfig:
    BASE_SURFACE_AREA = 600.0  # พื้นที่ผิวกล่อง 10x10x10 cm
    RSC_PRODUCTION_FACTOR = 1.1
    DIECUT_PRODUCTION_FACTOR = 1.5
    MIN_FACTOR = 1.0
    DEFAULT_PRICE = 3.5  # Fallback price
    
    # Fragile factor
    FRAGILE_WEIGHT_MULTIPLIER = 1.5


# ==================== ENUMS ====================
class FluteType(str, Enum):
    """ประเภทลอนกระดาษ"""
    E = "E"
    B = "B"
    C = "C"
    A = "A"
    BC = "BC"
    EB = "EB"


class BoxType(str, Enum):
    """ประเภทกล่อง"""
    RSC = "RSC"
    DIE_CUT = "Die-cut"


class SafetyStatus(str, Enum):
    """สถานะความปลอดภัย"""
    SAFE = "SAFE"
    WARNING = "WARNING"
    DANGER = "DANGER"


class RiskLevel(str, Enum):
    """ระดับความเสี่ยง"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ==================== FLUTE ORDER ====================
FLUTE_STRENGTH_ORDER: List[str] = ["E", "B", "C", "A", "EB", "BC"]
