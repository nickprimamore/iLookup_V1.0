from app import db
from datetime import datetime
from app.models import Product, Product_Release, Client
db.create_all()
product = Product(product_name="UNKNOWN")
client = Client(client_name="UNKNOWN")
product_release = Product_Release(product_id=1, release_number="UNKNOWN",inserted_at=datetime.utcnow())
db.session.add(product)
db.session.add(client)
db.session.add(product_release)
db.session.commit()
print("DB Created")