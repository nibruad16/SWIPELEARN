import * as React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const SharedCard = ({ children, className = "" }: CardProps) => {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-[#1a1a2e] p-6 shadow-lg ${className}`}
    >
      {children}
    </div>
  );
};
