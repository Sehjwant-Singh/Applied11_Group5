"""
product.py
----------
Product entity classes with proper OOP design.
Demonstrates: Encapsulation, Inheritance, Polymorphism, Abstraction
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict


class Product:
    """
    Base Product class representing items in the supermarket.
    Demonstrates encapsulation with private attributes and public methods.
    """
    
    def __init__(self, sku: str, name: str, brand: str, description: str,
                 category: str, subcategory: str, price: float,
                 member_price: float, quantity: int):
        """
        Initialize a Product instance.
        
        Args:
            sku (str): Stock Keeping Unit - unique product identifier
            name (str): Product name
            brand (str): Brand name
            description (str): Product description
            category (str): Product category
            subcategory (str): Product subcategory
            price (float): Regular price
            member_price (float): VIP member price
            quantity (int): Available stock quantity
        """
        # Private attributes (encapsulation)
        self.__sku = sku
        self.__name = name
        self.__brand = brand
        self.__description = description
        self.__category = category
        self.__subcategory = subcategory
        self.__price = price
        self.__member_price = member_price
        self.__quantity = quantity
    
    # Getters (Accessor methods)
    def get_sku(self) -> str:
        """Returns the product SKU."""
        return self.__sku
    
    def get_name(self) -> str:
        """Returns the product name."""
        return self.__name
    
    def get_brand(self) -> str:
        """Returns the product brand."""
        return self.__brand
    
    def get_description(self) -> str:
        """Returns the product description."""
        return self.__description
    
    def get_category(self) -> str:
        """Returns the product category."""
        return self.__category
    
    def get_subcategory(self) -> str:
        """Returns the product subcategory."""
        return self.__subcategory
    
    def get_price(self) -> float:
        """Returns the regular price."""
        return self.__price
    
    def get_member_price(self) -> float:
        """Returns the VIP member price."""
        return self.__member_price
    
    def get_quantity(self) -> int:
        """Returns the available stock quantity."""
        return self.__quantity
    
    def get_effective_price(self, is_vip: bool = False) -> float:
        """
        Returns the effective price based on VIP status.
        Demonstrates polymorphic behavior based on customer type.
        
        Args:
            is_vip (bool): Whether customer has VIP membership
            
        Returns:
            float: Member price if VIP, regular price otherwise
        """
        return self.__member_price if is_vip else self.__price
    
    # Setters (Mutator methods) with validation
    def set_name(self, name: str) -> None:
        """Updates product name."""
        if name and name.strip():
            self.__name = name.strip()
    
    def set_brand(self, brand: str) -> None:
        """Updates product brand."""
        if brand and brand.strip():
            self.__brand = brand.strip()
    
    def set_description(self, description: str) -> None:
        """Updates product description."""
        self.__description = description.strip()
    
    def set_category(self, category: str) -> None:
        """Updates product category."""
        if category and category.strip():
            self.__category = category.strip()
    
    def set_subcategory(self, subcategory: str) -> None:
        """Updates product subcategory."""
        if subcategory and subcategory.strip():
            self.__subcategory = subcategory.strip()
    
    def set_price(self, price: float) -> bool:
        """
        Updates regular price with validation.
        
        Args:
            price (float): New price
            
        Returns:
            bool: True if successful, False if invalid
        """
        if price > 0:
            self.__price = price
            return True
        return False
    
    def set_member_price(self, member_price: float) -> bool:
        """
        Updates member price with validation.
        Member price cannot exceed regular price.
        
        Args:
            member_price (float): New member price
            
        Returns:
            bool: True if successful, False if invalid
        """
        if 0 < member_price <= self.__price:
            self.__member_price = member_price
            return True
        return False
    
    def set_quantity(self, quantity: int) -> bool:
        """
        Updates stock quantity with validation.
        
        Args:
            quantity (int): New quantity
            
        Returns:
            bool: True if successful, False if invalid
        """
        if quantity >= 0:
            self.__quantity = quantity
            return True
        return False
    
    # Business logic methods (encapsulated behavior)
    def is_in_stock(self) -> bool:
        """
        Checks if product is available for purchase.
        
        Returns:
            bool: True if quantity > 0
        """
        return self.__quantity > 0
    
    def reduce_quantity(self, amount: int) -> bool:
        """
        Reduces stock quantity (used during checkout).
        
        Args:
            amount (int): Quantity to reduce
            
        Returns:
            bool: True if successful, False if insufficient stock
        """
        if amount <= 0:
            return False
        if amount > self.__quantity:
            return False
        self.__quantity -= amount
        return True
    
    def increase_quantity(self, amount: int) -> bool:
        """
        Increases stock quantity (used during inventory management).
        
        Args:
            amount (int): Quantity to add
            
        Returns:
            bool: True if successful, False if invalid amount
        """
        if amount <= 0:
            return False
        self.__quantity += amount
        return True
    
    def is_food_product(self) -> bool:
        """
        Determines if this is a food product.
        To be overridden by FoodProduct subclass (polymorphism).
        
        Returns:
            bool: False for base Product, True for FoodProduct
        """
        return False
    
    def get_food_details(self) -> Optional[Dict]:
        """
        Returns food-specific details.
        To be overridden by FoodProduct subclass (polymorphism).
        
        Returns:
            None for base Product, dict for FoodProduct
        """
        return None
    
    def to_dict(self) -> Dict:
        """
        Converts Product object to dictionary for CSV persistence.
        
        Returns:
            dict: Product data as dictionary
        """
        return {
            "sku": self.__sku,
            "name": self.__name,
            "brand": self.__brand,
            "description": self.__description,
            "category": self.__category,
            "subcategory": self.__subcategory,
            "price": f"{self.__price:.2f}",
            "member_price": f"{self.__member_price:.2f}",
            "quantity": str(self.__quantity),
            "is_food": "False",
            "expiry_date": "",
            "ingredients": "",
            "storage": "",
            "allergens": ""
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return (f"Product(sku={self.__sku}, name={self.__name}, "
                f"price=${self.__price:.2f}, qty={self.__quantity})")
    
    def __repr__(self) -> str:
        """Official string representation."""
        return self.__str__()


class FoodProduct(Product):
    """
    FoodProduct class extending Product with food-specific attributes.
    Demonstrates inheritance and polymorphism.
    """
    
    def __init__(self, sku: str, name: str, brand: str, description: str,
                 category: str, subcategory: str, price: float,
                 member_price: float, quantity: int,
                 expiry_date: str, ingredients: str, 
                 storage: str, allergens: str):
        """
        Initialize a FoodProduct instance.
        
        Args:
            All Product args plus:
            expiry_date (str): Expiration date (ISO format)
            ingredients (str): List of ingredients
            storage (str): Storage instructions
            allergens (str): Allergen information
        """
        # Call parent constructor (inheritance)
        super().__init__(sku, name, brand, description, category,
                        subcategory, price, member_price, quantity)
        
        # Food-specific private attributes
        self.__expiry_date = expiry_date
        self.__ingredients = ingredients
        self.__storage = storage
        self.__allergens = allergens
    
    # Food-specific getters
    def get_expiry_date(self) -> str:
        """Returns the expiry date."""
        return self.__expiry_date
    
    def get_ingredients(self) -> str:
        """Returns the ingredients list."""
        return self.__ingredients
    
    def get_storage(self) -> str:
        """Returns storage instructions."""
        return self.__storage
    
    def get_allergens(self) -> str:
        """Returns allergen information."""
        return self.__allergens
    
    # Food-specific setters
    def set_expiry_date(self, expiry_date: str) -> None:
        """Updates expiry date."""
        self.__expiry_date = expiry_date
    
    def set_ingredients(self, ingredients: str) -> None:
        """Updates ingredients list."""
        self.__ingredients = ingredients
    
    def set_storage(self, storage: str) -> None:
        """Updates storage instructions."""
        self.__storage = storage
    
    def set_allergens(self, allergens: str) -> None:
        """Updates allergen information."""
        self.__allergens = allergens
    
    # Polymorphism - Overriding parent methods
    def is_food_product(self) -> bool:
        """
        Override: Returns True for food products.
        
        Returns:
            bool: Always True for FoodProduct
        """
        return True
    
    def get_food_details(self) -> Dict:
        """
        Override: Returns food-specific details.
        
        Returns:
            dict: Food details including expiry, ingredients, etc.
        """
        return {
            "expiry_date": self.__expiry_date,
            "ingredients": self.__ingredients,
            "storage": self.__storage,
            "allergens": self.__allergens
        }
    
    # Food-specific business logic
    def is_expired(self) -> bool:
        """
        Checks if the food product has expired.
        
        Returns:
            bool: True if expired, False otherwise
        """
        if not self.__expiry_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.__expiry_date)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return False
    
    def has_allergen(self, allergen: str) -> bool:
        """
        Checks if product contains a specific allergen.
        
        Args:
            allergen (str): Allergen to check for
            
        Returns:
            bool: True if allergen present
        """
        if not self.__allergens or not allergen:
            return False
        return allergen.lower() in self.__allergens.lower()
    
    # Override to_dict to include food-specific fields
    def to_dict(self) -> Dict:
        """
        Converts FoodProduct to dictionary for CSV persistence.
        
        Returns:
            dict: Product data including food-specific fields
        """
        base_dict = super().to_dict()
        base_dict.update({
            "is_food": "True",
            "expiry_date": self.__expiry_date,
            "ingredients": self.__ingredients,
            "storage": self.__storage,
            "allergens": self.__allergens
        })
        return base_dict
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return (f"FoodProduct(sku={self.get_sku()}, name={self.get_name()}, "
                f"expires={self.__expiry_date}, allergens={self.__allergens})")


# Factory Pattern for creating products
class ProductFactory:
    """
    Factory class for creating Product instances.
    Demonstrates Factory design pattern.
    """
    
    @staticmethod
    def create_product(product_data: Dict) -> Product:
        """
        Creates appropriate Product or FoodProduct instance from dictionary.
        
        Args:
            product_data (dict): Product data from CSV
            
        Returns:
            Product or FoodProduct instance
        """
        is_food = product_data.get("is_food", "").lower() in ("true", "1")
        
        if is_food:
            return FoodProduct(
                sku=product_data["sku"],
                name=product_data["name"],
                brand=product_data["brand"],
                description=product_data["description"],
                category=product_data["category"],
                subcategory=product_data["subcategory"],
                price=float(product_data["price"]),
                member_price=float(product_data["member_price"]),
                quantity=int(product_data["quantity"]),
                expiry_date=product_data.get("expiry_date", ""),
                ingredients=product_data.get("ingredients", ""),
                storage=product_data.get("storage", ""),
                allergens=product_data.get("allergens", "")
            )
        else:
            return Product(
                sku=product_data["sku"],
                name=product_data["name"],
                brand=product_data["brand"],
                description=product_data["description"],
                category=product_data["category"],
                subcategory=product_data["subcategory"],
                price=float(product_data["price"]),
                member_price=float(product_data["member_price"]),
                quantity=int(product_data["quantity"])
            )
    
    @staticmethod
    def create_from_input(field_values: Dict) -> Product:
        """
        Creates Product from user input during admin product creation.
        
        Args:
            field_values (dict): Raw input values
            
        Returns:
            Product or FoodProduct instance
        """
        return ProductFactory.create_product(field_values)