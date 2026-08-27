import { afterEach, describe, expect, it, vi } from "vitest";

import { BookingError, bookSlot, fetchSlots } from "./api";

const BASE = "http://localhost:8000/api";

function mockResponse(
  body: unknown,
  init: { status?: number; statusText?: string } = {},
): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}

function stubFetch(fn: ReturnType<typeof vi.fn>): void {
  vi.stubGlobal("fetch", fn);
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("fetchSlots", () => {
  it("calls GET /slots and returns parsed JSON", async () => {
    const slots = [{ startsAt: "2026-01-01T10:00:00Z", availableDoctors: 3 }];
    const fn = vi.fn(async () => mockResponse(slots));
    stubFetch(fn);

    const result = await fetchSlots();

    expect(fn).toHaveBeenCalledWith(`${BASE}/slots`, {
      headers: { "Content-Type": "application/json" },
      signal: undefined,
    });
    expect(result).toEqual(slots);
  });

  it("passes an AbortSignal through", async () => {
    const fn = vi.fn(async () => mockResponse([]));
    stubFetch(fn);
    const controller = new AbortController();

    await fetchSlots(controller.signal);

    expect(fn).toHaveBeenCalledWith(
      `${BASE}/slots`,
      expect.objectContaining({ signal: controller.signal }),
    );
  });

  it("throws BookingError on non-200 response", async () => {
    const fn = vi.fn(async () =>
      mockResponse({ detail: "Internal error" }, { status: 500 }),
    );
    stubFetch(fn);

    await expect(fetchSlots()).rejects.toThrow(BookingError);
  });

  it("throws BookingError with status and detail", async () => {
    const fn = vi.fn(async () =>
      mockResponse({ detail: "Slot unavailable" }, { status: 404 }),
    );
    stubFetch(fn);

    try {
      await fetchSlots();
    } catch (e) {
      expect(e).toBeInstanceOf(BookingError);
      expect((e as BookingError).status).toBe(404);
      expect((e as BookingError).detail).toBe("Slot unavailable");
    }
  });

  it("falls back to statusText when body has no detail", async () => {
    const fn = vi.fn(
      async () =>
        new Response("Bad Request", { status: 400, statusText: "Bad Request" }),
    );
    stubFetch(fn);

    try {
      await fetchSlots();
    } catch (e) {
      expect(e).toBeInstanceOf(BookingError);
      expect((e as BookingError).status).toBe(400);
      expect((e as BookingError).detail).toBe("Bad Request");
    }
  });
});

describe("bookSlot", () => {
  it("calls POST /bookings with camelCase body", async () => {
    const booking = {
      id: 1,
      startsAt: "2026-01-01T10:00:00Z",
      endsAt: "2026-01-01T10:30:00Z",
      doctor: { id: 2, fullName: "Dr. Hart", specialty: "General Medicine" },
    };
    const fn = vi.fn(async () => mockResponse(booking));
    stubFetch(fn);

    const result = await bookSlot("2026-01-01T10:00:00Z");

    expect(fn).toHaveBeenCalledWith(`${BASE}/bookings`, {
      method: "POST",
      body: JSON.stringify({ startsAt: "2026-01-01T10:00:00Z" }),
      headers: { "Content-Type": "application/json" },
    });
    expect(result).toEqual(booking);
  });

  it("throws BookingError on 409 conflict", async () => {
    const fn = vi.fn(async () =>
      mockResponse({ detail: "Slot booked" }, { status: 409 }),
    );
    stubFetch(fn);

    await expect(bookSlot("2026-01-01T10:00:00Z")).rejects.toThrow(
      BookingError,
    );
  });
});
