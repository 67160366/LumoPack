"""
Box Designer - ออกแบบกล่องอัตโนมัติจากข้อมูลสินค้า

Features:
- คำนวณขนาดกล่องจากสินค้า
- แนะนำลอนที่เหมาะสม
- แนะนำ Inner ตามประเภทสินค้า
"""
import math
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from config import (
    BoxConfig,
    PricingConfig,
    FLUTE_STRENGTH_ORDER
)
from data.flute_specs import FLUTE_SPECS, STRONGEST_FLUTE
from data.materials import get_inner_recommendation
from utils.helpers import (
    get_item_dimensions,
    round_to_half,
    validate_dimensions
)
from utils.exceptions import NoProductsError


# ==================== ENUMS ====================
class ArrangementType(str, Enum):
    """ประเภทการจัดเรียงสินค้า"""
    AUTO = "auto"
    STACK = "stack"
    SIDE_BY_SIDE = "side_by_side"


class ArrangementName:
    """ชื่อการจัดเรียง (ภาษาไทย)"""
    SINGLE = "single"
    ROW = "แถวเดียว"
    STACKED = "วางซ้อน"
    TWO_ROWS = "2 แถว"
    SEQUENTIAL = "วางซ้อนตามลำดับ"


# ==================== DATA CLASSES ====================
@dataclass
class InnerDimensions:
    """ขนาดภายในที่ต้องการ"""
    width: float
    length: float
    height: float
    arrangement: str


@dataclass
class BoxDimensions:
    """ขนาดกล่องที่แนะนำ"""
    width: float
    length: float
    height: float


# ==================== BOX DESIGNER CLASS ====================
class BoxDesigner:
    """
    คลาสสำหรับออกแบบกล่องอัตโนมัติ
    
    Example:
        designer = BoxDesigner()
        result = designer.design_complete({
            "items": [{"width": 8, "length": 8, "height": 1, "weight": 0.05, "quantity": 3}],
            "is_fragile": True,
            "is_food": True
        })
    """
    
    def __init__(self, buffer_cm: float = BoxConfig.DEFAULT_BUFFER_CM):
        """
        Args:
            buffer_cm: ระยะเผื่อรอบสินค้า (cm)
        """
        self.buffer_cm = buffer_cm
    
    # ==================== PUBLIC METHODS ====================
    def calculate_box_size(
        self,
        items: List[Dict[str, Any]],
        arrangement: str = ArrangementType.AUTO
    ) -> Dict[str, Any]:
        """
        คำนวณขนาดกล่องจากข้อมูลสินค้า
        
        Args:
            items: รายการสินค้า [{width, length, height, weight, quantity}]
            arrangement: วิธีจัดเรียง ("auto", "stack", "side_by_side")
        
        Returns:
            {
                "inner_dimensions": {...},
                "recommended_box": {...},
                "total_weight_kg": float,
                "total_volume_cm3": float,
                "arrangement": str
            }
        
        Raises:
            NoProductsError: ถ้าไม่มีข้อมูลสินค้า
        """
        if not items:
            raise NoProductsError()
        
        # คำนวณขนาดภายใน
        inner = self._calculate_inner_dimensions(items, arrangement)
        
        # คำนวณน้ำหนักและปริมาตรรวม
        total_weight, total_volume = self._calculate_totals(items)
        
        # คำนวณขนาดกล่อง (เพิ่ม buffer)
        box = self._apply_buffer(inner)
        
        return {
            "inner_dimensions": {
                "width": round(inner.width, 1),
                "length": round(inner.length, 1),
                "height": round(inner.height, 1)
            },
            "recommended_box": {
                "width": box.width,
                "length": box.length,
                "height": box.height
            },
            "total_weight_kg": round(total_weight, 3),
            "total_volume_cm3": round(total_volume, 1),
            "arrangement": inner.arrangement,
            "buffer_cm": self.buffer_cm
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
            {
                "recommended_flute": str,
                "flute_info": dict,
                "alternatives": list,
                "calculation": dict
            }
        """
        # คำนวณน้ำหนักที่ต้องรับ
        stack_layers = BoxConfig.STACK_LAYERS if is_stackable else 1
        effective_weight = weight_kg * stack_layers
        
        # เพิ่ม safety factor ถ้าแตกง่าย
        fragile_factor = PricingConfig.FRAGILE_WEIGHT_MULTIPLIER if is_fragile else 1.0
        total_load = effective_weight * fragile_factor
        
        # หาลอนที่เหมาะสม
        recommended, alternatives = self._find_suitable_flutes(total_load)
        
        return {
            "recommended_flute": recommended,
            "flute_info": FLUTE_SPECS[recommended],
            "alternatives": alternatives[:2],
            "calculation": {
                "product_weight_kg": weight_kg,
                "assumed_stack": stack_layers,
                "total_load_kg": round(total_load, 2),
                "fragile_factor": fragile_factor
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
                "arrangement": str (optional)
            }
        
        Returns:
            ข้อมูลการออกแบบทั้งหมด
        
        Raises:
            NoProductsError: ถ้าไม่มีข้อมูลสินค้า
        """
        items = product_info.get("items", [])
        is_fragile = product_info.get("is_fragile", False)
        is_food = product_info.get("is_food", False)
        arrangement = product_info.get("arrangement", ArrangementType.AUTO)
        
        if not items:
            raise NoProductsError()
        
        # 1. คำนวณขนาดกล่อง
        box_size = self.calculate_box_size(items, arrangement)
        
        # 2. แนะนำลอน
        flute_rec = self.recommend_flute(
            box_size["total_weight_kg"],
            is_fragile=is_fragile
        )
        
        # 3. แนะนำ Inner
        inner_recommendation = get_inner_recommendation(is_fragile, is_food)
        
        # 4. สรุปผล
        return self._build_design_result(
            items, box_size, flute_rec, 
            is_fragile, is_food, inner_recommendation
        )
    
    # ==================== PRIVATE METHODS ====================
    def _calculate_inner_dimensions(
        self,
        items: List[Dict[str, Any]],
        arrangement: str
    ) -> InnerDimensions:
        """คำนวณขนาดภายในที่ต้องการ"""
        if len(items) == 1:
            return self._calculate_single_product(items[0], arrangement)
        return self._calculate_multiple_products(items)
    
    def _calculate_single_product(
        self,
        item: Dict[str, Any],
        arrangement: str
    ) -> InnerDimensions:
        """คำนวณสำหรับสินค้าชนิดเดียว"""
        width, length, height, _, quantity = get_item_dimensions(item)
        
        # สินค้าชิ้นเดียว
        if quantity == 1:
            return InnerDimensions(width, length, height, ArrangementName.SINGLE)
        
        # หาการจัดเรียงที่ดีที่สุด
        arrangements = self._generate_arrangements(width, length, height, quantity)
        best = self._select_best_arrangement(arrangements, arrangement)
        
        return InnerDimensions(
            best["width"], 
            best["length"], 
            best["height"], 
            best["name"]
        )
    
    def _generate_arrangements(
        self,
        w: float, 
        l: float, 
        h: float, 
        qty: int
    ) -> List[Dict[str, Any]]:
        """สร้างตัวเลือกการจัดเรียง"""
        arrangements = [
            {"name": ArrangementName.ROW, "width": w * qty, "length": l, "height": h},
            {"name": ArrangementName.STACKED, "width": w, "length": l, "height": h * qty},
        ]
        
        # เพิ่มตัวเลือก 2 แถว ถ้าจำนวน >= 2
        if qty >= 2:
            rows = math.ceil(qty / 2)
            arrangements.append({
                "name": ArrangementName.TWO_ROWS,
                "width": w * rows,
                "length": l * 2,
                "height": h
            })
        
        return arrangements
    
    def _select_best_arrangement(
        self,
        arrangements: List[Dict[str, Any]],
        preferred: str
    ) -> Dict[str, Any]:
        """เลือกการจัดเรียงที่ดีที่สุด"""
        if preferred == ArrangementType.STACK:
            return arrangements[1]  # วางซ้อน
        elif preferred == ArrangementType.SIDE_BY_SIDE:
            return arrangements[0]  # แถวเดียว
        
        # Auto: หาที่ใช้พื้นที่น้อยที่สุด
        return min(
            arrangements,
            key=lambda x: x["width"] * x["length"] * x["height"]
        )
    
    def _calculate_multiple_products(
        self,
        items: List[Dict[str, Any]]
    ) -> InnerDimensions:
        """คำนวณสำหรับหลายสินค้า (วางซ้อนตามลำดับ)"""
        max_width = 0.0
        max_length = 0.0
        total_height = 0.0
        
        for item in items:
            w, l, h, _, qty = get_item_dimensions(item)
            max_width = max(max_width, w)
            max_length = max(max_length, l)
            total_height += h * qty
        
        return InnerDimensions(
            max_width, max_length, total_height, 
            ArrangementName.SEQUENTIAL
        )
    
    def _calculate_totals(
        self,
        items: List[Dict[str, Any]]
    ) -> Tuple[float, float]:
        """คำนวณน้ำหนักและปริมาตรรวม"""
        total_weight = 0.0
        total_volume = 0.0
        
        for item in items:
            w, l, h, weight, qty = get_item_dimensions(item)
            total_weight += weight * qty
            total_volume += w * l * h * qty
        
        return total_weight, total_volume
    
    def _apply_buffer(self, inner: InnerDimensions) -> BoxDimensions:
        """เพิ่ม buffer และปัดเลข"""
        box_width = round_to_half(inner.width + self.buffer_cm * 2)
        box_length = round_to_half(inner.length + self.buffer_cm * 2)
        box_height = round_to_half(inner.height + self.buffer_cm)
        
        return BoxDimensions(box_width, box_length, box_height)
    
    def _find_suitable_flutes(
        self,
        total_load: float
    ) -> Tuple[str, List[str]]:
        """หาลอนที่เหมาะสมกับน้ำหนัก"""
        recommended = None
        alternatives = []
        
        for flute_code in FLUTE_STRENGTH_ORDER:
            if flute_code not in FLUTE_SPECS:
                continue
                
            max_weight = FLUTE_SPECS[flute_code]["max_weight"]
            if max_weight >= total_load:
                if recommended is None:
                    recommended = flute_code
                else:
                    alternatives.append(flute_code)
        
        # Fallback ถ้าไม่มีลอนไหนรับได้
        if recommended is None:
            recommended = STRONGEST_FLUTE
        
        return recommended, alternatives
    
    def _build_design_result(
        self,
        items: List[Dict[str, Any]],
        box_size: Dict[str, Any],
        flute_rec: Dict[str, Any],
        is_fragile: bool,
        is_food: bool,
        inner_recommendation: str
    ) -> Dict[str, Any]:
        """สร้างผลลัพธ์การออกแบบ"""
        total_items = sum(item.get("quantity", 1) for item in items)
        
        return {
            "product_summary": {
                "total_items": total_items,
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
