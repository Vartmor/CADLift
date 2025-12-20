/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./pages/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
        "./services/**/*.{js,ts,jsx,tsx}",
        "./utils/**/*.{js,ts,jsx,tsx}",
        "./hooks/**/*.{js,ts,jsx,tsx}",
        "./contexts/**/*.{js,ts,jsx,tsx}",
        "./config/**/*.{js,ts,jsx,tsx}",
        "./App.tsx",
        "./index.tsx"
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#ecfeff',
                    100: '#cffafe',
                    200: '#a5f3fc',
                    300: '#67e8f9',
                    400: '#22d3ee',
                    500: '#06b6d4',
                    600: '#0891b2',
                    700: '#0e7490',
                    800: '#155e75',
                    900: '#164e63',
                    950: '#083344',
                },
                slate: {
                    850: '#1e293b',
                    900: '#0f172a',
                    950: '#020617',
                }
            },
            animation: {
                blob: "blob 7s infinite",
                "fade-in": "fadeIn 0.5s ease-out forwards",
                "fade-in-up": "fadeInUp 0.7s ease-out forwards",
                "spin-slow": "spin 3s linear infinite",
                "shimmer": "shimmer 2s infinite linear",
                "aurora": "aurora 15s ease-in-out infinite",
                "gradient": "gradient 8s ease infinite",
                "glow": "glow 2s ease-in-out infinite",
                "float-slow": "floatSlow 12s ease-in-out infinite",
                "float-slower": "floatSlow 18s ease-in-out infinite reverse",
                "particle": "particle 20s linear infinite",
                "text-reveal": "textReveal 1s ease-out forwards",
                "border-flow": "borderFlow 3s linear infinite",
                "tilt": "tilt 10s ease-in-out infinite",
                "morph": "morph 8s ease-in-out infinite",
                "scale-pulse": "scalePulse 4s ease-in-out infinite",
            },
            keyframes: {
                blob: {
                    "0%": {
                        transform: "translate(0px, 0px) scale(1)",
                    },
                    "33%": {
                        transform: "translate(30px, -50px) scale(1.1)",
                    },
                    "66%": {
                        transform: "translate(-20px, 20px) scale(0.9)",
                    },
                    "100%": {
                        transform: "translate(0px, 0px) scale(1)",
                    },
                },
                fadeIn: {
                    "0%": { opacity: "0" },
                    "100%": { opacity: "1" },
                },
                fadeInUp: {
                    "0%": { opacity: "0", transform: "translateY(20px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                shimmer: {
                    "0%": { transform: "translateX(-100%)" },
                    "100%": { transform: "translateX(100%)" },
                },
                float: {
                    "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
                    "50%": { transform: "translateY(-20px) rotate(5deg)" },
                },
                aurora: {
                    "0%": { transform: "rotate(0deg) scale(1)", opacity: "0.5" },
                    "25%": { transform: "rotate(90deg) scale(1.2)", opacity: "0.7" },
                    "50%": { transform: "rotate(180deg) scale(1)", opacity: "0.5" },
                    "75%": { transform: "rotate(270deg) scale(1.3)", opacity: "0.6" },
                    "100%": { transform: "rotate(360deg) scale(1)", opacity: "0.5" },
                },
                gradient: {
                    "0%, 100%": { backgroundPosition: "0% 50%" },
                    "50%": { backgroundPosition: "100% 50%" },
                },
                glow: {
                    "0%, 100%": { boxShadow: "0 0 20px rgba(6, 182, 212, 0.4), 0 0 40px rgba(6, 182, 212, 0.2)" },
                    "50%": { boxShadow: "0 0 30px rgba(6, 182, 212, 0.6), 0 0 60px rgba(6, 182, 212, 0.3)" },
                },
                floatSlow: {
                    "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
                    "25%": { transform: "translateY(-15px) rotate(3deg)" },
                    "50%": { transform: "translateY(-30px) rotate(-3deg)" },
                    "75%": { transform: "translateY(-15px) rotate(2deg)" },
                },
                particle: {
                    "0%": { transform: "translateY(100vh) translateX(0)", opacity: "0" },
                    "10%": { opacity: "1" },
                    "90%": { opacity: "1" },
                    "100%": { transform: "translateY(-100vh) translateX(100px)", opacity: "0" },
                },
                textReveal: {
                    "0%": { opacity: "0", transform: "translateY(30px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                borderFlow: {
                    "0%": { backgroundPosition: "0% 50%" },
                    "50%": { backgroundPosition: "100% 50%" },
                    "100%": { backgroundPosition: "0% 50%" },
                },
                tilt: {
                    "0%, 100%": { transform: "perspective(1000px) rotateY(-5deg) rotateX(5deg)" },
                    "50%": { transform: "perspective(1000px) rotateY(5deg) rotateX(-5deg)" },
                },
                morph: {
                    "0%, 100%": { borderRadius: "60% 40% 30% 70% / 60% 30% 70% 40%" },
                    "25%": { borderRadius: "30% 60% 70% 40% / 50% 60% 30% 60%" },
                    "50%": { borderRadius: "50% 60% 30% 60% / 30% 60% 70% 40%" },
                    "75%": { borderRadius: "60% 40% 60% 30% / 70% 30% 50% 60%" },
                },
                scalePulse: {
                    "0%, 100%": { transform: "scale(1)" },
                    "50%": { transform: "scale(1.05)" },
                },
            },
        }
    }
}
