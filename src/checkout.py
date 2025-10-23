"""
checkout.py
-----------
Shopping cart and checkout functionality using full OOP architecture.
Integrates: Order, Promotion, Cart, Customer, Product, Repositories
Demonstrates complete OOP system with all design patterns.
"""

import os

from cart import CartManager
from order import OrderBuilder, OrderManager, Order
from promotion import PromotionFactory, PromotionManager, PromotionValidator

# ====== UI helpers (no colours) ======
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
    width = 72
    _line("=", width)
    print(title.center(width))
    if subtitle:
        print(subtitle.center(width))
    _line("=", width)

def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue…")

# ====== Cart rendering using OOP ======
def _render_cart(cart, is_vip: bool = False):
    """
    Renders shopping cart contents in a formatted table.
    Uses CartItem objects from ShoppingCart.
    Args:
        cart: ShoppingCart object
        is_vip (bool): Whether to show VIP pricing
    """
    cart_items = cart.get_items()
    if not cart_items:
        print("\nYour cart is empty.")
        return

    names = [item.get_name() for item in cart_items]
    w_name = max(4, min(28, max(len("Name"), *(len(n) for n in names))))

    print()
    print(f"{'SKU':<8} {'Name':<{w_name}} {'Qty':>3} {'Unit$':>10} {'VIP$':>10} {'Line$':>10}")
    print("-" * (8 + 1 + w_name + 1 + 3 + 1 + 10 + 1 + 10 + 1 + 10))
    for item in cart_items:
        unit = item.get_regular_price()
        vip_price = item.get_member_price()
        qty = item.get_quantity()
        line = item.get_line_total(is_vip)
        print(f"{item.get_sku():<8} {item.get_name():<{w_name}.{w_name}} "
              f"{qty:>3} {unit:>10.2f} {vip_price:>10.2f} {line:>10.2f}")
    print()

# ====== Main cart menu ======
def cart_menu(session):
    """
    Main cart menu - view cart, manage items, checkout.
    Uses OOP ShoppingCart and CartManager.
    Args:
        session (dict): Session with current_user, cart, repositories
    """
    customer = session["current_user"]
    cart = session["cart"]
    product_repo = session["product_repository"]

    cart_manager = CartManager(cart, product_repo)
    while True:
        banner("YOUR CART")
        is_vip = customer.is_vip() if hasattr(customer, 'is_vip') else False
        _render_cart(cart, is_vip)
        summary = cart.get_summary(is_vip)
        print(f"Total items: {summary['total_quantity']}/20")
        print(f"Subtotal: ${summary['subtotal']:.2f}")
        if is_vip and summary['vip_savings'] > 0:
            print(f"VIP Savings: ${summary['vip_savings']:.2f}")
        _line("-")
        print("1) Checkout")
        print("2) Remove an item")
        print("3) Update quantity")
        print("4) Clear cart")
        print("5) View available promotions")
        print("0) Back M) Main Menu")
        ch = input("\n> ").strip().lower()
        if ch in ("0", "m"):
            return
        elif ch == "1":
            _checkout_flow(session)
        elif ch == "2":
            _remove_item_flow(cart_manager)
        elif ch == "3":
            _update_quantity_flow(cart_manager)
        elif ch == "4":
            confirm = input("Clear all items from cart? (y/n): ").strip().lower()
            if confirm == 'y':
                cart_manager.clear_cart()
                print("✓ Cart cleared.")
                pause()
        elif ch == "5":
            _show_available_promotions(session)
        else:
            print("Invalid option.")
            pause()

# ====== Cart item management ======
def _remove_item_flow(cart_manager):
    """Handles removing item from cart."""
    cart = cart_manager.get_cart()
    if cart.is_empty():
        print("Cart is empty.")
        pause()
        return
    sku = input("\nEnter SKU to remove: ").strip()
    success, message = cart_manager.remove_product(sku)
    print(f"{'✓' if success else '✗'} {message}")
    pause()

def _update_quantity_flow(cart_manager):
    """Handles updating item quantity in cart."""
    cart = cart_manager.get_cart()
    if cart.is_empty():
        print("Cart is empty.")
        pause()
        return
    sku = input("\nEnter SKU to update: ").strip()
    item = cart.find_item_by_sku(sku)
    if not item:
        print("✗ Product not found in cart.")
        pause()
        return
    print(f"Current quantity: {item.get_quantity()}")
    new_qty_str = input("New quantity (1-10): ").strip()
    try:
        new_qty = int(new_qty_str)
    except ValueError:
        print("✗ Invalid quantity.")
        pause()
        return
    success, message = cart_manager.update_product_quantity(sku, new_qty)
    print(f"{'✓' if success else '✗'} {message}")
    pause()

# ====== Promotion display ======
def _show_available_promotions(session):
    """Shows all available promotions and their eligibility."""
    clear()
    _line("=")
    print("AVAILABLE PROMOTIONS".center(72))
    _line("=")
    customer = session["current_user"]
    order_repo = session["order_repository"]
    all_promos = PromotionFactory.get_all_promotions()
    if not all_promos:
        print("\nNo promotions currently available.")
        pause()
        return
    print()
    for code, promo in all_promos.items():
        print(f"Code: {promo.get_code()}")
        print(f" Description: {promo.get_description()}")
        print(f" Discount: {promo.get_discount_percentage()}% off products subtotal")
        print(f" Requirements: {promo.get_eligibility_requirements()}")
        eligible_delivery, _ = promo.is_eligible(customer, "DELIVERY", order_repo)
        eligible_pickup, _ = promo.is_eligible(customer, "PICKUP", order_repo)
        if eligible_delivery and eligible_pickup:
            print(f" ✓ Eligible for both delivery and pickup")
        elif eligible_delivery:
            print(f" ✓ Eligible for delivery orders")
        elif eligible_pickup:
            print(f" ✓ Eligible for pickup orders")
        else:
            print(f" ✗ Not currently eligible")
        print()
    pause()

# ====== Main checkout flow ======
def _checkout_flow(session):
    """
    Main checkout flow using OOP Order, Promotion, and repositories.
    This is the core of the checkout system!
    Args:
        session (dict): Complete session with all entities and repositories
    """
    customer = session["current_user"]
    cart = session["cart"]
    product_repo = session["product_repository"]
    order_repo = session["order_repository"]
    user_repo = session["user_repository"]

    # Validate customer role
    if customer.get_role() != "CUSTOMER":
        print("Only customers can checkout.")
        pause()
        return

    # Validate cart not empty
    if cart.is_empty():
        print("Your cart is empty.")
        pause()
        return

    # Validate stock availability
    valid, message = cart.validate_all_stock()
    if not valid:
        print(f"✗ Cannot proceed: {message}")
        pause()
        return

    # Step 1: Choose fulfilment type
    fulfilment_result = _choose_fulfilment(session)
    if not fulfilment_result:
        return  # User cancelled
    fulfilment, delivery_address, store_id = fulfilment_result

    # Step 2: Choose promotion (optional)
    promotion = _choose_promotion(session, fulfilment)

    # Step 3: Build the order step by step using the OrderBuilder
    # This is where we put together all the pieces: customer, items, delivery/pickup, and any promotions
    try:
        order_builder = OrderBuilder(customer)  # Start with the customer

        # Set up delivery or pickup based on what the customer chose
        if fulfilment == "DELIVERY":
            order_builder.set_delivery(delivery_address)
        else:
            order_builder.set_pickup(store_id)

        # Add all the items from their cart
        order_builder.add_items_from_cart(cart.get_items())

        # Apply any promotion code they might have
        if promotion:
            order_builder.apply_promotion(promotion)

        # Finally, build the complete order
        order = order_builder.build()
    except Exception as e:
        print(f"✗ Failed to create order: {e}")
        pause()
        return

    # Step 4: Show order summary and confirm
    _show_order_summary(order, customer)
    confirm = input("\nConfirm checkout? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Checkout cancelled.")
        pause()
        return

    # Step 5: Place order using OrderManager (Facade Pattern!)
    order_manager = OrderManager(order_repo, product_repo, user_repo)
    success, message = order_manager.place_order(order)
    if success:
        banner("ORDER CONFIRMED")
        print(f"Order ID: {order.get_order_id()}")
        print(f"✓ {message}")
        _show_order_summary(order, customer)
        cart.clear()
        print("\nThank you for your order!")
    else:
        print(f"\n✗ Order failed: {message}")
        pause()

# ====== Fulfilment selection ======
def _choose_fulfilment(session):
    """
    Handles fulfilment type selection (delivery or pickup).
    Returns tuple: (fulfilment, delivery_address, store_id) or None if cancelled.
    Args:
        session (dict): Session with current_user
    Returns:
        tuple or None: (fulfilment_type, address, store_id) or None
    """
    customer = session["current_user"]
    while True:
        banner("CHECKOUT – FULFILMENT")
        print("1) Delivery")
        print("2) Pickup")
        print("0) Cancel")
        ch = input("\n> ").strip()
        if ch == "0":
            return None
        elif ch == "1":
            delivery_address = customer.get_address()
            if not delivery_address:
                print("\n✗ No delivery address on file.")
                print("Please update your profile with a delivery address first.")
                pause()
                return None
            print(f"\nDelivery to: {delivery_address}")
            is_student = customer.is_student() if hasattr(customer, 'is_student') else False
            if is_student:
                print("Delivery fee: FREE (Monash student benefit)")
            else:
                print(f"Delivery fee: ${Order.DELIVERY_FEE:.2f}")
            confirm = input("\nConfirm delivery address? (y/n): ").strip().lower()
            if confirm == 'y':
                return ("DELIVERY", delivery_address, "")
        elif ch == "2":
            from data import get_store_repository
            store_repo = get_store_repository()
            stores = store_repo.find_all()
            if not stores:
                print("✗ No stores available.")
                pause()
                return None
            print("\nAvailable stores:")
            for store in stores:
                print(f" {store['store_id']}: {store['name']}")
                print(f" Address: {store['address']}")
                print(f" Phone: {store['phone']}")
                print(f" Hours: {store['hours']}")
                print()
            store_id = input("Enter Store ID: ").strip().upper()
            if not store_repo.store_exists(store_id):
                print("✗ Invalid store ID.")
                pause()
                continue
            is_student = customer.is_student() if hasattr(customer, 'is_student') else False
            if is_student:
                print(f"\nPickup discount: 5% off items (Monash student benefit)")
            return ("PICKUP", "", store_id)
        else:
            print("Invalid option.")
            pause()

# ====== Promotion selection ======
def _choose_promotion(session, fulfilment: str):
    """
    Handles promotion code selection with validation.
    Uses PromotionManager and PromotionValidator.
    Args:
        session (dict): Session with current_user, order_repository
        fulfilment (str): Selected fulfilment type
    Returns:
        PromotionStrategy or None: Selected promotion or None
    """
    customer = session["current_user"]
    order_repo = session["order_repository"]
    _line("-")
    print("\n" + PromotionFactory.get_promotion_list_display())
    _line("-")
    use_promo = input("\nApply a promo code? (y/n): ").strip().lower()
    if use_promo != 'y':
        return None
    code = input("Enter promo code: ").strip().upper()
    validator = PromotionValidator(order_repo)
    valid, message, promotion = validator.validate_promotion(code, customer, fulfilment)
    if valid:
        print(f"✓ {message}")
        return promotion
    else:
        print(f"✗ {message}")
        retry = input("Try another code? (y/n): ").strip().lower()
        if retry == 'y':
            return _choose_promotion(session, fulfilment)
    return None

# ====== Order summary display ======
def _show_order_summary(order, customer):
    """Displays complete order summary with all pricing details."""
    _line("=")
    print("ORDER SUMMARY".center(72))
    _line("=")
    print(f"Customer: {customer.get_full_name()} | Email: {customer.get_email()}")
    print(f"Fulfilment: {order.get_fulfilment()}")
    if order.get_fulfilment() == "DELIVERY":
        print(f"Delivery address: {order.get_delivery_address()}")
    else:
        print(f"Pickup store: {order.get_store_id()}")
    print("\nItems:")
    items = order.get_items()
    if items:
        names = [item.get_name() for item in items]
        w_name = max(4, min(28, max(len("Name"), *(len(n) for n in names))))
        print(f"{'SKU':<8} {'Name':<{w_name}} {'Qty':>3} {'Unit$':>10} {'VIP$':>10} {'Line$':>10}")
        print("-" * (8 + 1 + w_name + 1 + 3 + 1 + 10 + 1 + 10 + 1 + 10))
        for item in items:
            print(f"{item.get_sku():<8} {item.get_name():<{w_name}.{w_name}} "
                  f"{item.get_quantity():>3} {item.get_unit_price():>10.2f} "
                  f"{item.get_member_price():>10.2f} {item.get_line_total():>10.2f}")
        print()
    vip_note = "Yes" if order.is_vip_order() else "No"
    print(f"VIP prices applied: {vip_note}")
    print(f"\nItems subtotal: ${order.get_subtotal():>10.2f}")
    if order.get_student_discount() > 0:
        print(f"Student discount: -${order.get_student_discount():>10.2f}")
    if order.get_promo_code():
        print(f"Promo ({order.get_promo_code()}): -${order.get_promo_discount():>10.2f}")
    if order.get_delivery_fee() > 0:
        print(f"Delivery fee: +${order.get_delivery_fee():>10.2f}")
    _line("-")
    print(f"TOTAL: ${order.get_total():>10.2f}")
    _line("=")
