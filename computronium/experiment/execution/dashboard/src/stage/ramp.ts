/** The colour ramp (TODO69 Phase 5).

    A number needs a colour, and the colour has to come from the one
    palette the whole system uses: the ramp's anchors are palette entries,
    and the colours between them are the anchors mixed.
*/

import { PALETTE } from "../palette.js";

function parseHex(hex: string): [number, number, number] {
  const value = hex.replace("#", "");
  return [
    parseInt(value.slice(0, 2), 16),
    parseInt(value.slice(2, 4), 16),
    parseInt(value.slice(4, 6), 16),
  ];
}

function toHex(rgb: [number, number, number]): string {
  return `#${rgb
    .map((channel) =>
      Math.round(Math.max(0, Math.min(255, channel)))
        .toString(16)
        .padStart(2, "0"),
    )
    .join("")}`;
}

function mix(
  a: [number, number, number],
  b: [number, number, number],
  t: number,
): [number, number, number] {
  return [
    a[0] + (b[0] - a[0]) * t,
    a[1] + (b[1] - a[1]) * t,
    a[2] + (b[2] - a[2]) * t,
  ];
}

const LOW = parseHex(PALETTE.ramp_low);
const MID = parseHex(PALETTE.ramp_mid);
const HIGH = parseHex(PALETTE.ramp_high);

/** The colour of a number between zero and one. */
export function rampColor(value: number): string {
  const t = Math.max(0, Math.min(1, value));
  if (t <= 0.5) return toHex(mix(LOW, MID, t * 2));
  return toHex(mix(MID, HIGH, (t - 0.5) * 2));
}
