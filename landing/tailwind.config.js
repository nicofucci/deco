const defaultTheme = require("tailwindcss/defaultTheme");
const colors = require("tailwindcss/colors");
const {
    default: flattenColorPalette,
} = require("tailwindcss/lib/util/flattenColorPalette");

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                background: "#050505", // Deep Black
                foreground: "#06b6d4", // Cyan
                ai: {
                    base: "#050505",
                    card: "#0a0a0a",
                    cyan: "#06b6d4", // Electric Cyan
                    neon: "#10b981", // Bio-Neon Green
                    violet: "#8b5cf6", // AI Core Accent
                    text: "#e5e5e5",
                    dim: "#525252",
                },
                'ai-cyan': '#06b6d4',
                'ai-green': '#10b981',
                'ai-violet': '#8b5cf6',
                // Imported Design Colors
                cyber: {
                    500: '#10b981', // Emerald for positive security
                    900: '#064e3b',
                },
                void: '#050505',
                panel: '#0a0a0a',
            },
            fontFamily: {
                sans: ["var(--font-geist-sans)", ...defaultTheme.fontFamily.sans],
                mono: ["var(--font-geist-mono)", ...defaultTheme.fontFamily.mono], // Only for logs
            },
            backgroundImage: {
                "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
                "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
            },
            animation: {
                "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "float": "float 6s ease-in-out infinite",
                "scan": "scan 4s linear infinite",
                // Imported Animations
                'spin-slow': 'spin 15s linear infinite',
                'spin-reverse-slow': 'spin 20s linear infinite reverse',
                'pulse-glow': 'pulseGlow 4s ease-in-out infinite',
                'shimmer': 'shimmer 2s infinite',
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translateY(0)" },
                    "50%": { transform: "translateY(-20px)" },
                },
                scan: {
                    "0%": { transform: "translateY(-100%)" },
                    "100%": { transform: "translateY(100%)" },
                },
                pulseGlow: {
                    '0%, 100%': { opacity: '0.6', boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)' },
                    '50%': { opacity: '1', boxShadow: '0 0 40px rgba(16, 185, 129, 0.5)' },
                },
                shimmer: {
                    '100%': { transform: 'translateX(100%)' }, // Corrected direction for typical shimmer
                }
            },
        },
    },
    plugins: [addVariablesForColors],
};

// This plugin adds each Tailwind color as a global CSS variable, e.g. var(--gray-200).
function addVariablesForColors({ addBase, theme }) {
    let allColors = flattenColorPalette(theme("colors"));
    let newVars = Object.fromEntries(
        Object.entries(allColors).map(([key, val]) => [`--${key}`, val])
    );

    addBase({
        ":root": newVars,
    });
}
