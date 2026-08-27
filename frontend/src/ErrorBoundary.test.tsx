import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ErrorBoundary } from "./ErrorBoundary";

function GoodChild(): string {
  return "children rendered";
}

function BadChild(): never {
  throw new Error("Test explosion");
}

describe("ErrorBoundary", () => {
  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>,
    );
    expect(screen.getByText("children rendered")).toBeInTheDocument();
  });

  it("renders fallback when child throws", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>,
    );
    expect(
      screen.getByText("Something went wrong. Please reload the page."),
    ).toBeInTheDocument();
    spy.mockRestore();
  });
});
