import * as React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    appName: string;
    children: React.ReactNode;
}

export const SharedButton = ({ appName, children, ...props }: ButtonProps) => {
    return (
        <button
            className="group relative px-8 py-3 bg-blue-600 text-white rounded-full font-bold tracking-wide shadow-[0_5px_0_0_rgba(29,78,216,1)] hover:shadow-[0_2px_0_0_rgba(29,78,216,1)] hover:translate-y-[3px] active:translate-y-[5px] active:shadow-none transition-all duration-75 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
            {...props}
        >
            <span className="relative flex items-center justify-center gap-2">
                {children}
            </span>
        </button>
    );
};