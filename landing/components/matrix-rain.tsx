"use client";
import React, { useEffect, useRef } from 'react';

export function MatrixRain() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = window.innerWidth;
        let height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;

        const columns = Math.floor(width / 20);
        const drops = new Array(columns).fill(0).map(() => Math.random() * -100);

        // Matrix characters (Katakana + Latin + Numbers)
        const chars = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッンabcdefghijklmnopqrstuvwxyz1234567890";

        const colors = ["#00ff41", "#008F11", "#08f7fe"]; // Matrix Green, Dark Green, Cyan Accents

        const draw = () => {
            // Fade effect (trail)
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, width, height);

            ctx.font = '15px monospace';

            for (let i = 0; i < drops.length; i++) {
                // Randomize character and color
                const text = chars[Math.floor(Math.random() * chars.length)];
                const color = Math.random() > 0.98 ? "#fff" : colors[Math.floor(Math.random() * colors.length)];

                ctx.fillStyle = color;
                ctx.fillText(text, i * 20, drops[i] * 20);

                // Reset drop to top randomly
                if (drops[i] * 20 > height && Math.random() > 0.975) {
                    drops[i] = 0;
                }

                drops[i]++;
            }
        };

        const interval = setInterval(draw, 33);

        const handleResize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        };

        window.addEventListener('resize', handleResize);

        return () => {
            clearInterval(interval);
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 w-full h-full pointer-events-none z-[-1] opacity-30"
        />
    );
}
