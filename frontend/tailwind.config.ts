import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        // DecisionSphere Semantic Domain Tokens
        decision: {
          proceed: "hsl(var(--decision-proceed))",
          mitigate: "hsl(var(--decision-mitigate))",
          reject: "hsl(var(--decision-reject))",
        },
        risk: {
          low: "hsl(var(--risk-low))",
          moderate: "hsl(var(--risk-moderate))",
          high: "hsl(var(--risk-high))",
          severe: "hsl(var(--risk-severe))",
        },
        epistemic: {
          observed: "hsl(var(--epistemic-observed))",
          predicted: "hsl(var(--epistemic-predicted))",
          assumed: "hsl(var(--epistemic-assumed))",
          propagated: "hsl(var(--epistemic-propagated))",
          calculated: "hsl(var(--epistemic-calculated))",
          recommended: "hsl(var(--epistemic-recommended))",
        },
        status: {
          healthy: "hsl(var(--status-healthy))",
          degraded: "hsl(var(--status-degraded))",
          error: "hsl(var(--status-error))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
