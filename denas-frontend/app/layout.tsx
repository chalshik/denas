import "@/styles/globals.css";
import { Metadata } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Denas",
  description: "E-commerce platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
