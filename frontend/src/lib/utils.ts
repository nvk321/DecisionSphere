import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines conditional class names with Tailwind class collision resolution.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Formats a monetary number into standard or compact USD representation.
 */
export function formatCurrency(
  value: number | null | undefined,
  options: {
    compact?: boolean;
    showSign?: boolean;
    decimals?: number;
  } = {}
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "$0.00";
  }

  const { compact = false, showSign = false, decimals = 2 } = options;
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  let formatted = "";
  if (compact) {
    if (absValue >= 1_000_000) {
      formatted = `$${(absValue / 1_000_000).toFixed(1)}M`;
    } else if (absValue >= 1_000) {
      formatted = `$${(absValue / 1_000).toFixed(1)}K`;
    } else {
      formatted = `$${absValue.toFixed(decimals)}`;
    }
  } else {
    formatted = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(absValue);
  }

  if (isNegative) {
    return `-${formatted}`;
  }
  if (showSign && value > 0) {
    return `+${formatted}`;
  }
  return formatted;
}

/**
 * Formats a ratio or percentage value into an explicit percentage string.
 */
export function formatPercent(
  value: number | null | undefined,
  options: {
    isRatio?: boolean; // If true, multiplies by 100
    showSign?: boolean;
    decimals?: number;
  } = {}
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "0.0%";
  }

  const { isRatio = false, showSign = false, decimals = 1 } = options;
  const numericVal = isRatio ? value * 100 : value;
  const fixed = numericVal.toFixed(decimals);

  if (showSign && numericVal > 0) {
    return `+${fixed}%`;
  }
  return `${fixed}%`;
}

/**
 * Formats delta shifts with sign and units.
 */
export function formatDelta(
  delta: number | null | undefined,
  unit = "",
  decimals = 1
): string {
  if (delta === null || delta === undefined || isNaN(delta)) {
    return `0.0 ${unit}`.trim();
  }

  const sign = delta > 0 ? "+" : "";
  return `${sign}${delta.toFixed(decimals)} ${unit}`.trim();
}

/**
 * Truncates UUID or hash for display with copy action.
 */
export function truncateId(id: string, len = 8): string {
  if (!id) return "";
  if (id.length <= len * 2) return id;
  return `${id.slice(0, len)}...${id.slice(-len)}`;
}

/**
 * Formats standard ISO timestamp into readable localized date and time.
 */
export function formatDate(isoString: string | Date | null | undefined): string {
  if (!isoString) return "N/A";
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return String(isoString);

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  }).format(date);
}

/**
 * Safe clipboard copy with fallback.
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}
