from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import os
import json
import re

app = FastAPI()

# อนุญาตให้หน้าเว็บ (Frontend) คุยกับหลังบ้านได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIG GEMINI ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ใช้ google-genai library ตัวใหม่
from google import genai

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== MODELS ====================
class BoxDesign(BaseModel):
    length: float  # cm
    width: float   # cm
    height: float  # cm
    flute_type: str # A, B, C, E
    weight: float   # น้ำหนักสินค้า (kg)

class ChatMessage(BaseModel):
    role: str  # "user" หรือ "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    current_requirements: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    extracted_data: Dict[str, Any] = {}
    current_step: int = 1
    is_checkpoint: bool = False
    show_quotation: bool = False
    quotation_data: Dict[str, Any] = {}

# ==================== FLUTE SPECS ====================
FLUTE_SPECS = {
    "A": {"ect": 5.0, "thickness": 4.5},
    "B": {"ect": 4.0, "thickness": 2.5},
    "C": {"ect": 4.2, "thickness": 3.6},
    "E": {"ect": 3.0, "thickness": 1.5},
}

# ==================== PRICING DATA ====================
BASE_PRICES = {
    "RSC": {
        "ลูกฟูก": {"cost": 3.378, "paper_cost": 22, "thickness": 0.25, "density": 0.6, "labor": 1.2, "factor": 1.1},
        "คราฟท์": {"cost": 1.596, "paper_cost": 30, "thickness": 0.025, "density": 0.8, "labor": 1.2, "factor": 1.1},
    },
    "Die-cut": {
        "ลูกฟูก": {"cost": 3.57, "paper_cost": 22, "thickness": 0.25, "density": 0.6, "labor": 0.6, "factor": 1.5},
        "จั่วปัง": {"cost": 8.6, "paper_cost": 40, "thickness": 0.25, "density": 0.9, "labor": 0.6, "factor": 1.5},
        "อาร์ต": {"cost": 6.67, "paper_cost": 200, "thickness": 0.0375, "density": 0.9, "labor": 0.6, "factor": 1.5},
        "กล่องแป้ง": {"cost": 1.93, "paper_cost": 40, "thickness": 0.04375, "density": 0.85, "labor": 0.6, "factor": 1.5},
    }
}

INNER_PRICES = {
    "กระดาษฝอย": {"min": 1.5, "max": 2.5},
    "บับเบิ้ล": {"min": 0.8, "max": 1.2},
    "ถุงลม": {"min": 1.5, "max": 2.5},
}

COATING_PRICES = {
    "AQ Coating": {"min": 0.48, "max": 1.2},
    "PE Coating": {"min": 1.2, "max": 3.6},
    "Wax Coating": {"min": 1.2, "max": 3.0},
    "Bio Coating": {"min": 2.0, "max": 5.0},
}

GLOSS_PRICES = {
    "Gloss AQ": {"min": 0.6, "max": 1.2},
    "UV Gloss": {"min": 1.2, "max": 2.4},
    "OPP Gloss Film": {"min": 1.8, "max": 3.6},
}

MATTE_PRICES = {
    "UV ด้าน": {"min": 4, "max": 8},
    "ลามิเนตด้าน": {"min": 6, "max": 12},
    "วานิชด้าน": {"min": 8, "max": 15},
}

EMBOSS_PRICES = {
    "block_cost": {"min": 800, "max": 1500},
    "per_box": 2,
}

FOIL_PRICES = {
    "ฟอยล์ธรรมดา": {"block_min": 1000, "block_max": 2000, "per_box_min": 2, "per_box_max": 5},
    "ฟอยล์ละเอียด": {"block_min": 2000, "block_max": 3500, "per_box_min": 5, "per_box_max": 10},
    "ฟอยล์+นูน": {"block_min": 2500, "block_max": 5000, "per_box_min": 6, "per_box_max": 12},
}

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """คุณคือ "ลูโม่" (Lumo) ผู้ช่วย AI วิศวกรบรรจุภัณฑ์ของ LumoPack 
คุณมีหน้าที่ช่วยลูกค้าออกแบบกล่องบรรจุภัณฑ์ที่เหมาะสมกับความต้องการ

## บุคลิก
- พูดจาเป็นมิตร สุภาพ ใช้ภาษาไทยที่เข้าใจง่าย
- ใช้ emoji เล็กน้อยเพื่อความน่ารัก แต่ไม่มากเกินไป
- ตอบกระชับ ได้ใจความ ไม่ยืดเยื้อ
- ถ้าลูกค้าตอบแบบอิสระ ให้พยายามเข้าใจและสกัดข้อมูลออกมา

## ขั้นตอนการทำงาน (ทำตามลำดับ)

### Phase 1: เก็บข้อมูลโครงสร้าง
1. **ทักทาย** - แนะนำตัวและบอกว่าจะช่วยออกแบบกล่องให้
2. **ประเภทสินค้า** (บังคับ) - ถามว่าจะใส่อะไร: สินค้าทั่วไป / Non-food / Food-grade / เครื่องสำอาง
3. **ประเภทกล่อง** (บังคับ) - RSC (มาตรฐาน) หรือ Die-cut (เน้นโชว์แบรนด์)
4. **Inner** (Optional สำหรับ Die-cut) - แผ่นกันกระแทก / เคลือบกันชื้น / Food-grade coating
5. **ขนาดกล่อง** (บังคับ) - กว้าง x ยาว x สูง (ซม.)
6. **จำนวนผลิต** (บังคับ) - ขั้นต่ำ 500 ชิ้น

### Checkpoint 1: สรุปข้อมูลโครงสร้าง
- แสดงข้อมูลที่ได้รับทั้งหมด
- ขอยืนยันจากลูกค้า
- ถ้าลูกค้าขอแก้ไข/เพิ่ม ให้ทำตามแล้วสรุปใหม่

### Phase 2: เก็บข้อมูลการออกแบบ
7. **Mood & Tone** (Optional) - สดใส / เรียบหรู / มินิมอล / สนุก / พรีเมียม
8. **Logo & Font** (Optional) - มีโลโก้หรือไม่ ถ้ามีให้แนบมา และถามตำแหน่งที่ต้องการ
9. **ลูกเล่นพิเศษ** (Optional) - เคลือบเงา / เคลือบด้าน / ปั๊มนูน / ปั๊มจม / ปั๊มฟอยล์

### Checkpoint 2: สรุปข้อมูลการออกแบบ
- แสดงข้อมูลทั้งหมด (โครงสร้าง + ออกแบบ)
- ขอยืนยันจากลูกค้า

### Phase 3: ออกใบเสนอราคา
10. **แสดง Mockup** - บอกลักษณะกล่องที่จะได้
11. **แสดงใบเสนอราคา** - แยกราคาตามรายการ + ราคารวม
12. **ยืนยันคำสั่งซื้อ** - ถามยืนยัน
13. **จบการสนทนา** - ขอบคุณลูกค้า

## การตอบกลับ
ทุกครั้งที่ตอบ ให้ส่ง JSON ในรูปแบบนี้ท้ายข้อความ (ซ่อนไว้ในแท็ก):
<extracted_data>
{
  "product_type": "สินค้าทั่วไป/Non-food/Food-grade/เครื่องสำอาง หรือ null",
  "box_type": "RSC/Die-cut หรือ null",
  "inner": "ประเภท inner หรือ null",
  "dimensions": {"width": null, "length": null, "height": null},
  "quantity": null,
  "mood_tone": "สไตล์ หรือ null",
  "logo": {"has_logo": false, "position": null},
  "special_features": [],
  "current_step": 1,
  "is_checkpoint": false,
  "confirmed_structure": false,
  "confirmed_design": false,
  "confirmed_order": false
}
</extracted_data>

## กฎสำคัญ
- ถามทีละหัวข้อ ไม่ถามรวมกัน
- ถ้าลูกค้าบอก "ไม่" หรือ "ข้าม" ในหัวข้อ Optional ให้ข้ามไปขั้นตอนถัดไป
- ถ้าลูกค้าให้ข้อมูลหลายอย่างในคราวเดียว ให้สกัดข้อมูลทั้งหมดแล้วถามข้อที่ยังขาด
- เมื่อถึง Checkpoint ต้องสรุปข้อมูลให้ครบถ้วนก่อนขอยืนยัน
- ขนาดกล่องต้องเป็นตัวเลขในหน่วยเซนติเมตร
"""

# ==================== HELPER FUNCTIONS ====================
def calculate_surface_area(width: float, length: float, height: float) -> float:
    return 2 * ((width * length) + (width * height) + (length * height))

def calculate_factor(width: float, length: float, height: float, box_type: str) -> float:
    base_area = 600
    production_factor = 1.1 if box_type == "RSC" else 1.5
    base_area_with_factor = base_area * production_factor
    new_area = calculate_surface_area(width, length, height) * production_factor
    return new_area / base_area_with_factor

def calculate_box_price(width: float, length: float, height: float, 
                        box_type: str, material: str, quantity: int) -> Dict[str, Any]:
    factor = calculate_factor(width, length, height, box_type)
    
    if box_type == "RSC":
        base_price = BASE_PRICES["RSC"].get(material, BASE_PRICES["RSC"]["ลูกฟูก"])["cost"]
    else:
        base_price = BASE_PRICES["Die-cut"].get(material, BASE_PRICES["Die-cut"]["ลูกฟูก"])["cost"]
    
    price_per_box = base_price * factor
    total_price = price_per_box * quantity
    
    return {
        "factor": round(factor, 2),
        "price_per_box": round(price_per_box, 2),
        "total_price": round(total_price, 2),
        "quantity": quantity
    }

def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    pattern = r'<extracted_data>\s*(\{.*?\})\s*</extracted_data>'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return {}

def clean_response(response_text: str) -> str:
    pattern = r'<extracted_data>.*?</extracted_data>'
    return re.sub(pattern, '', response_text, flags=re.DOTALL).strip()

def generate_quotation(requirements: Dict[str, Any]) -> Dict[str, Any]:
    dimensions = requirements.get("dimensions", {"width": 10, "length": 10, "height": 10})
    box_type = requirements.get("box_type", "RSC")
    quantity = requirements.get("quantity", 500)
    
    product_type = requirements.get("product_type", "สินค้าทั่วไป")
    if box_type == "RSC":
        material = "ลูกฟูก"
    else:
        if product_type == "เครื่องสำอาง":
            material = "อาร์ต"
        elif product_type == "Food-grade":
            material = "กล่องแป้ง"
        else:
            material = "ลูกฟูก"
    
    box_price = calculate_box_price(
        dimensions.get("width", 10), 
        dimensions.get("length", 10), 
        dimensions.get("height", 10),
        box_type, material, quantity
    )
    
    special_features = requirements.get("special_features", [])
    features_total = 0
    
    inner_price = 0
    inner = requirements.get("inner")
    if inner:
        for name, prices in INNER_PRICES.items():
            if name in str(inner):
                avg_price = (prices["min"] + prices["max"]) / 2 * box_price["factor"]
                inner_price = avg_price * quantity
                break
    
    total_price = box_price["total_price"] + features_total + inner_price
    
    return {
        "box_type": box_type,
        "material": material,
        "dimensions": dimensions,
        "quantity": quantity,
        "inner": inner,
        "special_features": special_features,
        "pricing": {
            "box_price_per_unit": box_price["price_per_box"],
            "box_total": box_price["total_price"],
            "inner_total": round(inner_price, 2),
            "features_total": features_total,
            "grand_total": round(total_price, 2),
            "price_per_unit": round(total_price / quantity, 2)
        }
    }

# ==================== ENDPOINTS ====================
@app.get("/")
def read_root():
    return {"message": "Hello! LumoPack Brain is ready 🧠"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}

@app.post("/analyze")
def analyze_box(design: BoxDesign):
    spec = FLUTE_SPECS.get(design.flute_type, FLUTE_SPECS["C"])
    
    perimeter_inch = 2 * (design.length + design.width) * 0.3937
    bct_lbs = 5.87 * spec["ect"] * ((spec["thickness"] * 0.03937 * perimeter_inch) ** 0.5)
    max_load_kg = bct_lbs * 0.453592
    
    stack_load = design.weight * 4
    safety_score = max_load_kg / stack_load if stack_load > 0 else 100

    status = "SAFE"
    if safety_score < 1.5:
        status = "DANGER"
    elif safety_score < 3.0:
        status = "WARNING"

    return {
        "max_load_kg": round(max_load_kg, 2),
        "current_load": stack_load,
        "safety_score": round(safety_score, 2),
        "status": status,
        "recommendation": "Switch to Flute BC (Double Wall)" if status == "DANGER" else "Design is optimal (Safe)."
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        # สร้าง conversation content
        contents = []
        
        # เพิ่ม system prompt เป็นข้อความแรก
        contents.append({
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT}]
        })
        contents.append({
            "role": "model", 
            "parts": [{"text": "เข้าใจแล้วครับ ผมพร้อมทำหน้าที่เป็นลูโม่ ผู้ช่วย AI วิศวกรบรรจุภัณฑ์ของ LumoPack แล้วครับ"}]
        })
        
        # เพิ่ม conversation history
        for msg in request.conversation_history:
            role = "user" if msg.role == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        
        # เพิ่มข้อความใหม่พร้อม context
        user_message = request.message
        if request.current_requirements:
            user_message += f"\n\n[ข้อมูลที่เก็บได้: {json.dumps(request.current_requirements, ensure_ascii=False)}]"
        
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        # เรียก Gemini API ด้วย google-genai library ใหม่
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents
        )
        
        response_text = response.text
        
        # สกัดข้อมูลจากการตอบกลับ
        extracted_data = extract_json_from_response(response_text)
        clean_text = clean_response(response_text)
        
        # เตรียม response
        result = ChatResponse(
            response=clean_text,
            extracted_data=extracted_data,
            current_step=extracted_data.get("current_step", 1),
            is_checkpoint=extracted_data.get("is_checkpoint", False),
            show_quotation=False,
            quotation_data={}
        )
        
        # ถ้าถึงขั้นตอนออกใบเสนอราคา
        if extracted_data.get("confirmed_design") and extracted_data.get("current_step", 0) >= 10:
            quotation = generate_quotation(extracted_data)
            result.show_quotation = True
            result.quotation_data = quotation
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

@app.post("/api/calculate-price")
async def calculate_price(requirements: Dict[str, Any]):
    try:
        quotation = generate_quotation(requirements)
        return quotation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation Error: {str(e)}")