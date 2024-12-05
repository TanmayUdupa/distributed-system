import threading
from django.core.management.base import BaseCommand
from users.models import User
from products.models import Product
from orders.models import Order
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Insert data concurrently into Users, Products, and Orders'

    user_ready = threading.Event()
    product_ready = threading.Event()

    def insert_users(self):
        users_data = [
            {'name': 'Alice', 'email': 'alice@example.com'},
            {'name': 'Bob', 'email': 'bob@example.com'},
            {'name': 'Charlie', 'email': 'charlie@example.com'},
            {'name': 'David', 'email': 'david@example.com'},
            {'name': 'Eve', 'email': 'eve@example.com'},
            {'name': 'Frank', 'email': 'frank@example.com'},
            {'name': 'Grace', 'email': 'grace@example.com'},
            {'name': 'Alice', 'email': 'alice@example.com'},
            {'name': 'Henry', 'email': 'henry@example.com'},
            {'name': None, 'email': 'jane@example.com'},
        ]
        for user in users_data:
            if User.objects.filter(email=user['email']).exists():
                self.stdout.write(self.style.WARNING(f"Skipping user with duplicate email: {user['email']}"))
                continue

            if not user['name'] or not user['email']:
                self.stdout.write(self.style.WARNING(f"Skipping user with missing name or email: {user['email']}"))
                continue

            try:
                User.objects.create(**user)
                self.stdout.write(self.style.SUCCESS(f"Successfully inserted user: {user['name']}"))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error inserting user {user['name']}: {str(e)}"))
        self.user_ready.set()

    def insert_products(self):
        products_data = [
            {'name': 'Laptop', 'price': 1000.00},
            {'name': 'Smartphone', 'price': 700.00},
            {'name': 'Headphones', 'price': 150.00},
            {'name': 'Monitor', 'price': 300.00},
            {'name': 'Keyboard', 'price': 50.00},
            {'name': 'Mouse', 'price': 30.00},
            {'name': 'Laptop', 'price': 1000.00},
            {'name': 'Smartwatch', 'price': 250.00},
            {'name': 'Gaming Chair', 'price': 500.00},
            {'name': 'Earbuds', 'price': -50.00},
        ]
        for product in products_data:
            if product['price'] < 0:
                self.stdout.write(self.style.WARNING(f"Skipping product with invalid price: {product['name']}"))
                continue

            try:
                Product.objects.create(**product)
                self.stdout.write(self.style.SUCCESS(f"Successfully inserted product: {product['name']}"))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error inserting product {product['name']}: {str(e)}"))
        self.product_ready.set()

    def insert_orders(self):
        self.user_ready.wait()
        self.product_ready.wait()
        orders_data = [
            {'user_id': 1, 'product_id': 1, 'quantity': 2},
            {'user_id': 2, 'product_id': 2, 'quantity': 1},
            {'user_id': 3, 'product_id': 3, 'quantity': 5},
            {'user_id': 4, 'product_id': 4, 'quantity': 1},
            {'user_id': 5, 'product_id': 5, 'quantity': 3},
            {'user_id': 6, 'product_id': 6, 'quantity': 4},
            {'user_id': 7, 'product_id': 7, 'quantity': 2},
            {'user_id': 8, 'product_id': 8, 'quantity': 0},
            {'user_id': 9, 'product_id': 1, 'quantity': -1},
            {'user_id': 10, 'product_id': 10, 'quantity': 2},
        ]
        for order in orders_data:
            if not User.objects.filter(id=order['user_id']).exists():
                self.stdout.write(self.style.WARNING(f"Skipping order with invalid user_id: {order['user_id']}"))
                continue
            
            if not Product.objects.filter(id=order['product_id']).exists():
                self.stdout.write(self.style.WARNING(f"Skipping order with invalid product_id: {order['product_id']}"))
                continue

            # Validate quantity
            if order['quantity'] <= 0:
                self.stdout.write(self.style.WARNING(f"Skipping order with invalid quantity: {order['quantity']}"))
                continue

            try:
                Order.objects.create(**order)
                self.stdout.write(self.style.SUCCESS(f"Successfully inserted order {order['user_id']} - {order['product_id']}"))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error inserting order {order['user_id']} - {order['product_id']}: {str(e)}"))

    def handle(self, *args, **options):
        # Create threads for concurrent insertions
        threads = []

        user_thread = threading.Thread(target=self.insert_users)
        product_thread = threading.Thread(target=self.insert_products)
        order_thread = threading.Thread(target=self.insert_orders)

        threads.append(user_thread)
        threads.append(product_thread)
        threads.append(order_thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        self.stdout.write(self.style.SUCCESS('All data inserted successfully!'))
