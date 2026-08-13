export type SchoolPeriod = {
  id: string;
  name: string;
  eyebrow: string;
  start: string;
  end: string;
  weeks?: number;
  type: "term" | "vacation";
  nextLabel?: string;
};

export type CalendarSnapshot = {
  date: string;
  timezone: "Asia/Shanghai";
  schoolYear: string;
  phase: {
    id: string;
    name: string;
    type: "term" | "vacation";
    start: string;
    end: string;
    weeks: number | null;
  };
  display: {
    primaryLabel: string;
    primaryValue: number;
    primaryUnit: "天";
    secondaryLabel: string;
    secondaryValue: number;
    elapsedDays: number;
    remainingDays: number;
    progressPercent: number;
    teachingWeek: number | null;
  };
  nextEvent: {
    label: string;
    date: string;
    daysAway: number;
  } | null;
};

const DAY = 86_400_000;

export const periods: SchoolPeriod[] = [
  {
    id: "term-2025-1",
    name: "第一学期",
    eyebrow: "2025 学年",
    start: "2025-09-01",
    end: "2026-01-30",
    weeks: 22,
    type: "term",
  },
  {
    id: "winter-2026",
    name: "寒假",
    eyebrow: "2025 学年",
    start: "2026-01-31",
    end: "2026-03-01",
    type: "vacation",
    nextLabel: "春季开学",
  },
  {
    id: "term-2025-2",
    name: "第二学期",
    eyebrow: "2025 学年",
    start: "2026-03-02",
    end: "2026-06-30",
    weeks: 18,
    type: "term",
  },
  {
    id: "summer-2026",
    name: "暑假",
    eyebrow: "2025 学年",
    start: "2026-07-01",
    end: "2026-08-31",
    type: "vacation",
    nextLabel: "秋季开学",
  },
  {
    id: "term-2026-1",
    name: "第一学期",
    eyebrow: "2026 学年",
    start: "2026-09-01",
    end: "2027-01-22",
    weeks: 21,
    type: "term",
  },
  {
    id: "winter-2027",
    name: "寒假",
    eyebrow: "2026 学年",
    start: "2027-01-23",
    end: "2027-02-21",
    type: "vacation",
    nextLabel: "春季开学",
  },
  {
    id: "term-2026-2",
    name: "第二学期",
    eyebrow: "2026 学年",
    start: "2027-02-22",
    end: "2027-06-30",
    weeks: 19,
    type: "term",
  },
  {
    id: "summer-2027",
    name: "暑假",
    eyebrow: "2026 学年",
    start: "2027-07-01",
    end: "2027-08-31",
    type: "vacation",
  },
];

export const termCards = periods.filter(
  (period) => period.type === "term" && period.eyebrow === "2026 学年",
);

export function dateFromKey(key: string) {
  return new Date(`${key}T00:00:00+08:00`);
}

export function isDateKey(value: string) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = dateFromKey(value);
  return !Number.isNaN(parsed.getTime()) && shanghaiDateKey(parsed) === value;
}

export function shanghaiDateKey(date = new Date()) {
  const parts = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);

  const value = (type: string) =>
    parts.find((part) => part.type === type)?.value ?? "";
  return `${value("year")}-${value("month")}-${value("day")}`;
}

export function diffDays(from: string, to: string) {
  return Math.round((dateFromKey(to).getTime() - dateFromKey(from).getTime()) / DAY);
}

export function inclusiveDays(from: string, to: string) {
  return diffDays(from, to) + 1;
}

export function formatShortDate(key: string) {
  const [year, month, day] = key.split("-").map(Number);
  return `${year}.${String(month).padStart(2, "0")}.${String(day).padStart(2, "0")}`;
}

export function weekdayLabel(key: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    weekday: "long",
  }).format(dateFromKey(key));
}

export function findActivePeriod(today: string) {
  return (
    periods.find((period) => today >= period.start && today <= period.end) ??
    periods.find((period) => today < period.start) ??
    periods[periods.length - 1]
  );
}

export function calendarSnapshot(today: string): CalendarSnapshot {
  const current = findActivePeriod(today);
  const totalDays = inclusiveDays(current.start, current.end);
  const elapsedDays = Math.min(
    totalDays,
    Math.max(0, inclusiveDays(current.start, today)),
  );
  const remainingDays = Math.max(0, diffDays(today, current.end));
  const progressPercent = Math.min(
    100,
    Math.max(0, Math.round((elapsedDays / totalDays) * 100)),
  );
  const nextPeriod = periods[periods.indexOf(current) + 1] ?? null;
  const primaryValue =
    current.type === "term"
      ? elapsedDays
      : nextPeriod
        ? diffDays(today, nextPeriod.start)
        : remainingDays;
  const primaryLabel =
    current.type === "term"
      ? "开学第"
      : nextPeriod
        ? `距${current.nextLabel ?? "下一阶段"}`
        : "假期还剩";
  const secondaryLabel =
    current.type === "term" ? "距学期结束" : `${current.name}第`;
  const secondaryValue = current.type === "term" ? remainingDays : elapsedDays;
  const teachingWeek =
    current.type === "term"
      ? Math.min(current.weeks ?? 1, Math.ceil(elapsedDays / 7))
      : null;

  return {
    date: today,
    timezone: "Asia/Shanghai",
    schoolYear: current.eyebrow.replace(" ", ""),
    phase: {
      id: current.id,
      name: current.name,
      type: current.type,
      start: current.start,
      end: current.end,
      weeks: current.weeks ?? null,
    },
    display: {
      primaryLabel,
      primaryValue,
      primaryUnit: "天",
      secondaryLabel,
      secondaryValue,
      elapsedDays,
      remainingDays,
      progressPercent,
      teachingWeek,
    },
    nextEvent: nextPeriod
      ? {
          label: current.nextLabel ?? nextPeriod.name,
          date: nextPeriod.start,
          daysAway: Math.max(0, diffDays(today, nextPeriod.start)),
        }
      : null,
  };
}
