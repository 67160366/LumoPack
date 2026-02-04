"""
Pydantic models for LumoPack API
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class BoxDesign(BaseModel):
    """ข้อมูลสำหรับวิเคราะห์กล่อง"""
    length: float
    width: float
    height: float
    flute_type: str
    weight: float


class ProductItem(BaseModel):
    """ข้อมูลสินค้าแต่ละชิ้น"""
    name: Optional[str] = None
    width: float  # cm
    length: float  # cm
    height: float  # cm
    weight: float  # kg
    quantity: int = 1


class ProductInfo(BaseModel):
    """ข้อมูลสินค้าทั้งหมด"""
    name: Optional[str] = None
    items: List[ProductItem] = []
    is_fragile: bool = False
    is_food: bool = False
    arrangement: Optional[str] = None  # "stack" or "side_by_side"


class ChatMessage(BaseModel):
    """ข้อความในการสนทนา"""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request สำหรับ chat API"""
    message: str
    conversation_history: List[ChatMessage] = []
    current_requirements: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response จาก chat API"""
    response: str
    extracted_data: Dict[str, Any] = {}
    quick_replies: List[str] = []
    box_recommendation: Dict[str, Any] = {}
    show_heatmap: bool = False
    show_quotation: bool = False
    quotation_data: Dict[str, Any] = {}


class BoxSizeResult(BaseModel):
    """ผลลัพธ์การคำนวณขนาดกล่อง"""
    inner_dimensions: Dict[str, float]
    recommended_box: Dict[str, float]
    total_weight_kg: float
    total_volume_cm3: float


class StrengthAnalysis(BaseModel):
    """ผลการวิเคราะห์ความแข็งแรง"""
    max_load_kg: float
    current_load_kg: float
    safety_score: float
    status: str  # "SAFE", "WARNING", "DANGER"
    status_thai: str
    recommendation: str
    flute_used: str
    flute_name: str


class PriceResult(BaseModel):
    """ผลการคำนวณราคา"""
    box_type: str
    material: str
    dimensions: Dict[str, float]
    quantity: int
    factor: float
    price_per_box: float
    total_price: float
