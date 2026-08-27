import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled frontend error:", error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="app-shell">
          <p role="alert">Something went wrong. Please reload the page.</p>
        </main>
      );
    }
    return this.props.children;
  }
}
