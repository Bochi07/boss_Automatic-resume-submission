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

**AI**：Ollama 本地模型（可选，主链不依赖）

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
| `manualFilterWaitMs` | 每轮搜索后等用户手动筛选的时间(ms) | `10000` |
| `roundRestartDelayMs` | 轮次间缓冲时间(ms) | `2000` |
| `maxEmptyRounds` | 连续几轮无新岗位后切换关键词 | `3` |
| `detailTimeout` | 获取职位详情超时(ms) | `10000` |
| `greetTimeout` | 打招呼超时(ms) | `12000` |
| `preloadScrollPixels` | 预加载每轮下滑像素 | `180` |
| `preloadScrollWaitMs` | 预加载每轮等待(ms) | `450` |

### 后端参数（`backend`）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `job_score_delay_base_ms` | 打分接口基础延迟(ms) | `4000` |
| `job_score_delay_jitter_ms` | 延迟随机抖动范围(ms) | `500` |

延迟用于模拟人类行为，避免请求太快被风控。

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
├── core.py                  # 岗位评分 + 聊天逻辑
├── config.py                # 配置加载
├── schema.py                # 数据模型
├── prompts.py               # LLM提示词（遗留功能）
├── tools.py                 # 工具函数
├── cache.py                 # 遗留兼容层
├── web_script.js            # 浏览器油猴脚本
├── user_config.example.json # 配置模板
├── requirements.txt         # Python依赖
├── start_backend.bat        # Windows启动脚本
├── LICENSE
└── .gitignore
```

## 关于 Ollama

主链功能（打分、打招呼、发简历）不依赖 Ollama。

如果要启用遗留的自动聊天功能（`/reply`、`/is-need-resume`、`/is-need-works`），需要额外安装 [Ollama](https://ollama.com/) 并拉取模型：

```bash
ollama pull qwen3:0.6b
```

---

## 注意事项

使用前请了解以下已知特性，不影响主链正常使用：

1. **关键词匹配是子串匹配**：配置中的短关键词（如 `ai`、`web`）可能会匹配到包含该子串的无关词（如 `said`、`webview`）。建议优先使用较长、更具体的关键词，或在 `title_block_keywords` 中拦截误命中。

2. **`user_config.example.json` 与代码默认评分规则不同**：`config.py` 内置了一套默认评分规则，`user_config.example.json` 提供了另一套更精简的示例。创建 `user_config.json` 后以你的配置为准，两者不会冲突。

3. **评分是标题分 + JD分叠加**：一个岗位可能同时命中正向词和扣分词，最终分数是各维度叠加的结果。后端控制台和 `job_decisions.jsonl` 日志会记录详细的分数构成，排查时可参考。

4. **Boss 直聘页面结构变化**：脚本依赖 Boss 直聘的 DOM 选择器（如 `.job-card-box`、`.btn-startchat`）。如果 Boss 直聘改版，脚本可能需要同步更新选择器。

5. **多标签页不要手动刷新**：脚本通过 BroadcastChannel 在搜索页/详情页/聊天页之间通信。手动刷新某个标签页可能导致心跳断开，触发自动恢复逻辑。

6. **日志文件会持续增长**：`job_decisions.jsonl` 和 `job_actions.jsonl` 是运行时追加写入的日志，不会自动清理。长期使用时注意定期清理或加入 `.gitignore`。

7. **Ollama 为可选依赖**：主链（打分、打招呼、发简历）不需要 Ollama。只有遗留的自动聊天接口（`/reply` 等）才需要，不安装也不影响启动。

## License

[MIT](LICENSE)
