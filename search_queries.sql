use iLookup;

##see all clients or products
select * from Client;
select * from Product;

## see all products of client
select c.name, p.name
from CPRC 
inner join Client as c on c.client_id = CPRC.client_id 
inner join Product_Release as pr on pr.product_release_id = CPRC.product_release_id 
inner join Product as p on pr.product_id = p.product_id 
order by CPRC.client_id;

##select * from CPRC

## see clients belong to a particular cluster
select c.name, cl.name
from CPRC 
inner join Client as c on c.client_id = CPRC.client_id 
inner join Cluster as cl on cl.cluster_id = CPRC.cluster_id 
order by CPRC.client_id;

##see which revision the security components of AON
select c.name as client_name, cl.name as cluster_name, co.name as Component_name, td.revision
from CPRC 
inner join Client as c on c.client_id = CPRC.client_id 
inner join Cluster as cl on cl.cluster_id = CPRC.cluster_id 
inner join Component as co on co.cluster_id = cl.cluster_id
inner join Task_Definition as td on td.component_id = co.component_id 
inner join Component_Type as ct on ct.component_type_id = co.component_type_id
where c.name="AON" and ct.name = "Security"
order by td.revision;

##see all dev environent clusters for aon in N.virginia 
select c.name as client_name, cl.name as cluster_name
from CPRC 
inner join Client as c on c.client_id = CPRC.client_id 
inner join Cluster as cl on cl.cluster_id = CPRC.cluster_id 
where c.name="AON" and cl.region = 'N. Virginia' and cl.environment = 'dev';

##how much cpu does aon's security task use
select c.name as client_name, p.name as product_name, cl.name as cluster_name, ct.name as component_name, td.name as Task_definition, td.image_tag 
from CPRC 
inner join Client as c on c.client_id = CPRC.client_id 
inner join Product_Release as pr on pr.product_release_id = CPRC.product_release_id 
inner join Product as p on pr.product_id = p.product_id
inner join Cluster as cl on cl.cluster_id = CPRC.cluster_id 
inner join Component as co on co.cluster_id = cl.cluster_id
inner join Task_Definition as td on td.component_id = co.component_id 
inner join Component_Type as ct on ct.component_type_id = co.component_type_id and ct.product_id = p.product_id
where c.name="AON" 


