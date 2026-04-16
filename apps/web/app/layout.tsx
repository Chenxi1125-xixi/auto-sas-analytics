import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Auto SAS Analytics",
  description: "Automated SAS Analytics Platform MVP"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "Arial, sans-serif",
          background: "#f7f7fb",
          color: "#111"
        }}
      >
        <div
          style={{
            maxWidth: 1000,
            margin: "0 auto",
            padding: "24px"
          }}
        >
          {children}
        </div>
      </body>
    </html>
  );
}
