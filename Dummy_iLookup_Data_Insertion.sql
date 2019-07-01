use testdb;

insert into Client(client_name) values ('Aon');
insert into Client(client_name) values ('Marsh');
insert into Client(client_name) values ('Willis');

insert into Product(product_name) values ('iForms');
insert into Product(product_name) values ('iConductor');
insert into Product(product_name) values ('iVerify');

insert into Product_Release(product_id, release_number) values (1, '1.1.1.1');
insert into Product_Release(product_id, release_number) values (2, '1.1.2.2');
insert into Product_Release(product_id, release_number) values (3, '2.1.1.0');

#run this after populating cluster, product_release and client table
insert into CPRC(client_id, product_release_id, cluster_id) values (1,1,1);
insert into CPRC(client_id, product_release_id, cluster_id) values (2,1,2);
insert into CPRC(client_id, product_release_id, cluster_id) values (3,1,3);
insert into CPRC(client_id, product_release_id, cluster_id) values (1,2,1);
insert into CPRC(client_id, product_release_id, cluster_id) values (2,2,2);
insert into CPRC(client_id, product_release_id, cluster_id) values (3,2,3);
insert into CPRC(client_id, product_release_id, cluster_id) values (1,3,1);
insert into CPRC(client_id, product_release_id, cluster_id) values (2,3,2);
insert into CPRC(client_id, product_release_id, cluster_id) values (3,2,3);
insert into CPRC(client_id, product_release_id, cluster_id) values (1,3,3);
