"use client";

import { useEffect, useMemo, useState } from "react";
import {
  diffDays,
  findActivePeriod,
  formatShortDate,
  inclusiveDays,
  periods,
  shanghaiDateKey,
  termCards,
  weekdayLabel,
} from "../lib/school-calendar";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");

function apiHref(path: string) {
  return `${API_BASE_URL}${path}`;
}

function Calendar({ todayKey }: { todayKey: string }) {
  const [year, month, today] = todayKey.split("-").map(Number);
  const firstDay = new Date(Date.UTC(year, month - 1, 1)).getUTCDay();
  const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const cells = Array.from({ length: 42 }, (_, index) => {
    const day = index - firstDay + 1;
    return day > 0 && day <= daysInMonth ? day : null;
  });

  const markers: Record<string, string> = {
    "2026-09-01": "开学",
    "2027-01-22": "结课",
    "2027-02-22": "开学",
    "2027-06-30": "结课",
  };

  return (
    <section className="calendar-card" aria-labelledby="calendar-title">
      <div className="card-heading">
        <div>
          <p className="section-kicker">MONTH VIEW</p>
          <h2 id="calendar-title">{year} 年 {month} 月</h2>
        </div>
        <span className="today-chip">今天 · {today} 日</span>
      </div>

      <div className="calendar-grid weekday-row" aria-hidden="true">
        {['日', '一', '二', '三', '四', '五', '六'].map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      <div className="calendar-grid days-grid">
        {cells.map((day, index) => {
          const key = day
            ? `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            : '';
          const marker = markers[key];
          return (
            <div
              className={`calendar-day ${day === today ? 'is-today' : ''} ${marker ? 'has-marker' : ''}`}
              key={`${index}-${day ?? 'blank'}`}
            >
              {day && <span>{day}</span>}
              {marker && <small>{marker}</small>}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default function Home() {
  const [todayKey, setTodayKey] = useState(() => shanghaiDateKey());
  const [selectedTerm, setSelectedTerm] = useState(termCards[0].id);

  useEffect(() => {
    const timer = window.setInterval(() => setTodayKey(shanghaiDateKey()), 60_000);
    return () => window.clearInterval(timer);
  }, []);

  const current = useMemo(() => findActivePeriod(todayKey), [todayKey]);
  const totalDays = inclusiveDays(current.start, current.end);
  const elapsedDays = Math.min(
    totalDays,
    Math.max(0, inclusiveDays(current.start, todayKey)),
  );
  const remainingDays = Math.max(0, diffDays(todayKey, current.end));
  const progress = Math.min(100, Math.max(0, (elapsedDays / totalDays) * 100));
  const nextPeriod = periods[periods.indexOf(current) + 1];
  const mainNumber =
    current.type === "term"
      ? elapsedDays
      : nextPeriod
        ? diffDays(todayKey, nextPeriod.start)
        : remainingDays;
  const mainLabel =
    current.type === "term"
      ? "开学第"
      : nextPeriod
        ? `距离${current.nextLabel ?? "下一阶段"}`
        : "假期还剩";
  const mainUnit = current.type === "term" ? "天" : "天";
  const activeTerm = termCards.find((term) => term.id === selectedTerm) ?? termCards[0];

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="沪上校历首页">
          <span className="brand-mark" aria-hidden="true">沪</span>
          <span>
            <strong>沪上校历</strong>
            <small>SHANGHAI SCHOOL DAYS</small>
          </span>
        </a>
        <div className="header-meta">
          <span className="live-dot" aria-hidden="true" />
          <a href="#install">Quote/0 插件</a>
          <span>·</span>
          上海时间 · 自动更新
        </div>
      </header>

      <div className="page-shell" id="top">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="status-line">
              <span>{current.eyebrow}</span>
              <span className="divider" />
              <span>{current.name}进行中</span>
            </div>
            <p className="today-line">
              {formatShortDate(todayKey)} · {weekdayLabel(todayKey)}
            </p>
            <h1 id="hero-title">
              {mainLabel}
              <span className="hero-number">{mainNumber}</span>
              {mainUnit}
            </h1>
            <p className="hero-note">
              {current.type === "term"
                ? `本学期已进行 ${elapsedDays} 天，距离学期结束还有 ${remainingDays} 天。`
                : `${current.name}第 ${elapsedDays} 天，已经走过 ${Math.round(progress)}%。`}
            </p>

            <div className="hero-actions">
              <a className="primary-action" href="#install">查看插件安装</a>
              <a
                className="secondary-action"
                href="#content-studio"
              >
                Content Studio 接入
              </a>
            </div>

            <div className="progress-block">
              <div className="progress-labels">
                <span>{formatShortDate(current.start)}</span>
                <strong>{Math.round(progress)}%</strong>
                <span>{formatShortDate(current.end)}</span>
              </div>
              <div
                className="progress-track"
                role="progressbar"
                aria-label={`${current.name}进度`}
                aria-valuenow={Math.round(progress)}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <span style={{ width: `${progress}%` }} />
              </div>
            </div>
          </div>

          <aside className="ink-panel" aria-label="今日概览">
            <div className="ink-topline">
              <span>QUOTE / SCHOOL</span>
              <span>{String(new Date().getFullYear()).slice(-2)}</span>
            </div>
            <div className="ink-main">
              <span className="ink-label">{mainLabel}</span>
              <strong>{mainNumber}</strong>
              <span className="ink-unit">DAYS</span>
            </div>
            <div className="ink-footer">
              <span>{current.name}</span>
              <span>{Math.round(progress)}% · 上海</span>
            </div>
          </aside>
        </section>

        <section className="stat-strip" aria-label="校历关键数据">
          <div>
            <span>当前阶段</span>
            <strong>{current.name}</strong>
          </div>
          <div>
            <span>{current.type === "term" ? "当前教学周" : "假期进度"}</span>
            <strong>
              {current.type === "term"
                ? `第 ${Math.min(current.weeks ?? 1, Math.ceil(elapsedDays / 7))} 周`
                : `${Math.round(progress)}%`}
            </strong>
          </div>
          <div>
            <span>{nextPeriod ? "下一节点" : "本阶段结束"}</span>
            <strong>{nextPeriod ? formatShortDate(nextPeriod.start) : formatShortDate(current.end)}</strong>
          </div>
          <div>
            <span>数据范围</span>
            <strong>上海中小学</strong>
          </div>
        </section>

        <div className="content-grid">
          <Calendar todayKey={todayKey} />

          <section className="term-card" aria-labelledby="term-title">
            <div className="card-heading">
              <div>
                <p className="section-kicker">TERM PLAN</p>
                <h2 id="term-title">2026 学年</h2>
              </div>
              <span className="official-chip">官方校历</span>
            </div>

            <div className="term-switch" role="tablist" aria-label="选择学期">
              {termCards.map((term) => (
                <button
                  key={term.id}
                  type="button"
                  role="tab"
                  aria-selected={selectedTerm === term.id}
                  onClick={() => setSelectedTerm(term.id)}
                >
                  {term.name}
                </button>
              ))}
            </div>

            <div className="term-detail">
              <div className="term-number">
                <strong>{activeTerm.weeks}</strong>
                <span>教学周</span>
              </div>
              <div className="term-dates">
                <div>
                  <span>开学</span>
                  <strong>{formatShortDate(activeTerm.start)}</strong>
                </div>
                <i aria-hidden="true" />
                <div>
                  <span>结束</span>
                  <strong>{formatShortDate(activeTerm.end)}</strong>
                </div>
              </div>
            </div>

            <div className="milestones">
              <div>
                <span className="milestone-dot is-filled" />
                <p><strong>秋季开学</strong><small>2026.09.01</small></p>
              </div>
              <div>
                <span className="milestone-dot" />
                <p><strong>寒假开始</strong><small>2027.01.23</small></p>
              </div>
              <div>
                <span className="milestone-dot" />
                <p><strong>春季开学</strong><small>2027.02.22</small></p>
              </div>
              <div>
                <span className="milestone-dot" />
                <p><strong>暑假开始</strong><small>2027.07.01</small></p>
              </div>
            </div>
          </section>
        </div>

        <section className="plugin-section" id="install" aria-labelledby="plugin-title">
          <div className="plugin-intro">
            <p className="section-kicker">QUOTE/0 PLUGIN</p>
            <h2 id="plugin-title">把开学倒计时，<br />放进 296 × 152。</h2>
            <p>
              沪上校历为 Quote/0 原生墨水屏设计。每天自动计算上海中小学当前所处阶段，以清晰的黑白版式显示开学天数、学期余额、教学周和寒暑假进度。
            </p>
            <div className="plugin-tags" aria-label="插件特性">
              <span>1-bit 黑白</span>
              <span>官方 Image API</span>
              <span>Canvas API</span>
              <span>上海时间</span>
            </div>
          </div>

          <div className="install-card">
            <div className="install-heading">
              <span>个人版安装与推送</span>
              <small>3 STEPS</small>
            </div>
            <ol>
              <li>
                <span>01</span>
                <p><strong>添加 Image API</strong><small>在 Dot. App 的 Content Studio 中，将 Image API 加入设备内容。</small></p>
              </li>
              <li>
                <span>02</span>
                <p><strong>配置设备凭据</strong><small>设置 DOT_API_KEY 与 DOT_DEVICE_ID 环境变量，密钥只保存在本机。</small></p>
              </li>
              <li>
                <span>03</span>
                <p><strong>推送到墨水屏</strong><code>quote0-school push</code></p>
              </li>
            </ol>
            <div className="install-footer">
              <span>支持本地预览：quote0-school render</span>
              <a href="https://dot.mindreset.tech/docs/service/open/get_api" target="_blank" rel="noreferrer">获取 API Key ↗</a>
            </div>
          </div>
        </section>

        <section
          className="integration-section"
          id="content-studio"
          aria-labelledby="integration-title"
        >
          <div className="integration-heading">
            <div>
              <p className="section-kicker">CONTENT STUDIO INTEGRATION</p>
              <h2 id="integration-title">官方接入所需接口，已经就绪。</h2>
            </div>
            <span className="review-chip">待官方审核</span>
          </div>
          <p className="integration-lead">
            沪上校历提供无需登录的结构化数据源与 Quote/0 Canvas 原生布局。接口按上海时间自动计算，带官方校历来源、缓存策略和版本字段，可直接用于 Content Studio 接入评审。
          </p>

          <div className="endpoint-grid">
            <a href={apiHref("/api/calendar")} target="_blank" rel="noreferrer">
              <span>01 · REST DATA</span>
              <strong>校历数据 API</strong>
              <code>GET /api/calendar</code>
              <small>当前阶段、倒计时、教学周、进度与下一节点</small>
            </a>
            <a href={apiHref("/api/quote0/canvas")} target="_blank" rel="noreferrer">
              <span>02 · CANVAS</span>
              <strong>Quote/0 布局</strong>
              <code>GET /api/quote0/canvas</code>
              <small>原生 windowData、展示数据与点击落地页</small>
            </a>
            <a
              href="https://dot.mindreset.tech/docs/service/studio/join-content-studio"
              target="_blank"
              rel="noreferrer"
            >
              <span>03 · REVIEW</span>
              <strong>Content Studio</strong>
              <code>材料包已准备</code>
              <small>图标、内容说明、接口示例与设备适配信息</small>
            </a>
          </div>

          <div className="integration-footer">
            <span><i aria-hidden="true" /> API 公开在线 · 无需认证 · 6 小时缓存</span>
            <span>适配 Quote/0 · 296 × 152</span>
          </div>
        </section>

        <section className="source-note">
          <div className="source-icon" aria-hidden="true">校</div>
          <div>
            <strong>校历说明</strong>
            <p>
              日期依据上海市教育委员会《上海市中小学 2026 学年校历》。节假日与个别学校安排可能调整，请以学校最新通知为准。
            </p>
          </div>
          <a
            href="https://edu.sh.gov.cn/xxgk2_zdgz_jcjy_05/20260605/19ca2cb2e10a47fe86047bcc0bfdd0e8.html"
            target="_blank"
            rel="noreferrer"
          >
            查看来源 <span aria-hidden="true">↗</span>
          </a>
        </section>
      </div>

      <footer>
        <span>沪上校历 · 简单看见每一天</span>
        <span>更新时间：{formatShortDate(todayKey)}</span>
      </footer>
    </main>
  );
}
