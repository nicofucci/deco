import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    template: '%s | Deco-Security',
    default: 'Consola Master',
  },
  description: "Deco-Security Master Grid Console",
};

import { I18nProvider } from "@/lib/i18n";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-slate-950 text-slate-200`}>
        <I18nProvider>
          {children}
        </I18nProvider>
      </body>
    </html>
  );
}
