"""
Price Calculator - คำนวณราคากล่อง
"""
from typing import Dict, Any, Optional
from data.pricing import (
    BASE_BOX_PRICES, 
    INNER_PRICES, 
    COATING_PRICES,
    EMBOSS_PRICES,
    FOIL_PRICES,
    FLUTE_PRICE_MULTIPLIER
)
from data.materials import get_material_recommendation


class PriceCalculator:
    """คลาสสำหรับคำนวณราคากล่อง"""
    
    BASE_SURFACE_AREA = 600  # พื้นที่ผิวกล่อง 10x10x10 cm
    
    def calculate_surface_area(
        self,
        width: float,
        length: float,
        height: float
    ) -> float:
        """คำนวณพื้นที่ผิวกล่อง 6 ด้าน"""
        return 2 * ((width * length) + (width * height) + (length * height))
    
    def calculate_factor(
        self,
        width: float,
        length: float,
        height: float,
        box_type: str = "RSC"
    ) -> float:
        """คำนวณ Factor เทียบกับกล่องมาตรฐาน 10x10x10"""
        production_factor = 1.1 if box_type == "RSC" else 1.5
        base_area_with_factor = self.BASE_SURFACE_AREA * production_factor
        new_area = self.calculate_surface_area(width, length, height) * production_factor
        return max(1.0, new_area / base_area_with_factor)
    
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
        factor = self.calculate_factor(width, length, height, box_type)
        
        # ดึงราคาพื้นฐาน
        box_prices = BASE_BOX_PRICES.get(box_type, BASE_BOX_PRICES["RSC"])
        material_data = box_prices.get(material, box_prices.get("ลูกฟูก", {"cost": 3.5}))
        base_price = material_data["cost"]
        
        # ปรับราคาตามลอน
        flute_multiplier = FLUTE_PRICE_MULTIPLIER.get(flute_type, 1.0)
        
        # คำนวณราคา
        price_per_box = base_price * factor * flute_multiplier
        total_price = price_per_box * quantity
        
        return {
            "box_type": box_type,
            "material": material,
            "flute_type": flute_type,
            "dimensions": {
                "width": width,
                "length": length,
                "height": height
            },
            "quantity": quantity,
            "factor": round(factor, 2),
            "flute_multiplier": flute_multiplier,
            "price_per_box": round(price_per_box, 2),
            "total_price": round(total_price, 2)
        }
    
    def calculate_inner_price(
        self,
        inner_type: str,
        factor: float,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคา Inner (แผ่นกันกระแทก)"""
        if not inner_type or inner_type not in INNER_PRICES:
            return {"type": None, "total": 0}
        
        price_data = INNER_PRICES[inner_type]
        avg_price_per_kg = (price_data["min"] + price_data["max"]) / 2
        weight = price_data["weight_per_box"] * factor
        total = avg_price_per_kg * weight * quantity
        
        return {
            "type": inner_type,
            "price_per_kg": avg_price_per_kg,
            "weight_per_box": round(weight, 4),
            "total": round(total, 2)
        }
    
    def calculate_coating_price(
        self,
        coating_type: str,
        factor: float,
        quantity: int
    ) -> Dict[str, Any]:
        """คำนวณราคาเคลือบ"""
        if not coating_type or coating_type not in COATING_PRICES:
            return {"type": None, "total": 0}
        
        price_data = COATING_PRICES[coating_type]
        avg_price = (price_data["min"] + price_data["max"]) / 2 * factor
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
            return {"enabled": False, "total": 0}
        
        block_cost = 0
        if not has_existing_block:
            block_cost = (EMBOSS_PRICES["block"]["min"] + EMBOSS_PRICES["block"]["max"]) / 2
        
        per_box_cost = EMBOSS_PRICES["per_box"] * quantity
        total = block_cost + per_box_cost
        
        return {
            "enabled": True,
            "block_cost": block_cost,
            "per_box_cost": round(per_box_cost, 2),
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
            return {"enabled": False, "total": 0}
        
        # ค่าบล็อก
        block_cost = 0
        if not has_existing_block:
            if "นูน" in foil_type:
                block_data = FOIL_PRICES["block"]["emboss_foil"]
            elif "ละเอียด" in foil_type or "ใหญ่" in foil_type:
                block_data = FOIL_PRICES["block"]["detailed"]
            else:
                block_data = FOIL_PRICES["block"]["standard"]
            block_cost = (block_data["min"] + block_data["max"]) / 2
        
        # ค่าปั๊มต่อกล่อง
        if "นูน" in foil_type:
            per_box_data = FOIL_PRICES["per_box"]["emboss_foil"]
        elif "ละเอียด" in foil_type or "ใหญ่" in foil_type:
            per_box_data = FOIL_PRICES["per_box"]["large"]
        else:
            per_box_data = FOIL_PRICES["per_box"]["1_color"]
        
        avg_per_box = (per_box_data["min"] + per_box_data["max"]) / 2
        per_box_cost = avg_per_box * quantity
        total = block_cost + per_box_cost
        
        return {
            "enabled": True,
            "type": foil_type,
            "block_cost": block_cost,
            "per_box_cost": round(per_box_cost, 2),
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
            ใบเสนอราคา
        """
        # ดึงข้อมูลขนาดกล่อง
        dims = box_design.get("recommended_size_cm", {"width": 10, "length": 10, "height": 10})
        flute = box_design.get("flute", "B")
        
        # เลือกวัสดุตามประเภทสินค้า
        material_rec = get_material_recommendation(product_type, box_type)
        material = material_rec["material"]
        
        # คำนวณราคากล่อง
        box_price = self.calculate_box_price(
            dims["width"], dims["length"], dims["height"],
            box_type, material, flute, quantity
        )
        
        factor = box_price["factor"]
        
        # คำนวณราคา options
        inner_price = self.calculate_inner_price(inner_type, factor, quantity)
        coating_price = self.calculate_coating_price(coating_type, factor, quantity)
        emboss_price = self.calculate_emboss_price(has_emboss, has_emboss_block, quantity)
        foil_price = self.calculate_foil_price(foil_type, has_foil_block, quantity)
        
        # รวมราคา
        grand_total = (
            box_price["total_price"] +
            inner_price["total"] +
            coating_price["total"] +
            emboss_price["total"] +
            foil_price["total"]
        )
        
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
                "inner": inner_price,
                "coating": coating_price,
                "emboss": emboss_price,
                "foil": foil_price
            },
            "totals": {
                "box_total": box_price["total_price"],
                "options_total": round(
                    inner_price["total"] + 
                    coating_price["total"] + 
                    emboss_price["total"] + 
                    foil_price["total"], 2
                ),
                "grand_total": round(grand_total, 2),
                "price_per_unit": round(grand_total / quantity, 2)
            }
        }
