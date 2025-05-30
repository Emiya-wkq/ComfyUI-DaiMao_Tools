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
        
        print(f"节点 {my_unique_id} 接收到的 selected_data: {selected_data}")
        
        if selected_data:
            try:
                if isinstance(selected_data, str) and selected_data.strip():
                    data = json.loads(selected_data)
                    if isinstance(data, list):
                        selected_characters = data
                    else:
                        selected_characters = [data]
                else:
                    selected_characters = []
            except Exception as e:
                print(f"解析选中数据出错: {e}")
                selected_characters = []
        
        print(f"解析后的角色数据: {selected_characters}")
        
        # 格式化角色名称为"角色名称 《作品名称》"
        if selected_characters:
            formatted_names = []
            for character in selected_characters:
                if isinstance(character, dict):
                    # 获取角色名称（优先使用英文名）
                    char_name = character.get('character_english_name', '') or character.get('character_chinese_name', '')
                    # 获取作品名称（优先使用英文名）
                    anime_name = character.get('anime_english_name', '') or character.get('anime_chinese_name', '')
                    
                    print(f"处理角色: {char_name}, 作品: {anime_name}")
                    
                    if char_name and anime_name:
                        formatted_name = f"{char_name} 《{anime_name}》"
                        formatted_names.append(formatted_name)
                    elif char_name:
                        formatted_names.append(char_name)
                else:
                    # 如果是字符串，直接使用
                    formatted_names.append(str(character))
            
            names = ", ".join(formatted_names)
            
            # 将角色信息放在前面，如果有string内容则用逗号拼接
            if string and string.strip():
                result = f"{names}, {string}".strip()
            else:
                result = names
        else:
            # 如果没有选择角色，直接输出string
            result = string if string else ""
        
        print(f"节点 {my_unique_id} 最终输出: {result}")
        return (result,) 