"""
LumoPack Backend - AI Box Designer
FastAPI Application

Features:
- AI Chatbot สำหรับออกแบบกล่อง
- McKee Formula Analysis
- Price Calculator
- Auto Box Design
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Import models
from models import (
    BoxAnalysisRequest,
    ChatRequest,
    ChatResponse,
    PriceRequest,
    OptimalFluteRequest,
    HealthResponse
)

# Import services
from services import BoxDesigner, McKeeAnalyzer, PriceCalculator, AIChat

# Import data
from data import FLUTE_SPECS, BASE_BOX_PRICES, INNER_PRICES, COATING_PRICES
from data import PRODUCT_TYPE_MATERIALS

# Import prompts
from prompts import SYSTEM_PROMPT

# Import exceptions
from utils.exceptions import NoProductsError, AINotConfiguredError, AIResponseError


# ==================== APP CONFIGURATION ====================
APP_TITLE = "LumoPack API"
APP_DESCRIPTION = "AI-Powered Box Design & Quotation System"
APP_VERSION = "2.1.0"

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== SERVICE INSTANCES ====================
box_designer = BoxDesigner()
mckee_analyzer = McKeeAnalyzer()
price_calculator = PriceCalculator()
ai_chat = AIChat()


# ==================== HEALTH & INFO ENDPOINTS ====================
@app.get("/", tags=["Info"])
def root():
    """Root endpoint - API information"""
    return {
        "message": f"🎁 {APP_TITLE} is ready!",
        "version": APP_VERSION,
        "features": [
            "AI Chatbot",
            "Auto Box Design",
            "McKee Strength Analysis",
            "Price Calculator"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        ai_configured=ai_chat.is_configured,
        services={
            "box_designer": "ready",
            "mckee_analyzer": "ready",
            "price_calculator": "ready"
        }
    )


# ==================== BOX ANALYSIS ENDPOINTS ====================
@app.post("/analyze", tags=["Analysis"])
def analyze_box(request: BoxAnalysisRequest):
    """
    วิเคราะห์ความแข็งแรงของกล่อง (McKee Formula)
    
    - **width**: กว้าง (cm)
    - **length**: ยาว (cm)
    - **height**: สูง (cm)
    - **flute_type**: ลอน (E/B/C/A/BC)
    - **weight**: น้ำหนักสินค้า (kg)
    """
    return mckee_analyzer.analyze(
        request.width,
        request.length,
        request.height,
        request.flute_type,
        request.weight
    )


@app.post("/api/design-box", tags=["Design"])
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
        
        # วิเคราะห์ความแข็งแรง
        box = design_result["box_design"]["recommended_size_cm"]
        flute = design_result["box_design"]["flute"]
        weight = design_result["product_summary"]["total_weight_kg"]
        
        strength = mckee_analyzer.analyze(
            box["width"], box["length"], box["height"],
            flute, weight
        )
        
        # สร้าง heatmap data
        heatmap = mckee_analyzer.generate_heatmap_data(
            box["width"], box["length"], box["height"],
            flute, weight
        )
        
        return {
            "design": design_result,
            "strength_analysis": strength,
            "heatmap": heatmap
        }
        
    except NoProductsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design Error: {str(e)}")


@app.post("/api/find-optimal-flute", tags=["Design"])
async def find_optimal_flute(request: OptimalFluteRequest):
    """
    หาลอนที่เหมาะสมที่สุด (บางที่สุดที่ยังปลอดภัย)
    """
    return mckee_analyzer.find_optimal_flute(
        request.width,
        request.length,
        request.height,
        request.weight_kg,
        request.min_safety_score
    )


# ==================== PRICING ENDPOINTS ====================
@app.post("/api/calculate-price", tags=["Pricing"])
async def calculate_price(request: PriceRequest):
    """
    คำนวณราคากล่อง
    """
    try:
        return price_calculator.calculate_total(
            box_design=request.box_design,
            quantity=request.quantity,
            box_type=request.box_type,
            product_type=request.product_type,
            inner_type=request.inner_type,
            coating_type=request.coating_type,
            has_emboss=request.has_emboss,
            has_emboss_block=request.has_emboss_block,
            foil_type=request.foil_type,
            has_foil_block=request.has_foil_block
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation Error: {str(e)}")


# ==================== CHAT ENDPOINT ====================
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(request: ChatRequest):
    """
    AI Chatbot สำหรับออกแบบกล่อง
    """
    if not ai_chat.is_configured:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set GROQ_API_KEY."
        )
    
    try:
        # เรียก AI
        raw_response = ai_chat.send_message(
            user_message=request.message,
            conversation_history=[msg.model_dump() for msg in request.conversation_history],
            system_prompt=SYSTEM_PROMPT,
            current_requirements=request.current_requirements
        )
        
        # ประมวลผล response
        processed = ai_chat.process_response(raw_response)
        
        extracted_data = processed["extracted_data"]
        clean_text = processed["clean_text"]
        quick_replies = processed["quick_replies"]
        
        # สร้าง response
        result = ChatResponse(
            response=clean_text,
            extracted_data=extracted_data,
            quick_replies=quick_replies
        )
        
        # ถ้าพร้อมออกแบบกล่อง
        if extracted_data.get("ready_to_design"):
            result = _process_box_design(result, extracted_data)
        
        # ถ้าพร้อมออกใบเสนอราคา
        if extracted_data.get("ready_to_quote") and result.box_recommendation:
            result = _process_quotation(result, extracted_data)
        
        return result
        
    except AINotConfiguredError:
        raise HTTPException(status_code=503, detail="AI service not configured")
    except AIResponseError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")


def _process_box_design(result: ChatResponse, extracted_data: Dict[str, Any]) -> ChatResponse:
    """ประมวลผลการออกแบบกล่อง"""
    product_info = extracted_data.get("product_info", {})
    
    if not product_info.get("items"):
        return result
    
    try:
        # ออกแบบกล่อง
        design_result = box_designer.design_complete(product_info)
        
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
        
    except Exception:
        pass  # ถ้าเกิด error ก็ไม่แสดง box_recommendation
    
    return result


def _process_quotation(result: ChatResponse, extracted_data: Dict[str, Any]) -> ChatResponse:
    """ประมวลผลใบเสนอราคา"""
    design = result.box_recommendation.get("design", {})
    box_design = design.get("box_design", {})
    product_info = extracted_data.get("product_info", {})
    
    if not box_design:
        return result
    
    try:
        product_type = "Food-grade" if product_info.get("is_food") else "สินค้าทั่วไป"
        
        quotation = price_calculator.calculate_total(
            box_design=box_design,
            quantity=extracted_data.get("quantity", 500),
            box_type=extracted_data.get("box_type", "RSC"),
            product_type=product_type,
            inner_type=extracted_data.get("options", {}).get("inner"),
            coating_type=extracted_data.get("options", {}).get("coating"),
            has_emboss=extracted_data.get("options", {}).get("emboss", False),
            foil_type=extracted_data.get("options", {}).get("foil")
        )
        
        result.quotation_data = quotation
        result.show_quotation = True
        
    except Exception:
        pass
    
    return result


# ==================== INFO ENDPOINTS ====================
@app.get("/api/flute-info", tags=["Info"])
def get_flute_info():
    """ดูข้อมูลลอนกระดาษทั้งหมด"""
    return FLUTE_SPECS


@app.get("/api/pricing-info", tags=["Info"])
def get_pricing_info():
    """ดูข้อมูลราคาทั้งหมด"""
    return {
        "base_box_prices": BASE_BOX_PRICES,
        "inner_prices": INNER_PRICES,
        "coating_prices": COATING_PRICES
    }


@app.get("/api/materials", tags=["Info"])
def get_materials():
    """ดูข้อมูลวัสดุตามประเภทสินค้า"""
    return PRODUCT_TYPE_MATERIALS
