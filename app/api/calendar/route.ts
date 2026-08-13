import {
  calendarSnapshot,
  isDateKey,
  shanghaiDateKey,
} from "../../../lib/school-calendar";

const SOURCE_URL =
  "https://edu.sh.gov.cn/xxgk2_zdgz_jcjy_05/20260605/19ca2cb2e10a47fe86047bcc0bfdd0e8.html";

const headers = {
  "Access-Control-Allow-Origin": "*",
  "Cache-Control": "public, max-age=0, s-maxage=21600, stale-while-revalidate=86400",
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
};

export function GET(request: Request) {
  const url = new URL(request.url);
  const requestedDate = url.searchParams.get("date");
  const date = requestedDate ?? shanghaiDateKey();

  if (!isDateKey(date)) {
    return Response.json(
      {
        error: {
          code: "invalid_date",
          message: "date must use YYYY-MM-DD and be a valid calendar date",
        },
      },
      { status: 400, headers },
    );
  }

  return Response.json(
    {
      schemaVersion: 1,
      generatedAt: new Date().toISOString(),
      region: { code: "CN-SH", name: "上海" },
      audience: "primary_and_secondary_schools",
      ...calendarSnapshot(date),
      source: {
        name: "上海市教育委员会",
        document: "上海市中小学2026学年校历",
        url: SOURCE_URL,
        note: "节假日与个别学校安排可能调整，请以学校最新通知为准。",
      },
    },
    { headers },
  );
}

export function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    },
  });
}
