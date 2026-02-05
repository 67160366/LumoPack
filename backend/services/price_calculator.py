"""
Price Calculator - คำนวณราคากล่อง

คำนวณราคาจาก:
- ขนาดกล่อง (พื้นที่ผิว)
- ประเภทกล่อง (RSC / Die-cut)
- วัสดุ
- ลอน
- Options (Inner, เคลือบ, ปั๊ม)
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

from config import BoxConfig, PricingConfig
from data.pricing import (
    BASE_BOX_PRICES,
    INNER_PRICES,
    COATING_PRICES,
    EMBOSS_PRICES,
    FOIL_PRICES,
    get_base_price,
    get_flute_multiplier,
    categorize_foil_type
)
from data.materials import get_material_recommendation
from utils.helpers import calculate_surface_area, calculate_average_price, safe_divide


# ==================== DATA CLASSES ====================
@dataclass
class BoxPriceResult:
    """ผลการคำนวณราคากล่อง"""
    box_type: str
    material: str
    flute_type: str
    quantity: int
    factor: float
    price_per_box: float
    total_price: float


@dataclass
class QuotationResult:
    """ใบเสนอราคา"""
    box_total: float
    options_total: float
    grand_total: float
    price_per_unit: float


# ==================== PRICE CALCULATOR CLASS ====================
class PriceCalculator:
    """
    คลาสสำหรับคำนวณราคากล่อง
    
    ราคาคำนวณจาก:
    1. พื้นที่ผิวกล่องเทียบกับกล่องมาตรฐาน (factor)
    2. ราคาวัสดุพื้นฐาน
    3. ตัวคูณตามลอน
    4. จำนวนสั่งผลิต
    
    Example:
        calculator = PriceCalculator()
        result = calculator.calculate_total(
            box_design={"recommended_size_cm": {"width": 10, "length": 10, "height": 5}},
            quantity=1000
        )
    """
    
    def __init__(self):
        self.base_surface_area = PricingConfig.BASE_SURFACE_AREA
    
    # ==================== PUBLIC METHODS ====================
    def calculate_size_factor(
        self,
        width: float,
        length: float,
        height: float,
        box_type: str = "RSC"
    ) -> float:
        """
        คำนวณ Factor เทียบกับกล่องมาตรฐาน 10x10x10
        
        Args:
            width, length, height: ขนาดกล่อง (cm)
            box_type: ประเภทกล่อง
        
        Returns:
            Factor (>= 1.0)
        """
        production_factor = self._get_production_factor(box_type)
        base_area_adjusted = self.base_surface_area * production_factor
        
        new_area = calculate_surface_area(width, length, height)
        new_area_adjusted = new_area * production_factor
        
        return max(PricingConfig.MIN_FACTOR, new_area_adjusted / base_area_adjusted)
    
    def calculate_box_price(
        self,
        width: float,
        length: float,
        height: float,
        box_type: str,
        material: str,
        flute_type: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        คำนวณราคากล่องเปล่า
        
        Args:
            width, length, height: ขนาดกล่อง (cm)
            box_type: "RSC" หรือ "Die-cut"
            material: วัสดุ เช่น "ลูกฟูก", "อาร์ต"
            flute_type: ลอน เช่น "E", "B", "C"
            quantity: จำนวน
        
        Returns:
            รายละเอียดราคา
        """
        factor = self.calculate_size_factor(width, length, height, box_type)
        base_price = get_base_price(box_type, material)
        flute_multiplier = get_flute_multiplier(flute_type)
        
        price_per_box = base_price * factor * flute_multiplier
        total_price = price_per_box * quantity
        
        return {
            "box_type": box_type,
            "material": material,
            "flute_type": flute_type,
            "dimensions": {"width": width, "length": length, "height": height},
            "quantity": quantity,
            "factor": round(factor, 2),
            "flute_multiplier": flute_multiplier,
            "price_per_box": round(price_per_box, 2),
            "total_price": round(total_price, 2)
        }
    
    def calculate_inner_price(
        self,
        inner_type: Optional[str],
        factor: float,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคา Inner (แผ่นกันกระแทก)"""
        if not inner_type or inner_type not in INNER_PRICES:
            return self._empty_inner_result()
        
        price_data = INNER_PRICES[inner_type]
        avg_price_per_kg = calculate_average_price(price_data)
        weight_per_box = price_data["weight_per_box"] * factor
        total = avg_price_per_kg * weight_per_box * quantity
        
        return {
            "type": inner_type,
            "price_per_kg": avg_price_per_kg,
            "weight_per_box": round(weight_per_box, 4),
            "total": round(total, 2)
        }
    
    def calculate_coating_price(
        self,
        coating_type: Optional[str],
        factor: float,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคาเคลือบ"""
        if not coating_type or coating_type not in COATING_PRICES:
            return self._empty_coating_result()
        
        price_data = COATING_PRICES[coating_type]
        avg_price = calculate_average_price(price_data) * factor
        total = avg_price * quantity
        
        return {
            "type": coating_type,
            "price_per_box": round(avg_price, 2),
            "total": round(total, 2)
        }
    
    def calculate_emboss_price(
        self,
        has_emboss: bool,
        has_existing_block: bool,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคาปั๊มนูน/ปั๊มจม"""
        if not has_emboss:
            return self._empty_emboss_result()
        
        block_cost = self._calculate_emboss_block_cost(has_existing_block)
        per_box_total = EMBOSS_PRICES["per_box"] * quantity
        total = block_cost + per_box_total
        
        return {
            "enabled": True,
            "block_cost": block_cost,
            "per_box_cost": round(per_box_total, 2),
            "total": round(total, 2)
        }
    
    def calculate_foil_price(
        self,
        foil_type: Optional[str],
        has_existing_block: bool,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคาปั๊มฟอยล์"""
        if not foil_type:
            return self._empty_foil_result()
        
        category = categorize_foil_type(foil_type)
        block_cost = self._calculate_foil_block_cost(category, has_existing_block)
        per_box_total = self._calculate_foil_per_box_cost(category, quantity)
        total = block_cost + per_box_total
        
        return {
            "enabled": True,
            "type": foil_type,
            "block_cost": block_cost,
            "per_box_cost": round(per_box_total, 2),
            "total": round(total, 2)
        }
    
    def calculate_total(
        self,
        box_design: Dict[str, Any],
        quantity: int,
        box_type: str = "RSC",
        product_type: str = "สินค้าทั่วไป",
        inner_type: Optional[str] = None,
        coating_type: Optional[str] = None,
        has_emboss: bool = False,
        has_emboss_block: bool = False,
        foil_type: Optional[str] = None,
        has_foil_block: bool = False
    ) -> Dict[str, Any]:
        """
        คำนวณราคารวมทั้งหมด
        
        Args:
            box_design: ข้อมูลการออกแบบกล่อง
            quantity: จำนวน
            box_type: ประเภทกล่อง
            product_type: ประเภทสินค้า
            inner_type: ประเภท Inner
            coating_type: ประเภทเคลือบ
            has_emboss: มีปั๊มนูนหรือไม่
            has_emboss_block: มีบล็อกปั๊มนูนแล้วหรือไม่
            foil_type: ประเภทฟอยล์
            has_foil_block: มีบล็อกฟอยล์แล้วหรือไม่
        
        Returns:
            ใบเสนอราคาทั้งหมด
        """
        # Validate quantity
        quantity = max(quantity, 1)  # ป้องกัน division by zero
        
        # ดึงข้อมูลจาก box_design
        dims = self._extract_dimensions(box_design)
        flute = box_design.get("flute", "B")
        
        # เลือกวัสดุตามประเภทสินค้า
        material_rec = get_material_recommendation(product_type, box_type)
        material = material_rec["material"]
        
        # คำนวณราคากล่อง
        box_price = self.calculate_box_price(
            dims["width"], dims["length"], dims["height"],
            box_type, material, flute, quantity
        )
        
        # คำนวณราคา options
        factor = box_price["factor"]
        prices = self._calculate_all_options(
            factor, quantity, inner_type, coating_type,
            has_emboss, has_emboss_block, foil_type, has_foil_block
        )
        
        # รวมราคา
        return self._build_quotation(
            box_type, material, flute, dims, quantity,
            box_price, prices
        )
    
    # ==================== PRIVATE METHODS ====================
    def _get_production_factor(self, box_type: str) -> float:
        """ดึง production factor ตามประเภทกล่อง"""
        if box_type == "RSC":
            return PricingConfig.RSC_PRODUCTION_FACTOR
        return PricingConfig.DIECUT_PRODUCTION_FACTOR
    
    def _extract_dimensions(self, box_design: Dict[str, Any]) -> Dict[str, float]:
        """ดึง dimensions จาก box_design"""
        default_dims = {
            "width": BoxConfig.DEFAULT_WIDTH,
            "length": BoxConfig.DEFAULT_LENGTH,
            "height": BoxConfig.DEFAULT_HEIGHT
        }
        return box_design.get("recommended_size_cm", default_dims)
    
    def _calculate_emboss_block_cost(self, has_existing_block: bool) -> float:
        """คำนวณค่าบล็อกปั๊มนูน"""
        if has_existing_block:
            return 0.0
        return calculate_average_price(EMBOSS_PRICES["block"])
    
    def _calculate_foil_block_cost(
        self, 
        category: str, 
        has_existing_block: bool
    ) -> float:
        """คำนวณค่าบล็อกฟอยล์"""
        if has_existing_block:
            return 0.0
        
        block_prices = FOIL_PRICES["block"]
        price_data = block_prices.get(category, block_prices["standard"])
        return calculate_average_price(price_data)
    
    def _calculate_foil_per_box_cost(self, category: str, quantity: int) -> float:
        """คำนวณค่าปั๊มฟอยล์ต่อกล่อง"""
        per_box_prices = FOIL_PRICES["per_box"]
        
        # Map category to price key
        price_key_map = {
            "emboss_foil": "emboss_foil",
            "detailed": "large",
            "standard": "1_color"
        }
        price_key = price_key_map.get(category, "1_color")
        price_data = per_box_prices.get(price_key, per_box_prices["1_color"])
        
        avg_per_box = calculate_average_price(price_data)
        return avg_per_box * quantity
    
    def _calculate_all_options(
        self,
        factor: float,
        quantity: int,
        inner_type: Optional[str],
        coating_type: Optional[str],
        has_emboss: bool,
        has_emboss_block: bool,
        foil_type: Optional[str],
        has_foil_block: bool
    ) -> Dict[str, Dict[str, Any]]:
        """คำนวณราคา options ทั้งหมด"""
        return {
            "inner": self.calculate_inner_price(inner_type, factor, quantity),
            "coating": self.calculate_coating_price(coating_type, factor, quantity),
            "emboss": self.calculate_emboss_price(has_emboss, has_emboss_block, quantity),
            "foil": self.calculate_foil_price(foil_type, has_foil_block, quantity)
        }
    
    def _build_quotation(
        self,
        box_type: str,
        material: str,
        flute: str,
        dims: Dict[str, float],
        quantity: int,
        box_price: Dict[str, Any],
        prices: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """สร้างใบเสนอราคา"""
        options_total = sum(p.get("total", 0) for p in prices.values())
        grand_total = box_price["total_price"] + options_total
        price_per_unit = safe_divide(grand_total, quantity, default=grand_total)
        
        return {
            "summary": {
                "box_type": box_type,
                "material": material,
                "flute": flute,
                "dimensions": dims,
                "quantity": quantity
            },
            "pricing": {
                "box": box_price,
                **prices
            },
            "totals": {
                "box_total": box_price["total_price"],
                "options_total": round(options_total, 2),
                "grand_total": round(grand_total, 2),
                "price_per_unit": round(price_per_unit, 2)
            }
        }
    
    # ==================== EMPTY RESULTS ====================
    @staticmethod
    def _empty_inner_result() -> Dict[str, Any]:
        return {"type": None, "total": 0}
    
    @staticmethod
    def _empty_coating_result() -> Dict[str, Any]:
        return {"type": None, "total": 0}
    
    @staticmethod
    def _empty_emboss_result() -> Dict[str, Any]:
        return {"enabled": False, "total": 0}
    
    @staticmethod
    def _empty_foil_result() -> Dict[str, Any]:
        return {"enabled": False, "total": 0}
