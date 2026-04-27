import type { Metadata } from "next";
import "@swipelearn/ui/globals.css";

export const metadata: Metadata = {
  title: "SwipeLearn — Learn from the best thinkers",
  description:
    "Transform blog posts into TikTok-style swipeable Knowledge Cards. Follow your favorite creators and swipe through their insights.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
