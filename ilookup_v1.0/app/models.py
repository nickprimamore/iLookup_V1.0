from app import db
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'
    client_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    

class Product(Base):
    __tablename__ = 'product'
    product_id = Column(Integer, primary_key=True)
    name = Column(String(100))
 
class Product_Release(Base):
    __tablename__ = 'product_release'
    product_release_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    product_id = Column(Integer, ForeignKey('product.product_id'))
    product = relationship(
        Product,
        backref=backref('product_releases'))
        

class Cluster(Base):
    __tablename__ = 'cluster'
    cluster_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    environment = Column(String(100))
    region = Column(String(100))
 
class Component_Type(Base):
    __tablename__ = 'component_type'
    component_type_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    product_id = Column(Integer, ForeignKey('product.product_id'))
    product = relationship(
        Product,
        backref=backref('component_types'))
        
class Component(Base):
    __tablename__ = 'component'
    component_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    cluster_id = Column(Integer, ForeignKey('cluster.cluster_id'))
    component_type_id = Column(Integer, ForeignKey('component_type.component_type_id'))
    cluster = relationship(
        Cluster,
        backref=backref('component_cluster'))
    component_type = relationship(
        Component_Type,
        backref=backref('components'))
        
        
class Task_Definition(Base):
    __tablename__ = 'task_definition'
    task_definition_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    image_tag = Column(String(100))
    revision = Column(Integer)
    date = Column(String(100))
    cpu = Column(String(100))
    memory = Column(String(100))
    component_type_id = Column(Integer, ForeignKey('component_type.component_type_id'))
    component_type = relationship(
        Component_Type,
        backref=backref('task_definitions'))
        
class CPRC(Base):
    __tablename__ = 'cprc'
    cprc_id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey('cluster.cluster_id'))
    product_release_id = Column(Integer, ForeignKey('product_release.product_release_id'))
    client_id = Column(Integer, ForeignKey('client.client_id'))
    cluster = relationship(
        Cluster,
        backref=backref('clusters'))
    product_release = relationship(
        Product_Release,
        backref=backref('product_releases'))
    client = relationship(
        Client,
        backref=backref('clients'))
    
    
    
    
    
    
 

        