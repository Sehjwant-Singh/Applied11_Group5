"""
repositories.py
---------------
Repository classes for data persistence using Repository pattern.
Handles loading and saving entities from/to CSV files.
Demonstrates: Repository Pattern, Singleton Pattern, Separation of Concerns
"""

import csv
import os
from typing import List, Dict, Optional
from product import Product, FoodProduct, ProductFactory
from user import User, Customer, Administrator, UserFactory


class BaseRepository:
    """
    Base repository class with common CSV operations.
    Demonstrates inheritance and code reuse.
    """
    
    def __init__(self, csv_path: str, headers: List[str]):
        """
        Initialize repository.
        
        Args:
            csv_path (str): Path to CSV file
            headers (list): CSV column headers
        """
        self._csv_path = csv_path
        self._headers = headers
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Creates CSV file with headers if it doesn't exist."""
        if not os.path.exists(self._csv_path):
            with open(self._csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self._headers)
                writer.writeheader()
    
    def _read_all_rows(self) -> List[Dict]:
        """
        Reads all rows from CSV.
        
        Returns:
            list: List of dictionaries (one per row)
        """
        try:
            with open(self._csv_path, 'r', newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []
    
    def _write_all_rows(self, rows: List[Dict]) -> None:
        """
        Writes all rows to CSV (overwrites file).
        
        Args:
            rows (list): List of dictionaries to write
        """
        with open(self._csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._headers)
            writer.writeheader()
            writer.writerows(rows)
    
    def _append_row(self, row: Dict) -> None:
        """
        Appends a single row to CSV.
        
        Args:
            row (dict): Dictionary to append
        """
        with open(self._csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._headers)
            writer.writerow(row)


class ProductRepository(BaseRepository):
    """
    Repository for Product entity persistence.
    Demonstrates Repository pattern with domain objects.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, csv_path: str):
        """
        Singleton pattern - ensures only one repository instance exists.
        
        Args:
            csv_path (str): Path to products CSV
            
        Returns:
            ProductRepository: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(ProductRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str):
        """
        Initialize ProductRepository.
        
        Args:
            csv_path (str): Path to product_data.csv
        """
        if not hasattr(self, '_initialized'):
            headers = [
                "sku", "name", "brand", "description", "category", "subcategory",
                "price", "member_price", "quantity", "is_food",
                "expiry_date", "ingredients", "storage", "allergens"
            ]
            super().__init__(csv_path, headers)
            self._products: Dict[str, Product] = {}
            self._load_products()
            self._initialized = True
    
    def _load_products(self) -> None:
        """Loads all products from CSV into memory as Product objects."""
        rows = self._read_all_rows()
        self._products = {}
        
        for row in rows:
            try:
                product = ProductFactory.create_product(row)
                self._products[product.get_sku()] = product
            except (ValueError, KeyError) as e:
                # Skip invalid rows
                print(f"Warning: Skipping invalid product row: {e}")
                continue
    
    def find_by_sku(self, sku: str) -> Optional[Product]:
        """
        Finds a product by SKU.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            Product or None if not found
        """
        return self._products.get(sku)
    
    def find_all(self) -> List[Product]:
        """
        Returns all products.
        
        Returns:
            list: List of all Product objects
        """
        return list(self._products.values())
    
    def find_by_category(self, category: str) -> List[Product]:
        """
        Finds all products in a category.
        
        Args:
            category (str): Category name
            
        Returns:
            list: Products in the category
        """
        return [p for p in self._products.values() 
                if p.get_category().lower() == category.lower()]
    
    def find_in_stock(self) -> List[Product]:
        """
        Finds all products that are in stock.
        
        Returns:
            list: Products with quantity > 0
        """
        return [p for p in self._products.values() if p.is_in_stock()]
    
    def find_by_filter(self, filters: Dict) -> List[Product]:
        """
        Finds products matching filter criteria.
        
        Args:
            filters (dict): Filter criteria
                - category: str
                - subcategory: str
                - brand: str
                - price_min: float
                - price_max: float
                - availability: "in" or "out"
                
        Returns:
            list: Matching products
        """
        results = list(self._products.values())
        
        # Apply filters
        if 'category' in filters and filters['category']:
            cat = filters['category'].lower()
            results = [p for p in results if p.get_category().lower() == cat]
        
        if 'subcategory' in filters and filters['subcategory']:
            subcat = filters['subcategory'].lower()
            results = [p for p in results if p.get_subcategory().lower() == subcat]
        
        if 'brand' in filters and filters['brand']:
            brand = filters['brand'].lower()
            results = [p for p in results if p.get_brand().lower() == brand]
        
        if 'price_min' in filters and filters['price_min']:
            try:
                min_price = float(filters['price_min'])
                results = [p for p in results if p.get_price() >= min_price]
            except ValueError:
                pass
        
        if 'price_max' in filters and filters['price_max']:
            try:
                max_price = float(filters['price_max'])
                results = [p for p in results if p.get_price() <= max_price]
            except ValueError:
                pass
        
        if 'availability' in filters and filters['availability']:
            avail = filters['availability'].lower()
            if avail == 'in':
                results = [p for p in results if p.is_in_stock()]
            elif avail == 'out':
                results = [p for p in results if not p.is_in_stock()]
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """
        Returns all unique categories.
        
        Returns:
            list: Unique category names
        """
        categories = set()
        for product in self._products.values():
            categories.add(product.get_category())
        return sorted(list(categories))
    
    def count_categories(self) -> int:
        """
        Counts unique categories.
        
        Returns:
            int: Number of unique categories
        """
        return len(self.get_all_categories())
    
    def save(self, product: Product) -> bool:
        """
        Saves a product (add or update).
        
        Args:
            product (Product): Product to save
            
        Returns:
            bool: True if successful
        """
        self._products[product.get_sku()] = product
        self._persist()
        return True
    
    def delete(self, sku: str) -> bool:
        """
        Deletes a product by SKU.
        
        Args:
            sku (str): Product SKU
            
        Returns:
            bool: True if deleted, False if not found
        """
        if sku in self._products:
            del self._products[sku]
            self._persist()
            return True
        return False
    
    def _persist(self) -> None:
        """Writes all products back to CSV."""
        rows = [product.to_dict() for product in self._products.values()]
        self._write_all_rows(rows)
    
    def reload(self) -> None:
        """Reloads products from CSV (useful after external changes)."""
        self._load_products()
    
    def get_count(self) -> int:
        """
        Returns total number of products.
        
        Returns:
            int: Product count
        """
        return len(self._products)


class UserRepository(BaseRepository):
    """
    Repository for User entity persistence.
    Demonstrates Repository pattern with polymorphic entities.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, csv_path: str):
        """
        Singleton pattern - ensures only one repository instance exists.
        
        Args:
            csv_path (str): Path to users CSV
            
        Returns:
            UserRepository: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(UserRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str):
        """
        Initialize UserRepository.
        
        Args:
            csv_path (str): Path to users.csv
        """
        if not hasattr(self, '_initialized'):
            headers = [
                "email", "password", "role",
                "first_name", "last_name", "mobile", "address",
                "is_monash_student", "vip_years", "vip_expires", "funds"
            ]
            super().__init__(csv_path, headers)
            self._users: Dict[str, User] = {}
            self._load_users()
            self._initialized = True
    
    def _load_users(self) -> None:
        """Loads all users from CSV into memory as User objects."""
        rows = self._read_all_rows()
        self._users = {}
        
        for row in rows:
            try:
                user = UserFactory.create_user(row)
                self._users[user.get_email().lower()] = user
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid user row: {e}")
                continue
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Finds a user by email.
        
        Args:
            email (str): User email
            
        Returns:
            User or None if not found
        """
        return self._users.get(email.lower())
    
    def find_all(self) -> List[User]:
        """
        Returns all users.
        
        Returns:
            list: List of all User objects
        """
        return list(self._users.values())
    
    def find_customers(self) -> List[Customer]:
        """
        Returns all customers.
        
        Returns:
            list: List of Customer objects only
        """
        return [u for u in self._users.values() if isinstance(u, Customer)]
    
    def find_administrators(self) -> List[Administrator]:
        """
        Returns all administrators.
        
        Returns:
            list: List of Administrator objects only
        """
        return [u for u in self._users.values() if isinstance(u, Administrator)]
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticates a user by email and password.
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            User if credentials valid, None otherwise
        """
        user = self.find_by_email(email)
        if user and user.verify_password(password):
            return user
        return None
    
    def email_exists(self, email: str) -> bool:
        """
        Checks if email already exists.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email exists
        """
        return email.lower() in self._users
    
    def save(self, user: User) -> bool:
        """
        Saves a user (add or update).
        
        Args:
            user (User): User to save
            
        Returns:
            bool: True if successful
        """
        self._users[user.get_email().lower()] = user
        self._persist()
        return True
    
    def delete(self, email: str) -> bool:
        """
        Deletes a user by email.
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if deleted, False if not found
        """
        email_lower = email.lower()
        if email_lower in self._users:
            del self._users[email_lower]
            self._persist()
            return True
        return False
    
    def _persist(self) -> None:
        """Writes all users back to CSV."""
        rows = [user.to_dict() for user in self._users.values()]
        self._write_all_rows(rows)
    
    def reload(self) -> None:
        """Reloads users from CSV."""
        self._load_users()
    
    def get_count(self) -> int:
        """
        Returns total number of users.
        
        Returns:
            int: User count
        """
        return len(self._users)


class OrderRepository(BaseRepository):
    """
    Repository for Order persistence.
    Note: Order class will be created in next file, so this stores as dicts for now.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, csv_path: str):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(OrderRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str):
        """
        Initialize OrderRepository.
        
        Args:
            csv_path (str): Path to orders.csv
        """
        if not hasattr(self, '_initialized'):
            headers = [
                "order_id", "email", "datetime", "fulfilment", "delivery_address",
                "store_id", "promo_code", "promo_discount", "student_discount",
                "delivery_fee", "subtotal", "total", "lines_json"
            ]
            super().__init__(csv_path, headers)
            self._initialized = True
    
    def save(self, order_dict: Dict) -> bool:
        """
        Saves an order.
        
        Args:
            order_dict (dict): Order data as dictionary
            
        Returns:
            bool: True if successful
        """
        self._append_row(order_dict)
        return True
    
    def find_by_email(self, email: str) -> List[Dict]:
        """
        Finds all orders for a customer.
        
        Args:
            email (str): Customer email
            
        Returns:
            list: List of order dictionaries
        """
        all_orders = self._read_all_rows()
        return [o for o in all_orders if o.get('email', '').lower() == email.lower()]
    
    def find_by_order_id(self, order_id: str) -> Optional[Dict]:
        """
        Finds an order by ID.
        
        Args:
            order_id (str): Order ID
            
        Returns:
            dict or None
        """
        all_orders = self._read_all_rows()
        for order in all_orders:
            if order.get('order_id') == order_id:
                return order
        return None
    
    def find_all(self) -> List[Dict]:
        """
        Returns all orders.
        
        Returns:
            list: All order dictionaries
        """
        return self._read_all_rows()
    
    def customer_has_pickup_order(self, email: str) -> bool:
        """
        Checks if customer has any pickup orders.
        
        Args:
            email (str): Customer email
            
        Returns:
            bool: True if has pickup order
        """
        orders = self.find_by_email(email)
        for order in orders:
            if order.get('fulfilment', '').upper() == 'PICKUP':
                return True
        return False


class StoreRepository(BaseRepository):
    """
    Repository for Store/Pickup location data.
    Stores are simple dictionaries for now.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, csv_path: str):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(StoreRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str):
        """
        Initialize StoreRepository.
        
        Args:
            csv_path (str): Path to stores.csv
        """
        if not hasattr(self, '_initialized'):
            headers = ["store_id", "name", "address", "phone", "hours"]
            super().__init__(csv_path, headers)
            self._initialized = True
    
    def find_all(self) -> List[Dict]:
        """
        Returns all stores.
        
        Returns:
            list: All store dictionaries
        """
        return self._read_all_rows()
    
    def find_by_id(self, store_id: str) -> Optional[Dict]:
        """
        Finds a store by ID.
        
        Args:
            store_id (str): Store ID
            
        Returns:
            dict or None
        """
        stores = self.find_all()
        for store in stores:
            if store.get('store_id', '').upper() == store_id.upper():
                return store
        return None
    
    def store_exists(self, store_id: str) -> bool:
        """
        Checks if store exists.
        
        Args:
            store_id (str): Store ID
            
        Returns:
            bool: True if exists
        """
        return self.find_by_id(store_id) is not None


class MembershipHistoryRepository(BaseRepository):
    """
    Repository for VIP membership transaction history.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, csv_path: str):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MembershipHistoryRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str):
        """
        Initialize MembershipHistoryRepository.
        
        Args:
            csv_path (str): Path to membership.csv
        """
        if not hasattr(self, '_initialized'):
            headers = ["email", "action", "years", "amount", "datetime", "notes"]
            super().__init__(csv_path, headers)
            self._initialized = True
    
    def save(self, entry: Dict) -> bool:
        """
        Saves a membership history entry.
        
        Args:
            entry (dict): Membership transaction data
            
        Returns:
            bool: True if successful
        """
        self._append_row(entry)
        return True
    
    def find_by_email(self, email: str) -> List[Dict]:
        """
        Finds all membership history for a customer.
        
        Args:
            email (str): Customer email
            
        Returns:
            list: Membership history entries
        """
        all_entries = self._read_all_rows()
        return [e for e in all_entries if e.get('email', '').lower() == email.lower()]
    
    def find_all(self) -> List[Dict]:
        """
        Returns all membership history.
        
        Returns:
            list: All entries
        """
        return self._read_all_rows()