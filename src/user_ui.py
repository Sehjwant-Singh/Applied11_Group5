"""
user_ui.py
----------
User interface layer for customer profile and membership management.
Works with OOP User/Customer objects instead of dictionaries.
Handles: Profile viewing, funds top-up, VIP membership, order history, contact updates.
"""

import os
from datetime import datetime
from data import get_membership_repository, save_user_object


# ====== Simple helpers (no colors) ======
def clear():
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def _line(char="=", width=72):
    """Prints a horizontal line separator."""
    print(char * width)


def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue…")


# ====== CUSTOMER PROFILE MENU ======
def profile_menu(session):
    """
    Main profile and membership menu for customers.
    Works with Customer objects from session.
    
    Args:
        session (dict): Session containing current_user (Customer object)
    """
    # Only customers can access their profile - admins have different menus
    user = session["current_user"]
    if user.get_role() != "CUSTOMER":
        print("Profile is not available for admin accounts.")
        pause()
        return
    
    while True:
        clear()
        _line("=")
        print("PROFILE & MEMBERSHIP".center(72))
        _line("=")
        
        # Display customer information using OOP methods
        print(f"Name: {user.get_full_name()}")
        print(f"Email: {user.get_email()}")
        print(f"Mobile: {user.get_mobile()}")
        print(f"Address: {user.get_address()}")
        print(f"Role: {user.get_role()}")
        
        # Student status
        student_status = "Yes" if user.is_student() else "No"
        print(f"Monash student: {student_status}")
        
        # VIP status
        vip_status = user.get_vip_status_string()
        print(f"VIP Status: {vip_status}")
        
        # Funds
        print(f"Funds: ${user.get_funds():.2f}")
        
        _line("-")
        print("1) Top up funds")
        print("2) Buy/Renew VIP ($20/year)")
        print("3) View order history")
        print("4) Update Mobile / Address")
        print("5) View membership history")
        print("6) Cancel VIP (non-refundable)")
        print("0) Back   M) Main Menu")
        
        ch = input("\n> ").strip().lower()
        
        if ch in ("0", "m"):
            # Save user state before returning
            save_user_object(user)
            return
        elif ch == "1":
            _top_up_funds(user)
        elif ch == "2":
            _buy_vip(user)
        elif ch == "3":
            _view_order_history(session)
        elif ch == "4":
            _update_contact_info(user)
        elif ch == "5":
            _view_membership_history(user)
        elif ch == "6":
            _cancel_vip(user)
        else:
            print("Invalid option.")
            pause()


# ====== TOP UP FUNDS ======
def _top_up_funds(customer):
    """
    Handles funds top-up for customer.
    Uses Customer object methods.
    
    Args:
        customer: Customer object
    """
    clear()
    _line("=")
    print("TOP UP FUNDS".center(72))
    _line("=")
    print(f"Current balance: ${customer.get_funds():.2f}")
    print(f"Maximum top-up per transaction: ${customer.MAX_TOP_UP:.2f}")
    
    amt_s = input("\nAmount to top up: $").strip()
    
    try:
        amt = float(amt_s)
    except ValueError:
        print("Invalid amount.")
        pause()
        return
    
    # Use Customer's top_up_funds method (has validation built-in)
    success = customer.top_up_funds(amt)
    
    if success:
        print(f"\n✓ Topped up successfully!")
        print(f"New balance: ${customer.get_funds():.2f}")
        
        # Save updated customer
        save_user_object(customer)
    else:
        print(f"\n✗ Top-up failed.")
        print(f"Amount must be between $0 and ${customer.MAX_TOP_UP:.2f}")
    
    pause()


# ====== BUY/RENEW VIP ======
def _buy_vip(customer):
    """
    Handles VIP membership purchase/renewal.
    Uses Customer object methods and VIPMembership composition.
    
    Args:
        customer: Customer object
    """
    clear()
    _line("=")
    print("BUY / RENEW VIP MEMBERSHIP".center(72))
    _line("=")
    
    # Show current status
    if customer.is_vip():
        print(f"Current VIP Status: {customer.get_vip_status_string()}")
    else:
        print("Current VIP Status: No active membership")
    
    print(f"\nCurrent funds: ${customer.get_funds():.2f}")
    print(f"VIP Cost: $20 per year")
    _line("-")
    
    years_s = input("Buy how many years of VIP? ").strip()
    
    try:
        years = int(years_s)
    except ValueError:
        print("Invalid input.")
        pause()
        return
    
    # Use Customer's buy_vip_membership method (handles everything)
    success, message = customer.buy_vip_membership(years)
    
    if success:
        print(f"\n✓ {message}")
        print(f"New balance: ${customer.get_funds():.2f}")
        
        # Log to membership history
        membership_repo = get_membership_repository()
        membership_repo.save({
            "email": customer.get_email(),
            "action": "RENEW" if customer.get_vip_membership().get_years() > years else "BUY",
            "years": str(years),
            "amount": f"{20.0 * years:.2f}",
            "datetime": datetime.now().isoformat(timespec="seconds"),
            "notes": ""
        })
        
        # Save updated customer
        save_user_object(customer)
    else:
        print(f"\n✗ {message}")
    
    pause()


# ====== VIEW ORDER HISTORY ======
def _view_order_history(session):
    """
    Displays customer's order history.
    
    Args:
        session (dict): Session with current_user and order_repository
    """
    clear()
    _line("=")
    print("ORDER HISTORY".center(72))
    _line("=")
    
    customer = session["current_user"]
    order_repo = session["order_repository"]
    
    # Get orders from repository
    orders = order_repo.find_by_email(customer.get_email())
    
    if not orders:
        print("\nNo past orders found.")
        pause()
        return
    
    # Display orders
    print(f"\nFound {len(orders)} order(s):\n")
    for order in orders:
        order_id = order.get('order_id', 'N/A')
        order_date = order.get('datetime', 'N/A')
        fulfilment = order.get('fulfilment', 'N/A')
        total = float(order.get('total', 0))
        
        print(f"Order ID: {order_id}")
        print(f"  Date: {order_date}")
        print(f"  Type: {fulfilment}")
        print(f"  Total: ${total:.2f}")
        
        # Show promo if used
        promo = order.get('promo_code', '')
        if promo:
            promo_discount = float(order.get('promo_discount', 0))
            print(f"  Promo: {promo} (-${promo_discount:.2f})")
        
        print()
    
    pause()


# ====== UPDATE CONTACT INFO ======
def _update_contact_info(customer):
    """
    Allows customers to update mobile and address.
    Per spec 2.2: Only mobile and address can be updated.
    
    Args:
        customer: Customer object
    """
    clear()
    _line("=")
    print("UPDATE MOBILE / ADDRESS".center(72))
    _line("=")
    
    print("Press Enter to keep current values in brackets.\n")
    
    cur_mobile = customer.get_mobile()
    cur_address = customer.get_address()
    
    new_mobile = input(f"Mobile [{cur_mobile}]: ").strip()
    new_address = input(f"Address [{cur_address}]: ").strip()
    
    # Update mobile if provided
    if new_mobile:
        success = customer.set_mobile(new_mobile)
        if not success:
            print("\n✗ Mobile validation failed. Should contain only digits and spaces.")
            pause()
            return
    
    # Update address if provided
    if new_address:
        customer.set_address(new_address)
    
    # Save updated customer
    if new_mobile or new_address:
        save_user_object(customer)
        print("\n✓ Contact information updated.")
    else:
        print("\nNo changes made.")
    
    pause()


# ====== VIEW MEMBERSHIP HISTORY ======
def _view_membership_history(customer):
    """
    Displays customer's VIP membership transaction history.
    
    Args:
        customer: Customer object
    """
    clear()
    _line("=")
    print("MEMBERSHIP HISTORY".center(72))
    _line("=")
    
    membership_repo = get_membership_repository()
    entries = membership_repo.find_by_email(customer.get_email())
    
    if not entries:
        print("\nNo membership history found.")
        pause()
        return
    
    print(f"\nFound {len(entries)} transaction(s):\n")
    
    for entry in entries:
        action = entry.get('action', 'N/A')
        years = entry.get('years', '0')
        amount = entry.get('amount', '0.00')
        date = entry.get('datetime', 'N/A')
        notes = entry.get('notes', '')
        
        print(f"{date} | {action}")
        print(f"  Years: {years} | Amount: ${amount}")
        if notes:
            print(f"  Notes: {notes}")
        print()
    
    pause()


# ====== CANCEL VIP ======
def _cancel_vip(customer):
    """
    Cancels VIP membership (non-refundable).
    Uses Customer's VIPMembership composition.
    
    Args:
        customer: Customer object
    """
    clear()
    _line("=")
    print("CANCEL VIP (NON-REFUNDABLE)".center(72))
    _line("=")
    
    if not customer.is_vip():
        print("\nNo active VIP membership to cancel.")
        pause()
        return
    
    print(f"Current VIP Status: {customer.get_vip_status_string()}")
    print("\n  Warning: Cancellation is non-refundable!")
    
    confirm = input("\nConfirm cancel VIP? (y/n): ").strip().lower()
    
    if confirm != "y":
        print("Cancelled operation.")
        pause()
        return
    
    # Use Customer's cancel_vip_membership method
    success, message = customer.cancel_vip_membership()
    
    if success:
        print(f"\n✓ {message}")
        
        # Log to membership history
        membership_repo = get_membership_repository()
        membership_repo.save({
            "email": customer.get_email(),
            "action": "CANCEL",
            "years": "0",
            "amount": "0.00",
            "datetime": datetime.now().isoformat(timespec="seconds"),
            "notes": "non-refundable"
        })
        
        # Save updated customer
        save_user_object(customer)
    else:
        print(f"\n✗ {message}")
    
    pause()