"""
Custom exceptions for LumoPack
"""


class LumoPackError(Exception):
    """Base exception for LumoPack"""
    pass


class ValidationError(LumoPackError):
    """Raised when input validation fails"""
    pass


class InvalidDimensionsError(ValidationError):
    """Raised when box dimensions are invalid"""
    def __init__(self, width: float, length: float, height: float):
        self.width = width
        self.length = length
        self.height = height
        super().__init__(
            f"Invalid dimensions: {width} x {length} x {height} cm. "
            "All dimensions must be positive."
        )


class InvalidWeightError(ValidationError):
    """Raised when weight is invalid"""
    def __init__(self, weight: float):
        self.weight = weight
        super().__init__(f"Invalid weight: {weight} kg. Weight must be non-negative.")


class NoProductsError(ValidationError):
    """Raised when no products are provided"""
    def __init__(self):
        super().__init__("No products provided. At least one product is required.")


class InvalidFluteTypeError(ValidationError):
    """Raised when flute type is invalid"""
    def __init__(self, flute_type: str):
        self.flute_type = flute_type
        super().__init__(
            f"Invalid flute type: '{flute_type}'. "
            "Valid types are: E, B, C, A, BC, EB"
        )


class InvalidBoxTypeError(ValidationError):
    """Raised when box type is invalid"""
    def __init__(self, box_type: str):
        self.box_type = box_type
        super().__init__(
            f"Invalid box type: '{box_type}'. "
            "Valid types are: RSC, Die-cut"
        )


class InvalidQuantityError(ValidationError):
    """Raised when quantity is invalid"""
    def __init__(self, quantity: int, min_quantity: int = 1):
        self.quantity = quantity
        self.min_quantity = min_quantity
        super().__init__(
            f"Invalid quantity: {quantity}. "
            f"Minimum quantity is {min_quantity}."
        )


class AIServiceError(LumoPackError):
    """Raised when AI service fails"""
    pass


class AINotConfiguredError(AIServiceError):
    """Raised when AI API key is not configured"""
    def __init__(self):
        super().__init__(
            "AI service not configured. "
            "Please set GROQ_API_KEY environment variable."
        )


class AIResponseError(AIServiceError):
    """Raised when AI returns unexpected response"""
    def __init__(self, message: str = "Unexpected AI response"):
        super().__init__(message)


class PricingError(LumoPackError):
    """Raised when pricing calculation fails"""
    pass


class MaterialNotFoundError(PricingError):
    """Raised when material is not found in pricing data"""
    def __init__(self, material: str, box_type: str):
        self.material = material
        self.box_type = box_type
        super().__init__(
            f"Material '{material}' not found for box type '{box_type}'."
        )
