import * as React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { EmptyState } from "@/components/common/EmptyState";
import { CardSkeleton, TableSkeleton, Skeleton } from "@/components/common/LoadingSkeleton";

describe("Common State Components", () => {
  describe("ErrorBanner", () => {
    it("renders error message, code, and correlation ID", () => {
      render(
        <ErrorBanner
          title="Simulation Error"
          message="Simulation execution failed due to an upstream failure"
          code="EXECUTION_FAILED"
          requestId="req-test-99"
        />
      );

      expect(screen.getByText("Simulation Error")).toBeInTheDocument();
      expect(
        screen.getByText("Simulation execution failed due to an upstream failure")
      ).toBeInTheDocument();
      expect(screen.getByText("EXECUTION_FAILED")).toBeInTheDocument();
      expect(screen.getByText(/req-test-99/)).toBeInTheDocument();
    });

    it("triggers retry action when button clicked", () => {
      const retryFn = vi.fn();
      render(
        <ErrorBanner
          message="Network timeout"
          onRetry={retryFn}
        />
      );

      const retryBtn = screen.getByRole("button", { name: /Retry/i });
      fireEvent.click(retryBtn);
      expect(retryFn).toHaveBeenCalledTimes(1);
    });
  });

  describe("EmptyState", () => {
    it("renders empty state title, description and action button", () => {
      const actionFn = vi.fn();
      render(
        <EmptyState
          title="No Scenarios Configured"
          description="Create your first strategic planning scenario to begin."
          actionLabel="Create Scenario"
          onAction={actionFn}
        />
      );

      expect(screen.getByText("No Scenarios Configured")).toBeInTheDocument();
      expect(
        screen.getByText("Create your first strategic planning scenario to begin.")
      ).toBeInTheDocument();
      const btn = screen.getByRole("button", { name: "Create Scenario" });
      fireEvent.click(btn);
      expect(actionFn).toHaveBeenCalledTimes(1);
    });
  });

  describe("Loading Skeletons", () => {
    it("renders CardSkeleton with animate-pulse class", () => {
      const { container } = render(<CardSkeleton className="custom-card-skel" />);
      const pulsedElements = container.querySelectorAll(".animate-pulse");
      expect(pulsedElements.length).toBeGreaterThan(0);
      expect(container.querySelector(".custom-card-skel")).toBeInTheDocument();
    });

    it("renders TableSkeleton with specified rows", () => {
      const { container } = render(<TableSkeleton rows={4} />);
      const rows = container.querySelectorAll(".flex.items-center.gap-4");
      expect(rows.length).toBe(4);
    });
  });
});
