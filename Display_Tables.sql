select * from Client;
select * from Product;
select * from Product_Release;
select * from Cluster;
select * from Component_Type;
select * from Component;
select * from CPRC;
select * from Task_Definition;

select * from CPRC, Cluster where Cluster.cluster_id = CPRC.cluster_id AND Cluster.cluster_id=2 ;

select CPRC.cluster_id from CPRC, Client where Client.name="Aon" AND Client.client_id=CPRC.client_id;

select * from Component where Component.cluster_id=1;


