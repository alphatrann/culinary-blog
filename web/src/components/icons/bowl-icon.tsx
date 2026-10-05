import * as React from "react";

/** Brand mark / image placeholder: a steaming bowl (from the mockups). */
export function BowlIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="24"
      height="24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <path d="M3 12h18a9 9 0 0 1-18 0z" />
      <path d="M9 8c0-1.5 1-1.5 1-3" />
      <path d="M14 8c0-1.5 1-1.5 1-3" />
    </svg>
  );
}
