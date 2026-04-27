import * as React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  appName: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
}

export const SharedButton = ({
  appName,
  children,
  variant = "primary",
  ...props
}: ButtonProps) => {
  const base =
    "relative px-8 py-3 font-bold tracking-wide rounded-full transition-all duration-75 focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variants: Record<string, string> = {
    primary:
      "bg-indigo-600 text-white shadow-[0_5px_0_0_rgba(67,56,202,1)] hover:shadow-[0_2px_0_0_rgba(67,56,202,1)] hover:translate-y-[3px] focus:ring-indigo-400",
    secondary:
      "bg-cyan-500 text-white shadow-[0_5px_0_0_rgba(6,182,212,1)] hover:shadow-[0_2px_0_0_rgba(6,182,212,1)] hover:translate-y-[3px] focus:ring-cyan-400",
    ghost:
      "bg-transparent text-indigo-400 border border-indigo-400 hover:bg-indigo-400/10 focus:ring-indigo-400",
  };

  return (
    <button className={`${base} ${variants[variant]}`} {...props}>
      <span className="relative flex items-center justify-center gap-2">
        {children}
      </span>
    </button>
  );
};
