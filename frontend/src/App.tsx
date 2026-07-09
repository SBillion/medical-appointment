import { CalendarDays, CheckCircle2, Clock3 } from "lucide-react";
import { useMemo, useState } from "react";

import "./App.css";
import { mockSlots, type AppointmentSlot } from "./mockSlots";

function formatDay(value: string) {
  return new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }).format(new Date(value));
}

function groupSlotsByDay(slots: AppointmentSlot[]) {
  return slots.reduce<Record<string, AppointmentSlot[]>>((groups, slot) => {
    const key = slot.startsAt.slice(0, 10);
    groups[key] = groups[key] ?? [];
    groups[key].push(slot);
    return groups;
  }, {});
}

export default function App() {
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null);
  const [confirmedSlot, setConfirmedSlot] = useState<AppointmentSlot | null>(null);

  const slotsByDay = useMemo(() => groupSlotsByDay(mockSlots), []);

  function confirmSelection() {
    if (!selectedSlot) {
      return;
    }

    setConfirmedSlot(selectedSlot);
  }

  return (
    <main className="app-shell">
      <section className="appointment-layout">
        <header className="page-header">
          <div>
            <p className="eyebrow">Medical appointment</p>
            <h1>Choose a time slot</h1>
          </div>
          <div className="header-meta">
            <CalendarDays size={18} aria-hidden="true" />
            UTC schedule
          </div>
        </header>

        <section className="slot-panel" aria-labelledby="available-slots-title">
          <h2 id="available-slots-title">Available slots</h2>
          {Object.entries(slotsByDay).map(([day, slots]) => (
            <div className="day-group" key={day}>
              <div className="day-title">{formatDay(day)}</div>
              <div className="slot-grid">
                {slots.map((slot) => (
                  <button
                    className={
                      selectedSlot?.startsAt === slot.startsAt
                        ? "slot-button selected"
                        : "slot-button"
                    }
                    key={slot.startsAt}
                    onClick={() => setSelectedSlot(slot)}
                    type="button"
                  >
                    <span className="slot-time">{formatTime(slot.startsAt)}</span>
                    <span className="slot-capacity">
                      {slot.availableDoctors} doctor
                      {slot.availableDoctors > 1 ? "s" : ""} available
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </section>

        <aside className="summary-panel" aria-labelledby="summary-title">
          <h2 id="summary-title">Summary</h2>
          {selectedSlot ? (
            <p className="summary-detail">
              <strong>{formatDay(selectedSlot.startsAt)}</strong>
              {formatTime(selectedSlot.startsAt)}
            </p>
          ) : (
            <p className="summary-empty">Select a slot to continue.</p>
          )}

          <button
            className="confirm-button"
            disabled={!selectedSlot}
            onClick={confirmSelection}
            type="button"
          >
            <Clock3 size={18} aria-hidden="true" />
            Confirm appointment
          </button>

          {confirmedSlot && (
            <div className="status-message" role="status">
              <CheckCircle2 size={18} aria-hidden="true" />
              Appointment confirmed for {formatDay(confirmedSlot.startsAt)} at{" "}
              {formatTime(confirmedSlot.startsAt)}.
            </div>
          )}
        </aside>
      </section>
    </main>
  );
}
