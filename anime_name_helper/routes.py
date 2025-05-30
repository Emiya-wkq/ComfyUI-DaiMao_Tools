from aiohttp import web
from server import PromptServer
import os
import json

@PromptServer.instance.routes.get('/anime_name_helper/get_anime_names')
async def anime_name_helper_api(request):
    query = request.rel_url.query.get("query", "")
    filter = request.rel_url.query.get("filter", "")
    # 读取 data.json 并过滤
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return web.json_response({"error": f"读取数据失败: {str(e)}"}, status=500)
    # 简单过滤逻辑
    def match(item):
        if query and not any(query in str(v) for v in item.values()):
            return False
        if filter and not any(filter in str(v) for v in item.values()):
            return False
        return True
    result = [item for item in data if match(item)]
    return web.json_response(result) 