"""
user.py
-------
User entity classes with proper OOP design.
Demonstrates: Encapsulation, Inheritance, Polymorphism, Composition
Handles user authentication, profile management, VIP membership, and funds.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


class User(ABC):
    """
    Abstract base class for all users in the system.
    Demonstrates abstraction and provides common user functionality.
    """
    
    def __init__(self, email: str, password: str, first_name: str,
                 last_name: str, mobile: str):
        """
        Initialize a User instance.
        
        Args:
            email (str): User's email (unique identifier)
            password (str): User's password
            first_name (str): User's first name
            last_name (str): User's last name
            mobile (str): User's mobile number
        """
        # Private attributes (encapsulation)
        self._email = email.lower().strip()
        self._password = password
        self._first_name = first_name.strip()
        self._last_name = last_name.strip()
        self._mobile = mobile.strip()
    
    # Getters (Accessor methods)
    def get_email(self) -> str:
        """Returns the user's email."""
        return self._email
    
    def get_first_name(self) -> str:
        """Returns the user's first name."""
        return self._first_name
    
    def get_last_name(self) -> str:
        """Returns the user's last name."""
        return self._last_name
    
    def get_full_name(self) -> str:
        """Returns the user's full name."""
        return f"{self._first_name} {self._last_name}"
    
    def get_mobile(self) -> str:
        """Returns the user's mobile number."""
        return self._mobile
    
    # Setters (Mutator methods) with validation
    def set_mobile(self, mobile: str) -> bool:
        """
        Updates mobile number with validation.
        
        Args:
            mobile (str): New mobile number
            
        Returns:
            bool: True if successful, False if invalid
        """
        if mobile and mobile.replace(" ", "").replace("-", "").isdigit():
            self._mobile = mobile.strip()
            return True
        return False
    
    def verify_password(self, password: str) -> bool:
        """
        Verifies if provided password matches stored password.
        
        Args:
            password (str): Password to verify
            
        Returns:
            bool: True if password matches
        """
        return self._password == password
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Changes user password after verifying old password.
        
        Args:
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            bool: True if successful, False if old password incorrect
        """
        if not self.verify_password(old_password):
            return False
        
        # Validate new password (min 8 chars, 1 uppercase, 1 number)
        if (len(new_password) >= 8 and 
            any(c.isupper() for c in new_password) and
            any(c.isdigit() for c in new_password)):
            self._password = new_password
            return True
        return False
    
    # Abstract methods (must be implemented by subclasses)
    @abstractmethod
    def get_role(self) -> str:
        """
        Returns the user's role.
        Must be implemented by subclasses (polymorphism).
        
        Returns:
            str: "CUSTOMER" or "ADMIN"
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Converts User object to dictionary for CSV persistence.
        Must be implemented by subclasses.
        
        Returns:
            dict: User data as dictionary
        """
        pass
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"User(email={self._email}, name={self.get_full_name()}, role={self.get_role()})"
    
    def __repr__(self) -> str:
        """Official string representation."""
        return self.__str__()


class VIPMembership:
    """
    VIPMembership class representing a customer's VIP status.
    Demonstrates composition (Customer HAS-A VIPMembership).
    """
    
    COST_PER_YEAR = 20.0
    
    def __init__(self, years: int, purchase_date: datetime = None):
        """
        Initialize a VIP membership.
        
        Args:
            years (int): Number of years purchased
            purchase_date (datetime): Date of purchase (default: now)
        """
        self._years = years
        self._purchase_date = purchase_date or datetime.now()
        self._expiry_date = self._purchase_date + timedelta(days=365 * years)
        self._is_cancelled = False
    
    def get_years(self) -> int:
        """Returns total years purchased."""
        return self._years
    
    def get_expiry_date(self) -> datetime:
        """Returns expiry date as datetime."""
        return self._expiry_date
    
    def get_expiry_date_string(self) -> str:
        """Returns expiry date as ISO string."""
        return self._expiry_date.date().isoformat()
    
    def is_active(self) -> bool:
        """
        Checks if membership is currently active.
        
        Returns:
            bool: True if not expired and not cancelled
        """
        if self._is_cancelled:
            return False
        return datetime.now() < self._expiry_date
    
    def extend(self, additional_years: int) -> None:
        """
        Extends the membership by additional years.
        
        Args:
            additional_years (int): Years to add
        """
        self._years += additional_years
        self._expiry_date += timedelta(days=365 * additional_years)
    
    def cancel(self) -> None:
        """
        Cancels the membership (non-refundable).
        Sets expiry to now and marks as cancelled.
        """
        self._is_cancelled = True
        self._expiry_date = datetime.now()
    
    def days_remaining(self) -> int:
        """
        Calculates days remaining until expiry.
        
        Returns:
            int: Days remaining (0 if expired)
        """
        if not self.is_active():
            return 0
        delta = self._expiry_date - datetime.now()
        return max(0, delta.days)
    
    def __str__(self) -> str:
        """String representation."""
        status = "Active" if self.is_active() else "Expired/Cancelled"
        return f"VIPMembership({status}, expires={self.get_expiry_date_string()})"


class Customer(User):
    """
    Customer class representing a shopping user.
    Demonstrates inheritance from User and composition with VIPMembership.
    """
    
    INITIAL_FUNDS = 1000.0
    MAX_TOP_UP = 1000.0
    
    def __init__(self, email: str, password: str, first_name: str,
                 last_name: str, mobile: str, address: str,
                 is_monash_student: bool, funds: float = INITIAL_FUNDS,
                 vip_membership: Optional[VIPMembership] = None):
        """
        Initialize a Customer instance.
        
        Args:
            All User args plus:
            address (str): Customer's address
            is_monash_student (bool): Whether customer is Monash student
            funds (float): Account funds balance
            vip_membership (VIPMembership): VIP membership object (optional)
        """
        # Call parent constructor (inheritance)
        super().__init__(email, password, first_name, last_name, mobile)
        
        # Customer-specific private attributes
        self._address = address.strip()
        self._is_monash_student = is_monash_student
        self._funds = float(funds)
        self._vip_membership = vip_membership  # Composition
        self._order_history = []  # List of Order objects
    
    # Polymorphism - Implementing abstract method
    def get_role(self) -> str:
        """
        Returns customer role.
        
        Returns:
            str: Always "CUSTOMER"
        """
        return "CUSTOMER"
    
    # Customer-specific getters
    def get_address(self) -> str:
        """Returns customer's address."""
        return self._address
    
    def is_student(self) -> bool:
        """Returns whether customer is a Monash student."""
        return self._is_monash_student
    
    def get_funds(self) -> float:
        """Returns current account balance."""
        return self._funds
    
    def get_vip_membership(self) -> Optional[VIPMembership]:
        """Returns VIP membership object if exists."""
        return self._vip_membership
    
    # Customer-specific setters
    def set_address(self, address: str) -> bool:
        """
        Updates customer's address.
        
        Args:
            address (str): New address
            
        Returns:
            bool: True if successful, False if invalid
        """
        if address and address.strip():
            self._address = address.strip()
            return True
        return False
    
    # Funds management (encapsulated business logic)
    def top_up_funds(self, amount: float) -> bool:
        """
        Adds funds to customer account.
        
        Args:
            amount (float): Amount to add (max $1000 per transaction)
            
        Returns:
            bool: True if successful, False if invalid amount
        """
        if amount <= 0:
            return False
        if amount > self.MAX_TOP_UP:
            return False
        
        self._funds = round(self._funds + amount, 2)
        return True
    
    def deduct_funds(self, amount: float) -> bool:
        """
        Deducts funds from customer account.
        
        Args:
            amount (float): Amount to deduct
            
        Returns:
            bool: True if successful, False if insufficient funds
        """
        if amount <= 0:
            return False
        if amount > self._funds:
            return False
        
        self._funds = round(self._funds - amount, 2)
        return True
    
    def has_sufficient_funds(self, amount: float) -> bool:
        """
        Checks if customer can afford specified amount.
        
        Args:
            amount (float): Amount to check
            
        Returns:
            bool: True if funds >= amount
        """
        return self._funds >= amount
    
    # VIP membership management (demonstrates composition)
    def is_vip(self) -> bool:
        """
        Checks if customer has active VIP membership.
        
        Returns:
            bool: True if VIP is active
        """
        if self._vip_membership is None:
            return False
        return self._vip_membership.is_active()
    
    def buy_vip_membership(self, years: int) -> tuple[bool, str]:
        """
        Purchases or renews VIP membership.
        
        Args:
            years (int): Number of years to purchase
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Make sure they're buying at least 1 year
        if years <= 0:
            return False, "Years must be positive."
        
        # Calculate the total cost ($20 per year)
        cost = VIPMembership.COST_PER_YEAR * years
        
        # Check if they have enough money in their account
        if not self.has_sufficient_funds(cost):
            return False, f"Insufficient funds. Need ${cost:.2f}, have ${self._funds:.2f}."
        
        # Take the money out of their account
        self.deduct_funds(cost)
        
        # Either extend their existing membership or create a new one
        if self._vip_membership and self._vip_membership.is_active():
            # They already have VIP, so we're just adding more years
            self._vip_membership.extend(years)
            action = "renewed"
        else:
            # They don't have VIP yet, so create a new membership
            self._vip_membership = VIPMembership(years)
            action = "purchased"
        
        return True, f"VIP membership {action}. Expires: {self._vip_membership.get_expiry_date_string()}"
    
    def cancel_vip_membership(self) -> tuple[bool, str]:
        """
        Cancels VIP membership (non-refundable).
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self._vip_membership or not self._vip_membership.is_active():
            return False, "No active VIP membership to cancel."
        
        self._vip_membership.cancel()
        return True, "VIP membership cancelled (non-refundable)."
    
    def get_vip_status_string(self) -> str:
        """
        Returns VIP status as formatted string.
        
        Returns:
            str: VIP status information
        """
        if not self._vip_membership:
            return "No VIP membership"
        
        if self._vip_membership.is_active():
            days = self._vip_membership.days_remaining()
            return f"Active VIP (expires: {self._vip_membership.get_expiry_date_string()}, {days} days left)"
        else:
            return "VIP membership expired/cancelled"
    
    # Order history management
    def add_order(self, order) -> None:
        """
        Adds an order to customer's history.
        
        Args:
            order: Order object
        """
        self._order_history.append(order)
    
    def get_order_history(self) -> List:
        """
        Returns customer's order history.
        
        Returns:
            list: List of Order objects
        """
        return self._order_history
    
    def get_order_count(self) -> int:
        """Returns total number of orders placed."""
        return len(self._order_history)
    
    def has_placed_pickup_order(self) -> bool:
        """
        Checks if customer has any pickup orders in history.
        Used for promo eligibility.
        
        Returns:
            bool: True if has pickup order
        """
        for order in self._order_history:
            if hasattr(order, 'get_fulfilment') and order.get_fulfilment() == "PICKUP":
                return True
        return False
    
    # CSV persistence
    def to_dict(self) -> Dict:
        """
        Converts Customer to dictionary for CSV storage.
        
        Returns:
            dict: Customer data
        """
        vip_years = "0"
        vip_expires = ""
        
        if self._vip_membership:
            vip_years = str(self._vip_membership.get_years())
            vip_expires = self._vip_membership.get_expiry_date_string()
        
        return {
            "email": self._email,
            "password": self._password,
            "role": self.get_role(),
            "first_name": self._first_name,
            "last_name": self._last_name,
            "mobile": self._mobile,
            "address": self._address,
            "is_monash_student": "1" if self._is_monash_student else "0",
            "vip_years": vip_years,
            "vip_expires": vip_expires,
            "funds": f"{self._funds:.2f}"
        }
    
    def __str__(self) -> str:
        """String representation."""
        vip = "VIP" if self.is_vip() else "Regular"
        student = "Student" if self.is_student() else "Staff"
        return (f"Customer(email={self._email}, name={self.get_full_name()}, "
                f"{student}, {vip}, funds=${self._funds:.2f})")


class Administrator(User):
    """
    Administrator class representing an admin user.
    Demonstrates inheritance and polymorphism.
    """
    
    def __init__(self, email: str, password: str, first_name: str,
                 last_name: str, mobile: str):
        """
        Initialize an Administrator instance.
        
        Args:
            All User args (no additional fields for admin)
        """
        # Call parent constructor
        super().__init__(email, password, first_name, last_name, mobile)
    
    # Polymorphism - Implementing abstract method
    def get_role(self) -> str:
        """
        Returns administrator role.
        
        Returns:
            str: Always "ADMIN"
        """
        return "ADMIN"
    
    # Admin-specific capabilities
    def can_manage_products(self) -> bool:
        """
        Checks if user can manage products.
        
        Returns:
            bool: Always True for Administrator
        """
        return True
    
    def can_view_all_orders(self) -> bool:
        """
        Checks if user can view all orders.
        
        Returns:
            bool: Always True for Administrator
        """
        return True
    
    # CSV persistence
    def to_dict(self) -> Dict:
        """
        Converts Administrator to dictionary for CSV storage.
        
        Returns:
            dict: Administrator data
        """
        return {
            "email": self._email,
            "password": self._password,
            "role": self.get_role(),
            "first_name": self._first_name,
            "last_name": self._last_name,
            "mobile": self._mobile,
            "address": "",
            "is_monash_student": "0",
            "vip_years": "0",
            "vip_expires": "",
            "funds": "0.00"
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"Administrator(email={self._email}, name={self.get_full_name()})"


# Factory Pattern for creating users
class UserFactory:
    """
    Factory class for creating User instances.
    Demonstrates Factory design pattern.
    """
    
    @staticmethod
    def create_user(user_data: Dict) -> User:
        """
        Creates appropriate User subclass from dictionary.
        
        Args:
            user_data (dict): User data from CSV
            
        Returns:
            Customer or Administrator instance
        """
        role = user_data.get("role", "CUSTOMER").upper()
        
        if role == "ADMIN":
            return Administrator(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                mobile=user_data.get("mobile", "")
            )
        else:
            # Create VIP membership if exists
            vip_membership = None
            vip_expires = user_data.get("vip_expires", "")
            vip_years = int(user_data.get("vip_years", "0") or 0)
            
            if vip_expires and vip_years > 0:
                try:
                    expiry_date = datetime.fromisoformat(vip_expires)
                    purchase_date = expiry_date - timedelta(days=365 * vip_years)
                    vip_membership = VIPMembership(vip_years, purchase_date)
                    # Manually set expiry to match CSV
                    vip_membership._expiry_date = expiry_date
                except (ValueError, TypeError):
                    pass
            
            return Customer(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                mobile=user_data.get("mobile", ""),
                address=user_data.get("address", ""),
                is_monash_student=user_data.get("is_monash_student", "0") in ("1", "true", "True"),
                funds=float(user_data.get("funds", Customer.INITIAL_FUNDS)),
                vip_membership=vip_membership
            )
    
    @staticmethod
    def create_customer(email: str, password: str, first_name: str,
                       last_name: str, mobile: str, address: str,
                       is_monash_student: bool) -> Customer:
        """
        Creates a new Customer with default initial funds.
        
        Args:
            Basic customer information
            
        Returns:
            Customer instance with initial funds
        """
        return Customer(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile=mobile,
            address=address,
            is_monash_student=is_monash_student,
            funds=Customer.INITIAL_FUNDS
        )