"""
Box Designer - คำนวณขนาดกล่องจากข้อมูลสินค้า
"""
import math
from typing import List, Dict, Any, Optional
from data.flute_specs import FLUTE_SPECS, get_stronger_flute
from data.materials import get_recommended_flute_by_weight
from config import DEFAULT_BUFFER_CM


class BoxDesigner:
    """คลาสสำหรับออกแบบกล่อง"""
    
    def __init__(self, buffer_cm: float = DEFAULT_BUFFER_CM):
        self.buffer_cm = buffer_cm
    
    def calculate_box_size(
        self,
        items: List[Dict[str, Any]],
        arrangement: str = "auto"
    ) -> Dict[str, Any]:
        """
        คำนวณขนาดกล่องจากข้อมูลสินค้า
        
        Args:
            items: รายการสินค้า [{width, length, height, weight, quantity}]
            arrangement: "stack" (ซ้อน), "side_by_side" (วางข้างกัน), "auto"
        
        Returns:
            ข้อมูลขนาดกล่องที่แนะนำ
        """
        if not items:
            return {"error": "ไม่มีข้อมูลสินค้า"}
        
        total_weight = 0
        total_volume = 0
        
        # คำนวณขนาดรวม
        if len(items) == 1:
            # สินค้าชนิดเดียว
            result = self._calculate_single_product(items[0], arrangement)
        else:
            # หลายสินค้า
            result = self._calculate_multiple_products(items, arrangement)
        
        # คำนวณน้ำหนักและปริมาตรรวม
        for item in items:
            qty = item.get("quantity", 1)
            weight = item.get("weight", 0)
            w = item.get("width", 10)
            l = item.get("length", 10)
            h = item.get("height", 5)
            
            total_weight += weight * qty
            total_volume += w * l * h * qty
        
        # เพิ่ม buffer
        box_width = result["inner_width"] + (self.buffer_cm * 2)
        box_length = result["inner_length"] + (self.buffer_cm * 2)
        box_height = result["inner_height"] + self.buffer_cm
        
        # ปัดให้เป็นเลขกลมๆ
        box_width = math.ceil(box_width * 2) / 2
        box_length = math.ceil(box_length * 2) / 2
        box_height = math.ceil(box_height * 2) / 2
        
        return {
            "inner_dimensions": {
                "width": round(result["inner_width"], 1),
                "length": round(result["inner_length"], 1),
                "height": round(result["inner_height"], 1)
            },
            "recommended_box": {
                "width": box_width,
                "length": box_length,
                "height": box_height
            },
            "total_weight_kg": round(total_weight, 3),
            "total_volume_cm3": round(total_volume, 1),
            "arrangement": result["arrangement"],
            "buffer_cm": self.buffer_cm
        }
    
    def _calculate_single_product(
        self,
        item: Dict[str, Any],
        arrangement: str
    ) -> Dict[str, Any]:
        """คำนวณสำหรับสินค้าชนิดเดียว"""
        qty = item.get("quantity", 1)
        w = item.get("width", 10)
        l = item.get("length", 10)
        h = item.get("height", 5)
        
        if qty == 1:
            return {
                "inner_width": w,
                "inner_length": l,
                "inner_height": h,
                "arrangement": "single"
            }
        
        # หาการจัดเรียงที่ดีที่สุด
        arrangements = [
            {
                "name": "แถวเดียว",
                "inner_width": w * qty,
                "inner_length": l,
                "inner_height": h
            },
            {
                "name": "วางซ้อน",
                "inner_width": w,
                "inner_length": l,
                "inner_height": h * qty
            },
        ]
        
        # เพิ่มตัวเลือก 2 แถว ถ้าจำนวนมากกว่า 1
        if qty >= 2:
            rows = math.ceil(qty / 2)
            arrangements.append({
                "name": "2 แถว",
                "inner_width": w * rows,
                "inner_length": l * 2,
                "inner_height": h
            })
        
        # เลือกตามที่ระบุ หรือหาที่ประหยัดพื้นที่ที่สุด
        if arrangement == "stack":
            best = arrangements[1]  # วางซ้อน
        elif arrangement == "side_by_side":
            best = arrangements[0]  # แถวเดียว
        else:
            # auto - หาที่ใช้พื้นที่น้อยที่สุด
            best = min(
                arrangements,
                key=lambda x: x["inner_width"] * x["inner_length"] * x["inner_height"]
            )
        
        return {
            "inner_width": best["inner_width"],
            "inner_length": best["inner_length"],
            "inner_height": best["inner_height"],
            "arrangement": best["name"]
        }
    
    def _calculate_multiple_products(
        self,
        items: List[Dict[str, Any]],
        arrangement: str
    ) -> Dict[str, Any]:
        """คำนวณสำหรับหลายสินค้า"""
        max_width = 0
        max_length = 0
        total_height = 0
        
        for item in items:
            qty = item.get("quantity", 1)
            w = item.get("width", 10)
            l = item.get("length", 10)
            h = item.get("height", 5)
            
            max_width = max(max_width, w)
            max_length = max(max_length, l)
            total_height += h * qty
        
        return {
            "inner_width": max_width,
            "inner_length": max_length,
            "inner_height": total_height,
            "arrangement": "วางซ้อนตามลำดับ"
        }
    
    def recommend_flute(
        self,
        weight_kg: float,
        is_fragile: bool = False,
        is_stackable: bool = True
    ) -> Dict[str, Any]:
        """
        แนะนำลอนกระดาษที่เหมาะสม
        
        Args:
            weight_kg: น้ำหนักสินค้า (kg)
            is_fragile: สินค้าแตกง่ายหรือไม่
            is_stackable: ต้องวางซ้อนได้หรือไม่
        
        Returns:
            ข้อมูลลอนที่แนะนำ
        """
        # คำนวณน้ำหนักรวมถ้าวางซ้อน 4 ชั้น
        stack_weight = weight_kg * 4 if is_stackable else weight_kg
        
        # เพิ่ม factor ถ้าแตกง่าย
        if is_fragile:
            stack_weight *= 1.5
        
        # หาลอนที่เหมาะสม
        recommended = None
        alternatives = []
        
        for flute_code in ["E", "B", "C", "A", "BC"]:
            flute = FLUTE_SPECS[flute_code]
            if flute["max_weight"] >= stack_weight:
                if recommended is None:
                    recommended = flute_code
                else:
                    alternatives.append(flute_code)
        
        if recommended is None:
            recommended = "BC"
        
        return {
            "recommended_flute": recommended,
            "flute_info": FLUTE_SPECS[recommended],
            "alternatives": alternatives[:2],
            "calculation": {
                "product_weight_kg": weight_kg,
                "assumed_stack": 4 if is_stackable else 1,
                "total_load_kg": stack_weight,
                "fragile_factor": 1.5 if is_fragile else 1.0
            }
        }
    
    def design_complete(
        self,
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ออกแบบกล่องครบวงจร
        
        Args:
            product_info: {
                "items": [...],
                "is_fragile": bool,
                "is_food": bool,
                "arrangement": str
            }
        
        Returns:
            ข้อมูลการออกแบบทั้งหมด
        """
        items = product_info.get("items", [])
        is_fragile = product_info.get("is_fragile", False)
        is_food = product_info.get("is_food", False)
        arrangement = product_info.get("arrangement", "auto")
        
        if not items:
            return {"error": "ไม่มีข้อมูลสินค้า"}
        
        # 1. คำนวณขนาดกล่อง
        box_size = self.calculate_box_size(items, arrangement)
        
        if "error" in box_size:
            return box_size
        
        # 2. แนะนำลอน
        flute_rec = self.recommend_flute(
            box_size["total_weight_kg"],
            is_fragile=is_fragile
        )
        
        # 3. แนะนำ Inner
        inner_recommendation = None
        if is_fragile:
            inner_recommendation = "บับเบิ้ล หรือ โฟม"
        elif is_food:
            inner_recommendation = "กระดาษรองอาหาร (Food-grade)"
        
        return {
            "product_summary": {
                "total_items": sum(item.get("quantity", 1) for item in items),
                "total_weight_kg": box_size["total_weight_kg"],
                "is_fragile": is_fragile,
                "is_food": is_food
            },
            "box_design": {
                "inner_size_cm": box_size["inner_dimensions"],
                "recommended_size_cm": box_size["recommended_box"],
                "arrangement": box_size["arrangement"],
                "flute": flute_rec["recommended_flute"],
                "flute_name": flute_rec["flute_info"]["name"],
                "flute_reason": flute_rec["flute_info"]["description"]
            },
            "flute_recommendation": flute_rec,
            "inner_recommendation": inner_recommendation,
            "alternatives": {
                "other_flutes": flute_rec["alternatives"]
            }
        }
