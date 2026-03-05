/**
 * StarRating — interactive 1-5 star rating widget.
 *
 * Usage:
 *   <StarRating value={3} onChange={setRating} />        // editable
 *   <StarRating value={4.2} readonly size="sm" />        // read-only display
 */

import React, { useState } from "react";

interface StarRatingProps {
  /** Current value (1-5, fractional for display). */
  value: number;
  /** Called with the new whole-number rating (1-5). */
  onChange?: (rating: number) => void;
  /** If true, stars are display-only. */
  readonly?: boolean;
  /** Visual size preset. */
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES: Record<string, string> = {
  sm: "w-4 h-4",
  md: "w-5 h-5",
  lg: "w-6 h-6",
};

function StarIcon({ filled, half, className }: { filled: boolean; half?: boolean; className?: string }) {
  if (half) {
    return (
      <svg className={className} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="halfStar">
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="50%" stopColor="#d1d5db" />
          </linearGradient>
        </defs>
        <path
          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.921-.755 1.688-1.54 1.118l-3.37-2.448a1 1 0 00-1.176 0l-3.37 2.448c-.784.57-1.838-.197-1.539-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.384c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.957z"
          fill="url(#halfStar)"
        />
      </svg>
    );
  }
  return (
    <svg className={className} viewBox="0 0 20 20" fill={filled ? "#f59e0b" : "#d1d5db"} xmlns="http://www.w3.org/2000/svg">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.921-.755 1.688-1.54 1.118l-3.37-2.448a1 1 0 00-1.176 0l-3.37 2.448c-.784.57-1.838-.197-1.539-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.384c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.957z" />
    </svg>
  );
}

export function StarRating({ value, onChange, readonly = false, size = "md" }: StarRatingProps) {
  const [hoverValue, setHoverValue] = useState(0);
  const sizeClass = SIZE_CLASSES[size] ?? SIZE_CLASSES.md;

  const displayValue = hoverValue || value;

  return (
    <div className="inline-flex items-center gap-0.5" role="group" aria-label={`Rating: ${value} out of 5`}>
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= Math.floor(displayValue);
        const half = !filled && star === Math.ceil(displayValue) && displayValue % 1 >= 0.25;

        return (
          <button
            key={star}
            type="button"
            disabled={readonly}
            className={`${readonly ? "cursor-default" : "cursor-pointer hover:scale-110"} transition-transform focus:outline-none`}
            onClick={() => onChange?.(star)}
            onMouseEnter={() => !readonly && setHoverValue(star)}
            onMouseLeave={() => !readonly && setHoverValue(0)}
            aria-label={`${star} star${star > 1 ? "s" : ""}`}
          >
            <StarIcon filled={filled} half={half} className={sizeClass} />
          </button>
        );
      })}
    </div>
  );
}
