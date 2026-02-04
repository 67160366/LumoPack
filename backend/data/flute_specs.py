"""
ข้อมูลลอนกระดาษ (Flute Specifications)
"""

FLUTE_SPECS = {
    "E": {
        "name": "ลอน E (Micro Flute)",
        "name_en": "E-Flute (Micro)",
        "ect": 3.0,  # Edge Crush Test (kN/m)
        "thickness": 1.5,  # mm
        "flutes_per_meter": 290,
        "description": "บาง เรียบ พิมพ์สวย เหมาะกับสินค้าเบา",
        "max_weight": 3,  # kg - น้ำหนักสูงสุดที่รองรับได้
        "use_case": "เครื่องสำอาง, อาหารเบา, ของขวัญ, กล่องแสดงสินค้า",
        "pros": ["พิมพ์ได้คมชัด", "ผิวเรียบ", "ประหยัดพื้นที่"],
        "cons": ["กันกระแทกน้อย", "รับน้ำหนักได้จำกัด"]
    },
    "B": {
        "name": "ลอน B",
        "name_en": "B-Flute",
        "ect": 4.0,
        "thickness": 2.5,  # mm
        "flutes_per_meter": 150,
        "description": "กันกระแทกดี พิมพ์ได้ ใช้งานทั่วไป",
        "max_weight": 10,  # kg
        "use_case": "อาหาร, สินค้าทั่วไป, อิเล็กทรอนิกส์เบา",
        "pros": ["สมดุลระหว่างความแข็งแรงและพิมพ์ได้", "กันกระแทกดี"],
        "cons": ["หนากว่าลอน E"]
    },
    "C": {
        "name": "ลอน C",
        "name_en": "C-Flute",
        "ect": 4.2,
        "thickness": 3.6,  # mm
        "flutes_per_meter": 130,
        "description": "มาตรฐานทั่วไป แข็งแรง กันกระแทกดี",
        "max_weight": 20,  # kg
        "use_case": "สินค้าทั่วไป, ของใช้ในบ้าน, เฟอร์นิเจอร์เล็ก",
        "pros": ["แข็งแรงมาตรฐาน", "ใช้งานได้หลากหลาย", "ราคาเหมาะสม"],
        "cons": ["พิมพ์ได้แต่ไม่คมเท่าลอน E/B"]
    },
    "A": {
        "name": "ลอน A",
        "name_en": "A-Flute",
        "ect": 5.0,
        "thickness": 4.5,  # mm
        "flutes_per_meter": 105,
        "description": "หนา กันกระแทกดีมาก เหมาะกับสินค้าหนัก",
        "max_weight": 30,  # kg
        "use_case": "สินค้าหนัก, เครื่องใช้ไฟฟ้า, อุปกรณ์",
        "pros": ["กันกระแทกดีมาก", "รับน้ำหนักได้มาก"],
        "cons": ["หนา ใช้พื้นที่มาก", "พิมพ์ไม่คม"]
    },
    "BC": {
        "name": "ลอน BC (Double Wall)",
        "name_en": "BC-Flute (Double Wall)",
        "ect": 6.5,
        "thickness": 6.0,  # mm
        "flutes_per_meter": None,  # Combined
        "description": "2 ชั้น (B+C) แข็งแรงสูงสุด",
        "max_weight": 50,  # kg
        "use_case": "สินค้าหนักมาก, เครื่องจักร, ส่งออก, สินค้าแตกง่าย",
        "pros": ["แข็งแรงสูงสุด", "กันกระแทกดีเยี่ยม", "ซ้อนได้หลายชั้น"],
        "cons": ["หนามาก", "ราคาสูง"]
    },
    "EB": {
        "name": "ลอน EB (Double Wall)",
        "name_en": "EB-Flute (Double Wall)",
        "ect": 5.5,
        "thickness": 4.0,  # mm
        "flutes_per_meter": None,
        "description": "2 ชั้น (E+B) แข็งแรงและพิมพ์ได้",
        "max_weight": 25,  # kg
        "use_case": "สินค้าหนักปานกลาง ต้องการพิมพ์สวย",
        "pros": ["พิมพ์ได้ดีกว่า BC", "แข็งแรงพอสมควร"],
        "cons": ["แข็งแรงน้อยกว่า BC"]
    }
}

# ลำดับความแข็งแรง (จากน้อยไปมาก)
FLUTE_STRENGTH_ORDER = ["E", "B", "C", "A", "EB", "BC"]

def get_stronger_flute(current_flute: str) -> str:
    """หาลอนที่แข็งแรงกว่า"""
    try:
        idx = FLUTE_STRENGTH_ORDER.index(current_flute)
        if idx < len(FLUTE_STRENGTH_ORDER) - 1:
            return FLUTE_STRENGTH_ORDER[idx + 1]
    except ValueError:
        pass
    return "BC"

def get_weaker_flute(current_flute: str) -> str:
    """หาลอนที่บางกว่า"""
    try:
        idx = FLUTE_STRENGTH_ORDER.index(current_flute)
        if idx > 0:
            return FLUTE_STRENGTH_ORDER[idx - 1]
    except ValueError:
        pass
    return "E"
