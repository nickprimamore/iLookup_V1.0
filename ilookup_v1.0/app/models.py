from app import db
 

class Client(db.Model):
    __tablename__ = 'client'
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    
    def __repr__(self):
        return '<Client {}>'.format(self.name)    

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = {'sqlite_autoincrement': True}
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))


    def __repr__(self):
        return '<Product {}>'.format(self.name)
 
class Product_Release(db.Model):
    __tablename__ = 'product_release'
    product_release_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    release = db.Column(db.String(100))
    product = db.relationship('Product', backref='product_releases')


    def __repr__(self):
        return '<Product_Release {}>'.format(self.name, self.product_id)
        

class Cluster(db.Model):
    __tablename__ = 'cluster'
    cluster_id = db.Column(db.Integer, primary_key=True)
    cluster_name = db.Column(db.String(100))
    environment = db.Column(db.String(100))
    region = db.Column(db.String(100))


    def __repr__(self):
        return '<Cluster {}>'.format(self.name, self.environment, self.region)
 
class Component_Type(db.Model):
    __tablename__ = 'component_type'
    component_type_id = db.Column(db.Integer, primary_key=True)
    component_type_name = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    product = db.relationship('Product', backref='product_ref')


    def __repr__(self):
        return '<Component_Type {}>'.format(self.name, self.product_id)
        
class Component(db.Model):
    __tablename__ = 'component'
    component_id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(100))
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))
    component_type_id = db.Column(db.Integer, db.ForeignKey('component_type.component_type_id'))
    cluster = db.relationship('Cluster', backref='component_cluster')
    component_type = db.relationship('Component_Type', backref='components')


    def __repr__(self):
        return '<Component {}>'.format(self.name, self.cluster_id, self.component_type_id)
        
        
class Task_Definition(db.Model):
    __tablename__ = 'task_definition'
    task_definition_id = db.Column(db.Integer, primary_key=True)
    task_definition_name = db.Column(db.String(100))
    image_tag = db.Column(db.String(100))
    revision = db.Column(db.Integer)
    date = db.Column(db.String(100))
    cpu = db.Column(db.String(100))
    memory = db.Column(db.String(100))
    component_type_id = db.Column(db.Integer, db.ForeignKey('component_type.component_type_id'))
    component_type = db.relationship('Component_Type', backref='task_definitions')


    def __repr__(self):
        return '<Task_Definition {}>'.format(self.name, self.image_tag, self.revision, self.date, self.cpu, self.memory, self.component_type_id)
        
class CPRC(db.Model):
    __tablename__ = 'cprc'
    cprc_id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))
    product_release_id = db.Column(db.Integer, db.ForeignKey('product_release.product_release_id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))
    cluster = db.relationship('Cluster', backref='clusters')
    product_release = db.relationship('Product_Release', backref='product_releases')
    client = db.relationship('Client', backref='clients')
    

    def __repr__(self):
        return '<CPRC {}>'.format(self.cluster_id, self.product_release_id, self.cluster_id)
    
    
    
    
    
 

        