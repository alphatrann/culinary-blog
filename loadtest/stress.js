// Find the knee: fixed VU steps (one scenario each, so the summary has per-step latency) up to 400 VUs.
// 800 VUs plus a raw --out export exhausted the 2 GB Docker VM (k6 and the API were OOM-killed), so keep it lean.
import { browse, setup as discover, thresholds } from "./lib.js";
import { sleep } from "k6";

const STEPS = (__ENV.STEPS || "100,150,200,300,400").split(",").map(Number); // e.g. -e STEPS=100 for one step
const STEP_SECONDS = 90;

export const options = {
  noCookiesReset: true,
  scenarios: Object.fromEntries(
    STEPS.map((vus, i) => [
      `s${vus}`,
      { executor: "constant-vus", vus, duration: `${STEP_SECONDS}s`, startTime: `${i * (STEP_SECONDS + 5)}s` },
    ]),
  ),
  // Stress is expected to break the SRS thresholds; these always-pass ones exist only to export per-step sub-metrics.
  thresholds: Object.fromEntries(
    STEPS.flatMap((vus) => [
      [`http_req_duration{scenario:s${vus}}`, ["p(95)<1e9"]],
      [`http_req_failed{scenario:s${vus}}`, ["rate<=1"]],
    ]),
  ),
};
export const setup = discover;
export default function (data) {
  browse(data);
  sleep(Math.random() + 0.2);
}
