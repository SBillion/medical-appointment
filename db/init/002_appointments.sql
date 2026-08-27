create table if not exists appointments (
  id bigserial primary key,
  doctor_availability_id bigint not null
    references doctor_availabilities(id) on delete cascade,
  created_at timestamp with time zone not null default now()
);

-- A doctor availability can be booked at most once. This is the
-- database-level guarantee that prevents double booking even under
-- concurrent requests.
create unique index if not exists uq_appointment_availability
  on appointments (doctor_availability_id);