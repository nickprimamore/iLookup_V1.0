from app import db


class Client(db.Model):
    __tablename__ = 'client'
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean,default=True)

    def __repr__(self):
        return '<Client {}>'.format(self.client_name)

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = {'sqlite_autoincrement': True}
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean,default=True)

    def __repr__(self):
        return '<Product {}>'.format(self.product_name)

class Product_Release(db.Model):
    __tablename__ = 'product_release'
    product_release_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    release_number = db.Column(db.String(100))
    product = db.relationship('Product', backref='product_releases')
    inserted_at = db.Column(db.String(100))


    def __repr__(self):
        return '<Product_Release {}>'.format(self.release_number, self.product_id)

class Cluster(db.Model):
    __tablename__ = 'cluster'
    cluster_id = db.Column(db.Integer, primary_key=True)
    cluster_name = db.Column(db.String(100))
    environment = db.Column(db.String(100))
    region = db.Column(db.String(100))
    is_active = db.Column(db.Boolean,default = True)


    def __repr__(self):
        return '<Cluster {}>'.format(self.cluster_name, self.environment, self.region)


class Component(db.Model):
    __tablename__ = 'component'
    component_id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(100))
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))
    is_active = db.Column(db.Boolean,default = True)
    cluster = db.relationship('Cluster', backref='component_cluster')


    def __repr__(self):
        return '<Component {}>'.format(self.component_name, self.cluster_id, self.component_type_id)

class Task_Definition(db.Model):
    __tablename__ = 'task_definition'
    task_definition_id = db.Column(db.Integer, primary_key=True)
    task_definition_name = db.Column(db.String(100))
    image_tag = db.Column(db.String(100))
    revision = db.Column(db.Integer)
    date = db.Column(db.String(100))
    cpu = db.Column(db.String(100))
    memory = db.Column(db.String(100))
    release_number = db.Column(db.String(100))
    inserted_at = db.Column(db.String(100))
    is_active = db.Column(db.Boolean,default=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'))
    component = db.relationship('Component', backref='task_definitions')


    def __repr__(self):
        return '<Task_Definition {}>'.format(self.task_definition_name, self.image_tag, self.revision, self.date, self.cpu, self.memory, self.component_id)

class CPRC(db.Model):
    __tablename__ = 'cprc'
    cprc_id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))
    product_release_id = db.Column(db.Integer, db.ForeignKey('product_release.product_release_id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))
    #is_active = db.Column(db.Boolean,default=True)
    cluster = db.relationship('Cluster', backref='clusters')
    product_release = db.relationship('Product_Release', backref='product_releases')
    client = db.relationship('Client', backref='clients')


    def __repr__(self):
        return '<CPRC {}>'.format(self.cluster_id, self.product_release_id, self.cluster_id)