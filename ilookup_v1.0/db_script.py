from app import db
from app.models import Product, Client, Cluster

iform = Product(product_name="iForm")
iconductor =  Product(product_name="iConductor")
iverify = Product(product_name="iVerify")
iconversion = Product(product_name="iConversion")

db.session.add(iform)
db.session.add(iconductor)
db.session.add(iverify)
db.session.add(iconversion)

db.session.commit()
#Checks for existing records
# exists = db.session.query(Client.client_name).filter_by(client_name="Marsh").scalar() is not None

# if exists:
# 	print("Already Exists")
# else:
# 	aon = Client(client_name="Aon")
# 	marsh = Client(client_name="Marsh")
# 	wills = Client(client_name="Wills")
# 	print("Adding Aon")
# 	db.session.add(aon)
# 	db.session.add(marsh)
# 	db.session.add(wills)

# 	db.session.commit()

print("Completed")
