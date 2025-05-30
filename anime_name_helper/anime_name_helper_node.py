import os
import json

class AnimeNameHelper:
    """动漫人物名称辅助器节点，动态下拉选择人物英文名，拼接 prompt 输出"""
    @classmethod
    def INPUT_TYPES(cls):
        # 动态读取 data.json，生成所有人物英文名
        data_path = os.path.join(os.path.dirname(__file__), "data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            character_names = [item["character_english_name"] for item in data]
        except Exception:
            character_names = [""]
        return {
            "required": {
                "string": ("STRING", {"forceInput": True}),
                "selected_data": ("STRING", {"default": "[]", "multiline": False}),
            },
            "hidden" : {
                "prompt": "PROMPT",
                "extra_info": "EXTRA_PNGINFO",
                "my_unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("输出",)
    FUNCTION = "run"
    CATEGORY = "动漫工具"
    DISPLAY_NAME = "动漫人物名称辅助器"

    def run(self, string, selected_data, prompt, extra_info, my_unique_id):
        # 解析选中的角色数据
        selected_characters = []
        
        if selected_data:
            try:
                if isinstance(selected_data, str) and selected_data.strip():
                    data = json.loads(selected_data)
                    if isinstance(data, list):
                        selected_characters = data
                    else:
                        selected_characters = [str(data)]
                else:
                    selected_characters = []
            except Exception as e:
                print(f"解析选中数据出错: {e}")
                selected_characters = [str(selected_data)] if selected_data else []
        
        # 拼接角色名称
        if selected_characters:
            names = ", ".join(str(name) for name in selected_characters)
        else:
            names = "无选中角色"
        
        # 拼接输出
        result = f"{string} {names}".strip()
        print(f"节点 {my_unique_id} 输出: {result}")
        print(f"选中的角色: {selected_characters}")
        return (result,) 