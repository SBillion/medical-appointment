export type AppointmentSlot = {
  startsAt: string;
  availableDoctors: number;
};

export type Booking = {
  id: number;
  startsAt: string;
  endsAt: string;
  doctor: { id: number; fullName: string; specialty: string };
};

export class BookingError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "BookingError";
    this.status = status;
    this.detail = detail;
  }
}

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000") + "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new BookingError(response.status, body.detail);
  }

  return response.json() as Promise<T>;
}

export function fetchSlots(signal?: AbortSignal): Promise<AppointmentSlot[]> {
  return request<AppointmentSlot[]>("/slots", { signal });
}

export function bookSlot(startsAt: string): Promise<Booking> {
  return request<Booking>("/bookings", {
    method: "POST",
    body: JSON.stringify({ startsAt }),
  });
}
