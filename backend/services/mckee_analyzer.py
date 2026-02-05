"""
McKee Analyzer - วิเคราะห์ความแข็งแรงของกล่อง

ใช้สูตร McKee Formula:
BCT = 5.87 × ECT × √(h × Z)

โดย:
- BCT: Box Compression Test (lbs)
- ECT: Edge Crush Test (kN/m)
- h: ความหนาลอน (inch)
- Z: เส้นรอบรูป = 2(L+W) (inch)
"""
import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from config import (
    BoxConfig,
    SafetyConfig,
    McKeeConfig,
    SafetyStatus,
    RiskLevel,
    FLUTE_STRENGTH_ORDER
)
from data.flute_specs import FLUTE_SPECS, get_flute_spec, get_stronger_flute
from utils.helpers import (
    cm_to_inch,
    mm_to_inch,
    lbs_to_kg,
    determine_safety_status,
    get_safety_display,
    clamp
)


# ==================== DATA CLASSES ====================
@dataclass
class StrengthResult:
    """ผลการวิเคราะห์ความแข็งแรง"""
    max_load_kg: float
    current_load_kg: float
    safety_score: float
    status: SafetyStatus
    recommendation: str


@dataclass
class WeakPoint:
    """จุดอ่อนของกล่อง"""
    area: str
    risk_level: RiskLevel
    reason: str
    suggestion: str


# ==================== MCKEE ANALYZER CLASS ====================
class McKeeAnalyzer:
    """
    คลาสสำหรับวิเคราะห์ความแข็งแรงกล่อง
    
    ใช้สูตร McKee Formula ในการคำนวณ Box Compression Test (BCT)
    
    Example:
        analyzer = McKeeAnalyzer()
        result = analyzer.analyze(10, 10, 5, "B", 0.5)
    """
    
    def __init__(self, stack_layers: int = BoxConfig.STACK_LAYERS):
        """
        Args:
            stack_layers: จำนวนชั้นที่สมมติวางซ้อน
        """
        self.stack_layers = stack_layers
    
    # ==================== PUBLIC METHODS ====================
    def calculate_bct(
        self,
        width: float,
        length: float,
        flute_type: str
    ) -> float:
        """
        คำนวณ Box Compression Test (BCT) ด้วยสูตร McKee
        
        Formula: BCT = 5.87 × ECT × √(h × Z)
        
        Args:
            width: กว้าง (cm)
            length: ยาว (cm)
            flute_type: รหัสลอน (E/B/C/A/BC)
        
        Returns:
            น้ำหนักสูงสุดที่รับได้ (kg)
        
        Note:
            height ไม่ได้ใช้ในสูตร McKee แต่ส่งผลต่อความมั่นคง
        """
        spec = get_flute_spec(flute_type)
        
        # แปลงหน่วย cm -> inch และ mm -> inch
        perimeter_inch = cm_to_inch(2 * (length + width))
        thickness_inch = mm_to_inch(spec["thickness"])
        
        # McKee Formula
        bct_lbs = (
            McKeeConfig.COEFFICIENT * 
            spec["ect"] * 
            math.sqrt(thickness_inch * perimeter_inch)
        )
        
        # แปลง lbs -> kg
        return round(lbs_to_kg(bct_lbs), 2)
    
    def analyze(
        self,
        width: float,
        length: float,
        height: float,
        flute_type: str,
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        วิเคราะห์ความแข็งแรงของกล่อง
        
        Args:
            width: กว้าง (cm)
            length: ยาว (cm)
            height: สูง (cm)
            flute_type: รหัสลอน
            weight_kg: น้ำหนักสินค้า (kg)
        
        Returns:
            ผลการวิเคราะห์ทั้งหมด
        """
        # คำนวณ BCT และ safety score
        max_load = self.calculate_bct(width, length, flute_type)
        stack_load = self._calculate_stack_load(weight_kg)
        safety_score = self._calculate_safety_score(max_load, stack_load)
        
        # กำหนดสถานะ
        status = determine_safety_status(safety_score)
        status_display = get_safety_display(status)
        recommendation = self._generate_recommendation(status, flute_type)
        
        return {
            "max_load_kg": max_load,
            "current_load_kg": round(stack_load, 2),
            "safety_score": round(safety_score, 2),
            "status": status.value,
            "status_thai": f"{status_display['thai']} {status_display['emoji']}",
            "color": status_display["color"],
            "recommendation": recommendation,
            "flute_used": flute_type,
            "flute_name": FLUTE_SPECS.get(flute_type, {}).get("name", flute_type),
            "stack_layers": self.stack_layers
        }
    
    def find_optimal_flute(
        self,
        width: float,
        length: float,
        height: float,
        weight_kg: float,
        min_safety_score: float = SafetyConfig.MIN_ACCEPTABLE_SCORE
    ) -> Dict[str, Any]:
        """
        หาลอนที่เหมาะสมที่สุด (บางที่สุดที่ยังปลอดภัย)
        
        Args:
            width, length, height: ขนาดกล่อง (cm)
            weight_kg: น้ำหนักสินค้า (kg)
            min_safety_score: Safety Score ขั้นต่ำที่ยอมรับได้
        
        Returns:
            ลอนที่แนะนำพร้อมเหตุผล
        """
        results = self._analyze_all_flutes(width, length, height, weight_kg)
        recommended = self._select_optimal_flute(results, min_safety_score)
        
        return {
            "recommended_flute": recommended["flute"],
            "recommended_analysis": recommended["analysis"],
            "all_options": results,
            "reason": self._build_recommendation_reason(recommended, weight_kg)
        }
    
    def generate_heatmap_data(
        self,
        width: float,
        length: float,
        height: float,
        flute_type: str,
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        สร้างข้อมูลสำหรับแสดง Heatmap
        
        Returns:
            ข้อมูลจุดอ่อนและความเสี่ยงของกล่อง
        """
        analysis = self.analyze(width, length, height, flute_type, weight_kg)
        weak_points = self._identify_weak_points(width, length, height, analysis)
        heatmap_grid = self._generate_risk_grid(analysis["safety_score"])
        
        return {
            "analysis": analysis,
            "weak_points": weak_points,
            "overall_risk": analysis["status"],
            "heatmap_grid": heatmap_grid,
            "dimensions": {
                "width": width,
                "length": length,
                "height": height
            }
        }
    
    # ==================== PRIVATE METHODS ====================
    def _calculate_stack_load(self, weight_kg: float) -> float:
        """คำนวณน้ำหนักที่ต้องรับเมื่อวางซ้อน"""
        return weight_kg * self.stack_layers
    
    def _calculate_safety_score(
        self, 
        max_load: float, 
        stack_load: float
    ) -> float:
        """คำนวณ Safety Score"""
        if stack_load <= 0:
            return SafetyConfig.MAX_SAFETY_SCORE
        return max_load / stack_load
    
    def _generate_recommendation(
        self, 
        status: SafetyStatus, 
        flute_type: str
    ) -> str:
        """สร้างคำแนะนำตามสถานะ"""
        if status == SafetyStatus.DANGER:
            stronger = get_stronger_flute(flute_type)
            return f"กล่องไม่แข็งแรงพอ แนะนำเปลี่ยนเป็น {FLUTE_SPECS.get(stronger, {}).get('name', stronger)}"
        
        if status == SafetyStatus.WARNING:
            return "กล่องพอใช้ได้ แต่ควรระวังการวางซ้อนหลายชั้น"
        
        return f"กล่องแข็งแรงเพียงพอ รองรับการซ้อน {self.stack_layers} ชั้นได้"
    
    def _analyze_all_flutes(
        self,
        width: float,
        length: float,
        height: float,
        weight_kg: float
    ) -> List[Dict[str, Any]]:
        """วิเคราะห์ทุกลอน"""
        results = []
        
        for flute_code in FLUTE_STRENGTH_ORDER:
            if flute_code not in FLUTE_SPECS:
                continue
                
            analysis = self.analyze(width, length, height, flute_code, weight_kg)
            results.append({
                "flute": flute_code,
                "analysis": analysis,
                "is_safe": analysis["safety_score"] >= SafetyConfig.MIN_ACCEPTABLE_SCORE
            })
        
        return results
    
    def _select_optimal_flute(
        self,
        results: List[Dict[str, Any]],
        min_safety_score: float
    ) -> Dict[str, Any]:
        """เลือกลอนที่เหมาะสมที่สุด"""
        # หาลอนที่บางที่สุดที่ยังปลอดภัย
        safe_options = [r for r in results if r["is_safe"]]
        
        if safe_options:
            return safe_options[0]  # ลอนบางที่สุดที่ปลอดภัย
        
        # ไม่มีลอนไหนปลอดภัย ใช้ลอนแข็งแรงที่สุด
        return results[-1] if results else {"flute": "BC", "analysis": {}}
    
    def _build_recommendation_reason(
        self, 
        recommended: Dict[str, Any], 
        weight_kg: float
    ) -> str:
        """สร้างเหตุผลคำแนะนำ"""
        flute = recommended["flute"]
        flute_name = FLUTE_SPECS.get(flute, {}).get("name", flute)
        return f"เลือก {flute_name} เพราะบางที่สุดที่รองรับน้ำหนัก {weight_kg} kg ได้"
    
    def _identify_weak_points(
        self,
        width: float,
        length: float,
        height: float,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ระบุจุดอ่อนของกล่อง"""
        weak_points = []
        
        # กล่องสูงเกินไป
        if self._is_too_tall(width, length, height):
            weak_points.append({
                "area": "ด้านข้าง",
                "risk_level": RiskLevel.HIGH.value,
                "risk_thai": "สูง",
                "reason": "กล่องสูงเกินไป อาจล้มง่ายเมื่อวางซ้อน",
                "suggestion": "ควรพิจารณาวางนอนแทน หรือใช้ลอนที่แข็งแรงกว่า"
            })
        
        # กล่องยาวเกินไป
        if self._is_too_long(width, length):
            weak_points.append({
                "area": "ตรงกลางด้านยาว",
                "risk_level": RiskLevel.MEDIUM.value,
                "risk_thai": "ปานกลาง",
                "reason": "กล่องยาวมาก อาจโค้งงอตรงกลาง",
                "suggestion": "ควรเพิ่ม divider หรือใช้ลอนหนาขึ้น"
            })
        
        # รับน้ำหนักไม่พอ
        if analysis["safety_score"] < SafetyConfig.MIN_ACCEPTABLE_SCORE:
            weak_points.append({
                "area": "ด้านบน",
                "risk_level": RiskLevel.HIGH.value,
                "risk_thai": "สูง",
                "reason": "รับน้ำหนักได้น้อย กล่องอาจยุบ",
                "suggestion": "ควรเปลี่ยนเป็นลอนที่แข็งแรงกว่า"
            })
        
        return weak_points
    
    def _is_too_tall(
        self, 
        width: float, 
        length: float, 
        height: float
    ) -> bool:
        """ตรวจสอบว่ากล่องสูงเกินไปหรือไม่ (สูง > 2 เท่าของกว้างหรือยาว)"""
        return height > width * 2 or height > length * 2
    
    def _is_too_long(self, width: float, length: float) -> bool:
        """ตรวจสอบว่ากล่องยาวเกินไปหรือไม่ (ยาว > 2 เท่าของกว้าง หรือกลับกัน)"""
        return width > length * 2 or length > width * 2
    
    def _generate_risk_grid(self, safety_score: float) -> List[List[float]]:
        """
        สร้าง 3x3 grid แสดงความเสี่ยงแต่ละจุด
        
        ค่า 0 = ไม่เสี่ยง, 1 = เสี่ยงสูงสุด
        """
        # คำนวณ base risk จาก safety score
        base_risk = clamp(
            1 - (safety_score / McKeeConfig.RISK_DIVISOR), 
            0, 
            1
        )
        
        grid = []
        grid_size = McKeeConfig.GRID_SIZE
        
        for row in range(grid_size):
            row_data = []
            for col in range(grid_size):
                risk = self._calculate_cell_risk(row, col, grid_size, base_risk)
                row_data.append(round(risk, 2))
            grid.append(row_data)
        
        return grid
    
    def _calculate_cell_risk(
        self, 
        row: int, 
        col: int, 
        grid_size: int, 
        base_risk: float
    ) -> float:
        """คำนวณความเสี่ยงของแต่ละช่องใน grid"""
        center = grid_size // 2
        
        # กลาง = เสี่ยงสูงสุด
        if row == center and col == center:
            return base_risk * McKeeConfig.CENTER_RISK_FACTOR
        
        # ขอบบน/ล่าง
        if row == 0 or row == grid_size - 1:
            return base_risk * McKeeConfig.EDGE_RISK_FACTOR
        
        # ขอบซ้าย/ขวา
        return base_risk * McKeeConfig.CORNER_RISK_FACTOR
