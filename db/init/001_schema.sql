create table doctors (
  id bigserial primary key,
  full_name text not null,
  specialty text not null,
  created_at timestamp with time zone not null default now()
);

create table doctor_availabilities (
  id bigserial primary key,
  doctor_id bigint not null references doctors(id) on delete cascade,
  starts_at timestamp with time zone not null,
  ends_at timestamp with time zone not null,
  created_at timestamp with time zone not null default now()
);

insert into doctors (full_name, specialty) values
  ('Dr. Amelia Hart', 'General Medicine'),
  ('Dr. Noah Silva', 'General Medicine'),
  ('Dr. Lina Moreau', 'Sleep Medicine'),
  ('Dr. Oscar Bennett', 'Internal Medicine'),
  ('Dr. Maya Chen', 'General Medicine');

with slots as (
  select generated_starts_at
  from generate_series(
    date_trunc('day', now()) - interval '7 days',
    date_trunc('day', now()) + interval '15 days',
    interval '30 minutes'
  ) as generated_starts_at
  where (generated_starts_at::time >= '10:00' and generated_starts_at::time < '14:00')
     or (generated_starts_at::time >= '16:00' and generated_starts_at::time < '19:00')
)
insert into doctor_availabilities (doctor_id, starts_at, ends_at)
select
  doctor.id,
  slot.generated_starts_at,
  slot.generated_starts_at + interval '30 minutes'
from slots as slot
cross join doctors as doctor
where random() < 0.5;
