// src/components/Badge.tsx
import React from "react";
import { cn } from "../utils/cn";

export type BadgeVariant = "primary" | "secondary" | "accent" | "success" | "danger";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

const variantClasses: Record<BadgeVariant, string> = {
  primary: "bg-[#2563EB] text-white",
  secondary: "bg-[#1E293B] text-white",
  accent: "bg-[#06B6D4] text-white",
  success: "bg-[#10B981] text-white",
  danger: "bg-[#EF4444] text-white",
};

export const Badge: React.FC<BadgeProps> = ({
  variant = "primary",
  className,
  children,
  ...rest
}) => {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variantClasses[variant],
        className
      )}
      {...rest}
    >
      {children}
    </span>
  );
};
