import * as React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";

describe("EpistemicBadge Component", () => {
  it("renders PREDICTED tier with appropriate accessibility label", () => {
    render(<EpistemicBadge tier="PREDICTED" />);
    const badge = screen.getByText("PREDICTED");
    expect(badge).toBeInTheDocument();
    const container = badge.closest("[aria-label]");
    expect(container).toHaveAttribute(
      "aria-label",
      expect.stringContaining("PREDICTED")
    );
  });

  it("renders CALCULATED tier with accounting styling", () => {
    render(<EpistemicBadge tier="CALCULATED" />);
    expect(screen.getByText("CALCULATED")).toBeInTheDocument();
  });

  it("renders ASSUMED tier for user levers", () => {
    render(<EpistemicBadge tier="ASSUMED" />);
    expect(screen.getByText("ASSUMED")).toBeInTheDocument();
  });

  it("falls back gracefully on unknown tier", () => {
    render(<EpistemicBadge tier="UNKNOWN" />);
    expect(screen.getByText("CALCULATED")).toBeInTheDocument();
  });
});
