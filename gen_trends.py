#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 / 刷新「北弄南巷 行业热点」trends.json
- 配置了 LLM_API_KEY：调用大模型生成周更草稿并写入 trends.json
- 未配置：不修改内容，直接退出（由 workflow 决定是否开 Issue 提醒）

环境变量：
  LLM_API_KEY   必填(启用自动生成时)
  LLM_BASE_URL  可选，默认 https://api.openai.com/v1
  LLM_MODEL     可选，默认 gpt-4o-mini
"""
import os, sys, json, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 'trends.json')

PROMPT = """你是文玩 / 珠宝首饰行业的品牌分析师。请只输出一个 JSON（不要任何多余文字、不要代码块围栏），结构严格如下：

{
  "HOT": {
    "北弄": [ {"t":"要点标题(不超过12字)","d":"一句话说明，含来源与年份"} ],
    "南巷": [ {"t":"要点标题(不超过12字)","d":"一句话说明，含来源与年份"} ]
  },
  "PICKS": {
    "北弄": [ {"n":"商品名","c":"品类","p":"价格带","w":"推荐理由(不超过40字)"} ],
    "南巷": [ {"n":"商品名","c":"品类","p":"价格带","w":"推荐理由(不超过40字)"} ]
  }
}

硬性要求：
1. 北弄 = 珍珠 / 天然石 / 新中式手串（江南院落、悦己疗愈、25-35 岁都市女性、主力价 168-368 元）。
   南巷 = 树籽 / 菩提 / 果核 / 平价文玩（18-30 岁、解压好玩、轻复古、主力价 69-199 元）。
2. 每个品牌 HOT 输出 6 条、PICKS 输出 6 条。
3. 只写近半年内可公开查证的趋势；引用请在 d 中注明来源与年份（如"(1688，2026)"）。
4. 不要编造精确数字；如不确定，请写"(待核实)"。
5. 全部中文。"""


def call_llm():
    key = os.environ.get('LLM_API_KEY', '').strip()
    if not key:
        return None
    base  = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    model = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的行业研究助手，只输出合法 JSON。"},
            {"role": "user", "content": PROMPT},
        ],
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        base + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read().decode('utf-8'))
    txt = j['choices'][0]['message']['content']
    return json.loads(txt)


def validate(data):
    if not isinstance(data, dict):
        return False
    h, p = data.get('HOT'), data.get('PICKS')
    if not (isinstance(h, dict) and isinstance(p, dict)):
        return False
    for b in ('北弄', '南巷'):
        if not isinstance(h.get(b), list) or not isinstance(p.get(b), list):
            return False
        for it in h[b]:
            if not (isinstance(it, dict) and it.get('t') and it.get('d')):
                return False
        for it in p[b]:
            if not (isinstance(it, dict) and it.get('n') and it.get('w')):
                return False
    return True


def main():
    if not os.environ.get('LLM_API_KEY', '').strip():
        print('[skip] 未配置 LLM_API_KEY，跳过自动生成（workflow 将决定是否开 Issue 提醒）。')
        return 0
    try:
        data = call_llm()
    except urllib.error.HTTPError as e:
        print('[error] 接口返回', e.code, e.read().decode('utf-8', 'ignore')[:300], file=sys.stderr)
        return 1
    except Exception as e:
        print('[error] 调用失败：', e, file=sys.stderr)
        return 1

    if not validate(data):
        print('[error] 模型返回结构不合法，已放弃写入。', file=sys.stderr)
        return 1

    data['updated'] = datetime.date.today().isoformat()
    data['source']  = 'auto-weekly'
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('[ok] 已写入', OUT, '·', data['updated'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
