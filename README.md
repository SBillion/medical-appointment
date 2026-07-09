# Backend Technical Exercise

## Context

You are given a small local application for booking medical appointments. The
repository contains a minimal backend, a PostgreSQL database with seeded data,
and a React frontend with a pre-built appointment selection screen using static
mock data.

Your task is to implement the backend API needed to power the booking flow, then
connect the frontend to it.

The exercise is intentionally small. We expect this to take around 1.5 to 2
hours.

## Goal

As a user, I want to see available appointment slots and confirm one of them, so
that an appointment is booked.

The booking flow starts on the appointment slot selection screen and ends once
the appointment has been confirmed.

## Provided Setup

The repository provides:

- A local PostgreSQL database with seeded data.
- A minimal Python backend starter.
- A React + TypeScript frontend with an existing appointment selection UI.
- A Docker Compose setup to run the database, backend, and frontend locally.

The starter implementation is only a suggested base. You may change the
structure, add dependencies, or adjust the implementation approach if you think
it improves the solution.

## Running Locally

Start the full local stack with:

```sh
docker compose up --build
```

Once running, the services are available at:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Backend healthcheck: `http://localhost:8000/health`
- PostgreSQL: `localhost:5432`

To reset the database and seeded data:

```sh
docker compose down -v
docker compose up --build
```

Resetting the database reseeds from the current date.

## Functional Requirements

### Available Slots

The application should display available appointment slots.

Doctor availability data is provided in the database. Multiple doctors may be
available at the same time.

Slots shown to the user must be aggregated by start time. For example, if two
doctors are available at `10:00`, the frontend should display a single `10:00`
slot, not one slot per doctor.

### Booking

When the user selects a slot and confirms it, the backend should book one
available doctor for that slot.

The user does not choose a doctor directly. The backend is responsible for
selecting an available doctor for the requested time.

The booking must be persisted in the database.

### Double Booking

The same underlying doctor availability must not be booked twice.

If a slot is no longer available when the user tries to confirm it, the
application should handle this case properly.

### Frontend Integration

The frontend currently uses static mock data.

You should replace the relevant mock behavior with calls to your backend API:

- Fetch available slots from the backend.
- Confirm a selected slot through the backend.
- Reflect the result in the UI.

## Out of Scope

The following topics are intentionally out of scope:

- Authentication.
- Patient account management.

Dates and times provided by the backend/database can be treated as UTC. You may
improve timezone handling if you want, but it is not required.

## API Design

No specific API contract is imposed.

You are expected to design the endpoint or endpoints you need for this flow. We
are interested in how you model the API, the database interactions, and the
error cases.

## Technical Expectations

We are primarily interested in:

- Clear backend design.
- Simple and appropriate data modeling.
- Correct SQL/database behavior.
- A clean API surface.
- Reasonable error handling.
- Code that is easy to read, review, and discuss.

Tests are welcome if you think they are useful, but they are not mandatory for
this exercise.

## Acceptance Criteria

Your solution should satisfy the following criteria:

- The project can be run locally.
- The user can see available appointment slots in the frontend.
- Slots are aggregated by start time.
- Confirming a slot creates a persisted appointment.
- The backend selects an available doctor for the selected slot.
- The same doctor availability cannot be booked twice.
- Functional errors, such as trying to book an unavailable slot, are handled
  cleanly.
- The frontend uses the backend instead of static mock data for the booking
  flow.
- The code remains simple, maintainable, and ready to review.
