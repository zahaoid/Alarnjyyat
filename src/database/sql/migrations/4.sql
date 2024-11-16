alter table contexts alter column trcontext type varchar(128);
alter table contexts alter column arcontext type varchar(128);
alter table entries add column elaboration varchar(4096) null;
