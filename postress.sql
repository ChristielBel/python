create table Product(
	id SERIAL Primary key,
	name varchar(50),
	ed varchar(20));

create table Client(
	id SERIAl Primary key,
	name varchar(50),
	address varchar(50),
	phone varchar(50));

create table Futura(
	id SERIAL PRIMARY KEY,
	idClient int REFERENCES Client(id),
	Data Date not null, 
	totalSum decimal(10,2) default 0
);

create table FuturaInfo(
	id SERIAL PRIMARY KEY,
	idFutura int REFERENCES Futura(id),
	idProduct int references Product(id),
	quantity int not null,
	price decimal(10,2) not null
);

CREATE OR REPLACE FUNCTION insert_futura_info() returns trigger as
$ad_fi_trigger$
begin
 update futura set totalSum = totalSum+New.quantity * New.price
  where futura.id = new.idFutura;
   return null;
end
$ad_fi_trigger$ language plpgsql;

create or replace function delete_futura_info() returns trigger as
$del_fi_trigger$
begin
 update futura set totalSum = totalSum+Old.quantity * Old.price
  where futura.id = old.idFutura;
   return null;
end
$del_fi_trigger$ language plpgsql;

create trigger ins_futura_info after insert on FuturaInfo
	for each row execute procedure insert_futura_info();

create trigger del_futura_info after delete on FuturaInfo
 for each row execute procedure delete_futura_info();


insert into product (name, ed) values ('товар 1', 'шт');
insert into product (name, ed) values ('товар 2', 'кг');
insert into product (name, ed) values ('товар 3', 'л');

insert into client (name, address, phone) values ('Клиент 1', 'Адрес 1', '+8324959345');
insert into client (name, address, phone) values ('Клиент 2', 'Адрес 2', '+8356469345');
insert into client (name, address, phone) values ('Клиент 3', 'Адрес 3', '+8324955445');

insert into futura (idClient, data) values (1, '2023-10-01');
insert into futura (idClient, data) values (2, '2023-10-08');

insert into futurainfo (idFutura, idProduct, quantity, price) values (1,1,10,100);
insert into futurainfo (idFutura, idProduct, quantity, price) values (1,2,5,200);
insert into futurainfo (idFutura, idProduct, quantity, price) values (2,3,8,150);
