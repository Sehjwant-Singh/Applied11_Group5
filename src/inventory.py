"""
inventory.py
-------------
Customer browsing (list/filter) + add-to-cart
Admin product management (CRUD)
Now uses OOP Product objects and ProductRepository.
"""

import os
import time
from typing import List, Dict
from product import Product, FoodProduct, ProductFactory
from cart import CartManager


# ====== Simple UI helpers (no colors) ======
def clear():
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def _line(char="=", width=72):
    """Prints a horizontal line separator."""
    print(char * width)


def banner(title: str, subtitle: str = ""):
    """
    Displays a banner with title and optional subtitle.
    
    Args:
        title (str): Main title
        subtitle (str): Optional subtitle
    """
    clear()
    _line("=")
    print(title.center(72))
    if subtitle:
        print(subtitle.center(72))
    _line("=")


def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue…")


# ====== Helper: sort in-stock products first ======
def _sorted_instock_first(products: List[Product]) -> List[Product]:
    """
    Sorts products with in-stock items first, then by name.
    
    Args:
        products (list): List of Product objects
        
    Returns:
        list: Sorted Product objects
    """
    return sorted(
        products,
        key=lambda p: (not p.is_in_stock(), p.get_name().lower())
    )


# ====== Filtering logic using repository ======
def list_products(session, filters: Dict = None) -> List[Product]:
    """
    Lists products with optional filters using ProductRepository.
    
    Args:
        session (dict): Session with product_repository
        filters (dict): Filter criteria (optional)
        
    Returns:
        list: List of Product objects
    """
    product_repo = session["product_repository"]
    
    if not filters:
        # Get all products
        products = product_repo.find_all()
    else:
        # Use repository's filter method
        products = product_repo.find_by_filter(filters)
    
    # Sort in-stock first
    return _sorted_instock_first(products)


# ====== Pretty table printer for Product objects ======
def _print_products(products: List[Product]):
    """
    Prints products in a formatted table.
    
    Args:
        products (list): List of Product objects
    """
    if not products:
        print("\nNo products matched.")
        return
    
    # Calculate column widths dynamically
    names = [p.get_name() for p in products]
    brands = [p.get_brand() for p in products]
    cats = [f"{p.get_category()}/{p.get_subcategory()}" for p in products]
    
    w_name = max(4, min(24, max(len("Name"), *(len(n) for n in names))))
    w_brand = max(4, min(14, max(len("Brand"), *(len(b) for b in brands))))
    w_cat = max(4, min(22, max(len("Cat/Subcat"), *(len(c) for c in cats))))
    w_price = 8
    w_vip = 8
    w_qty = 5
    
    # Print header
    print()
    print(f"{'SKU':<8} {'Name':<{w_name}} {'Brand':<{w_brand}} {'Cat/Subcat':<{w_cat}} "
          f"{'$Price':>{w_price}} {'$VIP':>{w_vip}} {'Qty':>{w_qty}}")
    print("-" * (8 + 1 + w_name + 1 + w_brand + 1 + w_cat + 1 + w_price + 1 + w_vip + 1 + w_qty))
    
    # Print products
    for p in products:
        cat = f"{p.get_category()}/{p.get_subcategory()}"
        print(f"{p.get_sku():<8} {p.get_name():<{w_name}.{w_name}} "
              f"{p.get_brand():<{w_brand}.{w_brand}} {cat:<{w_cat}.{w_cat}} "
              f"{p.get_price():>{w_price}.2f} {p.get_member_price():>{w_vip}.2f} "
              f"{p.get_quantity():>{w_qty}}")
    
    print()


# ====== Customer browsing menu ======
def browse_menu(session):
    """
    Customer product browsing and filtering menu.
    
    Args:
        session (dict): Session with current_user, cart, product_repository
    """
    while True:
        banner("BROWSE PRODUCTS")
        print("Tip: Enter 'M' anytime to return to Main Menu.")
        _line("-")
        print("1) List All")
        print("2) Filter")
        print("3) View Cart / Checkout")
        print("0) Back   M) Main Menu")
        ch = input("\n> ").strip().lower()
        
        if ch in ("0", "m"):
            return
        elif ch == "1":
            # List all products
            products = list_products(session)
            _print_products(products)
            _add_to_cart_flow(session, products)
            pause()
        elif ch == "2":
            # Filter products
            _filter_and_display(session)
        elif ch == "3":
            # View cart / checkout
            from checkout import cart_menu
            cart_menu(session)
        else:
            print("Invalid option.")
            pause()


def _filter_and_display(session):
    """
    Handles product filtering workflow.
    
    Args:
        session (dict): Session with product_repository
    """
    _line("-")
    print("Leave any field empty to skip it.")
    
    # Get filter inputs
    cat = input("Category: ").strip()
    sub = input("Subcategory: ").strip()
    brand = input("Brand: ").strip()
    price_min = input("Min price: ").strip()
    price_max = input("Max price: ").strip()
    avail = input("Availability [in/out]: ").strip()
    
    # Build filters dictionary
    filters = {}
    if cat:
        filters["category"] = cat
    if sub:
        filters["subcategory"] = sub
    if brand:
        filters["brand"] = brand
    if price_min:
        filters["price_min"] = price_min
    if price_max:
        filters["price_max"] = price_max
    if avail:
        filters["availability"] = avail
    
    # Apply filters and display
    products = list_products(session, filters)
    _print_products(products)
    _add_to_cart_flow(session, products)
    pause()


# ====== Add-to-cart logic (customer side) ======
def _add_to_cart_flow(session, products: List[Product]):
    """
    Handles adding products to cart.
    Uses CartManager for OOP cart operations.
    
    Args:
        session (dict): Session with cart and product_repository
        products (list): List of Product objects currently displayed
    """
    if not products:
        return
    
    # Create CartManager for easier operations
    cart = session["cart"]
    product_repo = session["product_repository"]
    cart_manager = CartManager(cart, product_repo)
    
    # Build lookup by SKU
    by_sku = {p.get_sku(): p for p in products}
    
    while True:
        _line("-")
        print("Add items to cart (Enter to stop).")
        sku = input("SKU: ").strip()
        
        if not sku:
            return
        
        if sku not in by_sku:
            print("Unknown SKU.")
            continue
        
        qty_s = input("Qty (1–10): ").strip()
        try:
            qty = int(qty_s)
        except ValueError:
            print("Invalid quantity.")
            continue
        
        # Use CartManager to add (handles all validation)
        success, message = cart_manager.add_product_by_sku(sku, qty)
        
        if success:
            print(f"✓ {message}")
            # Show cart summary
            summary = cart.get_summary(is_vip=session["current_user"].is_vip())
            print(f"Cart: {summary['total_quantity']}/20 items, ${summary['subtotal']:.2f}")
        else:
            print(f"✗ {message}")


# ====== Admin inventory management ======
def admin_inventory_menu(session):
    """
    Admin product management menu (CRUD operations).
    Uses Product objects and ProductRepository.
    
    Args:
        session (dict): Session with product_repository
    """
    product_repo = session["product_repository"]
    
    while True:
        banner("ADMIN – PRODUCT & INVENTORY")
        print("1) List Products")
        print("2) Add Product")
        print("3) Edit Product")
        print("4) Delete Product")
        print("0) Back   M) Main Menu")
        ch = input("\n> ").strip().lower()
        
        if ch in ("0", "m"):
            return
        elif ch == "1":
            _admin_list_products(product_repo)
        elif ch == "2":
            _admin_add_product(product_repo)
        elif ch == "3":
            _admin_edit_product(product_repo)
        elif ch == "4":
            _admin_delete_product(product_repo)
        else:
            print("Invalid option.")
            pause()


def _admin_list_products(product_repo):
    """
    Lists all products for admin view.
    
    Args:
        product_repo: ProductRepository instance
    """
    products = product_repo.find_all()
    products = _sorted_instock_first(products)
    _print_products(products)
    pause()


def _admin_add_product(product_repo):
    """
    Handles adding a new product.
    Uses ProductFactory to create Product/FoodProduct.
    
    Args:
        product_repo: ProductRepository instance
    """
    _line("-")
    print("Enter product fields. Leave blank for optional text fields.")
    
    # Collect required fields
    field_data = {}
    
    # Basic fields
    field_data["sku"] = input("SKU: ").strip()
    field_data["name"] = input("Name: ").strip()
    field_data["brand"] = input("Brand: ").strip()
    field_data["description"] = input("Description: ").strip()
    
    # Category (check 10-category limit)
    current_categories = product_repo.get_all_categories()
    print(f"\nExisting categories ({len(current_categories)}/10): {', '.join(current_categories)}")
    field_data["category"] = input("Category: ").strip()
    field_data["subcategory"] = input("Subcategory: ").strip()
    
    # Check category limit
    new_cat = field_data["category"]
    if new_cat and new_cat not in current_categories and len(current_categories) >= 10:
        print("\n✗ Cannot add product: category limit (10) reached.")
        print("Please reuse an existing category.")
        pause()
        return
    
    # Pricing
    field_data["price"] = input("Price: ").strip()
    field_data["member_price"] = input("Member Price: ").strip()
    field_data["quantity"] = input("Quantity: ").strip()
    
    # Is food?
    is_food = input("Is food product? (y/n): ").strip().lower() == 'y'
    field_data["is_food"] = "True" if is_food else "False"
    
    # Food-specific fields
    if is_food:
        field_data["expiry_date"] = input("Expiry Date (YYYY-MM-DD): ").strip()
        field_data["ingredients"] = input("Ingredients: ").strip()
        field_data["storage"] = input("Storage Instructions: ").strip()
        field_data["allergens"] = input("Allergens: ").strip()
    else:
        field_data["expiry_date"] = ""
        field_data["ingredients"] = ""
        field_data["storage"] = ""
        field_data["allergens"] = ""
    
    # Validate required fields
    if not all([field_data["sku"], field_data["name"], field_data["brand"],
                field_data["category"], field_data["subcategory"],
                field_data["price"], field_data["member_price"], field_data["quantity"]]):
        print("\n✗ Missing required fields.")
        pause()
        return
    
    # Check for duplicate SKU
    if product_repo.find_by_sku(field_data["sku"]):
        print(f"\n✗ Product with SKU {field_data['sku']} already exists.")
        pause()
        return
    
    # Validate pricing
    try:
        price = float(field_data["price"])
        member_price = float(field_data["member_price"])
        quantity = int(field_data["quantity"])
        
        if price <= 0:
            print("\n✗ Price must be positive.")
            pause()
            return
        
        if member_price > price:
            print("\n✗ Member price cannot exceed regular price.")
            pause()
            return
        
        if quantity < 0:
            print("\n✗ Quantity cannot be negative.")
            pause()
            return
    except ValueError:
        print("\n✗ Invalid numeric values.")
        pause()
        return
    
    # Create product using Factory
    try:
        product = ProductFactory.create_product(field_data)
        product_repo.save(product)
        print(f"\n✓ Product {product.get_sku()} added successfully.")
    except Exception as e:
        print(f"\n✗ Failed to create product: {e}")
    
    pause()


def _admin_edit_product(product_repo):
    """
    Handles editing an existing product.
    
    Args:
        product_repo: ProductRepository instance
    """
    _line("-")
    print("Available products:")
    products = _sorted_instock_first(product_repo.find_all())
    _print_products(products)
    
    sku = input("\nSKU to edit: ").strip()
    product = product_repo.find_by_sku(sku)
    
    if not product:
        print("✗ Product not found.")
        pause()
        return
    
    print("\nPress Enter to keep current value in brackets.")
    
    # Basic fields
    name = input(f"Name [{product.get_name()}]: ").strip()
    if name:
        product.set_name(name)
    
    brand = input(f"Brand [{product.get_brand()}]: ").strip()
    if brand:
        product.set_brand(brand)
    
    desc = input(f"Description [{product.get_description()}]: ").strip()
    if desc:
        product.set_description(desc)
    
    # Category
    original_category = product.get_category()
    current_categories = product_repo.get_all_categories()
    print(f"Existing categories: {', '.join(current_categories)}")
    
    cat = input(f"Category [{product.get_category()}]: ").strip()
    if cat and cat != original_category:
        # Check category limit
        if cat not in current_categories and len(current_categories) >= 10:
            print("✗ Category limit (10) exceeded. Keeping original category.")
            cat = original_category
        product.set_category(cat)
    
    subcat = input(f"Subcategory [{product.get_subcategory()}]: ").strip()
    if subcat:
        product.set_subcategory(subcat)
    
    # Pricing
    price_str = input(f"Price [{product.get_price():.2f}]: ").strip()
    if price_str:
        try:
            price = float(price_str)
            if not product.set_price(price):
                print("✗ Invalid price (must be positive).")
        except ValueError:
            print("✗ Invalid price format.")
    
    member_price_str = input(f"Member Price [{product.get_member_price():.2f}]: ").strip()
    if member_price_str:
        try:
            member_price = float(member_price_str)
            if not product.set_member_price(member_price):
                print("✗ Invalid member price (must be ≤ regular price).")
        except ValueError:
            print("✗ Invalid member price format.")
    
    qty_str = input(f"Quantity [{product.get_quantity()}]: ").strip()
    if qty_str:
        try:
            qty = int(qty_str)
            if not product.set_quantity(qty):
                print("✗ Invalid quantity (must be ≥ 0).")
        except ValueError:
            print("✗ Invalid quantity format.")
    
    # Food-specific fields (if food product)
    if product.is_food_product():
        food_product = product  # It's a FoodProduct instance
        
        expiry = input(f"Expiry Date [{food_product.get_expiry_date()}]: ").strip()
        if expiry:
            food_product.set_expiry_date(expiry)
        
        ingredients = input(f"Ingredients [{food_product.get_ingredients()}]: ").strip()
        if ingredients:
            food_product.set_ingredients(ingredients)
        
        storage = input(f"Storage [{food_product.get_storage()}]: ").strip()
        if storage:
            food_product.set_storage(storage)
        
        allergens = input(f"Allergens [{food_product.get_allergens()}]: ").strip()
        if allergens:
            food_product.set_allergens(allergens)
    
    # Save updated product
    product_repo.save(product)
    print(f"\n✓ Product {product.get_sku()} updated successfully.")
    pause()


def _admin_delete_product(product_repo):
    """
    Handles deleting a product.
    
    Args:
        product_repo: ProductRepository instance
    """
    _line("-")
    sku = input("SKU to delete: ").strip()
    
    product = product_repo.find_by_sku(sku)
    if not product:
        print("✗ Product not found.")
        pause()
        return
    
    # Confirm deletion
    confirm = input(f"Delete '{product.get_name()}' (SKU: {sku})? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        pause()
        return
    
    # Delete
    success = product_repo.delete(sku)
    if success:
        print(f"✓ Product {sku} deleted successfully.")
    else:
        print(f"✗ Failed to delete product.")
    
    pause()