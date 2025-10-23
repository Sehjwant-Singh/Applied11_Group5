"""
main.py
-------
MMOSS Monash Merchant Online Supermarket System (Terminal Edition)
Entry point for the application using OOP architecture.
Initializes repositories and manages application session.
"""

import os
import sys
from data import get_user_repository, get_product_repository, get_order_repository
from cart import ShoppingCart


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
    width = 72
    _line("=", width)
    print(title.center(width))
    if subtitle:
        print(subtitle.center(width))
    _line("=", width)


def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue…")


# ====== Login Menu ======
def login_menu():
    """
    Displays login menu and authenticates user.
    Returns User object (Customer or Administrator) or None.
    
    Returns:
        User: Authenticated User object or None if exit
    """
    user_repo = get_user_repository()
    
    while True:
        clear()
        _line("=")
        print("MMOSS LOGIN".center(72))
        _line("=")
        print("1) Login")
        print("0) Exit")
        choice = input("\n> ").strip()
        
        if choice == "0":
            return None
        
        if choice == "1":
            email = input("Email: ").strip()
            
            # Use getpass for password (hidden input)
            try:
                import getpass
                pwd = getpass.getpass("Password: ")
            except:
                pwd = input("Password: ")
            
            # Authenticate using repository (returns User object)
            user = user_repo.authenticate(email, pwd)
            
            if user:
                print(f"\nWelcome, {user.get_first_name()}! Role: {user.get_role()}")
                pause()
                return user
            else:
                print("Invalid credentials. Try again.")
                pause()
        else:
            print("Invalid option.")
            pause()


# ====== Main Application Loop ======
def run() -> None:
    """
    Main application entry point.
    Manages login and runs main menu loop.
    CSV files are auto-initialized when data.py is imported.
    """
    # Initialize repositories (lazy loaded when accessed)
    user_repo = get_user_repository()
    product_repo = get_product_repository()
    order_repo = get_order_repository()
    
    # Keep the app running until the user decides to quit
    while True:
        # First, get the user to log in
        user = login_menu()
        if not user:
            print("Goodbye!")
            break
        
        # Set up everything the user will need for their session
        # This includes their shopping cart and access to all the data
        session = {
            "current_user": user,  # User object (Customer or Administrator)
            "cart": ShoppingCart(),  # OOP ShoppingCart
            "user_repository": user_repo,
            "product_repository": product_repo,
            "order_repository": order_repo
        }
        
        # Main menu loop
        while True:
            banner("MAIN MENU")
            print(f"Logged in as: {user.get_full_name()}  ({user.get_role()})")
            print(f"Email: {user.get_email()}")
            _line("-", 72)
            print("Tip: Enter 'M' anytime in menus to return here.")
            _line("-", 72)
            
            if user.get_role() == "ADMIN":
                # Admin menu
                print("4) Admin: Product & Inventory")
                print("9) Logout")
                choice = input("\n> ").strip().lower()
                
                if choice == "4":
                    from inventory import admin_inventory_menu
                    admin_inventory_menu(session)
                elif choice in ("9", "m"):
                    print("\nLogging out…")
                    pause()
                    break
                else:
                    print("Invalid option.")
                    pause()
            else:
                # Customer menu
                # Display funds and VIP status
                if hasattr(user, 'get_funds'):
                    print(f"Funds: ${user.get_funds():.2f}", end="")
                    if hasattr(user, 'is_vip') and user.is_vip():
                        vip_status = user.get_vip_status_string()
                        print(f"  |  {vip_status}")
                    else:
                        print()
                _line("-", 72)
                
                print("1) Browse & Shop")
                print("2) View Cart / Checkout")
                print("3) Profile & Membership")
                print("9) Logout")
                choice = input("\n> ").strip().lower()
                
                if choice == "1":
                    from inventory import browse_menu
                    browse_menu(session)
                elif choice == "2":
                    from checkout import cart_menu
                    cart_menu(session)
                elif choice == "3":
                    from user_ui import profile_menu
                    profile_menu(session)
                elif choice in ("9", "m"):
                    print("\nLogging out…")
                    # Save user state before logout
                    user_repo.save(user)
                    pause()
                    break
                else:
                    print("Invalid option.")
                    pause()


# ====== Application Entry Point ======
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\nSession terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)