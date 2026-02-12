import React from "react";

type Props = React.HTMLAttributes<HTMLSpanElement>;

export const Badge: React.FC<Props> = ({ className = "", children, ...rest }) => (
  <span
    className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${className}`}
    {...rest}
  >
    {children}
  </span>
);

export default Badge;
