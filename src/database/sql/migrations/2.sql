create table contexts (entryid int references entries not null, trcontext varchar(64) not null, arcontext varchar(64) not null);

ALTER TABLE corrections DROP CONSTRAINT corrections_pkey;