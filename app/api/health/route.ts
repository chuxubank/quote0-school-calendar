import { corsOptions, healthApi } from "../../../lib/quote0-api";

export function GET() {
  return healthApi();
}

export const OPTIONS = corsOptions;
