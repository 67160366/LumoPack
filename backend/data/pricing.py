"""
ข้อมูลราคากล่องและวัสดุ
ราคาเป็นบาท สำหรับกล่องขนาด 10x10x10 ซม.
"""

# ==================== ราคากล่องพื้นฐาน ====================
BASE_BOX_PRICES = {
    "RSC": {
        "ลูกฟูก": {
            "cost": 3.378,
            "paper_cost": 22,
            "thickness": 0.25,
            "density": 0.6,
            "labor": 1.2,
            "production_factor": 1.1,
            "description": "กล่องลูกฟูกมาตรฐาน"
        },
        "คราฟท์": {
            "cost": 1.596,
            "paper_cost": 30,
            "thickness": 0.025,
            "density": 0.8,
            "labor": 1.2,
            "production_factor": 1.1,
            "description": "กล่องกระดาษคราฟท์"
        },
    },
    "Die-cut": {
        "ลูกฟูก": {
            "cost": 3.57,
            "paper_cost": 22,
            "thickness": 0.25,
            "density": 0.6,
            "labor": 0.6,
            "production_factor": 1.5,
            "description": "กล่องไดคัทลูกฟูก"
        },
        "จั่วปัง": {
            "cost": 8.6,
            "paper_cost": 40,
            "thickness": 0.25,
            "density": 0.9,
            "labor": 0.6,
            "production_factor": 1.5,
            "description": "กล่องจั่วปัง พรีเมียม"
        },
        "อาร์ต": {
            "cost": 6.67,
            "paper_cost": 200,
            "thickness": 0.0375,
            "density": 0.9,
            "labor": 0.6,
            "production_factor": 1.5,
            "description": "กล่องกระดาษอาร์ต พิมพ์สี่สี"
        },
        "กล่องแป้ง": {
            "cost": 1.93,
            "paper_cost": 40,
            "thickness": 0.04375,
            "density": 0.85,
            "labor": 0.6,
            "production_factor": 1.5,
            "description": "กล่องแป้ง Food-grade"
        },
    }
}

# ==================== ราคา Inner (แผ่นกันกระแทก) ====================
# ราคาเป็นบาท/กก.
INNER_PRICES = {
    "กระดาษฝอย": {
        "min": 120,
        "max": 170,
        "unit": "บาท/kg",
        "weight_per_box": 0.02,  # kg ต่อกล่องขนาดมาตรฐาน
        "description": "กระดาษฝอยรอง กันกระแทก"
    },
    "บับเบิ้ล": {
        "min": 60,
        "max": 90,
        "unit": "บาท/kg",
        "weight_per_box": 0.015,
        "description": "แผ่นบับเบิ้ลกันกระแทก"
    },
    "ถุงลม": {
        "min": 120,
        "max": 200,
        "unit": "บาท/kg",
        "weight_per_box": 0.01,
        "description": "ถุงลมกันกระแทก"
    },
    "โฟม": {
        "min": 80,
        "max": 150,
        "unit": "บาท/kg",
        "weight_per_box": 0.025,
        "description": "โฟมกันกระแทก"
    },
    "กระดาษลูกฟูก": {
        "min": 50,
        "max": 80,
        "unit": "บาท/kg",
        "weight_per_box": 0.03,
        "description": "แผ่นกระดาษลูกฟูกรอง"
    }
}

# ==================== ราคาเคลือบ ====================
COATING_PRICES = {
    # เคลือบกันชื้น
    "AQ Coating": {
        "min": 0.48,
        "max": 1.2,
        "type": "moisture",
        "description": "Acrylic polymer - ต้นทุนต่ำ"
    },
    "PE Coating": {
        "min": 1.2,
        "max": 3.6,
        "type": "moisture",
        "description": "Polyethylene - กันชื้นดี"
    },
    "Wax Coating": {
        "min": 1.2,
        "max": 3.0,
        "type": "moisture",
        "description": "Paraffin wax - กันชื้นดี"
    },
    
    # Food-grade coating
    "Food-grade Water-based": {
        "min": 0.8,
        "max": 1.5,
        "type": "food",
        "description": "เคลือบ Food-grade น้ำ"
    },
    "Food-grade PE": {
        "min": 1.2,
        "max": 2.0,
        "type": "food",
        "description": "เคลือบ Food-grade PE"
    },
    
    # เคลือบเงา
    "Gloss AQ": {
        "min": 0.6,
        "max": 1.2,
        "type": "gloss",
        "description": "เคลือบเงา AQ"
    },
    "UV Gloss": {
        "min": 1.2,
        "max": 2.4,
        "type": "gloss",
        "description": "เคลือบเงา UV"
    },
    
    # เคลือบด้าน
    "UV Matte": {
        "min": 4.0,
        "max": 8.0,
        "type": "matte",
        "description": "เคลือบด้าน UV"
    },
    "Laminate Matte": {
        "min": 6.0,
        "max": 12.0,
        "type": "matte",
        "description": "ลามิเนตด้าน"
    }
}

# ==================== ราคาปั๊ม ====================
EMBOSS_PRICES = {
    "block": {
        "min": 800,
        "max": 1500,
        "unit": "บาท/บล็อก"
    },
    "per_box": 2.0  # บาท/กล่อง
}

FOIL_PRICES = {
    "block": {
        "standard": {"min": 1000, "max": 2000},
        "detailed": {"min": 2000, "max": 3500},
        "emboss_foil": {"min": 2500, "max": 5000}
    },
    "per_box": {
        "1_color": {"min": 2, "max": 5},
        "large": {"min": 5, "max": 10},
        "emboss_foil": {"min": 6, "max": 12}
    }
}

# ==================== ตัวคูณราคาตามลอน ====================
FLUTE_PRICE_MULTIPLIER = {
    "E": 0.9,
    "B": 1.0,
    "C": 1.1,
    "A": 1.2,
    "EB": 1.3,
    "BC": 1.5
}
