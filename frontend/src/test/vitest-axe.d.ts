/** Type declarations for vitest-axe matchers. */

/* eslint-disable @typescript-eslint/no-explicit-any */
import "vitest";

interface AxeMatchers {
  toHaveNoViolations(): any;
}

declare module "vitest" {
  interface Assertion extends AxeMatchers {}
  interface AsymmetricMatchersContaining extends AxeMatchers {}
}
