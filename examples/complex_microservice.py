"""
Complex Microservice Architecture Example
This code demonstrates various architectural patterns and potential issues
for comprehensive code review testing.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import redis
import sqlite3

# ISSUE: Missing proper configuration management
REDIS_URL = "redis://localhost:6379/0"
DATABASE_URL = "sqlite:///app.db"
API_TIMEOUT = 30
MAX_RETRIES = 3


class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Order:
    id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: OrderStatus
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": self.items,
            "total_amount": self.total_amount,
            "status": self.status.value,
            "created_at": self.created_at,
        }


class PaymentGateway(ABC):
    """Abstract payment gateway interface"""

    @abstractmethod
    async def process_payment(self, amount: float, card_token: str) -> bool:
        pass


class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # ISSUE: No connection pooling for HTTP requests

    async def process_payment(self, amount: float, card_token: str) -> bool:
        try:
            # ISSUE: Synchronous HTTP call in async function
            response = requests.post(
                "https://api.stripe.com/v1/charges",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data={
                    "amount": int(amount * 100),  # Convert to cents
                    "currency": "usd",
                    "source": card_token,
                },
                timeout=API_TIMEOUT,
            )
            return response.status_code == 200
        except Exception as e:
            # ISSUE: Generic exception handling
            logging.error(f"Payment processing failed: {e}")
            return False


class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url
        # ISSUE: No connection pooling
        self._connection = None

    def connect(self):
        # ISSUE: Potential race condition with threading
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_url, check_same_thread=False)
        return self._connection

    def save_order(self, order: Order):
        conn = self.connect()
        cursor = conn.cursor()

        # ISSUE: SQL injection potential if order data is not sanitized
        sql = """
        INSERT INTO orders (id, customer_id, items, total_amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        try:
            cursor.execute(
                sql,
                (
                    order.id,
                    order.customer_id,
                    json.dumps(
                        order.items
                    ),  # ISSUE: No validation of JSON serialization
                    order.total_amount,
                    order.status.value,
                    order.created_at,
                ),
            )
            conn.commit()
        except Exception as e:
            # ISSUE: No proper transaction rollback
            logging.error(f"Failed to save order: {e}")
            raise

    def get_order(self, order_id: str) -> Optional[Order]:
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()

        if row:
            return Order(
                id=row[0],
                customer_id=row[1],
                items=json.loads(row[2]),
                total_amount=row[3],
                status=OrderStatus(row[4]),
                created_at=row[5],
            )
        return None


class CacheManager:
    def __init__(self, redis_url: str):
        # ISSUE: No connection error handling
        self.redis_client = redis.from_url(redis_url)

    def set_cache(self, key: str, value: Any, ttl: int = 3600):
        try:
            # ISSUE: No serialization error handling
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            # ISSUE: Cache failures should not break the application
            logging.error(f"Cache set failed: {e}")

    def get_cache(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value.decode("utf-8"))
        except Exception as e:
            logging.error(f"Cache get failed: {e}")
        return None


class OrderService:
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager,
        payment_gateway: PaymentGateway,
    ):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.payment_gateway = payment_gateway
        # ISSUE: No proper resource cleanup mechanisms

    async def create_order(
        self, customer_id: str, items: List[Dict[str, Any]], card_token: str
    ) -> Optional[Order]:
        """Create a new order with payment processing"""

        # ISSUE: No input validation
        total_amount = sum(item["price"] * item["quantity"] for item in items)

        order = Order(
            id=f"order_{int(time.time())}_{customer_id}",  # ISSUE: Weak ID generation
            customer_id=customer_id,
            items=items,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            created_at=time.time(),
        )

        try:
            # ISSUE: No distributed locking for concurrent operations
            self.db_manager.save_order(order)

            # Process payment
            order.status = OrderStatus.PROCESSING
            self.db_manager.save_order(order)

            # ISSUE: No idempotency handling
            payment_success = await self.payment_gateway.process_payment(
                total_amount, card_token
            )

            if payment_success:
                order.status = OrderStatus.COMPLETED
                # ISSUE: Cache invalidation strategy missing
                self.cache_manager.set_cache(f"order:{order.id}", order.to_dict())
            else:
                order.status = OrderStatus.FAILED

            self.db_manager.save_order(order)
            return order

        except Exception as e:
            # ISSUE: No proper error recovery mechanism
            logging.error(f"Order creation failed: {e}")
            order.status = OrderStatus.FAILED
            try:
                self.db_manager.save_order(order)
            except:
                pass  # ISSUE: Silent failure
            return None

    def get_order_with_cache(self, order_id: str) -> Optional[Order]:
        # Try cache first
        cached_order = self.cache_manager.get_cache(f"order:{order_id}")
        if cached_order:
            return Order(**cached_order)

        # Fallback to database
        order = self.db_manager.get_order(order_id)
        if order:
            # ISSUE: Cache stampede potential
            self.cache_manager.set_cache(f"order:{order.id}", order.to_dict())

        return order


class OrderProcessorWorker:
    """Background worker for processing orders"""

    def __init__(self, order_service: OrderService):
        self.order_service = order_service
        self.running = False
        self.thread_pool = ThreadPoolExecutor(
            max_workers=5
        )  # ISSUE: Fixed thread count

    def start(self):
        self.running = True
        # ISSUE: No graceful shutdown mechanism
        threading.Thread(target=self._process_orders, daemon=True).start()

    def stop(self):
        self.running = False
        # ISSUE: No proper thread cleanup

    def _process_orders(self):
        while self.running:
            try:
                # ISSUE: Polling instead of event-driven processing
                # In a real system, this would listen to a message queue
                time.sleep(1)

                # ISSUE: No proper work distribution among threads
                # This is just a placeholder for demonstration

            except Exception as e:
                # ISSUE: Worker threads can die silently
                logging.error(f"Order processing error: {e}")
                time.sleep(5)  # ISSUE: Fixed retry delay


# ISSUE: Global state management
global_metrics = {
    "orders_processed": 0,
    "payments_failed": 0,
    "cache_hits": 0,
    "cache_misses": 0,
}


def update_metrics(metric_name: str, increment: int = 1):
    # ISSUE: Not thread-safe
    global global_metrics
    global_metrics[metric_name] += increment


class MetricsCollector:
    """Collect and expose application metrics"""

    def __init__(self):
        # ISSUE: No proper metrics aggregation strategy
        self.start_time = time.time()

    def get_metrics(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time

        return {
            "uptime_seconds": uptime,
            "orders_processed": global_metrics["orders_processed"],
            "payments_failed": global_metrics["payments_failed"],
            "cache_hit_ratio": self._calculate_cache_hit_ratio(),
            "memory_usage": self._get_memory_usage(),  # ISSUE: May not work on all systems
        }

    def _calculate_cache_hit_ratio(self) -> float:
        total_requests = global_metrics["cache_hits"] + global_metrics["cache_misses"]
        if total_requests == 0:
            return 0.0
        return global_metrics["cache_hits"] / total_requests

    def _get_memory_usage(self) -> Dict[str, Any]:
        # ISSUE: Platform-specific code without error handling
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
        }


# Example usage and testing
if __name__ == "__main__":
    # ISSUE: Configuration should be environment-based
    logging.basicConfig(level=logging.INFO)

    # Initialize components
    db_manager = DatabaseManager(DATABASE_URL)
    cache_manager = CacheManager(REDIS_URL)
    payment_gateway = StripePaymentGateway("sk_test_fake_key")

    order_service = OrderService(db_manager, cache_manager, payment_gateway)
    metrics_collector = MetricsCollector()

    # ISSUE: No proper application lifecycle management
    worker = OrderProcessorWorker(order_service)
    worker.start()

    async def test_order_creation():
        # ISSUE: No proper test isolation
        test_items = [
            {"name": "Widget A", "price": 29.99, "quantity": 2},
            {"name": "Widget B", "price": 15.50, "quantity": 1},
        ]

        order = await order_service.create_order(
            customer_id="cust_123", items=test_items, card_token="tok_visa"
        )

        if order:
            print(f"Order created: {order.id}")
            update_metrics("orders_processed")
        else:
            print("Order creation failed")
            update_metrics("payments_failed")

    # ISSUE: Mixing sync and async code without proper handling
    asyncio.run(test_order_creation())

    # Display metrics
    print("Current metrics:", metrics_collector.get_metrics())

    # ISSUE: No cleanup on exit
    worker.stop()
