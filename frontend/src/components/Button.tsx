// src/components/Button.tsx
import React from "react";
import { cn } from "../utils/cn";

export type ButtonVariant = "primary" | "secondary" | "accent";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-[#2563EB] text-white hover:bg-[#1D4ED8] focus-visible:ring-[#2563EB]",
  secondary: "bg-[#1E293B] text-white hover:bg-[#111827] focus-visible:ring-[#1E293B]",
  accent: "bg-[#06B6D4] text-white hover:bg-[#0597A5] focus-visible:ring-[#06B6D4]",
};

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  className,
  children,
  ...rest
}) => {
  return (
    <button
      className={cn(
        "px-6 py-3 rounded-md font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
        variantClasses[variant],
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
};
