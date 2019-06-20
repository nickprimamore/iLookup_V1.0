use iLookup;

insert into Client(name) values ('Aon');
insert into Client(name) values ('Marsh');
insert into Client(name) values ('Willis');

insert into Product(name) values ('iForms');
insert into Product(name) values ('iConductor');
insert into Product(name) values ('iVerify');

insert into Product_Release(product_id, release_number) values (1, '1.1.1.1');
insert into Product_Release(product_id, release_number) values (2, '1.1.2.2');
insert into Product_Release(product_id, release_number) values (3, '2.1.1.0');

insert into Cluster(name, environment, region) values ('Aon-dev-iForms-cluster', 'dev', 'N. Virginia');
insert into Cluster(name, environment, region) values ('Marsh-Willis-dev-iForms-cluster', 'dev', 'London');
insert into Cluster(name, environment, region) values ('Aon-qa-iForms-cluster', 'qa', 'N. Virginia');

insert into Component_Type(name, product_id) values ('Security', 1);
insert into Component_Type(name, product_id) values ('UI', 3);
insert into Component_Type(name, product_id) values ('Logging', 2);

insert into Component(name, cluster_id, component_type_id) values ('Aon-dev-security-task', 1, 1);
insert into Component(name, cluster_id, component_type_id) values ('Marsh-Willis-dev-ui-task', 2, 2);
insert into Component(name, cluster_id, component_type_id) values ('Aon-qa-logging-task', 3, 3);

insert into CPRC(client_id, product_release_id, cluster_id) values (1,1,1);
insert into CPRC(client_id, product_release_id, cluster_id) values (2,1,2);
insert into CPRC(client_id, product_release_id, cluster_id) values (3,1,2);

insert into Task_Definition(name, image_tag, revision, date, cpu, memory, component_id) values ('Aon-dev-iforms-security-task:13',
'3fc3e6e', 13, '06/06/19','1024', '2048', 1);
insert into Task_Definition(name, image_tag, revision, date, cpu, memory, component_id) values ('Marsh-Willis-dev-iforms-ui-task:14',
'2fd5n2p', 14, '06/14/19','1024', '2048', 2);