import {
  calendarSnapshot,
  formatShortDate,
  isDateKey,
  shanghaiDateKey,
} from "../../../../lib/school-calendar";

const LANDING_URL = "https://quote0-school-calendar.chuxubank.chatgpt.site";

const headers = {
  "Access-Control-Allow-Origin": "*",
  "Cache-Control": "public, max-age=0, s-maxage=21600, stale-while-revalidate=86400",
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
};

function canvasTemplate() {
  return {
    default: [
      {
        type: "div",
        props: {
          tw: "flex flex-col w-full h-full min-w-0 min-h-0 bg-white text-black gap-[5px]",
          children: [
            {
              type: "div",
              props: {
                tw: "flex flex-row items-center justify-between shrink-0 text-9-chillduansans",
                children: [
                  {
                    type: "span",
                    props: {
                      tw: "font-bold",
                      children: "沪上校历 · {{get inputData \"phase\" default=\"校历\"}}",
                    },
                  },
                  {
                    type: "span",
                    props: { children: "{{get inputData \"date\" default=\"--\"}}" },
                  },
                ],
              },
            },
            {
              type: "div",
              props: { tw: "w-full h-px bg-black shrink-0", children: "" },
            },
            {
              type: "div",
              props: {
                tw: "flex flex-row flex-1 min-h-0 gap-[10px]",
                children: [
                  {
                    type: "div",
                    props: {
                      tw: "flex flex-col flex-[3] min-w-0 justify-center",
                      children: [
                        {
                          type: "span",
                          props: {
                            tw: "text-11-chillduansans font-bold",
                            children: "{{get inputData \"primaryLabel\" default=\"今日\"}}",
                          },
                        },
                        {
                          type: "div",
                          props: {
                            tw: "flex flex-row items-end gap-[4px]",
                            children: [
                              {
                                type: "span",
                                props: {
                                  tw: "text-52-chillduansans font-bold leading-none",
                                  children: "{{get inputData \"primaryValue\" default=\"--\"}}",
                                },
                              },
                              {
                                type: "span",
                                props: {
                                  tw: "text-11-chillduansans font-bold pb-[4px]",
                                  children: "天",
                                },
                              },
                            ],
                          },
                        },
                      ],
                    },
                  },
                  {
                    type: "div",
                    props: { tw: "w-px h-full bg-black shrink-0", children: "" },
                  },
                  {
                    type: "div",
                    props: {
                      tw: "flex flex-col flex-[2] min-w-0 justify-center gap-[5px]",
                      children: [
                        {
                          type: "span",
                          props: {
                            tw: "text-9-chillduansans",
                            children: "{{get inputData \"secondaryLabel\" default=\"进度\"}}",
                          },
                        },
                        {
                          type: "span",
                          props: {
                            tw: "text-20-chillduansans font-bold leading-none",
                            children: "{{get inputData \"secondaryValue\" default=\"--\"}} 天",
                          },
                        },
                        {
                          type: "span",
                          props: {
                            tw: "text-9-chillduansans",
                            children: "{{get inputData \"detail\" default=\"上海中小学\"}}",
                          },
                        },
                        {
                          type: "div",
                          props: {
                            tw: "flex flex-row items-center gap-[4px]",
                            children: [
                              {
                                type: "div",
                                props: { tw: "w-[58px] h-[5px] border border-black", children: "" },
                              },
                              {
                                type: "span",
                                props: {
                                  tw: "text-8-chillduansans font-bold",
                                  children: "{{get inputData \"progress\" default=\"0\"}}%",
                                },
                              },
                            ],
                          },
                        },
                        {
                          type: "span",
                          props: {
                            tw: "text-8-chillduansans",
                            children: "{{get inputData \"nextEvent\" default=\"\"}}",
                          },
                        },
                      ],
                    },
                  },
                ],
              },
            },
            {
              type: "div",
              props: {
                tw: "flex flex-row items-center justify-between shrink-0 text-8-chillduansans",
                children: [
                  { type: "span", props: { children: "上海市教委校历" } },
                  { type: "span", props: { children: "QUOTE / SCHOOL" } },
                ],
              },
            },
          ],
        },
      },
    ],
  };
}

export function GET(request: Request) {
  const url = new URL(request.url);
  const requestedDate = url.searchParams.get("date");
  const date = requestedDate ?? shanghaiDateKey();

  if (!isDateKey(date)) {
    return Response.json(
      { error: { code: "invalid_date", message: "date must use YYYY-MM-DD" } },
      { status: 400, headers },
    );
  }

  const snapshot = calendarSnapshot(date);
  const detail = snapshot.display.teachingWeek
    ? `第 ${snapshot.display.teachingWeek} 周 · 学期进度`
    : `${snapshot.phase.name}进度`;
  const nextEvent = snapshot.nextEvent
    ? `${formatShortDate(snapshot.nextEvent.date).slice(5)} ${snapshot.nextEvent.label}`
    : `${formatShortDate(snapshot.phase.end).slice(5)} 结束`;

  return Response.json(
    {
      refreshNow: false,
      taskAlias: "沪上校历",
      data: {
        date: formatShortDate(snapshot.date),
        phase: snapshot.phase.name,
        primaryLabel: snapshot.display.primaryLabel,
        primaryValue: snapshot.display.primaryValue,
        secondaryLabel: snapshot.display.secondaryLabel,
        secondaryValue: snapshot.display.secondaryValue,
        progress: snapshot.display.progressPercent,
        detail,
        nextEvent,
      },
      windowData: canvasTemplate(),
      layoutFull: { tw: "p-[10px]" },
      link: LANDING_URL,
      border: 0,
      meta: {
        schemaVersion: 1,
        generatedAt: new Date().toISOString(),
        target: "quote_0_296x152",
        dataEndpoint: `${LANDING_URL}/api/calendar`,
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
