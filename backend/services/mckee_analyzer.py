"""
McKee Analyzer - วิเคราะห์ความแข็งแรงของกล่อง
ใช้สูตร McKee Formula
"""
import math
from typing import Dict, Any
from data.flute_specs import FLUTE_SPECS, get_stronger_flute
from config import SAFETY_DANGER_THRESHOLD, SAFETY_WARNING_THRESHOLD, STACK_LAYERS


class McKeeAnalyzer:
    """คลาสสำหรับวิเคราะห์ความแข็งแรงกล่อง"""
    
    def __init__(self, stack_layers: int = STACK_LAYERS):
        self.stack_layers = stack_layers
    
    def calculate_bct(
        self,
        width: float,
        length: float,
        height: float,
        flute_type: str
    ) -> float:
        """
        คำนวณ Box Compression Test (BCT) ด้วยสูตร McKee
        
        McKee Formula: BCT = 5.87 × ECT × √(h × Z)
        - ECT: Edge Crush Test (kN/m)
        - h: ความหนาลอน (mm)
        - Z: เส้นรอบรูป = 2(L+W)
        
        Args:
            width: กว้าง (cm)
            length: ยาว (cm)
            height: สูง (cm) - ไม่ใช้ในสูตรแต่เก็บไว้
            flute_type: รหัสลอน (E/B/C/A/BC)
        
        Returns:
            น้ำหนักสูงสุดที่รับได้ (kg)
        """
        spec = FLUTE_SPECS.get(flute_type, FLUTE_SPECS["C"])
        
        # แปลงหน่วย cm -> inch
        perimeter_inch = 2 * (length + width) * 0.3937
        thickness_inch = spec["thickness"] * 0.03937
        
        # McKee Formula
        bct_lbs = 5.87 * spec["ect"] * math.sqrt(thickness_inch * perimeter_inch)
        
        # แปลง lbs -> kg
        max_load_kg = bct_lbs * 0.453592
        
        return round(max_load_kg, 2)
    
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
            ผลการวิเคราะห์
        """
        # คำนวณน้ำหนักสูงสุดที่รับได้
        max_load = self.calculate_bct(width, length, height, flute_type)
        
        # คำนวณน้ำหนักที่ต้องรับ (สมมติวางซ้อน 4 ชั้น)
        stack_load = weight_kg * self.stack_layers
        
        # คำนวณ Safety Score
        safety_score = max_load / stack_load if stack_load > 0 else 100
        
        # กำหนดสถานะ
        if safety_score < SAFETY_DANGER_THRESHOLD:
            status = "DANGER"
            status_thai = "อันตราย ❌"
            color = "red"
            stronger_flute = get_stronger_flute(flute_type)
            recommendation = f"กล่องไม่แข็งแรงพอ แนะนำเปลี่ยนเป็น {FLUTE_SPECS[stronger_flute]['name']}"
        elif safety_score < SAFETY_WARNING_THRESHOLD:
            status = "WARNING"
            status_thai = "ควรระวัง ⚠️"
            color = "yellow"
            recommendation = "กล่องพอใช้ได้ แต่ควรระวังการวางซ้อนหลายชั้น"
        else:
            status = "SAFE"
            status_thai = "ปลอดภัย ✅"
            color = "green"
            recommendation = "กล่องแข็งแรงเพียงพอ รองรับการซ้อน 4 ชั้นได้"
        
        return {
            "max_load_kg": max_load,
            "current_load_kg": round(stack_load, 2),
            "safety_score": round(safety_score, 2),
            "status": status,
            "status_thai": status_thai,
            "color": color,
            "recommendation": recommendation,
            "flute_used": flute_type,
            "flute_name": FLUTE_SPECS[flute_type]["name"],
            "stack_layers": self.stack_layers
        }
    
    def find_optimal_flute(
        self,
        width: float,
        length: float,
        height: float,
        weight_kg: float,
        min_safety_score: float = 2.0
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
        results = []
        
        for flute_code in ["E", "B", "C", "A", "BC"]:
            analysis = self.analyze(width, length, height, flute_code, weight_kg)
            results.append({
                "flute": flute_code,
                "analysis": analysis,
                "is_safe": analysis["safety_score"] >= min_safety_score
            })
        
        # หาลอนที่บางที่สุดที่ยังปลอดภัย
        safe_options = [r for r in results if r["is_safe"]]
        
        if safe_options:
            # เลือกลอนที่บางที่สุด (ลำดับแรกที่ปลอดภัย)
            recommended = safe_options[0]
        else:
            # ไม่มีลอนไหนปลอดภัย ใช้ BC
            recommended = results[-1]  # BC
        
        return {
            "recommended_flute": recommended["flute"],
            "recommended_analysis": recommended["analysis"],
            "all_options": results,
            "reason": f"เลือก {FLUTE_SPECS[recommended['flute']]['name']} เพราะบางที่สุดที่รองรับน้ำหนัก {weight_kg} kg ได้"
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
        
        weak_points = []
        
        # ตรวจสอบสัดส่วนกล่อง
        if height > width * 2 or height > length * 2:
            weak_points.append({
                "area": "ด้านข้าง",
                "risk_level": "high",
                "risk_thai": "สูง",
                "reason": "กล่องสูงเกินไป อาจล้มง่ายเมื่อวางซ้อน",
                "suggestion": "ควรพิจารณาวางนอนแทน หรือใช้ลอนที่แข็งแรงกว่า"
            })
        
        if width > length * 2 or length > width * 2:
            weak_points.append({
                "area": "ตรงกลางด้านยาว",
                "risk_level": "medium",
                "risk_thai": "ปานกลาง",
                "reason": "กล่องยาวมาก อาจโค้งงอตรงกลาง",
                "suggestion": "ควรเพิ่ม divider หรือใช้ลอนหนาขึ้น"
            })
        
        # ตรวจสอบน้ำหนัก
        if analysis["safety_score"] < 2:
            weak_points.append({
                "area": "ด้านบน",
                "risk_level": "high",
                "risk_thai": "สูง",
                "reason": "รับน้ำหนักได้น้อย กล่องอาจยุบ",
                "suggestion": "ควรเปลี่ยนเป็นลอนที่แข็งแรงกว่า"
            })
        
        # สร้าง heatmap grid (simplified)
        heatmap_grid = self._generate_grid(width, length, height, analysis["safety_score"])
        
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
    
    def _generate_grid(
        self,
        width: float,
        length: float,
        height: float,
        safety_score: float
    ) -> list:
        """สร้าง grid สำหรับ heatmap (simplified)"""
        # สร้าง 3x3 grid แสดงความเสี่ยงแต่ละจุด
        base_risk = max(0, min(1, 1 - (safety_score / 5)))
        
        grid = []
        for row in range(3):
            row_data = []
            for col in range(3):
                # ขอบมีความเสี่ยงต่ำกว่ากลาง
                if row == 1 and col == 1:
                    risk = base_risk  # กลาง
                elif row == 0 or row == 2:
                    risk = base_risk * 0.8  # บน/ล่าง
                else:
                    risk = base_risk * 0.6  # ขอบ
                
                row_data.append(round(risk, 2))
            grid.append(row_data)
        
        return grid
