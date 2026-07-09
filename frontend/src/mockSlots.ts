// Illustrative placeholder data only. Real slots come from the API you will
// build; these dates and counts do not match the seeded database.
export type AppointmentSlot = {
  startsAt: string;
  availableDoctors: number;
};

export const mockSlots: AppointmentSlot[] = [
  {
    startsAt: "2026-08-03T08:00:00Z",
    availableDoctors: 2,
  },
  {
    startsAt: "2026-08-03T08:30:00Z",
    availableDoctors: 1,
  },
  {
    startsAt: "2026-08-03T09:00:00Z",
    availableDoctors: 3,
  },
  {
    startsAt: "2026-08-03T10:00:00Z",
    availableDoctors: 2,
  },
  {
    startsAt: "2026-08-03T10:30:00Z",
    availableDoctors: 1,
  },
  {
    startsAt: "2026-08-04T08:00:00Z",
    availableDoctors: 2,
  },
  {
    startsAt: "2026-08-04T08:30:00Z",
    availableDoctors: 1,
  },
  {
    startsAt: "2026-08-04T09:00:00Z",
    availableDoctors: 2,
  },
  {
    startsAt: "2026-08-04T10:00:00Z",
    availableDoctors: 1,
  },
];
