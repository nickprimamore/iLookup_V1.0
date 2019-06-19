##creating database iLookup 
CREATE DATABASE iLookup;

##selecting the newly created database
USE iLookup;

##creating client table
CREATE TABLE Client
(
	client_id INT AUTO_INCREMENT, 
    name VARCHAR(50),
    PRIMARY KEY(client_id)
);
    
##creating product table
CREATE TABLE Product
(
	product_id INT AUTO_INCREMENT, 
    name VARCHAR(50),
    PRIMARY KEY(product_id)
);

##creating product_release table
CREATE TABLE Product_Release
(
	product_release_id INT AUTO_INCREMENT, 
    product_id INT, 
    release_number VARCHAR(50),
    PRIMARY KEY(product_release_id),
	FOREIGN KEY(product_id) REFERENCES Product(product_id)
);

##creating cluster table
CREATE TABLE Cluster
(
	cluster_id INT AUTO_INCREMENT, 
    name VARCHAR(50),
    environment VARCHAR(50),
    region VARCHAR(50),
    PRIMARY KEY(cluster_id)
);


##creating component_type table
CREATE TABLE Component_Type
(
	component_type_id INT AUTO_INCREMENT, 
    name VARCHAR(50),
	product_id INT,
    PRIMARY KEY(component_type_id),
	FOREIGN KEY(product_id) REFERENCES Product(product_id)
);

##creating component table
CREATE TABLE Component
(
	component_id INT AUTO_INCREMENT, 
    name VARCHAR(100),
	cluster_id INT,
    component_type_id INT,
    PRIMARY KEY(component_id),
	FOREIGN KEY(cluster_id) REFERENCES Cluster(cluster_id),
    FOREIGN KEY(component_type_id) REFERENCES Component_Type(component_type_id)
);

##creating CPRC table
CREATE TABLE CPRC
(
	cprc_id INT AUTO_INCREMENT, 
	client_id INT,
    product_release_id INT,
    cluster_id INT,
    PRIMARY KEY(cprc_id),
	FOREIGN KEY(cluster_id) REFERENCES Cluster(cluster_id),
    FOREIGN KEY(client_id) REFERENCES Client(client_id),
    FOREIGN KEY(product_release_id) REFERENCES Product_Release(product_release_id)
);

##creating task_definition table
CREATE TABLE Task_Definition
(
	task_definition_id INT AUTO_INCREMENT, 
    name VARCHAR(100),
    image_tag VARCHAR(100),
	revision INT,
    date VARCHAR(50),
    cpu VARCHAR(50),
    memory VARCHAR(50), 
    component_id INT,
    PRIMARY KEY(task_definition_id),
    FOREIGN KEY(component_id) REFERENCES Component(component_id)
);














