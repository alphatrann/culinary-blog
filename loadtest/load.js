// NFR-PERF-002: >= 100 concurrent users without degradation. Ramp, hold 5 min, ramp down.
import { browse, setup as discover, thresholds } from "./lib.js";
import { sleep } from "k6";
export const options = {
  stages: [{ duration: "1m", target: 100 }, { duration: "5m", target: 100 }, { duration: "30s", target: 0 }],
  noCookiesReset: true, thresholds: thresholds(),
};
export const setup = discover;
export default function (data) {
  browse(data);
  sleep(Math.random() * 2 + 0.5); // think time
}
