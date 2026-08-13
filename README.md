# 沪上校历 · Quote/0

面向上海地区中小学的 Quote/0 墨水屏校历：自动显示开学多久、距离学期结束还有多久，以及寒暑假和教学周进度。

[在线落地页](https://quote0-school-calendar.chuxubank.chatgpt.site/) · [校历 REST API](https://quote0-school-calendar.chuxubank.chatgpt.site/api/calendar) · [Quote/0 Canvas API](https://quote0-school-calendar.chuxubank.chatgpt.site/api/quote0/canvas)

## 项目组成

- `app/`：公开落地页与 API 路由；
- `lib/school-calendar.ts`：共享的上海校历计算逻辑；
- `quote0-school-cli/`：生成 296 × 152 黑白 PNG，并通过 Quote/0 Image API 推送到设备的 Python CLI；
- `content-studio/`：Quote/0 Content Studio 申报材料、100 × 100 图标和响应示例；
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
```

REST API 支持传入日期以复现状态：

```text
GET /api/calendar?date=2026-08-13
GET /api/quote0/canvas?date=2026-08-13
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
