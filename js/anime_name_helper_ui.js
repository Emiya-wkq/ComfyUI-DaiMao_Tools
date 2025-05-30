import { app } from "../../../../scripts/app.js";
import { api } from "../../../../scripts/api.js";
import { $el } from "../../../../scripts/ui.js";

console.log("anime_name_helper.js 已加载");

// 缓存动漫人物列表
let anime_characters_cache = []

// 获取动漫人物列表
async function getAnimeCharacters(query = "", filter = "") {
    // 这里假设后端节点名为 anime_name_helper，参数为 query 和 filter
    // 实际API路径和参数名请根据你的后端适配
    const resp = await api.fetchApi(`/anime_name_helper/get_anime_names?query=${encodeURIComponent(query)}&filter=${encodeURIComponent(filter)}`);
       if (resp.status === 200) {
            let data = await resp.json();
        anime_characters_cache = data;
            return data;
    }
    return [];
}

// 渲染动漫人物标签列表
function getCharacterTagList(node, characters, language = 'zh-CN') {
    console.log( app.graph._nodes_by_id)
    let rlist = [];
    characters.forEach((item, i) => {
        const name = language === 'zh-CN' ? item.character_chinese_name : item.character_english_name;
        const anime = language === 'zh-CN' ? item.anime_chinese_name : item.anime_english_name;
        rlist.push($el(
            "label.anime-character-tag",
            {
                dataset: {
                    name: name,
                    englishName: item.character_english_name,
                    anime: anime,
                    gender: item.gender,
                    role: item.role,
                    index: i
                },
                $: (el) => {
                    el.onclick = () => {
                        console.log("点击")
                        console.log(node)
                        el.classList.toggle("anime-character-tag-selected");
                        el.children[0].checked = el.classList.contains("anime-character-tag-selected");
                        
                        // 获取所有已选英文名
                        let selected = Array.from(el.parentElement.querySelectorAll(".anime-character-tag-selected"))
                            .map(tag => tag.dataset.englishName);
                        console.log("选中的角色:", selected);
                        
                        // 找到 selected_data widget 并更新值
                        const selectedDataWidget = node.widgets.find(w => w.name === "selected_data");
                        if (selectedDataWidget) {
                            selectedDataWidget.value = JSON.stringify(selected);
                            console.log("已更新 selected_data widget:", selectedDataWidget.value);
                            
                            // 标记节点需要重新执行
                            node.setDirtyCanvas(true, true);
                        } else {
                            console.error("未找到 selected_data widget");
                            console.log("可用的 widgets:", node.widgets.map(w => w.name));
                        }
                    };
                },
            },
            [
                $el("input", {
                    type: 'checkbox',
                    name: name
                }),
                $el("span", {
                    textContent: `${name}（${anime}）`
                }),
                $el("span", {
                    textContent: `【${item.gender}·${item.role}】`,
                    style: { color: "#888", fontSize: "12px", marginLeft: "8px" }
                })
            ]
        ));
    });
    return rlist;
}

// 注册节点前端
app.registerExtension({
    name: 'comfy.animeNameHelper',
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name == 'anime_name_helper') {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 隐藏 selected_data widget
                setTimeout(() => {
                    const selectedDataWidget = this.widgets.find(w => w.name === "selected_data");
                    if (selectedDataWidget) {
                        selectedDataWidget.type = "hidden";
                        selectedDataWidget.computeSize = () => [0, -4]; // 隐藏widget
                        console.log("已隐藏 selected_data widget");
                    }
                }, 100);
                
                const language = localStorage['AGL.Locale'] || localStorage['Comfy.Settings.AGL.Locale'] || 'zh-CN';
                const list = $el("ul.anime-character-list", []);
                let selector = this.addDOMWidget('select_characters', "btn", $el('div.anime-character-selector', [
                    $el('div.tools', [
                        $el('button.delete', {
                            textContent: '清空选择',
                            onclick: () => {
                                selector.element.querySelectorAll(".anime-character-tag-selected").forEach(el => {
                                    el.classList.remove("anime-character-tag-selected");
                                    el.children[0].checked = false;
                                });
                                
                                // 清空 selected_data widget
                                const selectedDataWidget = this.widgets.find(w => w.name === "selected_data");
                                if (selectedDataWidget) {
                                    selectedDataWidget.value = "[]";
                                    console.log("已清空 selected_data widget");
                                    
                                    // 标记节点需要重新执行
                                    this.setDirtyCanvas(true, true);
                                }
                            }
                        }),
                        $el('input', {
                            className: "search",
                            placeholder: "🔎 输入关键词搜索动漫人物 ...",
                            oninput: async (e) => {
                                let value = e.target.value;
                                const data = await getAnimeCharacters(value, "");
                                list.innerHTML = '';
                                list.append(...getCharacterTagList(this, data, language));
                            }
                        })
                    ]),
                    list
                ]));

                // 初始化加载
                getAnimeCharacters().then(data => {
                    list.append(...getCharacterTagList(this, data, language));
                });

                // 可选：多选回填逻辑
            }
        }
    }
});