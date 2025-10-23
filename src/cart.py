"""
cart.py
-------
Shopping cart classes with proper OOP design.
Demonstrates: Encapsulation, Composition, Business Rule Enforcement
Handles cart items, cart management, and shopping constraints.
"""

from typing import List, Optional, Dict
from product import Product
import time


class CartItem:
    """
    Represents a single item in the shopping cart.
    Demonstrates encapsulation of cart line logic.
    """
    
    MAX_QUANTITY_PER_ITEM = 10
    
    def __init__(self, product: Product, quantity: int):
        """
        Initialize a cart item.
        
        Args:
            product (Product): Product object
            quantity (int): Quantity to purchase (1-10)
            
        Raises:
            ValueError: If quantity is invalid
        """
        if quantity < 1 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Quantity must be between 1 and {self.MAX_QUANTITY_PER_ITEM}")
        
        self._product = product
        self._quantity = quantity
        self._time_added = time.time()  # Track when added for ordering
    
    # Getters
    def get_product(self) -> Product:
        """Returns the product object."""
        return self._product
    
    def get_quantity(self) -> int:
        """Returns the quantity."""
        return self._quantity
    
    def get_time_added(self) -> float:
        """Returns timestamp when item was added."""
        return self._time_added
    
    def get_sku(self) -> str:
        """Returns product SKU for convenience."""
        return self._product.get_sku()
    
    def get_name(self) -> str:
        """Returns product name for convenience."""
        return self._product.get_name()
    
    # Setters with validation
    def set_quantity(self, quantity: int) -> bool:
        """
        Updates quantity with validation.
        
        Args:
            quantity (int): New quantity
            
        Returns:
            bool: True if successful, False if invalid
        """
        if quantity < 1 or quantity > self.MAX_QUANTITY_PER_ITEM:
            return False
        self._quantity = quantity
        return True
    
    def increase_quantity(self, amount: int = 1) -> bool:
        """
        Increases quantity by specified amount.
        
        Args:
            amount (int): Amount to increase
            
        Returns:
            bool: True if successful, False if would exceed max
        """
        new_qty = self._quantity + amount
        if new_qty > self.MAX_QUANTITY_PER_ITEM:
            return False
        self._quantity = new_qty
        return True
    
    def decrease_quantity(self, amount: int = 1) -> bool:
        """
        Decreases quantity by specified amount.
        
        Args:
            amount (int): Amount to decrease
            
        Returns:
            bool: True if successful, False if would go below 1
        """
        new_qty = self._quantity - amount
        if new_qty < 1:
            return False
        self._quantity = new_qty
        return True
    
    # Price calculations
    def get_unit_price(self, is_vip: bool = False) -> float:
        """
        Returns unit price based on VIP status.
        
        Args:
            is_vip (bool): Whether customer is VIP
            
        Returns:
            float: Unit price
        """
        return self._product.get_effective_price(is_vip)
    
    def get_line_total(self, is_vip: bool = False) -> float:
        """
        Calculates line total (unit price × quantity).
        
        Args:
            is_vip (bool): Whether customer is VIP
            
        Returns:
            float: Line total
        """
        return round(self.get_unit_price(is_vip) * self._quantity, 2)
    
    def get_regular_price(self) -> float:
        """Returns regular unit price."""
        return self._product.get_price()
    
    def get_member_price(self) -> float:
        """Returns VIP member unit price."""
        return self._product.get_member_price()
    
    # Stock validation
    def validate_stock(self) -> tuple[bool, str]:
        """
        Validates if sufficient stock available.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self._product.is_in_stock():
            return False, f"{self._product.get_name()} is out of stock"
        
        available = self._product.get_quantity()
        if self._quantity > available:
            return False, f"Only {available} units of {self._product.get_name()} available"
        
        return True, ""
    
    # Conversion methods
    def to_dict(self) -> Dict:
        """
        Converts CartItem to dictionary.
        
        Returns:
            dict: Cart item data
        """
        return {
            "sku": self.get_sku(),
            "name": self.get_name(),
            "unit_price": self.get_regular_price(),
            "member_price": self.get_member_price(),
            "qty": self._quantity,
            "time_added": self._time_added
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"CartItem({self.get_sku()}: {self.get_name()} × {self._quantity})"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return self.__str__()


class ShoppingCart:
    """
    Shopping cart with business rules enforcement.
    Demonstrates encapsulation of cart constraints and operations.
    """
    
    MAX_TOTAL_ITEMS = 20
    MAX_QUANTITY_PER_PRODUCT = 10
    
    def __init__(self):
        """Initialize an empty shopping cart."""
        self._items: List[CartItem] = []
    
    # Query methods
    def is_empty(self) -> bool:
        """
        Checks if cart is empty.
        
        Returns:
            bool: True if no items in cart
        """
        return len(self._items) == 0
    
    def get_item_count(self) -> int:
        """
        Returns number of distinct items in cart.
        
        Returns:
            int: Number of cart items
        """
        return len(self._items)
    
    def get_total_quantity(self) -> int:
        """
        Returns total quantity of all items.
        
        Returns:
            int: Sum of all quantities
        """
        return sum(item.get_quantity() for item in self._items)
    
    def get_items(self) -> List[CartItem]:
        """
        Returns all cart items ordered by time added.
        
        Returns:
            list: CartItem objects sorted by time_added
        """
        return sorted(self._items, key=lambda x: x.get_time_added())
    
    def find_item_by_sku(self, sku: str) -> Optional[CartItem]:
        """
        Finds a cart item by product SKU.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            CartItem or None if not found
        """
        for item in self._items:
            if item.get_sku() == sku:
                return item
        return None
    
    def contains_product(self, sku: str) -> bool:
        """
        Checks if cart contains a product.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            bool: True if product in cart
        """
        return self.find_item_by_sku(sku) is not None
    
    # Cart modification methods with business rules
    def add_item(self, product: Product, quantity: int) -> tuple[bool, str]:
        """
        Adds item to cart with validation.
        Enforces business rules:
        - Max 20 total items
        - Max 10 per product
        - Product must be in stock
        
        Args:
            product (Product): Product to add
            quantity (int): Quantity to add
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validate quantity
        if quantity < 1 or quantity > self.MAX_QUANTITY_PER_PRODUCT:
            return False, f"Quantity must be between 1 and {self.MAX_QUANTITY_PER_PRODUCT}"
        
        # Check stock
        if not product.is_in_stock():
            return False, f"{product.get_name()} is out of stock"
        
        if quantity > product.get_quantity():
            return False, f"Only {product.get_quantity()} units of {product.get_name()} available"
        
        # Don't let people add the same item twice - they need to update quantity instead
        existing_item = self.find_item_by_sku(product.get_sku())
        if existing_item:
            return False, f"{product.get_name()} is already in cart. Use update to change quantity."
        
        # Make sure we don't exceed the cart limit (20 items total)
        current_total = self.get_total_quantity()
        if current_total + quantity > self.MAX_TOTAL_ITEMS:
            available_space = self.MAX_TOTAL_ITEMS - current_total
            if available_space > 0:
                return False, f"Cart limit: only {available_space} more items allowed (max {self.MAX_TOTAL_ITEMS} total)"
            else:
                return False, f"Cart is full (max {self.MAX_TOTAL_ITEMS} items)"
        
        # Add item
        try:
            cart_item = CartItem(product, quantity)
            self._items.append(cart_item)
            return True, f"Added {quantity} × {product.get_name()} to cart"
        except ValueError as e:
            return False, str(e)
    
    def update_quantity(self, sku: str, new_quantity: int) -> tuple[bool, str]:
        """
        Updates quantity of an item in cart.
        
        Args:
            sku (str): Product SKU
            new_quantity (int): New quantity
            
        Returns:
            tuple: (success: bool, message: str)
        """
        item = self.find_item_by_sku(sku)
        if not item:
            return False, "Product not found in cart"
        
        if new_quantity < 1 or new_quantity > self.MAX_QUANTITY_PER_PRODUCT:
            return False, f"Quantity must be between 1 and {self.MAX_QUANTITY_PER_PRODUCT}"
        
        # Check if new quantity would exceed total items limit
        current_total = self.get_total_quantity()
        old_quantity = item.get_quantity()
        quantity_difference = new_quantity - old_quantity
        
        if current_total + quantity_difference > self.MAX_TOTAL_ITEMS:
            return False, f"Cart limit exceeded (max {self.MAX_TOTAL_ITEMS} total items)"
        
        # Check stock
        if new_quantity > item.get_product().get_quantity():
            return False, f"Only {item.get_product().get_quantity()} units available"
        
        item.set_quantity(new_quantity)
        return True, f"Updated quantity to {new_quantity}"
    
    def remove_item(self, sku: str) -> tuple[bool, str]:
        """
        Removes item from cart.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            tuple: (success: bool, message: str)
        """
        for i, item in enumerate(self._items):
            if item.get_sku() == sku:
                product_name = item.get_name()
                del self._items[i]
                return True, f"Removed {product_name} from cart"
        
        return False, "Product not found in cart"
    
    def clear(self) -> None:
        """Removes all items from cart."""
        self._items = []
    
    # Calculation methods
    def calculate_subtotal(self, is_vip: bool = False) -> float:
        """
        Calculates cart subtotal.
        
        Args:
            is_vip (bool): Whether to apply VIP pricing
            
        Returns:
            float: Subtotal amount
        """
        return round(sum(item.get_line_total(is_vip) for item in self._items), 2)
    
    def calculate_savings(self) -> float:
        """
        Calculates VIP savings (regular price - member price).
        
        Returns:
            float: Total savings if VIP
        """
        regular_total = self.calculate_subtotal(is_vip=False)
        vip_total = self.calculate_subtotal(is_vip=True)
        return round(regular_total - vip_total, 2)
    
    # Stock validation
    def validate_all_stock(self) -> tuple[bool, str]:
        """
        Validates stock for all items in cart.
        
        Returns:
            tuple: (all_valid: bool, error_message: str)
        """
        for item in self._items:
            valid, message = item.validate_stock()
            if not valid:
                return False, message
        return True, ""
    
    # Conversion methods
    def to_dict_list(self) -> List[Dict]:
        """
        Converts cart to list of dictionaries.
        
        Returns:
            list: List of cart item dictionaries
        """
        return [item.to_dict() for item in self.get_items()]
    
    def get_summary(self, is_vip: bool = False) -> Dict:
        """
        Returns cart summary information.
        
        Args:
            is_vip (bool): Whether customer is VIP
            
        Returns:
            dict: Cart summary with counts and totals
        """
        return {
            "item_count": self.get_item_count(),
            "total_quantity": self.get_total_quantity(),
            "subtotal": self.calculate_subtotal(is_vip),
            "vip_savings": self.calculate_savings() if is_vip else 0.0,
            "is_empty": self.is_empty(),
            "items_remaining": self.MAX_TOTAL_ITEMS - self.get_total_quantity()
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"ShoppingCart({self.get_item_count()} items, {self.get_total_quantity()} total units)"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return self.__str__()


class CartManager:
    """
    High-level cart management with session handling.
    Demonstrates Facade pattern for simplified cart operations.
    """
    
    def __init__(self, cart: ShoppingCart, product_repository):
        """
        Initialize CartManager.
        
        Args:
            cart (ShoppingCart): Shopping cart instance
            product_repository: ProductRepository for product lookups
        """
        self._cart = cart
        self._product_repo = product_repository
    
    def add_product_by_sku(self, sku: str, quantity: int) -> tuple[bool, str]:
        """
        Adds product to cart by SKU lookup.
        
        Args:
            sku (str): Product SKU
            quantity (int): Quantity to add
            
        Returns:
            tuple: (success: bool, message: str)
        """
        product = self._product_repo.find_by_sku(sku)
        if not product:
            return False, f"Product with SKU {sku} not found"
        
        return self._cart.add_item(product, quantity)
    
    def update_product_quantity(self, sku: str, new_quantity: int) -> tuple[bool, str]:
        """
        Updates product quantity in cart.
        
        Args:
            sku (str): Product SKU
            new_quantity (int): New quantity
            
        Returns:
            tuple: (success: bool, message: str)
        """
        return self._cart.update_quantity(sku, new_quantity)
    
    def remove_product(self, sku: str) -> tuple[bool, str]:
        """
        Removes product from cart.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            tuple: (success: bool, message: str)
        """
        return self._cart.remove_item(sku)
    
    def clear_cart(self) -> None:
        """Clears all items from cart."""
        self._cart.clear()
    
    def get_cart(self) -> ShoppingCart:
        """Returns the shopping cart instance."""
        return self._cart
    
    def validate_checkout_ready(self) -> tuple[bool, str]:
        """
        Validates if cart is ready for checkout.
        
        Returns:
            tuple: (ready: bool, message: str)
        """
        if self._cart.is_empty():
            return False, "Cart is empty"
        
        valid, message = self._cart.validate_all_stock()
        if not valid:
            return False, message
        
        return True, "Cart is ready for checkout"