import os
import json
from threading import Lock
import json_repair
from openai import OpenAI
from core.utils.config_utils import load_key
from rich import print as rprint
from core.utils.decorator import except_handler

# ------------
# cache gpt response
# ------------

LOCK = Lock()
GPT_LOG_FOLDER = 'output/gpt_log'


def _normalize_json_response(resp):
    if isinstance(resp, list):
        dict_items = [item for item in resp if isinstance(item, dict)]
        if len(resp) == 1 and dict_items:
            return dict_items[0]
        if len(dict_items) == 1:
            return dict_items[0]
    return resp


def _validate_response(model, prompt, resp_content, resp_type, resp, valid_def):
    if not valid_def:
        return resp

    try:
        valid_resp = valid_def(resp)
    except Exception as exc:
        _save_cache(
            model,
            prompt,
            resp_content,
            resp_type,
            resp,
            log_title="error",
            message=f"Response validation failed: {exc}"
        )
        raise ValueError(f"❎ API response validation failed: {exc}") from exc

    if valid_resp['status'] != 'success':
        _save_cache(model, prompt, resp_content, resp_type, resp, log_title="error", message=valid_resp['message'])
        raise ValueError(f"❎ API response error: {valid_resp['message']}")

    return resp

def _save_cache(model, prompt, resp_content, resp_type, resp, message=None, log_title="default"):
    with LOCK:
        logs = []
        file = os.path.join(GPT_LOG_FOLDER, f"{log_title}.json")
        os.makedirs(os.path.dirname(file), exist_ok=True)
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append({"model": model, "prompt": prompt, "resp_content": resp_content, "resp_type": resp_type, "resp": resp, "message": message})
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

def _load_cache(prompt, resp_type, log_title):
    with LOCK:
        file = os.path.join(GPT_LOG_FOLDER, f"{log_title}.json")
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                for item in reversed(json.load(f)):
                    if item["prompt"] == prompt and item["resp_type"] == resp_type:
                        return item["resp"]
        return False

# ------------
# ask gpt once
# ------------

@except_handler("GPT request failed", retry=5)
def ask_gpt(prompt, resp_type=None, valid_def=None, log_title="default"):
    if not load_key("api.key"):
        raise ValueError("API key is not set")
    model = load_key("api.model")
    # check cache
    cached = _load_cache(prompt, resp_type, log_title)
    if cached is not False:
        rprint("use cache response")
        if resp_type == "json":
            cached = _normalize_json_response(cached)
        try:
            return _validate_response(model, prompt, "<cached>", resp_type, cached, valid_def)
        except ValueError as exc:
            rprint(f"[yellow]cached response invalid, retrying with live request: {exc}[/yellow]")

    base_url = load_key("api.base_url")
    if 'ark' in base_url:
        base_url = "https://ark.cn-beijing.volces.com/api/v3" # huoshan base url
    elif 'v1' not in base_url:
        base_url = base_url.strip('/') + '/v1'
    client = OpenAI(api_key=load_key("api.key"), base_url=base_url)
    response_format = {"type": "json_object"} if resp_type == "json" and load_key("api.llm_support_json") else None

    messages = [{"role": "user", "content": prompt}]

    params = dict(
        model=model,
        messages=messages,
        response_format=response_format,
        timeout=300
    )
    resp_raw = client.chat.completions.create(**params)

    # process and return full result
    resp_content = resp_raw.choices[0].message.content
    if resp_type == "json":
        resp = json_repair.loads(resp_content)
        resp = _normalize_json_response(resp)
    else:
        resp = resp_content

    resp = _validate_response(model, prompt, resp_content, resp_type, resp, valid_def)

    _save_cache(model, prompt, resp_content, resp_type, resp, log_title=log_title)
    return resp


if __name__ == '__main__':
    from rich import print as rprint
    
    result = ask_gpt("""test respond ```json\n{\"code\": 200, \"message\": \"success\"}\n```""", resp_type="json")
    rprint(f"Test json output result: {result}")
