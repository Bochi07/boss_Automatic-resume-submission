# goodJobs - Boss直聘自动投递工具

浏览器油猴脚本 + 本地 Python 后端，自动在 Boss 直聘上筛选岗位、打招呼、发简历。

> 仅供学习交流，请遵守 Boss 直聘平台规则，使用风险自担。

## 能做什么

- 按关键词自动搜索岗位
- 根据标题 + JD 内容自动打分筛选
- 分数达标自动打招呼
- 收到 HR 新消息自动发简历
- 关键词用完自动切换下一个继续

## 技术栈

**后端**：Python + FastAPI + Uvicorn + Pydantic

**前端**：Tampermonkey 油猴脚本（原生 JS）+ BroadcastChannel 多标签页通信

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建配置

```bash
cp user_config.example.json user_config.json
```

编辑 `user_config.json`，至少改这几项：

```json
{
  "introduce": "你好，我对这个岗位感兴趣，想了解一下~",
  "tags": ["你的目标岗位关键词1", "关键词2", "关键词3"],
  "frontend": {
    "resumeIndex": 0,
    "thread": 50
  }
}
```

| 字段 | 说明 |
|------|------|
| `introduce` | 打招呼语，发给 HR 的第一句话 |
| `tags` | 搜索关键词列表，脚本会自动轮换 |
| `resumeIndex` | 发第几份简历，从 0 开始 |
| `thread` | 匹配分数阈值（0-100），低于此值不投递 |

### 3. 启动后端

```bash
python main.py
```

Windows 也可以双击 `start_backend.bat`。

后端默认监听 `http://127.0.0.1:8000`。

### 4. 安装浏览器脚本

1. 浏览器安装 [Tampermonkey](https://www.tampermonkey.net/) 插件
2. Tampermonkey 中新建脚本，把 `web_script.js` 内容全部粘贴进去，保存
3. 打开 [Boss直聘](https://www.zhipin.com/) 页面，脚本自动运行

---

## 工作流程

```
按关键词搜索岗位
  → 滚动预加载岗位列表
  → 逐个打开详情页，提取标题/薪资/JD描述
  → 后端规则打分
  → 分数 ≥ 阈值 → 自动打招呼
  → 收到HR新消息 → 自动发简历
  → 关键词用完 → 自动切换下一个继续
```

## 打分规则

打分 = 标题分 + JD正文分 + 组合加分 - 扣分（满分100）

| 类型 | 说明 | 示例 |
|------|------|------|
| 标题拦截词 | 命中直接 0 分，跳过 | 测试、销售、算法 |
| 标题强正向词 | 命中给高分 | AI应用、Agent、Vibe Coding |
| 标题中匹配词 | 命中给中分 | AI、自动化、运维 |
| JD加分词 | 描述里出现就加分 | k8s、docker、python |
| JD扣分词 | 描述里出现就扣分 | spring、react、vue |

所有关键词和分值都在 `user_config.json` 的 `scoring` 中配置，格式为 `"关键词": 分数`。

---

## 参数修改指南

### 基础配置

```json
{
  "introduce": "打招呼语",
  "tags": ["关键词1", "关键词2"],
  "character": "简洁 直接 礼貌"
}
```

### 前端行为（`frontend`）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `thread` | 投递分数阈值 | `50` |
| `onlyGreet` | 只打招呼不自动聊天 | `false` |
| `manualFilterWaitMs` | 每轮搜索后等用户手动筛选的时间(ms) | `9876` |
| `roundRestartDelayMs` | 轮次间缓冲时间(ms) | `2057` |
| `maxEmptyRounds` | 连续几轮无新岗位后切换关键词 | `3` |
| `detailTimeout` | 获取职位详情超时(ms) | `9987` |
| `greetTimeout` | 打招呼超时(ms) | `11843` |
| `preloadScrollPixels` | 预加载每轮下滑像素 | `180` |
| `preloadScrollWaitMs` | 预加载每轮等待(ms) | `468` |

### 后端参数（`backend`）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `job_score_delay_base_ms` | 打分接口基础延迟(ms) | `4187` |
| `job_score_delay_jitter_ms` | 延迟随机抖动范围(ms) | `836` |

延迟用于模拟人类行为，避免请求太快被风控。所有时间参数均为非整十毫秒的基准值，并在运行时叠加随机抖动（`web_script.js` 的 `tools.jitter`，默认 ±16%），避免出现固定的整数/整十间隔。

### 评分规则（`scoring`）

在 `user_config.json` 中按需增删关键词：

```json
"scoring": {
  "title_block_keywords": { "不想投的词": 100 },
  "title_strong_keywords": { "想投的词": 88 },
  "title_medium_keywords": { "一般想投的词": 60 },
  "detail_infra_keywords": { "jd里出现会加分的词": 10 },
  "detail_negative_keywords": { "jd里出现会扣分的词": 16 }
}
```

---

## 文件说明

```
├── main.py                  # 后端入口
├── core.py                  # 岗位评分 + 打招呼逻辑
├── config.py                # 配置加载
├── web_script.js            # 浏览器油猴脚本
├── user_config.example.json # 配置模板
├── requirements.txt         # Python依赖
├── start_backend.bat        # Windows启动脚本
├── LICENSE
└── .gitignore
```

---

## 注意事项

使用前请了解以下已知特性，不影响主链正常使用：

1. **关键词匹配是子串匹配**：配置中的短关键词（如 `ai`、`web`）可能会匹配到包含该子串的无关词（如 `said`、`webview`）。建议优先使用较长、更具体的关键词，或在 `title_block_keywords` 中拦截误命中。

2. **延迟参数是"非整十基准 + 随机抖动"**：本次改版后，所有动作间隔（打分延迟、点击、输入、滚动、轮次缓冲、心跳等）都改为非整十毫秒的基准值，再叠加 `tools.jitter` 的 ±16% 随机抖动和 0~1ms 小数扰动，实际等待时间每次都不一样，且不再出现 `1000/2000/3000` 这类整十毫秒。这是刻意用于贴近真人操作节奏，请勿为了"跑得快"改回固定小整数——固定间隔反而更容易被识别。注意前端 `setTimeout` 最终会把毫秒取整，因此浏览器里实际间隔是"非整十的整数毫秒"（如 `634`、`712`）；后端 `asyncio.sleep` 则保留小数毫秒（如 `4187.35`）。

3. **超时参数是固定上限，不参与抖动**：`timestampTimeout` / `detailTimeout` / `greetTimeout` 是"等待多久后判超时"的兜底上限，代码中保持固定值（同样建议非整十，如 `3057`/`9987`/`11843`），不要把它当作动作间隔去随机化，否则可能缩短超时导致误判。

4. **`user_config.example.json` 与代码默认规则不同**：评分关键词两侧仍是两套（`user_config.example.json` 是精简示例、`config.py` 是内置默认），创建 `user_config.json` 后以你的配置为准。时间参数两侧已统一为非整十默认值；若在 `user_config.json` 里自定义延迟，建议同样写成非整十基准（如 `4187`、`836`），否则抖动会围绕整十基准波动，削弱随机化效果。

5. **评分是标题分 + JD分叠加**：一个岗位可能同时命中正向词和扣分词，最终分数是各维度叠加的结果。后端控制台和 `job_decisions.jsonl` 日志会记录详细的分数构成，排查时可参考。

6. **Boss 直聘页面结构变化**：脚本依赖 Boss 直聘的 DOM 选择器（如 `.job-card-box`、`.btn-startchat`）。如果 Boss 直聘改版，脚本可能需要同步更新选择器。

7. **多标签页不要手动刷新**：脚本通过 BroadcastChannel 在搜索页/详情页/聊天页之间通信。手动刷新某个标签页可能导致心跳断开，触发自动恢复逻辑。

8. **日志文件会持续增长**：`job_decisions.jsonl` 和 `job_actions.jsonl` 是运行时追加写入的日志，不会自动清理。长期使用时注意定期清理或加入 `.gitignore`。

## License

[MIT](LICENSE)
