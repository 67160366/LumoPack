"""
Configuration settings for LumoPack Backend
"""
import os

# ==================== API KEYS ====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ==================== LLM SETTINGS ====================
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048
LLM_BASE_URL = "https://api.groq.com/openai/v1"

# ==================== BOX SETTINGS ====================
DEFAULT_BUFFER_CM = 1.0  # ระยะเผื่อรอบสินค้า
MIN_ORDER_QUANTITY = 500  # จำนวนสั่งขั้นต่ำ
STACK_LAYERS = 4  # จำนวนชั้นที่สมมติวางซ้อน

# ==================== SAFETY THRESHOLDS ====================
SAFETY_DANGER_THRESHOLD = 1.5
SAFETY_WARNING_THRESHOLD = 3.0
