"""
promotion.py
------------
Promotion strategy classes using Strategy Pattern.
Demonstrates: Strategy Pattern, Abstraction, Polymorphism, Encapsulation
Implements business rules for promotional discounts.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime


class PromotionStrategy(ABC):
    """
    Abstract base class for all promotion strategies.
    Demonstrates Strategy Pattern - defines interface for promotion algorithms.
    Each concrete strategy implements different discount logic.
    """
    
    def __init__(self, code: str, description: str, discount_rate: float):
        """
        Initialize promotion strategy.
        
        Args:
            code (str): Promotion code (e.g., "NEWMONASH20")
            description (str): Human-readable description
            discount_rate (float): Discount as decimal (0.20 = 20%)
        """
        self._code = code.upper()
        self._description = description
        self._discount_rate = discount_rate
    
    # Getters
    def get_code(self) -> str:
        """Returns the promotion code."""
        return self._code
    
    def get_description(self) -> str:
        """Returns the promotion description."""
        return self._description
    
    def get_discount_rate(self) -> float:
        """Returns the discount rate as decimal."""
        return self._discount_rate
    
    def get_discount_percentage(self) -> int:
        """Returns the discount as percentage."""
        return int(self._discount_rate * 100)
    
    # Abstract methods (must be implemented by subclasses)
    @abstractmethod
    def is_eligible(self, customer, fulfilment: str, order_repository) -> tuple[bool, str]:
        """
        Checks if customer is eligible for this promotion.
        Must be implemented by each concrete strategy (polymorphism).
        
        Args:
            customer: Customer object
            fulfilment (str): "DELIVERY" or "PICKUP"
            order_repository: OrderRepository for checking history
            
        Returns:
            tuple: (eligible: bool, reason: str)
        """
        pass
    
    @abstractmethod
    def get_eligibility_requirements(self) -> str:
        """
        Returns human-readable eligibility requirements.
        
        Returns:
            str: Requirements description
        """
        pass
    
    # Concrete methods (shared by all strategies)
    def calculate_discount(self, subtotal: float) -> float:
        """
        Calculates discount amount based on subtotal.
        Discount applies to products subtotal only (not delivery fees).
        
        Args:
            subtotal (float): Products subtotal
            
        Returns:
            float: Discount amount
        """
        return round(subtotal * self._discount_rate, 2)
    
    def apply_to_amount(self, amount: float) -> float:
        """
        Applies discount to an amount and returns final price.
        
        Args:
            amount (float): Original amount
            
        Returns:
            float: Amount after discount
        """
        discount = self.calculate_discount(amount)
        return round(amount - discount, 2)
    
    def validate_and_calculate(self, customer, fulfilment: str, 
                               subtotal: float, order_repository) -> tuple[bool, float, str]:
        """
        Validates eligibility and calculates discount in one operation.
        
        Args:
            customer: Customer object
            fulfilment (str): Fulfilment type
            subtotal (float): Products subtotal
            order_repository: Order repository
            
        Returns:
            tuple: (valid: bool, discount_amount: float, message: str)
        """
        eligible, reason = self.is_eligible(customer, fulfilment, order_repository)
        if not eligible:
            return False, 0.0, reason
        
        discount = self.calculate_discount(subtotal)
        return True, discount, f"{self.get_code()} applied: -${discount:.2f}"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self._code}: {self._description} ({self.get_discount_percentage()}% off)"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return f"PromotionStrategy(code={self._code}, rate={self._discount_rate})"


class NewMonashPromotion(PromotionStrategy):
    """
    NEWMONASH20 promotion strategy.
    20% off products subtotal for first-time PICKUP orders only.
    Demonstrates concrete implementation of Strategy Pattern.
    """
    
    CODE = "NEWMONASH20"
    DISCOUNT_RATE = 0.20  # 20%
    DESCRIPTION = "20% off products subtotal - first-time PICKUP order only"
    
    def __init__(self):
        """Initialize NewMonash promotion with predefined values."""
        super().__init__(
            code=self.CODE,
            description=self.DESCRIPTION,
            discount_rate=self.DISCOUNT_RATE
        )
    
    def is_eligible(self, customer, fulfilment: str, order_repository) -> tuple[bool, str]:
        """
        Checks eligibility for NEWMONASH20 promotion.
        
        Business Rules:
        1. Must be PICKUP order
        2. Customer must not have any previous PICKUP orders
        
        Args:
            customer: Customer object
            fulfilment (str): "DELIVERY" or "PICKUP"
            order_repository: OrderRepository to check history
            
        Returns:
            tuple: (eligible: bool, reason: str)
        """
        # Rule 1: Must be pickup order
        if fulfilment.upper() != "PICKUP":
            return False, f"{self.CODE} is only valid for PICKUP orders"
        
        # Rule 2: Must be first-time pickup
        has_pickup = order_repository.customer_has_pickup_order(customer.get_email())
        if has_pickup:
            return False, f"{self.CODE} is only valid for your first PICKUP order"
        
        return True, ""
    
    def get_eligibility_requirements(self) -> str:
        """
        Returns eligibility requirements.
        
        Returns:
            str: Requirements description
        """
        return "Must be your first PICKUP order (not available for delivery)"
    
    def __str__(self) -> str:
        """String representation."""
        return f"NEWMONASH20: First-time pickup 20% off"


class StaffPromotion(PromotionStrategy):
    """
    STAFF5 promotion strategy.
    5% off products subtotal - available to all customers with no restrictions.
    Demonstrates second promotion strategy (requirement for 4-member teams).
    
    Business Justification:
    - Rewards Monash staff members
    - Lower discount rate encourages repeat purchases
    - No restrictions to maximize usage
    - Can be combined with VIP pricing
    """
    
    CODE = "STAFF5"
    DISCOUNT_RATE = 0.05  # 5%
    DESCRIPTION = "5% off products subtotal - available for all orders"
    
    def __init__(self):
        """Initialize Staff promotion with predefined values."""
        super().__init__(
            code=self.CODE,
            description=self.DESCRIPTION,
            discount_rate=self.DISCOUNT_RATE
        )
    
    def is_eligible(self, customer, fulfilment: str, order_repository) -> tuple[bool, str]:
        """
        Checks eligibility for STAFF5 promotion.
        
        Business Rules:
        - No restrictions - available to all customers
        - Works with both DELIVERY and PICKUP
        - Can be used multiple times
        
        Args:
            customer: Customer object
            fulfilment (str): "DELIVERY" or "PICKUP"
            order_repository: OrderRepository (not used for this promo)
            
        Returns:
            tuple: (eligible: bool, reason: str) - always eligible
        """
        # No restrictions for STAFF5
        return True, ""
    
    def get_eligibility_requirements(self) -> str:
        """
        Returns eligibility requirements.
        
        Returns:
            str: Requirements description
        """
        return "Available for all customers on all orders (delivery or pickup)"
    
    def __str__(self) -> str:
        """String representation."""
        return "STAFF5: 5% off all orders"


class PromotionFactory:
    """
    Factory class for creating and managing promotion strategies.
    Demonstrates Factory Pattern for promotion creation.
    Provides central registry of all available promotions.
    """
    
    # Registry of all available promotions (Singleton pattern for each promo)
    _promotions: Dict[str, PromotionStrategy] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls) -> None:
        """
        Initializes the promotion registry with all available promotions.
        Called once at application startup.
        """
        if not cls._initialized:
            cls._promotions = {
                NewMonashPromotion.CODE: NewMonashPromotion(),
                StaffPromotion.CODE: StaffPromotion()
            }
            cls._initialized = True
    
    @classmethod
    def get_promotion(cls, code: str) -> Optional[PromotionStrategy]:
        """
        Gets a promotion strategy by code.
        
        Args:
            code (str): Promotion code
            
        Returns:
            PromotionStrategy or None if code not found
        """
        cls.initialize()  # Ensure initialized
        return cls._promotions.get(code.upper())
    
    @classmethod
    def get_all_promotions(cls) -> Dict[str, PromotionStrategy]:
        """
        Returns all available promotions.
        
        Returns:
            dict: Map of code -> PromotionStrategy
        """
        cls.initialize()
        return cls._promotions.copy()
    
    @classmethod
    def get_promotion_codes(cls) -> list[str]:
        """
        Returns list of all valid promotion codes.
        
        Returns:
            list: Promotion codes
        """
        cls.initialize()
        return list(cls._promotions.keys())
    
    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        """
        Checks if a promotion code is valid.
        
        Args:
            code (str): Promotion code to check
            
        Returns:
            bool: True if code exists
        """
        cls.initialize()
        return code.upper() in cls._promotions
    
    @classmethod
    def get_promotion_list_display(cls) -> str:
        """
        Returns formatted string of all promotions for display.
        
        Returns:
            str: Multi-line string listing all promotions
        """
        cls.initialize()
        lines = ["Available Promotion Codes:"]
        for promo in cls._promotions.values():
            lines.append(f"  • {promo.get_code()}: {promo.get_description()}")
            lines.append(f"    Requirements: {promo.get_eligibility_requirements()}")
        return "\n".join(lines)
    
    @classmethod
    def register_promotion(cls, promotion: PromotionStrategy) -> bool:
        """
        Registers a new promotion strategy (for future extensibility).
        
        Args:
            promotion (PromotionStrategy): Promotion to register
            
        Returns:
            bool: True if registered, False if code already exists
        """
        cls.initialize()
        code = promotion.get_code()
        if code in cls._promotions:
            return False
        cls._promotions[code] = promotion
        return True


class PromotionValidator:
    """
    Utility class for validating and applying promotions.
    Demonstrates Separation of Concerns - validation logic separate from strategies.
    """
    
    def __init__(self, order_repository):
        """
        Initialize validator.
        
        Args:
            order_repository: OrderRepository for checking order history
        """
        self._order_repo = order_repository
        PromotionFactory.initialize()
    
    def validate_promotion(self, code: str, customer, fulfilment: str) -> tuple[bool, str, Optional[PromotionStrategy]]:
        """
        Validates a promotion code for a specific customer and order.
        
        Args:
            code (str): Promotion code
            customer: Customer object
            fulfilment (str): "DELIVERY" or "PICKUP"
            
        Returns:
            tuple: (valid: bool, message: str, promotion: PromotionStrategy or None)
        """
        # First, check if this promotion code actually exists in our system
        promotion = PromotionFactory.get_promotion(code)
        if not promotion:
            return False, f"Invalid promotion code: {code}", None
        
        # Now check if this customer is actually eligible for this promotion
        # (e.g., NEWMONASH20 only works for first-time pickup orders)
        eligible, reason = promotion.is_eligible(customer, fulfilment, self._order_repo)
        if not eligible:
            return False, reason, None
        
        # If we get here, the promotion is valid and can be used
        return True, f"{promotion.get_code()} is valid and applicable", promotion
    
    def apply_best_promotion(self, codes: list[str], customer, fulfilment: str, subtotal: float) -> tuple[Optional[PromotionStrategy], float, str]:
        """
        From a list of codes, finds and applies the best (highest discount) eligible promotion.
        
        Args:
            codes (list): List of promotion codes to try
            customer: Customer object
            fulfilment (str): Fulfilment type
            subtotal (float): Products subtotal
            
        Returns:
            tuple: (best_promotion: PromotionStrategy or None, discount: float, message: str)
        """
        best_promotion = None
        best_discount = 0.0
        best_message = "No eligible promotions found"
        
        for code in codes:
            valid, message, promotion = self.validate_promotion(code, customer, fulfilment)
            if valid:
                discount = promotion.calculate_discount(subtotal)
                if discount > best_discount:
                    best_promotion = promotion
                    best_discount = discount
                    best_message = f"Applied {promotion.get_code()}: -${discount:.2f}"
        
        return best_promotion, best_discount, best_message
    
    def get_eligible_promotions(self, customer, fulfilment: str) -> list[PromotionStrategy]:
        """
        Returns all promotions eligible for a customer and order type.
        
        Args:
            customer: Customer object
            fulfilment (str): Fulfilment type
            
        Returns:
            list: List of eligible PromotionStrategy objects
        """
        eligible = []
        for promotion in PromotionFactory.get_all_promotions().values():
            is_eligible, _ = promotion.is_eligible(customer, fulfilment, self._order_repo)
            if is_eligible:
                eligible.append(promotion)
        return eligible


class PromotionManager:
    """
    High-level manager for promotion operations.
    Demonstrates Facade Pattern - simplified interface for complex promotion logic.
    """
    
    def __init__(self, order_repository):
        """
        Initialize promotion manager.
        
        Args:
            order_repository: OrderRepository for validation
        """
        self._validator = PromotionValidator(order_repository)
        self._current_promotion: Optional[PromotionStrategy] = None
    
    def apply_promotion(self, code: str, customer, fulfilment: str) -> tuple[bool, str]:
        """
        Applies a promotion code to the current order context.
        
        Args:
            code (str): Promotion code
            customer: Customer object
            fulfilment (str): Fulfilment type
            
        Returns:
            tuple: (success: bool, message: str)
        """
        valid, message, promotion = self._validator.validate_promotion(code, customer, fulfilment)
        if valid:
            self._current_promotion = promotion
            return True, message
        return False, message
    
    def get_current_promotion(self) -> Optional[PromotionStrategy]:
        """
        Returns the currently applied promotion.
        
        Returns:
            PromotionStrategy or None
        """
        return self._current_promotion
    
    def clear_promotion(self) -> None:
        """Clears the currently applied promotion."""
        self._current_promotion = None
    
    def calculate_current_discount(self, subtotal: float) -> float:
        """
        Calculates discount for currently applied promotion.
        
        Args:
            subtotal (float): Products subtotal
            
        Returns:
            float: Discount amount (0 if no promotion applied)
        """
        if self._current_promotion:
            return self._current_promotion.calculate_discount(subtotal)
        return 0.0
    
    def get_promotion_summary(self, subtotal: float) -> Dict:
        """
        Returns summary of current promotion application.
        
        Args:
            subtotal (float): Products subtotal
            
        Returns:
            dict: Promotion summary information
        """
        if not self._current_promotion:
            return {
                "has_promotion": False,
                "code": "",
                "description": "",
                "discount": 0.0,
                "final_amount": subtotal
            }
        
        discount = self._current_promotion.calculate_discount(subtotal)
        return {
            "has_promotion": True,
            "code": self._current_promotion.get_code(),
            "description": self._current_promotion.get_description(),
            "discount": discount,
            "final_amount": round(subtotal - discount, 2)
        }


# Initialize promotions when module is loaded
PromotionFactory.initialize()