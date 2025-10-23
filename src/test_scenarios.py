#!/usr/bin/env python3
"""
Test Scenarios for MMOSS System
Tests all the edge cases and validation scenarios mentioned.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Import the system modules
from data import get_user_repository, get_product_repository, get_order_repository
from user import Customer, Administrator, UserFactory
from product import Product, FoodProduct, ProductFactory
from cart import ShoppingCart, CartItem
from order import OrderBuilder, OrderManager
from repositories import UserRepository, ProductRepository, OrderRepository

class TestRunner:
    """Comprehensive test runner for MMOSS system validation."""
    
    def __init__(self):
        """Initialize test runner with repositories."""
        self.user_repo = get_user_repository()
        self.product_repo = get_product_repository()
        self.order_repo = get_order_repository()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    def test_order_quantity_over_10(self):
        """Test: Order quantity over 10 should fail."""
        print("\n=== Testing: Order quantity over 10 should fail ===")
        
        try:
            # Get a product
            product = self.product_repo.find_by_sku("BK001")
            if not product:
                self.log_test("Order quantity over 10", False, "Test product not found")
                return
            
            # Try to create cart item with quantity > 10
            try:
                cart_item = CartItem(product, 11)  # This should raise ValueError
                self.log_test("Order quantity over 10", False, "Should have failed but didn't")
            except ValueError as e:
                if "Quantity must be between 1 and 10" in str(e):
                    self.log_test("Order quantity over 10", True, "Correctly rejected quantity > 10")
                else:
                    self.log_test("Order quantity over 10", False, f"Wrong error message: {e}")
            except Exception as e:
                self.log_test("Order quantity over 10", False, f"Unexpected error: {e}")
                
        except Exception as e:
            self.log_test("Order quantity over 10", False, f"Test setup failed: {e}")
    
    def test_insufficient_funds(self):
        """Test: Order without sufficient funds should fail."""
        print("\n=== Testing: Order without sufficient funds should fail ===")
        
        try:
            # Get a customer and manually reduce their funds
            customer = self.user_repo.find_by_email("student@student.monash.edu")
            if not customer:
                self.log_test("Insufficient funds", False, "Test customer not found")
                return
            
            # Manually reduce customer funds to insufficient amount
            original_funds = customer.get_funds()
            customer._funds = 10.0  # Set to very low amount
            
            # Get a product with high price
            product = self.product_repo.find_by_sku("EL003")  # $199.99 headphones
            if not product:
                self.log_test("Insufficient funds", False, "Test product not found")
                return
            
            # Create cart and add expensive item
            cart = ShoppingCart()
            success, msg = cart.add_item(product, 1)
            if not success:
                self.log_test("Insufficient funds", False, f"Failed to add item to cart: {msg}")
                return
            
            # Try to create order
            order_builder = OrderBuilder(customer)
            order_builder.set_delivery("Test Address")
            order_builder.add_items_from_cart(cart.get_items())
            
            try:
                order = order_builder.build()
                order_manager = OrderManager(self.order_repo, self.product_repo, self.user_repo)
                success, message = order_manager.place_order(order)
                
                if not success and "Insufficient funds" in message:
                    self.log_test("Insufficient funds", True, "Correctly rejected insufficient funds")
                else:
                    self.log_test("Insufficient funds", False, f"Should have failed but didn't: {message}")
                    
            except Exception as e:
                self.log_test("Insufficient funds", False, f"Order creation failed: {e}")
            
            # Restore original funds
            customer._funds = original_funds
                
        except Exception as e:
            self.log_test("Insufficient funds", False, f"Test setup failed: {e}")
    
    def test_change_product_category(self):
        """Test: Change category of an existing product."""
        print("\n=== Testing: Change category of an existing product ===")
        
        try:
            # Get a product
            product = self.product_repo.find_by_sku("BK001")
            if not product:
                self.log_test("Change product category", False, "Test product not found")
                return
            
            original_category = product.get_category()
            new_category = "Electronics"
            
            # Change category
            product.set_category(new_category)
            
            if product.get_category() == new_category:
                self.log_test("Change product category", True, f"Successfully changed from {original_category} to {new_category}")
            else:
                self.log_test("Change product category", False, "Category change failed")
                
        except Exception as e:
            self.log_test("Change product category", False, f"Test failed: {e}")
    
    def test_incomplete_product_fields(self):
        """Test: Adding new product with incomplete fields should fail."""
        print("\n=== Testing: Adding new product with incomplete fields should fail ===")
        
        try:
            # Try to create product with missing required fields
            incomplete_data = {
                "sku": "TEST001",
                "name": "Test Product",
                # Missing brand, description, etc.
            }
            
            # This should fail when trying to create the product
            try:
                product = ProductFactory.create_product(incomplete_data)
                self.log_test("Incomplete product fields", False, "Should have failed but didn't")
            except Exception as e:
                self.log_test("Incomplete product fields", True, f"Correctly rejected incomplete data: {type(e).__name__}")
                
        except Exception as e:
            self.log_test("Incomplete product fields", False, f"Test setup failed: {e}")
    
    def test_invalid_password_login(self):
        """Test: Invalid password login should fail."""
        print("\n=== Testing: Invalid password login should fail ===")
        
        try:
            # Try to authenticate with wrong password
            user = self.user_repo.authenticate("student@student.monash.edu", "WrongPassword123!")
            
            if user is None:
                self.log_test("Invalid password login", True, "Correctly rejected invalid password")
            else:
                self.log_test("Invalid password login", False, "Should have failed but didn't")
                
        except Exception as e:
            self.log_test("Invalid password login", False, f"Test failed: {e}")
    
    def test_order_more_than_stock(self):
        """Test: Ordering more than stock available should fail."""
        print("\n=== Testing: Ordering more than stock available should fail ===")
        
        try:
            # Get a product with limited stock
            product = self.product_repo.find_by_sku("BK002")  # Only 8 in stock
            if not product:
                self.log_test("Order more than stock", False, "Test product not found")
                return
            
            available_stock = product.get_quantity()
            order_quantity = available_stock + 1  # Try to order more than available
            
            # Try to add to cart
            cart = ShoppingCart()
            success, msg = cart.add_item(product, order_quantity)
            
            if not success and "Only" in msg and "available" in msg:
                self.log_test("Order more than stock", True, f"Correctly rejected order of {order_quantity} when only {available_stock} available")
            else:
                self.log_test("Order more than stock", False, f"Should have failed but didn't: {msg}")
                
        except Exception as e:
            self.log_test("Order more than stock", False, f"Test failed: {e}")
    
    def test_delete_membership_rebuy(self):
        """Test: Delete membership and buy again scenario."""
        print("\n=== Testing: Delete membership and buy again scenario ===")
        
        try:
            # Get a customer with VIP membership
            customer = self.user_repo.find_by_email("staff@monash.edu")
            if not customer or not hasattr(customer, 'get_vip_membership'):
                self.log_test("Delete membership rebuy", False, "Test customer with VIP not found")
                return
            
            # Check if customer has VIP
            if not customer.is_vip():
                self.log_test("Delete membership rebuy", False, "Customer doesn't have VIP membership")
                return
            
            # Cancel VIP membership
            success, msg = customer.cancel_vip_membership()
            if not success:
                self.log_test("Delete membership rebuy", False, f"Failed to cancel membership: {msg}")
                return
            
            # Verify membership is cancelled
            if not customer.is_vip():
                self.log_test("Delete membership rebuy", True, "Successfully cancelled VIP membership")
            else:
                self.log_test("Delete membership rebuy", False, "Membership still active after cancellation")
                
        except Exception as e:
            self.log_test("Delete membership rebuy", False, f"Test failed: {e}")
    
    def test_negative_quantity(self):
        """Test: Changing quantity to negative should fail."""
        print("\n=== Testing: Changing quantity to negative should fail ===")
        
        try:
            # Get a product
            product = self.product_repo.find_by_sku("BK001")
            if not product:
                self.log_test("Negative quantity", False, "Test product not found")
                return
            
            # Try to set negative quantity
            success = product.set_quantity(-1)
            
            if not success:
                self.log_test("Negative quantity", True, "Correctly rejected negative quantity")
            else:
                self.log_test("Negative quantity", False, "Should have failed but didn't")
                
        except Exception as e:
            self.log_test("Negative quantity", False, f"Test failed: {e}")
    
    def test_negative_price(self):
        """Test: Changing price to negative should fail."""
        print("\n=== Testing: Changing price to negative should fail ===")
        
        try:
            # Get a product
            product = self.product_repo.find_by_sku("BK001")
            if not product:
                self.log_test("Negative price", False, "Test product not found")
                return
            
            # Try to set negative price
            success = product.set_price(-10.0)
            
            if not success:
                self.log_test("Negative price", True, "Correctly rejected negative price")
            else:
                self.log_test("Negative price", False, "Should have failed but didn't")
                
        except Exception as e:
            self.log_test("Negative price", False, f"Test failed: {e}")
    
    def test_price_3_decimals(self):
        """Test: Editing price to 3 decimals (edge case)."""
        print("\n=== Testing: Editing price to 3 decimals (edge case) ===")
        
        try:
            # Get a product
            product = self.product_repo.find_by_sku("BK001")
            if not product:
                self.log_test("Price 3 decimals", False, "Test product not found")
                return
            
            # Set price with 3 decimal places
            price_3_decimals = 59.999
            success = product.set_price(price_3_decimals)
            
            if success:
                # Check if the price is properly rounded/stored
                stored_price = product.get_price()
                if stored_price == 59.999 or stored_price == 60.0:  # Either exact or rounded
                    self.log_test("Price 3 decimals", True, f"Price set to {stored_price} (handled appropriately)")
                else:
                    self.log_test("Price 3 decimals", False, f"Price not handled correctly: {stored_price}")
            else:
                self.log_test("Price 3 decimals", False, "Failed to set 3-decimal price")
                
        except Exception as e:
            self.log_test("Price 3 decimals", False, f"Test failed: {e}")
    
    def test_inventory_update(self):
        """Test: Inventory update after purchase."""
        print("\n=== Testing: Inventory update after purchase ===")
        
        try:
            # Get a product and record initial stock
            product = self.product_repo.find_by_sku("ST001")
            if not product:
                self.log_test("Inventory update", False, "Test product not found")
                return
            
            initial_stock = product.get_quantity()
            order_quantity = 2
            
            # Create a customer with sufficient funds
            customer = self.user_repo.find_by_email("student@student.monash.edu")
            if not customer:
                self.log_test("Inventory update", False, "Test customer not found")
                return
            
            # Create cart and add item
            cart = ShoppingCart()
            success, msg = cart.add_item(product, order_quantity)
            if not success:
                self.log_test("Inventory update", False, f"Failed to add item to cart: {msg}")
                return
            
            # Create and place order
            order_builder = OrderBuilder(customer)
            order_builder.set_delivery("Test Address")
            order_builder.add_items_from_cart(cart.get_items())
            
            order = order_builder.build()
            order_manager = OrderManager(self.order_repo, self.product_repo, self.user_repo)
            success, message = order_manager.place_order(order)
            
            if success:
                # Check if inventory was updated
                updated_product = self.product_repo.find_by_sku("ST001")
                new_stock = updated_product.get_quantity()
                expected_stock = initial_stock - order_quantity
                
                if new_stock == expected_stock:
                    self.log_test("Inventory update", True, f"Stock correctly updated from {initial_stock} to {new_stock}")
                else:
                    self.log_test("Inventory update", False, f"Stock not updated correctly: {initial_stock} -> {new_stock}, expected {expected_stock}")
            else:
                self.log_test("Inventory update", False, f"Order failed: {message}")
                
        except Exception as e:
            self.log_test("Inventory update", False, f"Test failed: {e}")
    
    def test_cart_add_delete(self):
        """Test: Add items to cart then delete items not present."""
        print("\n=== Testing: Add items to cart then delete items not present ===")
        
        try:
            # Get products
            product1 = self.product_repo.find_by_sku("BK001")
            product2 = self.product_repo.find_by_sku("ST001")
            if not product1 or not product2:
                self.log_test("Cart add delete", False, "Test products not found")
                return
            
            cart = ShoppingCart()
            
            # Add items to cart
            success1, msg1 = cart.add_item(product1, 2)
            success2, msg2 = cart.add_item(product2, 1)
            
            if not success1 or not success2:
                self.log_test("Cart add delete", False, f"Failed to add items: {msg1}, {msg2}")
                return
            
            # Try to delete item not in cart
            success, msg = cart.remove_item("NONEXISTENT")
            
            if not success and "not found" in msg.lower():
                self.log_test("Cart add delete", True, "Correctly handled deletion of non-existent item")
            else:
                self.log_test("Cart add delete", False, f"Should have failed but didn't: {msg}")
                
        except Exception as e:
            self.log_test("Cart add delete", False, f"Test failed: {e}")
    
    def test_manual_insufficient_funds(self):
        """Test: Manually change funds to insufficient then checkout."""
        print("\n=== Testing: Manually change funds to insufficient then checkout ===")
        
        try:
            # Get a customer
            customer = self.user_repo.find_by_email("student@student.monash.edu")
            if not customer:
                self.log_test("Manual insufficient funds", False, "Test customer not found")
                return
            
            # Get a product
            product = self.product_repo.find_by_sku("EL003")  # Expensive item
            if not product:
                self.log_test("Manual insufficient funds", False, "Test product not found")
                return
            
            # Manually reduce customer funds to insufficient amount
            original_funds = customer.get_funds()
            customer._funds = 10.0  # Set to very low amount
            
            # Create cart and add expensive item
            cart = ShoppingCart()
            success, msg = cart.add_item(product, 1)
            if not success:
                self.log_test("Manual insufficient funds", False, f"Failed to add item to cart: {msg}")
                return
            
            # Try to checkout
            order_builder = OrderBuilder(customer)
            order_builder.set_delivery("Test Address")
            order_builder.add_items_from_cart(cart.get_items())
            
            order = order_builder.build()
            order_manager = OrderManager(self.order_repo, self.product_repo, self.user_repo)
            success, message = order_manager.place_order(order)
            
            if not success and "Insufficient funds" in message:
                self.log_test("Manual insufficient funds", True, "Correctly rejected checkout with insufficient funds")
            else:
                self.log_test("Manual insufficient funds", False, f"Should have failed but didn't: {message}")
            
            # Restore original funds
            customer._funds = original_funds
                
        except Exception as e:
            self.log_test("Manual insufficient funds", False, f"Test failed: {e}")
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("=" * 60)
        print("MMOSS SYSTEM TEST SCENARIOS")
        print("=" * 60)
        
        # Run all tests
        self.test_order_quantity_over_10()
        self.test_insufficient_funds()
        self.test_change_product_category()
        self.test_incomplete_product_fields()
        self.test_invalid_password_login()
        self.test_order_more_than_stock()
        self.test_delete_membership_rebuy()
        self.test_negative_quantity()
        self.test_negative_price()
        self.test_price_3_decimals()
        self.test_inventory_update()
        self.test_cart_add_delete()
        self.test_manual_insufficient_funds()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✓" if result["passed"] else "✗"
            print(f"{status} {result['test']}: {result['message']}")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()
