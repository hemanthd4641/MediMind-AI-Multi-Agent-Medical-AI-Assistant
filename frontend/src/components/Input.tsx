// src/components/Input.tsx
import React from "react";
import { cn } from "../utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  className,
  ...rest
}) => {
  const base = "block w-full rounded-md border border-[#E2E8F0] bg-white px-3 py-2 text-sm placeholder-gray-400 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]";

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-[#1E293B]">{label}</label>
      )}
      <input className={cn(base, className)} {...rest} />
      {error && <p className="mt-1 text-xs text-[#EF4444]">{error}</p>}
    </div>
  );
};
