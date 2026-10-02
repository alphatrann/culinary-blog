import { browse, login, setup as discover, thresholds } from "./lib.js";
export const options = { vus: 2, duration: "30s", noCookiesReset: true, thresholds: thresholds() };
export const setup = discover;
export default function (data) {
  browse(data);
  if (__ITER % 20 === 0) login(data);
}
