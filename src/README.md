# MMOSS - Monash Merchant Online Supermarket System

## 📋 Table of Contents
- [Overview](#overview)
- [Installation Guidelines](#installation-guidelines)
- [System Requirements](#system-requirements)
- [Quick Start Guide](#quick-start-guide)
- [User Guide](#user-guide)
- [Troubleshooting](#troubleshooting)
- [Technical Documentation](#technical-documentation)
- [Support](#support)

## 🏪 Overview

MMOSS (Monash Merchant Online Supermarket System) is a comprehensive e-commerce platform built with Python using Object-Oriented Programming principles. The system provides a complete shopping experience with user authentication, product browsing, shopping cart management, order processing, and administrative functions.

### Key Features
- **User Management**: Student, Staff, and Admin accounts
- **Product Catalog**: Browse and search products with filtering
- **Shopping Cart**: Add, remove, and manage items
- **Order Processing**: Delivery and pickup options
- **Promotion System**: Discount codes and student benefits
- **VIP Membership**: Premium customer features
- **Admin Panel**: Product and inventory management
- **Data Persistence**: CSV-based data storage

## 🛠️ Installation Guidelines

### System Requirements

**Minimum Requirements:**
- Python 3.13.x or higher
- 50MB free disk space
- Terminal/Command Prompt access
- Text editor or IDE (recommended: VS Code, PyCharm)

**Recommended:**
- Python 3.13+
- 100MB free disk space
- Modern IDE with Python support
- Git (for version control)

### Step 1: Download and Extract Project

1. **Download the project files** to your local machine
2. **Extract the files** to a folder (e.g., `MMOSS/`)
3. **Navigate to the project directory** in your terminal/command prompt

```bash
cd /path/to/MMOSS
```

### Step 2: Verify Python Installation

**Check Python version:**
```bash
python --version
# or
python3 --version
```

**Expected output:**
```
Python 3.13.x or higher
```

**If Python is not installed:**
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: Use package manager: `sudo apt install python3`

### Step 3: Run the Application

**Method 1: Direct Execution**
```bash
python main.py
# or
python3 main.py
```

**Method 2: Using IDE**
1. Open your preferred IDE (VS Code, PyCharm, etc.)
2. Open the project folder
3. Run `main.py` directly from the IDE

### Step 4: Verify Installation

When the application starts successfully, you should see:

```
========================================================================
                              MMOSS LOGIN                               
========================================================================
1) Login
0) Exit

> 
```

## 🚀 Quick Start Guide

### First Time Setup

1. **Start the application** using the installation steps above
2. **Choose option 1** to login
3. **Use the default test accounts:**

| Account Type | Email | Password | Role |
|--------------|-------|----------|------|
| Student | student@student.monash.edu | Monash1234! | Customer |
| Staff | staff@monash.edu | Monash1234! | Customer |
| Admin | admin@monash.edu | Admin1234! | Administrator |

### Basic Usage Flow

1. **Login** with any of the test accounts
2. **Browse Products** (Option 1) to see available items
3. **Add Items to Cart** by entering product SKUs
4. **View Cart** (Option 2) to manage your items
5. **Checkout** to place an order
6. **Logout** (Option 9) when finished

## 👥 User Guide

### For Customers

#### Shopping Process
1. **Browse Products**: View all available items with prices and stock
2. **Filter Products**: Search by category, brand, or price range
3. **Add to Cart**: Enter product SKU and quantity
4. **Manage Cart**: Update quantities, remove items, or clear cart
5. **Checkout**: Choose delivery or pickup, apply promotions
6. **Complete Order**: Review and confirm your purchase

#### VIP Membership
- **Purchase VIP**: $20/year for member pricing on all products
- **Benefits**: Discounted prices, priority access
- **Management**: View status, renew, or cancel membership

#### Student Benefits
- **Free Delivery**: No delivery fees for Monash students
- **Pickup Discount**: 5% off pickup orders
- **Promotion Codes**: Access to student-specific discounts

### For Administrators

#### Product Management
1. **Login** as admin (admin@monash.edu)
2. **Access Admin Panel** (Option 4)
3. **Manage Products**: Add, edit, delete, or view products
4. **Inventory Control**: Update stock levels and product information

#### Available Operations
- **List Products**: View all products with details
- **Add Product**: Create new products with full specifications
- **Edit Product**: Modify existing product information
- **Delete Product**: Remove products from the system

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "python: command not found" or "python3: command not found"

**Problem**: Python is not installed or not in PATH

**Solutions**:
1. **Install Python** from [python.org](https://python.org)
2. **Add Python to PATH** during installation
3. **Restart terminal/command prompt** after installation
4. **Verify installation**: `python --version`

#### Issue 2: "ModuleNotFoundError" or Import Errors

**Problem**: Missing Python modules or incorrect file structure

**Solutions**:
1. **Check file structure** - ensure all `.py` files are in the same directory
2. **Verify Python version** - use Python 3.8 or higher
3. **Check file permissions** - ensure files are readable
4. **Run from correct directory** - navigate to project folder first

#### Issue 3: "Permission denied" or File Access Errors

**Problem**: Insufficient permissions to read/write files

**Solutions**:
1. **Run as administrator** (Windows) or with `sudo` (Linux/Mac)
2. **Check file permissions**: `chmod +x main.py`
3. **Move project to user directory** (avoid system directories)
4. **Ensure write permissions** for CSV files

#### Issue 4: CSV Files Not Created

**Problem**: Data files not being generated

**Solutions**:
1. **Check directory permissions** - ensure write access
2. **Verify Python execution** - run from project directory
3. **Check disk space** - ensure sufficient storage
4. **Review error messages** - look for specific error details

#### Issue 5: Login Not Working

**Problem**: Cannot authenticate with default accounts

**Solutions**:
1. **Verify account credentials** - use exact email/password combinations
2. **Check CSV files** - ensure `users.csv` exists and is readable
3. **Reset data** - delete CSV files to regenerate default accounts
4. **Check file encoding** - ensure UTF-8 encoding

#### Issue 6: Order Placement Fails

**Problem**: Cannot complete checkout process

**Solutions**:
1. **Check cart contents** - ensure items are added to cart
2. **Verify customer funds** - ensure sufficient account balance
3. **Check product stock** - ensure items are in stock
4. **Review error messages** - look for specific failure reasons

### Advanced Troubleshooting

#### Debug Mode
Enable detailed error reporting by modifying `main.py`:

```python
# Add at the top of main.py
import traceback
import sys

# Replace the exception handler with:
except Exception as e:
    print(f"\n\nFatal error: {e}")
    traceback.print_exc()
    sys.exit(1)
```

#### Data Reset
If you need to reset all data:

1. **Delete CSV files**:
   ```bash
   rm *.csv
   ```

2. **Restart application** - files will be regenerated with default data

#### Performance Issues
If the application runs slowly:

1. **Check system resources** - ensure adequate RAM and CPU
2. **Close other applications** - free up system resources
3. **Check file sizes** - large CSV files may cause delays
4. **Restart application** - clear memory and reload data

## 📚 Technical Documentation

### System Architecture

**Design Patterns Used**:
- **Repository Pattern**: Data access abstraction
- **Builder Pattern**: Order construction
- **Strategy Pattern**: Promotion algorithms
- **Factory Pattern**: Object creation
- **Facade Pattern**: Simplified interfaces
- **Singleton Pattern**: Repository instances

**File Structure**:
```
MMOSS/
├── main.py              # Application entry point
├── cart.py              # Shopping cart classes
├── checkout.py          # Checkout process
├── data.py              # Data initialization
├── inventory.py          # Product browsing
├── order.py             # Order management
├── product.py           # Product classes
├── promotion.py         # Promotion system
├── repositories.py      # Data persistence
├── user.py              # User classes
├── user_ui.py           # User interface
├── users.csv            # User data
├── product_data.csv     # Product catalog
├── orders.csv           # Order history
├── stores.csv           # Store locations
└── membership.csv       # VIP membership history
```

### Data Models

**User Types**:
- **Customer**: Shopping users with funds and VIP status
- **Administrator**: System administrators with management access

**Product Types**:
- **Product**: General merchandise
- **FoodProduct**: Food items with expiry dates and allergens

**Order Components**:
- **Order**: Complete order with items, pricing, and delivery
- **CartItem**: Individual items in shopping cart
- **Promotion**: Discount codes and eligibility rules

### Business Rules

**Shopping Constraints**:
- Maximum 20 items per cart
- Maximum 10 units per product
- Stock validation before purchase
- Funds verification for payment

**Pricing Rules**:
- Regular pricing for all customers
- VIP member pricing for premium customers
- Student benefits: free delivery, pickup discounts
- Promotion codes: various discount percentages

**Order Processing**:
- Delivery fee: $20 (waived for students)
- Student pickup discount: 5% (exclusive with promotions)
- VIP member pricing: automatic application
- Promotion validation: eligibility checking

## 🆘 Support

### Getting Help

**Common Resources**:
1. **Check this README** for installation and usage guidance
2. **Review error messages** for specific issue details
3. **Verify system requirements** before reporting issues
4. **Test with default accounts** to isolate problems

**Reporting Issues**:
When reporting problems, include:
- **Operating System** (Windows/macOS/Linux)
- **Python Version** (`python --version`)
- **Error Messages** (complete error text)
- **Steps to Reproduce** (what you did before the error)
- **Expected Behavior** (what should happen)

**System Information**:
```bash
# Get system information
python --version
python -c "import sys; print(sys.platform)"
python -c "import os; print(os.getcwd())"
```

### Contact Information

For technical support or questions about the MMOSS system:
- **Project**: Monash Merchant Online Supermarket System
- **Version**: 1.0.0
- **Language**: Python 3.13.x
- **Architecture**: Object-Oriented Programming

---

## 📄 License

This project is developed for educational purposes as part of the Monash University software engineering curriculum.

---

**🎉 Thank you for using MMOSS - Your complete e-commerce solution!**










# MMOSS Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Application
```bash
# Navigate to project directory
cd /path/to/MMOSS

# Run the application
python main.py
```

**Expected Output:**
```
========================================================================
                              MMOSS LOGIN                               
========================================================================
1) Login
0) Exit

> 
```

### Step 2: Login with Test Account
```
> 1
Email: student@student.monash.edu
Password: Monash1234!
```

**Expected Output:**
```
Welcome, Stu! Role: CUSTOMER

Press Enter to continue…
```

### Step 3: Explore the System
```
========================================================================
                               MAIN MENU                                
========================================================================
Logged in as: Stu Dent  (CUSTOMER)
Email: student@student.monash.edu
------------------------------------------------------------------------
Tip: Enter 'M' anytime in menus to return here.
------------------------------------------------------------------------
Funds: $1020.00
------------------------------------------------------------------------
1) Browse & Shop
2) View Cart / Checkout
3) Profile & Membership
9) Logout

> 
```

## 🛍️ Quick Shopping Demo

### Browse Products
```
> 1
========================================================================
                            BROWSE PRODUCTS                             
========================================================================
1) List All
2) Filter
3) View Cart / Checkout
0) Back   M) Main Menu

> 1
```

**Sample Product List:**
```
SKU      Name                     Brand       Cat/Subcat               $Price     $VIP   Qty
--------------------------------------------------------------------------------------------
FD001    Organic Moringa Powder   NutriThrive Food/Superfoods           19.99    15.99    25
BK001    Intro to Python          O'Reilly    Books/Textbook            59.99    49.99    15
FD003    Black Tea - Darjeeling   NutriThrive Food/Beverages            14.99    11.99    34
```

### Add Items to Cart
```
> 1
Enter product number: 1
Enter quantity: 2
✓ Added 2 × Organic Moringa Powder to cart
```

### View Cart
```
> 3
========================================================================
                               YOUR CART                                
========================================================================
SKU      Name                     Qty    Unit Price    Line Total
----------------------------------------------------------------
FD001    Organic Moringa Powder   2      $19.99        $39.98
----------------------------------------------------------------
Total items: 2/20
Subtotal: $39.98
------------------------------------------------------------------------
1) Checkout
2) Remove an item
3) Update quantity
4) Clear cart
5) View available promotions
0) Back M) Main Menu

> 1
```

### Complete Checkout
```
> 1
Confirm delivery address? (y/n): y
Available Promotion Codes:
- NEWMONASH20: 20% off products subtotal - first-time PICKUP order only
- STAFF5: 5% off products subtotal - available for Monash staff only

Apply a promo code? (y/n): n
```

**Order Summary:**
```
========================================================================
                               ORDER SUMMARY                            
========================================================================
Order ID: ORD-ABC123
Customer: Stu Dent (student@student.monash.edu)
Fulfilment: DELIVERY
Delivery Address: 8 College Walk, Clayton VIC
------------------------------------------------------------------------
Items:
FD001    Organic Moringa Powder   2      $19.99        $39.98
------------------------------------------------------------------------
Subtotal: $39.98
Student Discount: $0.00
Promo Discount: $0.00
Delivery Fee: $0.00 (Free for students)
Total: $39.98
------------------------------------------------------------------------
Confirm checkout? (y/n): y
```

**Success Message:**
```
✓ Order placed successfully!
Order ID: ORD-ABC123
Total: $39.98
```

## 👨‍💼 Admin Quick Demo

### Login as Admin
```
> 1
Email: admin@monash.edu
Password: Admin1234!
```

**Admin Menu:**
```
========================================================================
                               MAIN MENU                                
========================================================================
Logged in as: Ad Min  (ADMIN)
Email: admin@monash.edu
------------------------------------------------------------------------
4) Admin: Product & Inventory
9) Logout

> 4
```

### Manage Products
```
========================================================================
                        ADMIN – PRODUCT & INVENTORY                     
========================================================================
1) List Products
2) Add Product
3) Edit Product
4) Delete Product
0) Back   M) Main Menu

> 1
```

**Product Management:**
```
SKU      Name                     Brand       Category    Price    Stock
-----------------------------------------------------------------------
FD001    Organic Moringa Powder   NutriThrive Food        19.99    25
BK001    Intro to Python          O'Reilly    Books       59.99    15
FD003    Black Tea - Darjeeling   NutriThrive Food        14.99    34
```

## 🎟️ Promotion System Demo

### View Available Promotions
```
> 5
Available Promotion Codes:
- NEWMONASH20: 20% off products subtotal - first-time PICKUP order only
- STAFF5: 5% off products subtotal - available for Monash staff only
```

### Apply Promotion Code
```
Apply a promo code? (y/n): y
Enter promotion code: STAFF5
✓ STAFF5 is valid and applicable
```

**Order with Promotion:**
```
Subtotal: $39.98
Student Discount: $0.00
Promo Discount: $2.00 (5% off)
Delivery Fee: $0.00
Total: $37.98
```

## 💎 VIP Membership Demo

### Access Profile
```
> 3
========================================================================
                            PROFILE & MEMBERSHIP                        
========================================================================
Name: Stu Dent
Email: student@student.monash.edu
Mobile: 0400000001
Address: 8 College Walk, Clayton VIC
Role: CUSTOMER
Monash student: Yes
VIP Status: No VIP membership
Funds: $1020.00
------------------------------------------------------------------------
1) Top up funds
2) Buy/Renew VIP ($20/year)
3) View order history
4) Update Mobile / Address
5) View membership history
6) Cancel VIP (non-refundable)
0) Back   M) Main Menu

> 2
```

### Purchase VIP Membership
```
Enter number of years: 1
✓ VIP membership purchased. Expires: 2025-12-31
```

**VIP Benefits:**
- Member pricing on all products
- Priority customer support
- Exclusive promotions

## 🔧 Troubleshooting Quick Fixes

### Common Issues

**Issue: "python: command not found"**
```bash
# Solution: Use python3
python3 main.py
```

**Issue: "Permission denied"**
```bash
# Solution: Fix permissions
chmod 644 *.csv
chmod +x main.py
```

**Issue: "Invalid credentials"**
```
# Solution: Use exact credentials
Email: student@student.monash.edu
Password: Monash1234!
```

**Issue: "Your cart is empty"**
```
# Solution: Add items first
1) Browse & Shop
1) List All
Enter product number: 1
Enter quantity: 1
```

### System Reset
If you encounter issues:
```bash
# Reset all data
rm *.csv
python main.py
```

## 📊 System Status Check

### Verify Installation
```bash
# Check Python version
python --version

# Check files
ls -la *.py

# Run application
python main.py
```

### Test Basic Functions
1. **Login** with test account
2. **Browse** products
3. **Add** item to cart
4. **View** cart
5. **Checkout** order
6. **Logout**

### Expected Results
- ✅ Login successful
- ✅ Products display (16+ items)
- ✅ Cart operations work
- ✅ Checkout completes
- ✅ Order saved to CSV

---

## 🎉 You're Ready to Use MMOSS!

**Next Steps:**
1. **Explore** all menu options
2. **Test** different user accounts
3. **Try** promotion codes
4. **Purchase** VIP membership
5. **Manage** products as admin

**Happy Shopping! 🛍️**
