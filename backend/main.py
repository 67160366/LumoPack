"""
LumoPack Backend - AI Box Designer
FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

# Import models
from models import (
    BoxDesign,
    ChatRequest,
    ChatResponse,
    ProductInfo
)

# Import services
from services.box_designer import BoxDesigner
from services.mckee_analyzer import McKeeAnalyzer
from services.price_calculator import PriceCalculator
from services.ai_chat import AIChat

# Import data
from data.flute_specs import FLUTE_SPECS
from data.pricing import BASE_BOX_PRICES, INNER_PRICES, COATING_PRICES

# Import prompts
from prompts.system_prompt import SYSTEM_PROMPT

# ==================== INITIALIZE APP ====================
app = FastAPI(
    title="LumoPack API",
    description="AI-Powered Box Design & Quotation System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INITIALIZE SERVICES ====================
box_designer = BoxDesigner()
mckee_analyzer = McKeeAnalyzer()
price_calculator = PriceCalculator()
ai_chat = AIChat()

# ==================== HEALTH & INFO ENDPOINTS ====================
@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "🎁 LumoPack AI Box Designer is ready!",
        "version": "2.0.0",
        "features": [
            "AI Chatbot",
            "Auto Box Design",
            "McKee Strength Analysis",
            "Price Calculator"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_configured": ai_chat.is_configured,
        "services": {
            "box_designer": "ready",
            "mckee_analyzer": "ready",
            "price_calculator": "ready"
        }
    }

# ==================== BOX ANALYSIS ENDPOINTS ====================
@app.post("/analyze")
def analyze_box(design: BoxDesign):
    """
    วิเคราะห์ความแข็งแรงของกล่อง (McKee Formula)
    
    - **width**: กว้าง (cm)
    - **length**: ยาว (cm)
    - **height**: สูง (cm)
    - **flute_type**: ลอน (E/B/C/A/BC)
    - **weight**: น้ำหนักสินค้า (kg)
    """
    result = mckee_analyzer.analyze(
        design.width,
        design.length,
        design.height,
        design.flute_type,
        design.weight
    )
    return result

@app.post("/api/design-box")
async def design_box(product_info: Dict[str, Any]):
    """
    ออกแบบกล่องอัตโนมัติจากข้อมูลสินค้า
    
    Request body:
    ```json
    {
        "items": [
            {"width": 8, "length": 8, "height": 1, "weight": 0.05, "quantity": 3}
        ],
        "is_fragile": true,
        "is_food": true
    }
    ```
    """
    try:
        # ออกแบบกล่อง
        design_result = box_designer.design_complete(product_info)
        
        if "error" in design_result:
            raise HTTPException(status_code=400, detail=design_result["error"])
        
        # วิเคราะห์ความแข็งแรง
        box = design_result["box_design"]["recommended_size_cm"]
        flute = design_result["box_design"]["flute"]
        weight = design_result["product_summary"]["total_weight_kg"]
        
        strength = mckee_analyzer.analyze(
            box["width"],
            box["length"],
            box["height"],
            flute,
            weight
        )
        
        # สร้าง heatmap data
        heatmap = mckee_analyzer.generate_heatmap_data(
            box["width"],
            box["length"],
            box["height"],
            flute,
            weight
        )
        
        return {
            "design": design_result,
            "strength_analysis": strength,
            "heatmap": heatmap
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design Error: {str(e)}")

@app.post("/api/find-optimal-flute")
async def find_optimal_flute(request: Dict[str, Any]):
    """
    หาลอนที่เหมาะสมที่สุด
    
    Request body:
    ```json
    {
        "width": 10,
        "length": 10,
        "height": 10,
        "weight_kg": 0.5
    }
    ```
    """
    try:
        result = mckee_analyzer.find_optimal_flute(
            request.get("width", 10),
            request.get("length", 10),
            request.get("height", 10),
            request.get("weight_kg", 0.5),
            request.get("min_safety_score", 2.0)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PRICING ENDPOINTS ====================
@app.post("/api/calculate-price")
async def calculate_price(request: Dict[str, Any]):
    """
    คำนวณราคากล่อง
    
    Request body:
    ```json
    {
        "box_design": {
            "recommended_size_cm": {"width": 10, "length": 10, "height": 5},
            "flute": "E"
        },
        "quantity": 1000,
        "box_type": "RSC",
        "product_type": "Food-grade",
        "inner_type": "บับเบิ้ล",
        "coating_type": null
    }
    ```
    """
    try:
        result = price_calculator.calculate_total(
            box_design=request.get("box_design", {}),
            quantity=request.get("quantity", 500),
            box_type=request.get("box_type", "RSC"),
            product_type=request.get("product_type", "สินค้าทั่วไป"),
            inner_type=request.get("inner_type"),
            coating_type=request.get("coating_type"),
            has_emboss=request.get("has_emboss", False),
            has_emboss_block=request.get("has_emboss_block", False),
            foil_type=request.get("foil_type"),
            has_foil_block=request.get("has_foil_block", False)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation Error: {str(e)}")

# ==================== CHAT ENDPOINT ====================
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    AI Chatbot สำหรับออกแบบกล่อง
    
    Request body:
    ```json
    {
        "message": "อยากได้กล่องใส่คุกกี้",
        "conversation_history": [],
        "current_requirements": {}
    }
    ```
    """
    if not ai_chat.is_configured:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    
    try:
        # เรียก AI
        raw_response = ai_chat.chat(
            user_message=request.message,
            conversation_history=[msg.dict() for msg in request.conversation_history],
            system_prompt=SYSTEM_PROMPT,
            current_requirements=request.current_requirements
        )
        
        # ประมวลผล response
        processed = ai_chat.process_response(raw_response)
        
        extracted_data = processed["extracted_data"]
        clean_text = processed["clean_text"]
        quick_replies = processed["quick_replies"]
        
        # เตรียม response
        result = ChatResponse(
            response=clean_text,
            extracted_data=extracted_data,
            quick_replies=quick_replies,
            box_recommendation={},
            show_heatmap=False,
            show_quotation=False,
            quotation_data={}
        )
        
        # ถ้าพร้อมออกแบบกล่อง
        if extracted_data.get("ready_to_design"):
            product_info = extracted_data.get("product_info", {})
            if product_info.get("items"):
                # ออกแบบกล่อง
                design_result = box_designer.design_complete(product_info)
                
                if "error" not in design_result:
                    # วิเคราะห์ความแข็งแรง
                    box = design_result["box_design"]["recommended_size_cm"]
                    flute = design_result["box_design"]["flute"]
                    weight = design_result["product_summary"]["total_weight_kg"]
                    
                    strength = mckee_analyzer.analyze(
                        box["width"], box["length"], box["height"],
                        flute, weight
                    )
                    
                    heatmap = mckee_analyzer.generate_heatmap_data(
                        box["width"], box["length"], box["height"],
                        flute, weight
                    )
                    
                    result.box_recommendation = {
                        "design": design_result,
                        "strength": strength,
                        "heatmap": heatmap
                    }
                    result.show_heatmap = True
        
        # ถ้าพร้อมออกใบเสนอราคา
        if extracted_data.get("ready_to_quote") and result.box_recommendation:
            design = result.box_recommendation.get("design", {})
            box_design = design.get("box_design", {})
            
            quotation = price_calculator.calculate_total(
                box_design=box_design,
                quantity=extracted_data.get("quantity", 500),
                box_type=extracted_data.get("box_type", "RSC"),
                product_type="Food-grade" if extracted_data.get("product_info", {}).get("is_food") else "สินค้าทั่วไป",
                inner_type=extracted_data.get("options", {}).get("inner"),
                coating_type=extracted_data.get("options", {}).get("coating"),
                has_emboss=extracted_data.get("options", {}).get("emboss", False),
                foil_type=extracted_data.get("options", {}).get("foil")
            )
            
            result.quotation_data = quotation
            result.show_quotation = True
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

# ==================== INFO ENDPOINTS ====================
@app.get("/api/flute-info")
def get_flute_info():
    """ดูข้อมูลลอนกระดาษทั้งหมด"""
    return FLUTE_SPECS

@app.get("/api/pricing-info")
def get_pricing_info():
    """ดูข้อมูลราคาทั้งหมด"""
    return {
        "base_box_prices": BASE_BOX_PRICES,
        "inner_prices": INNER_PRICES,
        "coating_prices": COATING_PRICES
    }

@app.get("/api/materials")
def get_materials():
    """ดูข้อมูลวัสดุตามประเภทสินค้า"""
    from data.materials import PRODUCT_TYPE_MATERIALS
    return PRODUCT_TYPE_MATERIALS
