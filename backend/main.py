from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import os
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIG GEMINI ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

from google import genai

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== MODELS ====================
class BoxDesign(BaseModel):
    length: float
    width: float
    height: float
    flute_type: str
    weight: float

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    current_requirements: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    extracted_data: Dict[str, Any] = {}
    quick_replies: List[str] = []
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
    "BC": {"ect": 6.5, "thickness": 6.0},
}

# ==================== PRICING DATA (ตาม Requirement) ====================
BASE_BOX_PRICES = {
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

# Inner - แผ่นกันกระแทก (ราคาต่อ kg)
INNER_PRICES = {
    "กระดาษฝอย": {"min": 120, "max": 170, "unit": "บาท/kg", "weight_per_box": 0.02},
    "บับเบิ้ล": {"min": 60, "max": 90, "unit": "บาท/kg", "weight_per_box": 0.015},
    "ถุงลม": {"min": 120, "max": 200, "unit": "บาท/kg", "weight_per_box": 0.01},
}

# เคลือบกันชื้น (ราคาสำหรับกล่อง 10x10x10)
MOISTURE_COATING_PRICES = {
    "AQ Coating": {"min": 0.48, "max": 1.2, "description": "Acrylic polymer"},
    "PE Coating": {"min": 1.2, "max": 3.6, "description": "Polyethylene"},
    "Wax Coating": {"min": 1.2, "max": 3.0, "description": "Paraffin wax"},
    "Bio Coating": {"min": 2.0, "max": 5.0, "description": "Bio/Water-based Barrier"},
}

# Food-grade coating (ราคาสำหรับกล่อง 10x10x10)
FOOD_COATING_PRICES = {
    "Water-based Food Coating": {"min": 0.8, "max": 1.5, "description": "Acrylic/PVOH food safe"},
    "PE Food-grade Coating": {"min": 1.2, "max": 2.0, "description": "LDPE food-grade resin"},
    "PLA/Bio Coating": {"min": 2.0, "max": 3.5, "description": "PLA/Bio-resin"},
    "Grease-resistant Coating": {"min": 1.5, "max": 3.0, "description": "Fluorine-free grease barrier"},
}

# เคลือบเงา (ราคาสำหรับกล่อง 10x10x10)
GLOSS_COATING_PRICES = {
    "Gloss AQ Coating": {"min": 0.6, "max": 1.2, "description": "ต้นทุนต่ำ กลิ่นน้อย"},
    "UV Gloss Coating": {"min": 1.2, "max": 2.4, "description": "เงามาก ทนรอยขีดข่วน"},
    "OPP Gloss Film": {"min": 1.8, "max": 3.6, "description": "ทนสูง กันน้ำ งาน premium"},
}

# เคลือบด้าน (ราคาสำหรับกล่อง 10x10x10)
MATTE_COATING_PRICES = {
    "UV ด้าน": {"min": 4.0, "max": 8.0, "description": "ราคาประหยัด ผิวเรียบด้าน"},
    "ลามิเนตด้าน (PVC Matte)": {"min": 6.0, "max": 12.0, "description": "นิยมสูงสุด ให้ความรู้สึกพรีเมียม"},
    "วานิชด้าน (Varnish)": {"min": 8.0, "max": 15.0, "description": "เรียบเนียนพิเศษ"},
}

# ปั๊มนูน/ปั๊มจม
EMBOSS_PRICES = {
    "block_price": {"min": 800, "max": 1500, "unit": "บาท/บล็อก"},
    "per_box": 2.0,
}

# ปั๊มฟอยล์ - ค่าบล็อก
FOIL_BLOCK_PRICES = {
    "ฟอยล์ธรรมดา": {"min": 1000, "max": 2000},
    "ฟอยล์ละเอียด/ลายใหญ่": {"min": 2000, "max": 3500},
    "ฟอยล์+นูน": {"min": 2500, "max": 5000},
}

# ปั๊มฟอยล์ - ราคาต่อกล่อง
FOIL_PER_BOX_PRICES = {
    "ฟอยล์ 1 สี 1 จุด": {"min": 2, "max": 5},
    "ลายใหญ่/ฟอยล์พิเศษ": {"min": 5, "max": 10},
    "ฟอยล์+นูน": {"min": 6, "max": 12},
}

# เลือกวัสดุตามประเภทสินค้า
PRODUCT_TYPE_MATERIALS = {
    "สินค้าทั่วไป": {"RSC": "ลูกฟูก", "Die-cut": "ลูกฟูก"},
    "Non-food": {"RSC": "ลูกฟูก", "Die-cut": "ลูกฟูก"},
    "Food-grade": {"RSC": "ลูกฟูก", "Die-cut": "กล่องแป้ง"},
    "เครื่องสำอาง": {"RSC": "คราฟท์", "Die-cut": "อาร์ต"},
}

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """คุณคือ "ลูโม่" (Lumo) ผู้ช่วย AI วิศวกรบรรจุภัณฑ์ของ LumoPack 

## บุคลิก
- พูดจาเป็นมิตร สุภาพ ใช้ภาษาไทยที่เข้าใจง่าย
- ใช้ emoji เล็กน้อย ตอบกระชับ ได้ใจความ
- ถ้าลูกค้าตอบแบบอิสระ ให้พยายามเข้าใจและสกัดข้อมูลออกมา

## ขั้นตอนการทำงาน

### Phase 1: เก็บข้อมูลโครงสร้าง
1. **ทักทาย** - แนะนำตัวและบอกว่าจะช่วยออกแบบกล่องให้
2. **ประเภทสินค้า** (บังคับ) - สินค้าทั่วไป / Non-food / Food-grade / เครื่องสำอาง
3. **ประเภทกล่อง** (บังคับ) - RSC (มาตรฐาน) / Die-cut (ไดคัท)
4. **Inner** (Optional - ถามเฉพาะ Die-cut)
   - แผ่นกันกระแทก: กระดาษฝอย / บับเบิ้ล / ถุงลม
   - เคลือบกันชื้น: AQ Coating / PE Coating / Wax Coating / Bio Coating
   - Food-grade coating: Water-based / PE Food-grade / PLA/Bio / Grease-resistant
5. **ขนาดกล่อง** (บังคับ) - กว้าง x ยาว x สูง (ซม.)
6. **จำนวนผลิต** (บังคับ) - ขั้นต่ำ 500 ชิ้น

### Checkpoint 1: สรุปข้อมูลโครงสร้าง
แสดง: ประเภทสินค้า, ประเภทกล่อง, Inner (ถ้ามี หรือ "ไม่ได้กำหนด"), ขนาด, จำนวน
ขอยืนยัน - ถ้าแก้ไข/เพิ่ม ให้สรุปใหม่

### Phase 2: เก็บข้อมูลการออกแบบ
7. **Mood & Tone** (Optional) - สดใส / เรียบหรู / มินิมอล / สนุก / พรีเมียม
8. **Logo & Font** (Optional) - มีโลโก้หรือไม่ ถ้ามี ถามตำแหน่ง
9. **ลูกเล่นพิเศษ** (Optional) - เลือกได้หลายอย่าง
   - เคลือบเงา: Gloss AQ / UV Gloss / OPP Gloss Film
   - เคลือบด้าน: UV ด้าน / ลามิเนตด้าน / วานิชด้าน
   - ปั๊มนูน/ปั๊มจม (ถามว่าเคยทำบล็อกหรือยัง)
   - ปั๊มฟอยล์: ทอง/เงิน/โรสโกลด์/โฮโลแกรม/ฟอยล์+นูน (ถามว่าเคยทำบล็อกหรือยัง)

### Checkpoint 2: สรุปข้อมูลการออกแบบ
แสดง: ประเภทกล่อง, ขนาด, Mood&Tone, Logo, ลูกเล่นพิเศษ
ขอยืนยัน

### Phase 3: ออกใบเสนอราคา
10. **แสดง Mockup** - บอกลักษณะกล่องที่จะได้
11. **แสดงใบเสนอราคา** - ประเภทกล่อง, วัสดุ, Inner, ขนาด, จำนวน, ลูกเล่นพิเศษ, ราคาแยก, ราคารวม
12. **ยืนยันคำสั่งซื้อ**
13. **จบการสนทนา** - ขอบคุณ

## การตอบกลับ
ทุกครั้งต้องส่ง JSON ท้ายข้อความ:

<extracted_data>
{
  "product_type": "สินค้าทั่วไป/Non-food/Food-grade/เครื่องสำอาง หรือ null",
  "box_type": "RSC/Die-cut หรือ null",
  "inner": {
    "cushioning": "กระดาษฝอย/บับเบิ้ล/ถุงลม หรือ null",
    "moisture_coating": "AQ Coating/PE Coating/Wax Coating/Bio Coating หรือ null",
    "food_coating": "Water-based Food Coating/PE Food-grade Coating/PLA/Bio Coating/Grease-resistant Coating หรือ null"
  },
  "dimensions": {"width": null, "length": null, "height": null},
  "quantity": null,
  "mood_tone": null,
  "logo": {"has_logo": false, "position": null},
  "special_features": {
    "gloss_coating": null,
    "matte_coating": null,
    "emboss": {"type": null, "has_block": false},
    "foil": {"type": null, "color": null, "has_block": false}
  },
  "current_step": 1,
  "is_checkpoint": false,
  "confirmed_structure": false,
  "confirmed_design": false,
  "confirmed_order": false,
  "quick_replies": []
}
</extracted_data>

## กฎสำคัญสำหรับ quick_replies (ต้องตรงกับคำถาม!)
- ถามประเภทสินค้า → ["สินค้าทั่วไป", "Non-food", "Food-grade", "เครื่องสำอาง"]
- ถามประเภทกล่อง → ["RSC (มาตรฐาน)", "Die-cut (ไดคัท)"]
- ถามแผ่นกันกระแทก → ["ไม่ต้องการ", "กระดาษฝอย", "บับเบิ้ล", "ถุงลม"]
- ถามเคลือบกันชื้น → ["ไม่ต้องการ", "AQ Coating", "PE Coating", "Wax Coating", "Bio Coating"]
- ถาม Food-grade coating → ["ไม่ต้องการ", "Water-based", "PE Food-grade", "PLA/Bio", "Grease-resistant"]
- ถามขนาด → [] (พิมพ์เอง)
- ถามจำนวน → ["500", "1000", "2000", "5000"]
- Checkpoint → ["ยืนยัน ✓", "ขอแก้ไข"]
- ถาม Mood & Tone → ["ข้าม", "มินิมอล", "พรีเมียม", "สดใส", "เรียบหรู"]
- ถาม Logo → ["ไม่มีโลโก้", "มีโลโก้"]
- ถามตำแหน่ง Logo → ["ด้านบน", "ด้านล่าง", "ทุกด้าน", "ด้านกว้าง", "ด้านยาว"]
- ถามลูกเล่นพิเศษ → ["ไม่ต้องการ", "เคลือบเงา", "เคลือบด้าน", "ปั๊มนูน", "ปั๊มจม", "ปั๊มฟอยล์"]
- ถามเคลือบเงา → ["Gloss AQ Coating", "UV Gloss Coating", "OPP Gloss Film"]
- ถามเคลือบด้าน → ["UV ด้าน", "ลามิเนตด้าน", "วานิชด้าน"]
- ถามสีฟอยล์ → ["ทอง", "เงิน", "โรสโกลด์", "โฮโลแกรม", "ฟอยล์+นูน"]
- ถามเคยทำบล็อก → ["เคยทำแล้ว", "ยังไม่เคย", "ใช้บล็อกเดิม"]
- ยืนยันคำสั่งซื้อ → ["ยืนยันคำสั่งซื้อ ✓", "ขอแก้ไข"]

## กฎอื่นๆ
- ถามทีละหัวข้อ ไม่ถามรวมกัน
- "ไม่" หรือ "ข้าม" = ข้ามไปขั้นตอนถัดไป
- ปั๊มนูน/ปั๊มฟอยล์ ต้องถามเรื่องบล็อก
- จำนวนขั้นต่ำ 500 ชิ้น
"""

# ==================== HELPER FUNCTIONS ====================
def calculate_surface_area(width: float, length: float, height: float) -> float:
    return 2 * ((width * length) + (width * height) + (length * height))

def calculate_factor(width: float, length: float, height: float, box_type: str) -> float:
    base_area = 600
    production_factor = 1.1 if box_type == "RSC" else 1.5
    base_area_with_factor = base_area * production_factor
    new_area = calculate_surface_area(width, length, height) * production_factor
    return max(1.0, new_area / base_area_with_factor)

def get_material_for_product(product_type: str, box_type: str) -> str:
    if product_type in PRODUCT_TYPE_MATERIALS:
        return PRODUCT_TYPE_MATERIALS[product_type].get(box_type, "ลูกฟูก")
    return "ลูกฟูก"

def calculate_box_price(width: float, length: float, height: float, 
                        box_type: str, material: str, quantity: int) -> Dict[str, Any]:
    factor = calculate_factor(width, length, height, box_type)
    
    if box_type == "RSC":
        base_price = BASE_BOX_PRICES["RSC"].get(material, BASE_BOX_PRICES["RSC"]["ลูกฟูก"])["cost"]
    else:
        base_price = BASE_BOX_PRICES["Die-cut"].get(material, BASE_BOX_PRICES["Die-cut"]["ลูกฟูก"])["cost"]
    
    price_per_box = base_price * factor
    total_price = price_per_box * quantity
    
    return {
        "factor": round(factor, 2),
        "price_per_box": round(price_per_box, 2),
        "total_price": round(total_price, 2),
        "quantity": quantity
    }

def calculate_inner_price(inner: Dict[str, Any], factor: float, quantity: int) -> Dict[str, float]:
    result = {"cushioning": 0, "moisture_coating": 0, "food_coating": 0, "total": 0}
    
    if not inner:
        return result
    
    cushioning = inner.get("cushioning")
    if cushioning and cushioning in INNER_PRICES:
        price_data = INNER_PRICES[cushioning]
        avg_price_per_kg = (price_data["min"] + price_data["max"]) / 2
        weight = price_data["weight_per_box"] * factor
        result["cushioning"] = round(avg_price_per_kg * weight * quantity, 2)
    
    moisture = inner.get("moisture_coating")
    if moisture and moisture in MOISTURE_COATING_PRICES:
        price_data = MOISTURE_COATING_PRICES[moisture]
        avg_price = (price_data["min"] + price_data["max"]) / 2 * factor
        result["moisture_coating"] = round(avg_price * quantity, 2)
    
    food = inner.get("food_coating")
    if food and food in FOOD_COATING_PRICES:
        price_data = FOOD_COATING_PRICES[food]
        avg_price = (price_data["min"] + price_data["max"]) / 2 * factor
        result["food_coating"] = round(avg_price * quantity, 2)
    
    result["total"] = result["cushioning"] + result["moisture_coating"] + result["food_coating"]
    return result

def calculate_special_features_price(features: Dict[str, Any], factor: float, quantity: int) -> Dict[str, Any]:
    result = {
        "gloss_coating": 0,
        "matte_coating": 0,
        "emboss": {"block": 0, "per_box": 0, "total": 0},
        "foil": {"block": 0, "per_box": 0, "total": 0},
        "grand_total": 0
    }
    
    if not features:
        return result
    
    gloss = features.get("gloss_coating")
    if gloss and gloss in GLOSS_COATING_PRICES:
        price_data = GLOSS_COATING_PRICES[gloss]
        avg_price = (price_data["min"] + price_data["max"]) / 2 * factor
        result["gloss_coating"] = round(avg_price * quantity, 2)
    
    matte = features.get("matte_coating")
    if matte and matte in MATTE_COATING_PRICES:
        price_data = MATTE_COATING_PRICES[matte]
        avg_price = (price_data["min"] + price_data["max"]) / 2 * factor
        result["matte_coating"] = round(avg_price * quantity, 2)
    
    emboss = features.get("emboss", {})
    if emboss.get("type"):
        if not emboss.get("has_block"):
            result["emboss"]["block"] = (EMBOSS_PRICES["block_price"]["min"] + EMBOSS_PRICES["block_price"]["max"]) / 2
        result["emboss"]["per_box"] = round(EMBOSS_PRICES["per_box"] * quantity, 2)
        result["emboss"]["total"] = result["emboss"]["block"] + result["emboss"]["per_box"]
    
    foil = features.get("foil", {})
    foil_type = foil.get("type")
    if foil_type:
        if not foil.get("has_block"):
            if foil_type in FOIL_BLOCK_PRICES:
                block_price = FOIL_BLOCK_PRICES[foil_type]
                result["foil"]["block"] = (block_price["min"] + block_price["max"]) / 2
            else:
                result["foil"]["block"] = 1500
        
        if "นูน" in str(foil_type):
            per_box = FOIL_PER_BOX_PRICES["ฟอยล์+นูน"]
        elif "ละเอียด" in str(foil_type) or "ใหญ่" in str(foil_type):
            per_box = FOIL_PER_BOX_PRICES["ลายใหญ่/ฟอยล์พิเศษ"]
        else:
            per_box = FOIL_PER_BOX_PRICES["ฟอยล์ 1 สี 1 จุด"]
        
        avg_per_box = (per_box["min"] + per_box["max"]) / 2
        result["foil"]["per_box"] = round(avg_per_box * quantity, 2)
        result["foil"]["total"] = result["foil"]["block"] + result["foil"]["per_box"]
    
    result["grand_total"] = (
        result["gloss_coating"] + 
        result["matte_coating"] + 
        result["emboss"]["total"] + 
        result["foil"]["total"]
    )
    
    return result

def generate_quotation(requirements: Dict[str, Any]) -> Dict[str, Any]:
    dimensions = requirements.get("dimensions", {"width": 10, "length": 10, "height": 10})
    box_type = requirements.get("box_type", "RSC")
    quantity = requirements.get("quantity", 500)
    product_type = requirements.get("product_type", "สินค้าทั่วไป")
    
    material = get_material_for_product(product_type, box_type)
    
    box_price = calculate_box_price(
        dimensions.get("width", 10), 
        dimensions.get("length", 10), 
        dimensions.get("height", 10),
        box_type, material, quantity
    )
    
    factor = box_price["factor"]
    
    inner = requirements.get("inner", {})
    inner_price = calculate_inner_price(inner, factor, quantity)
    
    special_features = requirements.get("special_features", {})
    features_price = calculate_special_features_price(special_features, factor, quantity)
    
    grand_total = box_price["total_price"] + inner_price["total"] + features_price["grand_total"]
    
    return {
        "product_type": product_type,
        "box_type": box_type,
        "material": material,
        "dimensions": dimensions,
        "quantity": quantity,
        "inner": inner,
        "special_features": special_features,
        "pricing": {
            "factor": factor,
            "box_price_per_unit": box_price["price_per_box"],
            "box_total": box_price["total_price"],
            "inner_breakdown": inner_price,
            "inner_total": inner_price["total"],
            "features_breakdown": features_price,
            "features_total": features_price["grand_total"],
            "grand_total": round(grand_total, 2),
            "price_per_unit": round(grand_total / quantity, 2)
        }
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
        contents = []
        
        contents.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})
        contents.append({"role": "model", "parts": [{"text": "เข้าใจแล้วครับ พร้อมทำหน้าที่ลูโม่แล้วครับ"}]})
        
        for msg in request.conversation_history:
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})
        
        user_message = request.message
        if request.current_requirements:
            user_message += f"\n\n[ข้อมูลที่เก็บได้: {json.dumps(request.current_requirements, ensure_ascii=False)}]"
        
        contents.append({"role": "user", "parts": [{"text": user_message}]})
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=contents
        )
        
        response_text = response.text
        
        extracted_data = extract_json_from_response(response_text)
        clean_text = clean_response(response_text)
        
        quick_replies = extracted_data.get("quick_replies", [])
        
        result = ChatResponse(
            response=clean_text,
            extracted_data=extracted_data,
            quick_replies=quick_replies,
            current_step=extracted_data.get("current_step", 1),
            is_checkpoint=extracted_data.get("is_checkpoint", False),
            show_quotation=False,
            quotation_data={}
        )
        
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

@app.get("/api/pricing-info")
def get_pricing_info():
    return {
        "base_box_prices": BASE_BOX_PRICES,
        "inner_prices": INNER_PRICES,
        "moisture_coating_prices": MOISTURE_COATING_PRICES,
        "food_coating_prices": FOOD_COATING_PRICES,
        "gloss_coating_prices": GLOSS_COATING_PRICES,
        "matte_coating_prices": MATTE_COATING_PRICES,
        "emboss_prices": EMBOSS_PRICES,
        "foil_block_prices": FOIL_BLOCK_PRICES,
        "foil_per_box_prices": FOIL_PER_BOX_PRICES,
        "product_type_materials": PRODUCT_TYPE_MATERIALS
    }