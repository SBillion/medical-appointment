import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const BASE = "http://localhost:8000/api";

function futureISO(days: number, hour: number, minute = 0): string {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() + days);
  d.setUTCHours(hour, minute, 0, 0);
  return d.toISOString().replace(/\.\d{3}Z$/, "Z");
}

function formatDay(value: string): string {
  return new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

function formatTime(value: string): string {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }).format(new Date(value));
}

const day1 = futureISO(1, 10);
const day1Slot2 = futureISO(1, 10, 30);
const day2 = futureISO(2, 16);
const day1Ends = futureISO(1, 10, 30);

function mockSlotsResponse(slots: unknown[]): Response {
  return new Response(JSON.stringify(slots), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function mockBookingResponse(booking: unknown): Response {
  return new Response(JSON.stringify(booking), {
    status: 201,
    headers: { "Content-Type": "application/json" },
  });
}

function mockErrorResponse(status: number, detail: string): Response {
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function mockFetch(
  slots: unknown[] = [],
  bookingResponse: Response = mockBookingResponse({
    id: 1,
    startsAt: day1,
    endsAt: day1Ends,
    doctor: { id: 1, fullName: "Dr. Hart", specialty: "General Medicine" },
  }),
): void {
  const fn = vi.fn(async (url: string, init?: RequestInit) => {
    if (url === `${BASE}/slots`) return mockSlotsResponse(slots);
    if (url === `${BASE}/bookings` && init?.method === "POST")
      return bookingResponse;
    return new Response("Not found", { status: 404 });
  });
  vi.stubGlobal("fetch", fn);
}

const sampleSlots = [
  { startsAt: day1, availableDoctors: 2 },
  { startsAt: day1Slot2, availableDoctors: 1 },
  { startsAt: day2, availableDoctors: 3 },
];

const sampleBooking = {
  id: 1,
  startsAt: day1,
  endsAt: day1Ends,
  doctor: { id: 1, fullName: "Dr. Hart", specialty: "General Medicine" },
};

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("shows loading state then renders slots grouped by day", async () => {
    mockFetch(sampleSlots);
    render(<App />);

    expect(screen.getByText("Loading slots…")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText("Loading slots…")).not.toBeInTheDocument();
    });

    expect(screen.getByText(formatDay(day1))).toBeInTheDocument();
    expect(screen.getByText(formatDay(day2))).toBeInTheDocument();
  });

  it("displays doctor count per slot", async () => {
    mockFetch(sampleSlots);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("2 doctors available")).toBeInTheDocument();
      expect(screen.getByText("1 doctor available")).toBeInTheDocument();
      expect(screen.getByText("3 doctors available")).toBeInTheDocument();
    });
  });

  it("shows empty state when no slots available", async () => {
    mockFetch([]);
    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("No slots available right now."),
      ).toBeInTheDocument();
    });
  });

  it("shows error when fetch fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Network error");
      }),
    );
    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("Failed to load available slots. Please try again."),
      ).toBeInTheDocument();
    });
  });

  it("selects a slot and confirms booking successfully", async () => {
    const user = userEvent.setup();
    mockFetch(sampleSlots);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    expect(screen.getByText("Confirm appointment")).toBeEnabled();

    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(screen.getByText("Appointment confirmed")).toBeInTheDocument();
    });
  });

  it("shows doctor info after booking", async () => {
    const user = userEvent.setup();
    mockFetch(sampleSlots);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(screen.getByText("Dr. Hart")).toBeInTheDocument();
      expect(screen.getByText("General Medicine")).toBeInTheDocument();
    });
  });

  it("shows prominent time in summary card when slot selected", async () => {
    const user = userEvent.setup();
    mockFetch(sampleSlots);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));

    const times = screen.getAllByText(formatTime(day1));
    expect(times.length).toBeGreaterThanOrEqual(2);
    const days = screen.getAllByText(formatDay(day1));
    expect(days.length).toBeGreaterThanOrEqual(2);
  });

  it("shows conflict message on 409 and refreshes slots", async () => {
    const user = userEvent.setup();
    const fn = vi.fn(async (url: string) => {
      if (url === `${BASE}/slots`) return mockSlotsResponse(sampleSlots);
      if (url === `${BASE}/bookings`)
        return mockErrorResponse(409, "Slot booked");
      return new Response("Not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fn);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(
        screen.getByText(
          "That slot was just booked. Please choose another time.",
        ),
      ).toBeInTheDocument();
    });
  });

  it("shows not-found message on 404", async () => {
    const user = userEvent.setup();
    const fn = vi.fn(async (url: string) => {
      if (url === `${BASE}/slots`) return mockSlotsResponse(sampleSlots);
      if (url === `${BASE}/bookings`)
        return mockErrorResponse(404, "Slot not found");
      return new Response("Not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fn);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(
        screen.getByText("That slot is no longer available."),
      ).toBeInTheDocument();
    });
  });

  it("disables confirm button while booking", async () => {
    const user = userEvent.setup();
    let resolveBooking!: (value: Response) => void;
    const bookingPromise = new Promise<Response>((resolve) => {
      resolveBooking = resolve;
    });

    const fn = vi.fn(async (url: string) => {
      if (url === `${BASE}/slots`) return mockSlotsResponse(sampleSlots);
      if (url === `${BASE}/bookings`) return bookingPromise;
      return new Response("Not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fn);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(screen.getByText("Booking…")).toBeDisabled();
    });

    resolveBooking(mockBookingResponse(sampleBooking));

    await waitFor(() => {
      expect(screen.getByText("Confirm appointment")).toBeInTheDocument();
    });
  });

  it("shows generic error on network failure during booking", async () => {
    const user = userEvent.setup();
    const fn = vi.fn(async (url: string) => {
      if (url === `${BASE}/slots`) return mockSlotsResponse(sampleSlots);
      if (url === `${BASE}/bookings`) throw new TypeError("Network error");
      return new Response("Not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fn);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(
        screen.getByText("A network error occurred. Please try again."),
      ).toBeInTheDocument();
    });
  });

  it("refresh button reloads slots", async () => {
    const user = userEvent.setup();
    mockFetch(sampleSlots);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByLabelText("Refresh slots"));

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });
  });

  it("shows generic booking error on 500", async () => {
    const user = userEvent.setup();
    const fn = vi.fn(async (url: string) => {
      if (url === `${BASE}/slots`) return mockSlotsResponse(sampleSlots);
      if (url === `${BASE}/bookings`)
        return mockErrorResponse(500, "Internal server error");
      return new Response("Not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fn);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(formatTime(day1))).toBeInTheDocument();
    });

    await user.click(screen.getByText(formatTime(day1)));
    await user.click(screen.getByText("Confirm appointment"));

    await waitFor(() => {
      expect(
        screen.getByText("Failed to book the appointment. Please try again."),
      ).toBeInTheDocument();
    });
  });
});
