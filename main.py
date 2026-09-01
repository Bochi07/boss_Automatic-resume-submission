from datetime import datetime
import asyncio
import random
import json
import sys
import threading
from pathlib import Path
from fastapi import FastAPI, Body
from core import evaluateSingleRouteDelivery
from config import Config


app = FastAPI()
LOG_PATH = Path(__file__).resolve().parent / 'job_decisions.jsonl'
ACTION_LOG_PATH = Path(__file__).resolve().parent / 'job_actions.jsonl'
_LOG_LOCK = threading.Lock()


def append_job_decision_log(result: dict, raw_job: str, delay_ms: int):
    log_record = {
        'loggedAt': datetime.now().isoformat(timespec='seconds'),
        'title': result.get('title'),
        'detail': result.get('detail'),
        'matchedField': result.get('matched_field'),
        'keyword': result.get('keyword'),
        'score': result.get('score'),
        'introduce': result.get('introduce'),
        'resumeIndex': result.get('resumeIndex'),
        'titleScore': result.get('title_score'),
        'detailScore': result.get('detail_score'),
        'comboScore': result.get('combo_score'),
        'titlePenaltyScore': result.get('title_penalty_score'),
        'penaltyScore': result.get('penalty_score'),
        'reason': result.get('reason'),
        'delayMs': delay_ms,
        'rawJob': raw_job,
    }
    try:
        with _LOG_LOCK:
            with LOG_PATH.open('a', encoding='utf-8') as f:
                f.write(json.dumps(log_record, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[WARN] 写入决策日志失败: {e}", file=sys.stderr, flush=True)


def append_job_action_log(action: dict):
    action_record = {
        'loggedAt': datetime.now().isoformat(timespec='seconds'),
        **action,
    }
    try:
        with _LOG_LOCK:
            with ACTION_LOG_PATH.open('a', encoding='utf-8') as f:
                f.write(json.dumps(action_record, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[WARN] 写入动作日志失败: {e}", file=sys.stderr, flush=True)


@app.get("/tags", summary="获取职位标签")
async def get_tags():
    return {
        'tags': Config.tags
    }


@app.get("/get-introduce", summary="获取自我介绍")
async def get_introduce():
    return {
        'introduce': Config.get_default_introduce()
    }


@app.get("/client-config", summary="获取前端运行配置")
async def get_client_config():
    return Config.get_client_config()


@app.post("/get-job-score", summary="获取职位匹配度")
async def get_job_score(job: str = Body(..., description="职位信息")):
    result = await asyncio.to_thread(evaluateSingleRouteDelivery, job)
    delay_ms = max(0.0, Config.job_score_delay_base_ms + random.uniform(
        -Config.job_score_delay_jitter_ms,
        Config.job_score_delay_jitter_ms,
    ) + random.random() * 0.7)
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = result['title'] or '未识别标题'
    keyword = result['keyword'] or '无'
    matched_field_map = {
        'title': '岗位名称',
        'detail': '职位描述',
        'none': '未命中',
        'title_negative': '标题负向拦截',
    }
    print(
        f"[{time_str}] /get-job-score | "
        f"title={title} | "
        f"matched={matched_field_map.get(result['matched_field'], result['matched_field'])} | "
        f"keyword={keyword} | "
        f"title_score={result['title_score']} | "
        f"detail_score={result['detail_score']} | "
        f"combo_score={result['combo_score']} | "
        f"title_penalty_score={result.get('title_penalty_score', 0)} | "
        f"penalty_score={result['penalty_score']} | "
        f"delay_ms={delay_ms} | "
        f"score={result['score']} | "
        f"reason={result['reason']}",
        flush=True
    )
    append_job_decision_log(result, job, delay_ms)
    await asyncio.sleep(delay_ms / 1000)
    return {
        'score': result['score'],
        'introduce': result['introduce'],
        'resumeIndex': result['resumeIndex'],
    }


@app.post("/log-action", summary="记录前端动作日志")
async def log_action(action: dict = Body(..., description="动作日志")):
    append_job_action_log(action)
    return {'success': True}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
