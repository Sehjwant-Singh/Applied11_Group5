"""
data.py
-------
Centralized data persistence initialization for MMOSS.
Initializes repositories and provides backward-compatible CSV access.
Now uses Repository pattern with OOP entities.
"""

import os
import csv
from typing import List, Dict

# === Base directory: always points to the folder containing this file (src/) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === File paths (always inside src) ===
PRODUCTS_CSV = os.path.join(BASE_DIR, "product_data.csv")
USERS_CSV = os.path.join(BASE_DIR, "users.csv")
ORDERS_CSV = os.path.join(BASE_DIR, "orders.csv")
STORES_CSV = os.path.join(BASE_DIR, "stores.csv")
MEMBERSHIP_CSV = os.path.join(BASE_DIR, "membership.csv")

# === CSV Headers ===
PRODUCT_HEADERS = [
    "sku", "name", "brand", "description", "category", "subcategory",
    "price", "member_price", "quantity", "is_food",
    "expiry_date", "ingredients", "storage", "allergens"
]

USER_HEADERS = [
    "email", "password", "role",
    "first_name", "last_name", "mobile", "address",
    "is_monash_student", "vip_years", "vip_expires", "funds"
]

ORDER_HEADERS = [
    "order_id", "email", "datetime", "fulfilment", "delivery_address",
    "store_id", "promo_code", "promo_discount", "student_discount",
    "delivery_fee", "subtotal", "total", "lines_json"
]

STORE_HEADERS = ["store_id", "name", "address", "phone", "hours"]

MEMBERSHIP_HEADERS = ["email", "action", "years", "amount", "datetime", "notes"]


# === Initialize all CSVs with headers and seed data ===
def init_storage() -> None:
    """
    Creates all CSVs in src/ if they don't exist and seeds default data.
    This is called at application startup.
    """
    # Create the products CSV file if it doesn't exist yet
    if not os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=PRODUCT_HEADERS).writeheader()
    
    # Create the users CSV file and add some default test accounts
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=USER_HEADERS)
            w.writeheader()
            # Add some test accounts so people can log in and try the system
            w.writerow({
                "email": "student@student.monash.edu",
                "password": "Monash1234!",
                "role": "CUSTOMER",
                "first_name": "Stu",
                "last_name": "Dent",
                "mobile": "0400000001",
                "address": "8 College Walk, Clayton VIC",
                "is_monash_student": "1",
                "vip_years": "0",
                "vip_expires": "",
                "funds": "1000.00"
            })
            w.writerow({
                "email": "staff@monash.edu",
                "password": "Monash1234!",
                "role": "CUSTOMER",
                "first_name": "Sta",
                "last_name": "Ff",
                "mobile": "0400000002",
                "address": "1 Wellington Rd, Clayton VIC",
                "is_monash_student": "0",
                "vip_years": "0",
                "vip_expires": "",
                "funds": "1000.00"
            })
            w.writerow({
                "email": "admin@monash.edu",
                "password": "Admin1234!",
                "role": "ADMIN",
                "first_name": "Ad",
                "last_name": "Min",
                "mobile": "0400000003",
                "address": "900 Dandenong Rd, Caulfield VIC",
                "is_monash_student": "0",
                "vip_years": "0",
                "vip_expires": "",
                "funds": "0.00"
            })
    
    # Create orders CSV
    if not os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=ORDER_HEADERS).writeheader()
    
    # Create and seed stores CSV
    if not os.path.exists(STORES_CSV):
        with open(STORES_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=STORE_HEADERS)
            w.writeheader()
            w.writerow({
                "store_id": "S1",
                "name": "MMOSS Caulfield",
                "address": "900 Dandenong Rd, Caulfield",
                "phone": "03 9999 9999",
                "hours": "9-5 Mon-Fri"
            })
            w.writerow({
                "store_id": "S2",
                "name": "MMOSS Clayton",
                "address": "Wellington Rd, Clayton",
                "phone": "03 8888 8888",
                "hours": "9-5 Mon-Fri"
            })
    
    # Create membership history CSV
    if not os.path.exists(MEMBERSHIP_CSV):
        with open(MEMBERSHIP_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=MEMBERSHIP_HEADERS).writeheader()


# === Repository Singleton Instances (Lazy Initialization) ===
_product_repository = None
_user_repository = None
_order_repository = None
_store_repository = None
_membership_repository = None


def get_product_repository():
    """
    Returns the ProductRepository singleton instance.
    Lazy initialization - creates on first call.
    
    Returns:
        ProductRepository: Singleton instance
    """
    global _product_repository
    if _product_repository is None:
        from repositories import ProductRepository
        _product_repository = ProductRepository(PRODUCTS_CSV)
    return _product_repository


def get_user_repository():
    """
    Returns the UserRepository singleton instance.
    
    Returns:
        UserRepository: Singleton instance
    """
    global _user_repository
    if _user_repository is None:
        from repositories import UserRepository
        _user_repository = UserRepository(USERS_CSV)
    return _user_repository


def get_order_repository():
    """
    Returns the OrderRepository singleton instance.
    
    Returns:
        OrderRepository: Singleton instance
    """
    global _order_repository
    if _order_repository is None:
        from repositories import OrderRepository
        _order_repository = OrderRepository(ORDERS_CSV)
    return _order_repository


def get_store_repository():
    """
    Returns the StoreRepository singleton instance.
    
    Returns:
        StoreRepository: Singleton instance
    """
    global _store_repository
    if _store_repository is None:
        from repositories import StoreRepository
        _store_repository = StoreRepository(STORES_CSV)
    return _store_repository


def get_membership_repository():
    """
    Returns the MembershipHistoryRepository singleton instance.
    
    Returns:
        MembershipHistoryRepository: Singleton instance
    """
    global _membership_repository
    if _membership_repository is None:
        from repositories import MembershipHistoryRepository
        _membership_repository = MembershipHistoryRepository(MEMBERSHIP_CSV)
    return _membership_repository


# === Backward Compatibility Functions ===
# These functions provide compatibility with old code that used dictionaries
# They will be gradually phased out as we update UI files

def load_products() -> List[Dict]:
    """
    BACKWARD COMPATIBILITY: Loads products as dictionaries.
    
    Returns:
        list: List of product dictionaries
    """
    product_repo = get_product_repository()
    products = product_repo.find_all()
    return [p.to_dict() for p in products]


def save_products(items: List[Dict]) -> None:
    """
    BACKWARD COMPATIBILITY: Saves products from dictionaries.
    
    Args:
        items (list): List of product dictionaries
    """
    from product import ProductFactory
    product_repo = get_product_repository()
    
    # Convert dictionaries to Product objects
    for item_dict in items:
        try:
            product = ProductFactory.create_product(item_dict)
            product_repo.save(product)
        except Exception as e:
            print(f"Warning: Could not save product {item_dict.get('sku', 'unknown')}: {e}")


def load_users() -> List[Dict]:
    """
    BACKWARD COMPATIBILITY: Loads users as dictionaries.
    
    Returns:
        list: List of user dictionaries
    """
    user_repo = get_user_repository()
    users = user_repo.find_all()
    return [u.to_dict() for u in users]


def save_users(items: List[Dict]) -> None:
    """
    BACKWARD COMPATIBILITY: Saves users from dictionaries.
    
    Args:
        items (list): List of user dictionaries
    """
    from user import UserFactory
    user_repo = get_user_repository()
    
    # Convert dictionaries to User objects
    for item_dict in items:
        try:
            user = UserFactory.create_user(item_dict)
            user_repo.save(user)
        except Exception as e:
            print(f"Warning: Could not save user {item_dict.get('email', 'unknown')}: {e}")


def append_order(order_row: Dict) -> None:
    """
    BACKWARD COMPATIBILITY: Appends an order from dictionary.
    
    Args:
        order_row (dict): Order data dictionary
    """
    order_repo = get_order_repository()
    order_repo.save(order_row)


def load_stores() -> List[Dict]:
    """
    Loads all stores.
    
    Returns:
        list: List of store dictionaries
    """
    store_repo = get_store_repository()
    return store_repo.find_all()


def append_membership(entry: Dict) -> None:
    """
    Appends a membership history entry.
    
    Args:
        entry (dict): Membership transaction data
    """
    membership_repo = get_membership_repository()
    membership_repo.save(entry)


def load_membership_history() -> List[Dict]:
    """
    Loads all membership history.
    
    Returns:
        list: List of membership history entries
    """
    membership_repo = get_membership_repository()
    return membership_repo.find_all()


# === OOP Helper Functions (NEW) ===
# These are the preferred way to access data using OOP entities

def authenticate_user(email: str, password: str):
    """
    Authenticates a user and returns User object.
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        User object or None if authentication fails
    """
    user_repo = get_user_repository()
    return user_repo.authenticate(email, password)


def find_product_by_sku(sku: str):
    """
    Finds a product by SKU.
    
    Args:
        sku (str): Product SKU
        
    Returns:
        Product object or None
    """
    product_repo = get_product_repository()
    return product_repo.find_by_sku(sku)


def get_all_products():
    """
    Returns all products as Product objects.
    
    Returns:
        list: List of Product objects
    """
    product_repo = get_product_repository()
    return product_repo.find_all()


def filter_products(filters: Dict):
    """
    Filters products based on criteria.
    
    Args:
        filters (dict): Filter criteria
        
    Returns:
        list: List of matching Product objects
    """
    product_repo = get_product_repository()
    return product_repo.find_by_filter(filters)


def save_user_object(user) -> bool:
    """
    Saves a User object.
    
    Args:
        user: User/Customer/Administrator object
        
    Returns:
        bool: True if successful
    """
    user_repo = get_user_repository()
    return user_repo.save(user)


def save_product_object(product) -> bool:
    """
    Saves a Product object.
    
    Args:
        product: Product/FoodProduct object
        
    Returns:
        bool: True if successful
    """
    product_repo = get_product_repository()
    return product_repo.save(product)


def get_customer_orders(email: str) -> List[Dict]:
    """
    Gets all orders for a customer.
    
    Args:
        email (str): Customer email
        
    Returns:
        list: List of order dictionaries
    """
    order_repo = get_order_repository()
    return order_repo.find_by_email(email)


def customer_has_pickup_order(email: str) -> bool:
    """
    Checks if customer has any pickup orders.
    
    Args:
        email (str): Customer email
        
    Returns:
        bool: True if has pickup order
    """
    order_repo = get_order_repository()
    return order_repo.customer_has_pickup_order(email)


# === Initialization on module import ===
# Ensure CSV files exist when this module is imported
init_storage()