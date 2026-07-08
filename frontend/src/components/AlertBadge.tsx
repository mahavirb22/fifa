/** Severity indicator — color + text + icon (never color alone). */

import type { AlertSeverity } from "../lib/types";
import { formatSeverity } from "../lib/format";

interface Props {
  severity: AlertSeverity;
}

export function AlertBadge({ severity }: Props) {
  return (
    <span className={`severity-badge ${severity}`} aria-label={`Severity: ${severity}`}>
      {formatSeverity(severity)}
    </span>
  );
}
