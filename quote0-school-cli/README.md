# 沪上校历 · Quote/0

为 Quote/0 生成上海中小学校历，自动显示当前学期或寒暑假进度。CLI 同时支持官方 **Image API** 与 **Canvas API**：前者推送 296 × 152 黑白 PNG，后者推送可由设备渲染的结构化布局。

校历数据依据上海市教育委员会《上海市中小学 2025 学年校历》和《上海市中小学 2026 学年校历》。个别学校安排及节假日调整以学校通知为准。

## 安装

需要 Python 3.11+ 与 `uv`：

```bash
uv tool install .
```

安装后可在任意目录运行 `quote0-school`。

## 配置

在 Dot. App 的「更多 → API Key」创建并保存密钥；设备序列号位于「更多 → 设备列表 → 设备序列号」。

```bash
export DOT_API_KEY='dot_app_...'
export DOT_DEVICE_ID='ABCD1234ABCD'
```

也可以只保存非敏感的设备号：

```bash
quote0-school init --device-id ABCD1234ABCD
```

API Key 始终建议使用环境变量，不会由本项目写入配置文件。

在 Dot. App 的 Content Studio 中，需要先把对应的 **Image API** 或 **Canvas API** 内容加入设备的固定内容或循环内容；否则官方接口会返回 404。

## 使用

```bash
# 检查环境
quote0-school doctor

# 本地生成预览
quote0-school render --output preview.png

# 用指定日期验证版式
quote0-school render --date 2026-09-08 --output preview.png

# 查看设备、状态与内容任务；也可以只看 Canvas API 内容
quote0-school devices
quote0-school status
quote0-school tasks
quote0-school tasks --type canvas

# 先查看将要发送的请求摘要，再实际推送
quote0-school push --dry-run
quote0-school push

# 预览 Canvas 布局、检查完整结构化请求，再通过 Canvas API 推送
quote0-school canvas-preview --output canvas-preview.png
quote0-school push-canvas --dry-run --preview canvas-preview.png
quote0-school push-canvas
```

当设备存在多个 Image API 内容时，使用 `tasks` 返回的 `key`：

```bash
quote0-school push --task-key image_task_1
```

## JSON 输出

所有命令均支持全局 `--json`，成功时输出：

```json
{"ok": true, "data": {}}
```

失败时输出：

```json
{"ok": false, "error": {"type": "config_error", "message": "..."}}
```

## 原始只读请求

高层命令未覆盖的读取操作可以使用：

```bash
quote0-school --json request get /api/authV2/open/devices
```

`request` 仅支持 GET，避免把未确认的写操作藏在通用命令中。

## 定时更新

若要每天自动刷新，可用 macOS `launchd`、Linux cron 或其他调度器定时运行 `quote0-school push`（Image API）或 `quote0-school push-canvas`（Canvas API）。设备休眠时，内容会先保存到服务端，并在设备下一次唤醒时显示。

## Content Studio 官方插件候选

本项目同时提供无需用户配置 API Key 的接口，供 Quote/0 Content Studio 审核与接入：

- 校历 REST API：<https://quote0-school-calendar.chuxubank.chatgpt.site/api/calendar>
- Canvas 布局接口：<https://quote0-school-calendar.chuxubank.chatgpt.site/api/quote0/canvas>
- 100 × 100 透明卡片图标：<https://quote0-school-calendar.chuxubank.chatgpt.site/content-studio-icon.png>
- 申报资料：[`content-studio/CONTENT_STUDIO_SUBMISSION.md`](content-studio/CONTENT_STUDIO_SUBMISSION.md)

接口支持 `?date=YYYY-MM-DD`，便于审核方复现任意日期的状态。站点与接口均已公开访问，接口本身没有额外鉴权。当前状态为“待官方审核”；在 Quote/0 官方确认上架前，仍可使用 CLI 的 Image API 或 Canvas API 推送方式。

## 官方资料

- [Quote/0 Image API](https://dot.mindreset.tech/docs/service/open/image_api)
- [加入 Content Studio](https://dot.mindreset.tech/docs/service/studio/join-content-studio)
- [Quote/0 Canvas API](https://dot.mindreset.tech/docs/service/open/canvas_api)
- [获取 API Key](https://dot.mindreset.tech/docs/service/open/get_api)
- [查看设备序列号](https://dot.mindreset.tech/docs/service/open/get_device_id)
- [上海市中小学 2026 学年校历](https://edu.sh.gov.cn/xxgk2_zdgz_jcjy_05/20260605/19ca2cb2e10a47fe86047bcc0bfdd0e8.html)
