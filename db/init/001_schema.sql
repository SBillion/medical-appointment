create table if not exists doctors (
  id bigserial primary key,
  full_name text not null,
  specialty text not null,
  created_at timestamp with time zone not null default now()
);

create table if not exists doctor_availabilities (
  id bigserial primary key,
  doctor_id bigint not null references doctors(id) on delete cascade,
  starts_at timestamp with time zone not null,
  ends_at timestamp with time zone not null,
  created_at timestamp with time zone not null default now()
);
