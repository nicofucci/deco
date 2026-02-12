import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    template: '%s | Deco-Security',
    default: 'Consola Partner',
  },
  description: "Deco-Security Partner Console",
};

import { I18nProvider } from "@/lib/i18n";

// Build ID to identify deployment version
const BUILD_ID = process.env.NEXT_PUBLIC_BUILD_ID || "DEV-BUILD-" + new Date().toISOString();

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <I18nProvider>
          {children}
        </I18nProvider>
        {process.env.NEXT_PUBLIC_SHOW_BUILD_STAMP === "true" && (
          <div className="fixed bottom-0 left-0 p-1 text-[10px] text-slate-800 bg-black/20 pointer-events-none z-50 font-mono">
            Build: {BUILD_ID}
          </div>
        )}
      </body>
    </html>
  );
}
