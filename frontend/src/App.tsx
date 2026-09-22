import {
  AlertCircle,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Info,
  RefreshCw,
  Stethoscope,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import "./App.css";
import {
  type AppointmentSlot,
  type Booking,
  BookingError,
  bookSlot,
  fetchSlots,
} from "./api";

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

function groupSlotsByDay(
  slots: AppointmentSlot[],
): Record<string, AppointmentSlot[]> {
  return slots.reduce<Record<string, AppointmentSlot[]>>((groups, slot) => {
    const key = slot.startsAt.slice(0, 10);
    groups[key] = groups[key] ?? [];
    groups[key].push(slot);
    return groups;
  }, {});
}

export default function App() {
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(
    null,
  );
  const [confirmedBooking, setConfirmedBooking] = useState<Booking | null>(
    null,
  );
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const successRef = useRef<HTMLDivElement | null>(null);

  const loadSlots = useCallback(async (isRefresh = false) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      setSlots(await fetchSlots(controller.signal));
    } catch {
      if (controller.signal.aborted) return;
      setError("Failed to load available slots. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, []);

  useEffect(() => {
    loadSlots();
    return () => abortRef.current?.abort();
  }, [loadSlots]);

  useEffect(() => {
    if (confirmedBooking && !error && successRef.current) {
      successRef.current.focus();
    }
  }, [confirmedBooking, error]);

  const visibleSlots = useMemo(
    () => slots.filter((s) => new Date(s.startsAt) > new Date()),
    [slots],
  );
  const visibleByDay = useMemo(
    () => groupSlotsByDay(visibleSlots),
    [visibleSlots],
  );

  const confirmSelection = useCallback(async () => {
    if (!selectedSlot || booking) return;

    setBooking(true);
    setError(null);
    try {
      const result = await bookSlot(selectedSlot.startsAt);
      setConfirmedBooking(result);
      setSelectedSlot(null);
      await loadSlots(true);
    } catch (e) {
      if (e instanceof BookingError) {
        if (e.status === 409) {
          setError("That slot was just booked. Please choose another time.");
        } else if (e.status === 404) {
          setError("That slot is no longer available.");
        } else {
          setError("Failed to book the appointment. Please try again.");
        }
        setSelectedSlot(null);
        await loadSlots(true);
      } else {
        setError("A network error occurred. Please try again.");
      }
    } finally {
      setBooking(false);
    }
  }, [selectedSlot, booking, loadSlots]);

  return (
    <main className="app-shell">
      <section className="appointment-layout">
        <header className="page-header">
          <div>
            <p className="eyebrow">Medical appointment</p>
            <h1>Choose a time slot</h1>
          </div>
          <div className="header-actions">
            <button
              className="refresh-button"
              disabled={refreshing || loading}
              onClick={() => loadSlots(true)}
              type="button"
              aria-label="Refresh slots"
            >
              <RefreshCw
                size={16}
                aria-hidden="true"
                className={refreshing ? "spin" : ""}
              />
            </button>
            <div className="header-meta">
              <CalendarDays size={18} aria-hidden="true" />
              UTC schedule
            </div>
          </div>
        </header>

        <section className="slot-panel" aria-labelledby="available-slots-title">
          <h2 id="available-slots-title">Available slots</h2>
          {loading && slots.length === 0 ? (
            <div className="status-message status-info">
              <Info size={18} aria-hidden="true" />
              Loading slots…
            </div>
          ) : !loading && Object.keys(visibleByDay).length === 0 ? (
            <div className="status-message status-info">
              <Info size={18} aria-hidden="true" />
              No slots available right now.
            </div>
          ) : (
            Object.entries(visibleByDay).map(([day, daySlots]) => (
              <div className="day-group" key={day}>
                <div className="day-title">{formatDay(day)}</div>
                {daySlots.length === 0 ? (
                  <p className="day-empty">No availability on this day.</p>
                ) : (
                  <div className="slot-grid">
                    {daySlots.map((slot, index) => {
                      const isSelected =
                        selectedSlot?.startsAt === slot.startsAt;
                      const isLowCapacity = slot.availableDoctors === 1;
                      return (
                        <button
                          className={
                            isSelected
                              ? "slot-button selected"
                              : isLowCapacity
                                ? "slot-button low-capacity"
                                : "slot-button"
                          }
                          key={`${slot.startsAt}-${index}`}
                          onClick={() => setSelectedSlot(slot)}
                          type="button"
                        >
                          <span className="slot-time">
                            {formatTime(slot.startsAt)}
                          </span>
                          <span className="slot-capacity">
                            {slot.availableDoctors} doctor
                            {slot.availableDoctors > 1 ? "s" : ""} available
                          </span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))
          )}
        </section>

        <aside className="summary-panel" aria-labelledby="summary-title">
          <h2 id="summary-title">Summary</h2>
          {selectedSlot ? (
            <div className="summary-card">
              <div className="summary-card-time">
                {formatTime(selectedSlot.startsAt)}
              </div>
              <div className="summary-card-day">
                {formatDay(selectedSlot.startsAt)}
              </div>
            </div>
          ) : confirmedBooking ? null : (
            <p className="summary-empty">Select a slot to continue.</p>
          )}

          <button
            className="confirm-button"
            disabled={!selectedSlot || booking}
            onClick={confirmSelection}
            type="button"
          >
            <Clock3 size={18} aria-hidden="true" />
            {booking ? "Booking…" : "Confirm appointment"}
          </button>

          <div aria-live="polite">
            {error && (
              <div
                className="status-message status-error"
                role="alert"
                tabIndex={-1}
              >
                <AlertCircle size={18} aria-hidden="true" />
                {error}
              </div>
            )}

            {confirmedBooking && !error && (
              <div
                ref={successRef}
                className="booking-confirmation"
                role="status"
                tabIndex={-1}
              >
                <div className="status-message status-success">
                  <CheckCircle2 size={18} aria-hidden="true" />
                  Appointment confirmed
                </div>
                <div className="confirmation-details">
                  <div className="confirmation-row">
                    <Clock3 size={16} aria-hidden="true" />
                    <span>
                      {formatDay(confirmedBooking.startsAt)} at{" "}
                      {formatTime(confirmedBooking.startsAt)}
                    </span>
                  </div>
                  <div className="confirmation-row">
                    <Stethoscope size={16} aria-hidden="true" />
                    <div>
                      <strong>{confirmedBooking.doctor.fullName}</strong>
                      <span className="confirmation-specialty">
                        {confirmedBooking.doctor.specialty}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}
