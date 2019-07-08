from app import db
from app.models import Product, Product_Release, Client
db.create_all()
product = Product(product_name="unknown")
client = Client(client_name="unknown")
product_release = Product_Release(product_id=1, release_number="unknown")
db.session.add(product)
db.session.add(client)
db.session.add(product_release)
db.session.commit()
print("DB Created")