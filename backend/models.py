"""
Pydantic models for LumoPack API

แบ่งเป็น:
- Request models (input)
- Response models (output)
- Internal models (data transfer)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

from config import BoxConfig


# ==================== REQUEST MODELS ====================
class BoxAnalysisRequest(BaseModel):
    """Request สำหรับวิเคราะห์ความแข็งแรงกล่อง"""
    length: float = Field(..., gt=0, description="ความยาว (cm)")
    width: float = Field(..., gt=0, description="ความกว้าง (cm)")
    height: float = Field(..., gt=0, description="ความสูง (cm)")
    flute_type: str = Field(..., description="ประเภทลอน (E/B/C/A/BC)")
    weight: float = Field(..., ge=0, description="น้ำหนักสินค้า (kg)")
    
    @field_validator('flute_type')
    @classmethod
    def validate_flute_type(cls, v: str) -> str:
        valid_types = {'E', 'B', 'C', 'A', 'BC', 'EB'}
        if v.upper() not in valid_types:
            raise ValueError(f"Invalid flute type. Must be one of: {valid_types}")
        return v.upper()


class ChatMessage(BaseModel):
    """ข้อความในการสนทนา"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="เนื้อหาข้อความ")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in {'user', 'assistant', 'system'}:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")
        return v


class ChatRequest(BaseModel):
    """Request สำหรับ chat API"""
    message: str = Field(..., min_length=1, description="ข้อความจากผู้ใช้")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="ประวัติการสนทนา"
    )
    current_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="ข้อมูลที่เก็บได้"
    )


class ProductItem(BaseModel):
    """ข้อมูลสินค้าแต่ละชิ้น"""
    name: Optional[str] = Field(None, description="ชื่อสินค้า")
    width: float = Field(
        default=BoxConfig.DEFAULT_WIDTH,
        gt=0,
        description="ความกว้าง (cm)"
    )
    length: float = Field(
        default=BoxConfig.DEFAULT_LENGTH,
        gt=0,
        description="ความยาว (cm)"
    )
    height: float = Field(
        default=BoxConfig.DEFAULT_HEIGHT,
        gt=0,
        description="ความสูง (cm)"
    )
    weight: float = Field(default=0.1, ge=0, description="น้ำหนัก (kg)")
    quantity: int = Field(default=1, ge=1, description="จำนวน")


class ProductInfo(BaseModel):
    """ข้อมูลสินค้าทั้งหมด"""
    name: Optional[str] = Field(None, description="ชื่อสินค้า")
    items: List[ProductItem] = Field(
        default_factory=list,
        description="รายการสินค้า"
    )
    is_fragile: bool = Field(default=False, description="แตกง่ายหรือไม่")
    is_food: bool = Field(default=False, description="เป็นอาหารหรือไม่")
    arrangement: Optional[str] = Field(
        None, 
        description="วิธีจัดเรียง: 'stack', 'side_by_side', 'auto'"
    )


class PriceRequest(BaseModel):
    """Request สำหรับคำนวณราคา"""
    box_design: Dict[str, Any] = Field(..., description="ข้อมูลการออกแบบกล่อง")
    quantity: int = Field(
        default=BoxConfig.MIN_ORDER_QUANTITY,
        ge=1,
        description="จำนวนสั่งผลิต"
    )
    box_type: str = Field(default="RSC", description="ประเภทกล่อง")
    product_type: str = Field(default="สินค้าทั่วไป", description="ประเภทสินค้า")
    inner_type: Optional[str] = Field(None, description="ประเภท Inner")
    coating_type: Optional[str] = Field(None, description="ประเภทเคลือบ")
    has_emboss: bool = Field(default=False, description="มีปั๊มนูนหรือไม่")
    has_emboss_block: bool = Field(default=False, description="มีบล็อกปั๊มนูนแล้วหรือไม่")
    foil_type: Optional[str] = Field(None, description="ประเภทฟอยล์")
    has_foil_block: bool = Field(default=False, description="มีบล็อกฟอยล์แล้วหรือไม่")


class OptimalFluteRequest(BaseModel):
    """Request สำหรับหาลอนที่เหมาะสม"""
    width: float = Field(..., gt=0, description="ความกว้าง (cm)")
    length: float = Field(..., gt=0, description="ความยาว (cm)")
    height: float = Field(..., gt=0, description="ความสูง (cm)")
    weight_kg: float = Field(..., ge=0, description="น้ำหนัก (kg)")
    min_safety_score: float = Field(default=2.0, ge=0, description="Safety score ขั้นต่ำ")


# ==================== RESPONSE MODELS ====================
class ChatResponse(BaseModel):
    """Response จาก chat API"""
    response: str = Field(..., description="ข้อความตอบกลับ")
    extracted_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="ข้อมูลที่สกัดได้"
    )
    quick_replies: List[str] = Field(
        default_factory=list,
        description="ตัวเลือกตอบด่วน"
    )
    box_recommendation: Dict[str, Any] = Field(
        default_factory=dict,
        description="คำแนะนำกล่อง"
    )
    show_heatmap: bool = Field(default=False, description="แสดง heatmap หรือไม่")
    show_quotation: bool = Field(default=False, description="แสดงใบเสนอราคาหรือไม่")
    quotation_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="ข้อมูลใบเสนอราคา"
    )


class StrengthAnalysisResponse(BaseModel):
    """Response จากการวิเคราะห์ความแข็งแรง"""
    max_load_kg: float = Field(..., description="น้ำหนักสูงสุดที่รับได้ (kg)")
    current_load_kg: float = Field(..., description="น้ำหนักที่ต้องรับ (kg)")
    safety_score: float = Field(..., description="คะแนนความปลอดภัย")
    status: str = Field(..., description="สถานะ: SAFE/WARNING/DANGER")
    status_thai: str = Field(..., description="สถานะภาษาไทย")
    color: str = Field(..., description="สี: green/yellow/red")
    recommendation: str = Field(..., description="คำแนะนำ")
    flute_used: str = Field(..., description="ลอนที่ใช้")
    flute_name: str = Field(..., description="ชื่อลอน")
    stack_layers: int = Field(..., description="จำนวนชั้นที่สมมติ")


class HealthResponse(BaseModel):
    """Response จาก health check"""
    status: str = Field(default="healthy")
    ai_configured: bool
    services: Dict[str, str]


# ==================== INTERNAL MODELS ====================
class BoxDimensions(BaseModel):
    """ขนาดกล่อง"""
    width: float
    length: float
    height: float


class BoxSizeResult(BaseModel):
    """ผลลัพธ์การคำนวณขนาดกล่อง"""
    inner_dimensions: BoxDimensions
    recommended_box: BoxDimensions
    total_weight_kg: float
    total_volume_cm3: float
    arrangement: str
    buffer_cm: float
