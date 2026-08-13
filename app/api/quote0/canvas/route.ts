import {
  canvasApi,
  corsOptions,
  DEFAULT_LANDING_URL,
} from "../../../../lib/quote0-api";

const landingUrl = process.env.NEXT_PUBLIC_LANDING_URL ?? DEFAULT_LANDING_URL;

export function GET(request: Request) {
  return canvasApi(request, {
    landingUrl,
    apiBaseUrl: landingUrl,
  });
}

export const OPTIONS = corsOptions;
