from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาตให้หน้าเว็บ (Frontend) คุยกับหลังบ้านได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. กำหนดรูปแบบข้อมูลที่รับเข้ามา (Input Model)
class BoxDesign(BaseModel):
    length: float  # cm
    width: float   # cm
    height: float  # cm
    flute_type: str # A, B, C, E
    weight: float   # น้ำหนักสินค้า (kg)

# 2. ฐานข้อมูลสเปคกระดาษ (Mock Database)
FLUTE_SPECS = {
    "A": {"ect": 5.0, "thickness": 4.5},
    "B": {"ect": 4.0, "thickness": 2.5},
    "C": {"ect": 4.2, "thickness": 3.6}, # มาตรฐานนิยม
    "E": {"ect": 3.0, "thickness": 1.5},
}

# เพิ่มตรงนี้: สร้างหน้าแรก (Home Page)
@app.get("/")
def read_root():
    return {"message": "Hello! LumoPack Brain is ready 🧠"}

# 3. API จุดรับคำนวณ (Endpoint)
@app.post("/analyze")
def analyze_box(design: BoxDesign):
    # ดึงค่าสเปคกระดาษ
    spec = FLUTE_SPECS.get(design.flute_type, FLUTE_SPECS["C"])
    
    # คำนวณเส้นรอบรูป (Perimeter) เป็นนิ้ว (สูตร McKee ใช้นิ้ว)
    # 1 cm = 0.3937 inch
    perimeter_inch = 2 * (design.length + design.width) * 0.3937
    
    # สูตร McKee (แบบย่อ): BCT = 5.87 * ECT * sqrt(Thickness * Perimeter)
    # ผลลัพธ์หน่วยเป็น ปอนด์ (lbs)
    bct_lbs = 5.87 * spec["ect"] * ((spec["thickness"] * 0.03937 * perimeter_inch) ** 0.5)
    
    # แปลงเป็น กิโลกรัม (kg)
    max_load_kg = bct_lbs * 0.453592
    
    # คำนวณ Safety Factor (วางซ้อน 5 ชั้น = รับน้ำหนัก 4 กล่อง)
    stack_load = design.weight * 4
    safety_score = max_load_kg / stack_load if stack_load > 0 else 100

    # ประเมินผล
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