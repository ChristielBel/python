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
	idFutura int REFERENCES Product(id),
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
