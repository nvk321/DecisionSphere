import { describe, it, expect } from "vitest";
import {
  formatCurrency,
  formatPercent,
  formatDelta,
  truncateId,
  cn,
} from "@/lib/utils";

describe("Frontend Formatters & Utilities", () => {
  describe("formatCurrency", () => {
    it("formats standard positive currency", () => {
      expect(formatCurrency(120400)).toBe("$120,400.00");
    });

    it("formats negative currency with minus sign", () => {
      expect(formatCurrency(-504500)).toBe("-$504,500.00");
    });

    it("formats compact positive currency", () => {
      expect(formatCurrency(120400, { compact: true })).toBe("$120.4K");
      expect(formatCurrency(1500000, { compact: true })).toBe("$1.5M");
    });

    it("formats compact negative currency with explicit minus sign", () => {
      expect(formatCurrency(-504500, { compact: true })).toBe("-$504.5K");
    });

    it("formats zero and handles null/undefined gracefully", () => {
      expect(formatCurrency(0)).toBe("$0.00");
      expect(formatCurrency(null)).toBe("$0.00");
      expect(formatCurrency(undefined)).toBe("$0.00");
    });

    it("includes explicit plus sign when showSign is true", () => {
      expect(formatCurrency(25000, { showSign: true })).toBe("+$25,000.00");
    });
  });

  describe("formatPercent", () => {
    it("formats standard percentage", () => {
      expect(formatPercent(15.5)).toBe("15.5%");
    });

    it("formats ratio to percentage", () => {
      expect(formatPercent(0.548, { isRatio: true })).toBe("54.8%");
    });

    it("includes plus sign for positive shifts", () => {
      expect(formatPercent(12.0, { showSign: true })).toBe("+12.0%");
    });

    it("handles null gracefully", () => {
      expect(formatPercent(null)).toBe("0.0%");
    });
  });

  describe("formatDelta", () => {
    it("formats positive delta with plus sign and unit", () => {
      expect(formatDelta(500, "Units", 0)).toBe("+500 Units");
    });

    it("formats negative delta with minus sign and unit", () => {
      expect(formatDelta(-3.5, "pp", 1)).toBe("-3.5 pp");
    });

    it("handles zero delta", () => {
      expect(formatDelta(0, "Days", 0)).toBe("0 Days");
    });
  });

  describe("truncateId", () => {
    it("truncates long UUIDs with ellipsis", () => {
      const uuid = "18e29557-529f-4318-8686-ec48eb9788f2";
      expect(truncateId(uuid, 6)).toBe("18e295...9788f2");
    });

    it("returns short string unmodified", () => {
      expect(truncateId("abc")).toBe("abc");
    });
  });

  describe("cn", () => {
    it("merges Tailwind classnames cleanly", () => {
      expect(cn("px-2 py-1", "bg-card", { "text-primary": true, "text-muted": false })).toBe(
        "px-2 py-1 bg-card text-primary"
      );
    });
  });
});
