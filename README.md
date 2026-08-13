# 沪上校历 · Quote/0

面向上海地区中小学的 Quote/0 墨水屏校历：自动显示开学多久、距离学期结束还有多久，以及寒暑假和教学周进度。

[在线落地页](https://quote0-school-calendar.chuxubank.chatgpt.site/) · [校历 REST API](https://quote0-school-calendar.chuxubank.chatgpt.site/api/calendar) · [Quote/0 Canvas API](https://quote0-school-calendar.chuxubank.chatgpt.site/api/quote0/canvas)

同一份代码支持三种部署目标：

- **GitHub Pages**：静态落地页，浏览器端自动计算当天进度；
- **Cloudflare Worker**：独立提供 REST、Canvas 与健康检查 API；
- **Docker**：在任意支持容器的平台自托管完整站点和 API。

## 项目组成

- `app/`：公开落地页与 API 路由；
- `lib/school-calendar.ts`：共享的上海校历计算逻辑；
- `quote0-school-cli/`：生成 296 × 152 黑白 PNG，并通过 Quote/0 Image API 推送到设备的 Python CLI；
- `content-studio/`：Quote/0 Content Studio 申报材料、100 × 100 图标和响应示例；
- `worker/api.ts`：无状态的独立 Worker API 入口；
- `.github/workflows/`：Pages、Worker 与 GHCR 自动发布；
- `tests/`：落地页、REST API、Canvas API 与图标回归测试。

## 本地运行落地页

需要 Node.js 22.13 或更新版本：

```bash
npm install
npm run dev
```

验证生产构建与接口：

```bash
npm test
npm run test:deploy
```

REST API 支持传入日期以复现状态：

```text
GET /api/calendar?date=2026-08-13
GET /api/quote0/canvas?date=2026-08-13
GET /api/health
```

## GitHub Pages + Worker

合并到 `main` 后，`deploy-pages.yml` 会构建 `dist/pages` 并发布到：

```text
https://chuxubank.github.io/quote0-school-calendar/
```

Pages 默认连接当前公开 API。独立 Worker 部署完成后，在 GitHub 仓库变量中设置：

```text
QUOTE0_API_BASE_URL=https://quote0-school-calendar-api.<你的 workers.dev 子域>.workers.dev
```

Worker 自动部署需要两个 GitHub Actions secrets：

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

也可以在本机验证或部署：

```bash
npm run build:worker
npx wrangler deploy --config wrangler.api.jsonc
```

Worker 路由：

```text
GET /api/health
GET /api/calendar?date=YYYY-MM-DD
GET /api/quote0/canvas?date=YYYY-MM-DD
```

## Docker

本地构建并启动完整站点：

```bash
docker compose up --build
```

随后访问 <http://localhost:3000>。健康检查位于
<http://localhost:3000/api/health>。

每次合并到 `main`，GitHub Actions 会发布容器镜像到：

```text
ghcr.io/chuxubank/quote0-school-calendar:latest
```

服务器可直接运行：

```bash
docker run -d \
  --name quote0-school-calendar \
  --restart unless-stopped \
  -p 3000:3000 \
  ghcr.io/chuxubank/quote0-school-calendar:latest
```

## Quote/0 本地推送

CLI 需要 Python 3.11+ 与 `uv`：

```bash
cd quote0-school-cli
uv tool install .
quote0-school doctor
quote0-school render --output preview.png
quote0-school push --dry-run
quote0-school push
```

推送前在 Dot. App 的 Content Studio 中添加 **Image API** 内容，并配置：

```bash
export DOT_API_KEY='dot_app_...'
export DOT_DEVICE_ID='ABCD1234ABCD'
```

API Key 只应保存在本机环境变量中，不要提交到仓库。

## 校历数据

数据依据上海市教育委员会发布的上海市中小学校历。已收录 2025 学年与 2026 学年；法定节假日、个别学校安排或临时调整以学校最新通知为准。

- [上海市中小学 2026 学年校历](https://edu.sh.gov.cn/xxgk2_zdgz_jcjy_05/20260605/19ca2cb2e10a47fe86047bcc0bfdd0e8.html)
- [Quote/0 加入 Content Studio](https://dot.mindreset.tech/docs/service/studio/join-content-studio)
- [Quote/0 Canvas API](https://dot.mindreset.tech/docs/service/open/canvas_api)
- [Quote/0 Image API](https://dot.mindreset.tech/docs/service/open/image_api)

## 状态

项目已经具备公开 REST API、Canvas 布局与申报资料，目前处于 Quote/0 Content Studio **待官方审核**状态，尚不代表已经官方上架。
