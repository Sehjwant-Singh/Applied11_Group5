"""
order.py
--------
Lean, UI-compatible order layer for your checkout flow.

Works with checkout.py:
- from order import OrderBuilder, OrderManager, Order
- OrderBuilder(customer)
    .set_delivery(address) / .set_pickup(store_id)
    .add_items_from_cart(cart_items)
    .apply_promotion(promotion)      # promotion can be None or a strategy-like object
    .build() -> Order
- Order getters used by UI:
    get_order_id(), get_fulfilment(), get_delivery_address(), get_store_id(),
    get_items(), is_vip_order(), get_subtotal(), get_student_discount(),
    get_promo_code(), get_promo_discount(), get_delivery_fee(), get_total()
- OrderManager(order_repo, product_repo, user_repo).place_order(order)
    Handles funds-only payment, stock decrement, and saving the order.

Business rules:
- VIP member prices apply when customer is VIP.
- Delivery fee $20; waived for students.
- Student pickup 5% discount; NOT combinable with any promo (no stacking).
- Promo applies to items subtotal only (never to delivery fee).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple
from uuid import uuid4
from datetime import datetime


# -----------------------------
# Small reflection helpers
# -----------------------------
def _get(obj: Any, *names, default=None):
    """Return first attribute or zero-arg method value matching names."""
    for n in names:
        if hasattr(obj, n):
            attr = getattr(obj, n)
            try:
                # if it's a method with no params
                return attr() if callable(attr) else attr
            except TypeError:
                pass
    return default


def _call(obj: Any, name: str, *args, **kwargs):
    """Call obj.name(*args) if possible; otherwise return None."""
    if hasattr(obj, name):
        fn = getattr(obj, name)
        if callable(fn):
            return fn(*args, **kwargs)
    return None


# -----------------------------
# Cart item view for summary UI
# -----------------------------
class _SummaryItem:
    """
    Wraps your CartItem so checkout summary can call:
      get_sku(), get_name(), get_quantity(),
      get_unit_price(), get_member_price(), get_line_total()
    """
    def __init__(self, cart_item, use_vip: bool):
        self._ci = cart_item
        self._vip = use_vip

    def get_sku(self):
        return _get(self._ci, "get_sku", "sku", default="")

    def get_name(self):
        return _get(self._ci, "get_name", "name", default="")

    def get_quantity(self) -> int:
        return int(_get(self._ci, "get_quantity", "quantity", default=0))

    def get_unit_price(self) -> float:
        # regular price
        return float(_get(self._ci, "get_unit_price", "get_regular_price", "unit_price", default=0.0))

    def get_member_price(self) -> float:
        mp = _get(self._ci, "get_member_price", "member_price", default=None)
        return float(mp if mp is not None else 0.0)

    def get_line_total(self) -> float:
        # Prefer CartItem's own calculator if it exists
        lt = _call(self._ci, "get_line_total", self._vip)
        if lt is None:
            price = self.get_member_price() if (self._vip and self.get_member_price() > 0) else self.get_unit_price()
            lt = round(price * self.get_quantity(), 2)
        return float(lt)


# -----------------------------
# Core Order
# -----------------------------
@dataclass
class _Pricing:
    subtotal: float = 0.0
    student_discount: float = 0.0
    promo_discount: float = 0.0
    delivery_fee: float = 0.0
    total: float = 0.0


class Order:
    DELIVERY_FEE = 20.00

    def __init__(
        self,
        customer: Any,
        cart_items: List[Any],
        fulfilment: str,
        delivery_address: str = "",
        store_id: str = "",
        promotion: Optional[Any] = None,
    ):
        self._id = f"ORD-{uuid4().hex[:8].upper()}"
        self._created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._customer = customer
        self._items = list(cart_items)          # store original CartItems
        self._fulfilment = fulfilment.upper()   # "DELIVERY" | "PICKUP"
        self._delivery_address = delivery_address
        self._store_id = store_id

        self._promotion = promotion
        self._promo_code = _get(promotion, "get_code", "code", default=None)

        self._is_student = bool(_get(customer, "is_student", default=False))
        self._is_vip = bool(_get(customer, "is_vip", default=False))

        self._pricing = _Pricing()
        self._recalculate()

    # ---- pricing rules ----
    def _compute_subtotal(self) -> float:
        subtotal = 0.0
        for ci in self._items:
            subtotal += _SummaryItem(ci, self._is_vip).get_line_total()
        return round(subtotal, 2)

    def _promo_amount(self, subtotal: float) -> float:
        """
        Promotion object should expose either:
          - calculate_discount(subtotal)
          - apply_discount(subtotal) -> returns discount amount
          - get_discount_amount(subtotal)
        We try all gracefully.
        """
        if self._promotion is None:
            return 0.0
        for method in ("calculate_discount", "apply_discount", "get_discount_amount"):
            amt = _call(self._promotion, method, subtotal)
            if isinstance(amt, (int, float)):
                return round(float(amt), 2)
        # fallback: percentage?
        pct = _get(self._promotion, "get_discount_percentage", default=None)
        if pct is not None:
            try:
                return round(subtotal * (float(pct) / 100.0), 2)
            except Exception:
                pass
        return 0.0

    def _recalculate(self):
        # Start with the basic subtotal from all items
        subtotal = self._compute_subtotal()

        # Figure out delivery costs - students get free delivery, everyone else pays $20
        delivery_fee = 0.0
        if self._fulfilment == "DELIVERY":
            delivery_fee = 0.0 if self._is_student else self.DELIVERY_FEE

        # Handle discounts - but remember, student discount and promo codes can't be combined!
        student_discount = 0.0
        promo_discount = 0.0

        # Students get 5% off pickup orders, but only if they're not using a promo code
        if self._fulfilment == "PICKUP" and self._is_student and self._promotion is None:
            student_discount = round(subtotal * 0.05, 2)

        # If there's a promo code, use that instead of the student discount
        # This prevents people from stacking discounts (which would be too generous!)
        if self._promotion is not None:
            promo_discount = self._promo_amount(subtotal)
            # Make sure the discount doesn't go negative or exceed the subtotal
            promo_discount = max(0.0, min(promo_discount, subtotal))
            student_discount = 0.0  # Can't have both discounts

        # Calculate the final total: subtotal minus discounts plus delivery fee
        total = round(subtotal - student_discount - promo_discount + delivery_fee, 2)
        # Just in case something goes wrong, make sure total never goes below zero
        if total < 0:
            total = 0.0

        self._pricing = _Pricing(
            subtotal=subtotal,
            student_discount=student_discount,
            promo_discount=promo_discount,
            delivery_fee=delivery_fee,
            total=total,
        )

    # ---- getters used by checkout UI ----
    def get_order_id(self) -> str:
        return self._id

    def get_created_at(self) -> str:
        return self._created_at

    def get_fulfilment(self) -> str:
        return self._fulfilment

    def get_delivery_address(self) -> str:
        return self._delivery_address

    def get_store_id(self) -> str:
        return self._store_id

    def get_items(self) -> List[_SummaryItem]:
        """Return items adapted for the summary table."""
        return [_SummaryItem(ci, self._is_vip) for ci in self._items]

    def is_vip_order(self) -> bool:
        return self._is_vip

    def get_subtotal(self) -> float:
        return self._pricing.subtotal

    def get_student_discount(self) -> float:
        return self._pricing.student_discount

    def get_promo_code(self) -> Optional[str]:
        return self._promo_code

    def get_promo_discount(self) -> float:
        return self._pricing.promo_discount

    def get_delivery_fee(self) -> float:
        return self._pricing.delivery_fee

    def get_total(self) -> float:
        return self._pricing.total

    # ---- internal helpers for manager/persistence ----
    def _as_record(self) -> dict:
        # Convert the order to a dictionary that matches the CSV headers
        # We need to serialize the items as JSON since CSV can't handle complex objects
        import json
        
        items_json = json.dumps([
            {
                "sku": _get(ci, "get_sku", "sku", default=""),
                "name": _get(ci, "get_name", "name", default=""),
                "qty": _get(ci, "get_quantity", "quantity", default=0),
                "unit_price": _get(ci, "get_unit_price", "get_regular_price", "unit_price", default=0.0),
                "member_price": _get(ci, "get_member_price", "member_price", default=None),
                "line_total": _SummaryItem(ci, self._is_vip).get_line_total(),
            }
            for ci in self._items
        ])
        
        return {
            "order_id": self._id,
            "email": _get(self._customer, "get_email", "email", default=""),
            "datetime": self._created_at,  # Use 'datetime' to match CSV header
            "fulfilment": self._fulfilment,
            "delivery_address": self._delivery_address,
            "store_id": self._store_id,
            "promo_code": self._promo_code,
            "promo_discount": self.get_promo_discount(),
            "student_discount": self.get_student_discount(),
            "delivery_fee": self.get_delivery_fee(),
            "subtotal": self.get_subtotal(),
            "total": self.get_total(),
            "lines_json": items_json  # Store items as JSON string
        }

    def _customer_email(self) -> str:
        return _get(self._customer, "get_email", "email", default="")


# -----------------------------
# Builder expected by checkout
# -----------------------------
class OrderBuilder:
    """
    Minimal builder that matches your checkout.py usage.
    """
    def __init__(self, customer: Any):
        self._customer = customer
        self._cart_items: List[Any] = []
        self._fulfilment: Optional[str] = None
        self._delivery_address: str = ""
        self._store_id: str = ""
        self._promotion: Optional[Any] = None

    def set_delivery(self, address: str) -> "OrderBuilder":
        self._fulfilment = "DELIVERY"
        self._delivery_address = address or ""
        self._store_id = ""
        return self

    def set_pickup(self, store_id: str) -> "OrderBuilder":
        self._fulfilment = "PICKUP"
        self._store_id = (store_id or "").upper()
        self._delivery_address = ""
        return self

    def add_items_from_cart(self, cart_items: List[Any]) -> "OrderBuilder":
        self._cart_items = list(cart_items or [])
        return self

    def apply_promotion(self, promotion: Optional[Any]) -> "OrderBuilder":
        # promotion can be None or a strategy object (validator returns it)
        self._promotion = promotion
        return self

    def build(self) -> Order:
        if not self._cart_items:
            raise ValueError("No items in cart to build order.")
        if self._fulfilment not in ("DELIVERY", "PICKUP"):
            raise ValueError("Fulfilment must be set to DELIVERY or PICKUP before build().")
        return Order(
            customer=self._customer,
            cart_items=self._cart_items,
            fulfilment=self._fulfilment,
            delivery_address=self._delivery_address,
            store_id=self._store_id,
            promotion=self._promotion,
        )


# -----------------------------
# Manager expected by checkout
# -----------------------------
class OrderManager:
    """
    Handles funds-only payment, stock decrement, and saving the order.
    Tries multiple common method names on your repositories to stay flexible.
    """
    def __init__(self, order_repo: Any, product_repo: Any, user_repo: Any):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._user_repo = user_repo

    def place_order(self, order: Order) -> Tuple[bool, str]:
        # 1) Funds-only payment
        customer = _get(order, "_customer", default=None)
        if customer is None:
            return False, "Missing customer on order."

        total = order.get_total()
        funds = float(_get(customer, "get_funds", "funds", default=0.0))
        if funds < total:
            return False, "Insufficient funds. Please top up."

        # Deduct funds (support both user object & repository persistence)
        new_balance = round(funds - total, 2)
        updated = False
        # prefer repo update if available
        for name in ("update_funds", "set_funds_for_email", "save_user_funds"):
            if _call(self._user_repo, name, order._customer_email(), new_balance) is not None:
                updated = True
                break
        if not updated:
            # fall back to mutating the in-memory user object
            if _call(customer, "set_funds", new_balance) is None:
                # last resort: try attribute assignment
                try:
                    customer.funds = new_balance
                    updated = True
                except Exception:
                    pass
            else:
                updated = True

        if not updated:
            return False, "Could not update user funds."

        # 2) Decrement inventory for each item
        for si in order.get_items():
            sku = si.get_sku()
            qty = int(si.get_quantity())
            # try common names
            did = (
                _call(self._product_repo, "decrement_stock", sku, qty) or
                _call(self._product_repo, "reduce_stock", sku, qty) or
                _call(self._product_repo, "update_stock", sku, -qty)
            )
            # if all return None but didn't throw, assume OK

        # 3) Save order record
        record = order._as_record()
        saved = False
        for name in ("save", "insert", "add", "create"):
            if _call(self._order_repo, name, record) is not None:
                saved = True
                break
        if not saved:
            # try generic "write" without return
            try:
                if hasattr(self._order_repo, "write"):
                    self._order_repo.write(record)  # type: ignore
                    saved = True
            except Exception:
                pass

        if not saved:
            return False, "Failed to save order."

        return True, "Order placed successfully."
