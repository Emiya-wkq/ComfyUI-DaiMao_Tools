import { app } from "../../../../scripts/app.js";
import { api } from "../../../../scripts/api.js";
import { $el } from "../../../../scripts/ui.js";

// 加载CSS样式
function loadCSS() {
    const cssPath = "./extensions/ComfyUI-DaiMao_Tools/css/anime_name_helper.css";
    if (!document.querySelector(`link[href="${cssPath}"]`)) {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.type = "text/css";
        link.href = cssPath;
        document.head.appendChild(link);
    }
}

// 立即加载CSS
loadCSS();

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

// 按作品分组角色数据
function groupCharactersByAnime(characters, language = 'zh-CN') {
    const groups = {};
    characters.forEach(character => {
        const animeKey = language === 'zh-CN' ? character.anime_chinese_name : character.anime_english_name;
        if (!groups[animeKey]) {
            groups[animeKey] = {
                anime_chinese_name: character.anime_chinese_name,
                anime_english_name: character.anime_english_name,
                characters: []
            };
        }
        groups[animeKey].characters.push(character);
    });
    return groups;
}

// 渲染单个角色标签
function createCharacterTag(node, character, language = 'zh-CN') {
    const name = language === 'zh-CN' ? character.character_chinese_name : character.character_english_name;
    
    return $el(
        "label.anime-character-tag",
        {
            dataset: {
                name: name,
                englishName: character.character_english_name,
                chineseName: character.character_chinese_name,
                animeEnglishName: character.anime_english_name,
                animeChineseName: character.anime_chinese_name,
                gender: character.gender,
                role: character.role
            },
            $: (el) => {
                el.onclick = (e) => {
                    e.preventDefault(); // 阻止默认的 label 行为
                    
                    el.classList.toggle("anime-character-tag-selected");
                    const checkbox = el.querySelector('input[type="checkbox"]');
                    if (checkbox) {
                        checkbox.checked = el.classList.contains("anime-character-tag-selected");
                    }
                    
                    // 获取所有已选角色的完整信息
                    let selected = Array.from(document.querySelectorAll(".anime-character-tag-selected"))
                        .map(tag => ({
                            character_english_name: tag.dataset.englishName,
                            character_chinese_name: tag.dataset.chineseName,
                            anime_english_name: tag.dataset.animeEnglishName,
                            anime_chinese_name: tag.dataset.animeChineseName,
                            gender: tag.dataset.gender,
                            role: tag.dataset.role
                        }));
                    
                    // 找到 selected_data widget 并更新值
                    const selectedDataWidget = node.widgets.find(w => w.name === "selected_data");
                    if (selectedDataWidget) {
                        selectedDataWidget.value = JSON.stringify(selected);
                        
                        // 标记节点需要重新执行
                        node.setDirtyCanvas(true, true);
                    } else {
                        console.error("未找到 selected_data widget");
                    }
                };
            },
        },
        [
            $el("input", {
                type: 'checkbox',
                name: name,
                $: (checkbox) => {
                    // 阻止复选框的点击事件冒泡，避免重复触发
                    checkbox.onclick = (e) => {
                        e.stopPropagation();
                    };
                }
            }),
            $el("span.character-name", {
                textContent: name
            }),
            $el("span.character-info", {
                textContent: `【${character.gender}·${character.role}】`
            })
        ]
    );
}

// 渲染作品分组列表
function getGroupedCharacterList(node, characters, language = 'zh-CN') {
    const groups = groupCharactersByAnime(characters, language);
    const groupElements = [];
    
    // 按作品名排序
    const sortedAnimes = Object.keys(groups).sort();
    
    sortedAnimes.forEach(animeKey => {
        const group = groups[animeKey];
        const animeDisplayName = language === 'zh-CN' ? group.anime_chinese_name : group.anime_english_name;
        
        // 创建角色容器
        const charactersContainer = $el("div.anime-characters-container");
        
        // 添加该作品的所有角色
        group.characters.forEach(character => {
            const characterTag = createCharacterTag(node, character, language);
            charactersContainer.appendChild(characterTag);
        });
        
        // 创建作品标题（可点击折叠/展开）
        const animeHeader = $el("div.anime-group-header", {
            $: (el) => {
                el.onclick = () => {
                    const isCollapsed = charactersContainer.classList.contains('collapsed');
                    
                    if (isCollapsed) {
                        charactersContainer.classList.remove('collapsed');
                    } else {
                        charactersContainer.classList.add('collapsed');
                    }
                    
                    // 更新箭头图标
                    const arrow = el.querySelector('.collapse-arrow');
                    if (arrow) {
                        arrow.textContent = isCollapsed ? '▼' : '▶';
                    }
                };
            }
        }, [
            $el("span", [
                $el("span.collapse-arrow", {
                    textContent: '▼',
                    style: { marginRight: '8px', fontSize: '12px' }
                }),
                $el("span", {
                    textContent: `📺 ${animeDisplayName} (${group.characters.length}人)`
                })
            ])
        ]);
        
        // 创建作品组容器
        const animeGroup = $el("div.anime-group", [animeHeader, charactersContainer]);
        
        groupElements.push(animeGroup);
    });
    
    return groupElements;
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
                        
                    }
                }, 100);
                
                const language = localStorage['AGL.Locale'] || localStorage['Comfy.Settings.AGL.Locale'] || 'zh-CN';
                const list = $el("div.anime-character-list");
                
                let selector = this.addDOMWidget('select_characters', "btn", $el('div.anime-character-selector', [
                    $el('div.tools', [
                        $el('button.delete', {
                            textContent: '清空选择',
                            onclick: () => {
                                document.querySelectorAll(".anime-character-tag-selected").forEach(el => {
                                    el.classList.remove("anime-character-tag-selected");
                                    const checkbox = el.querySelector('input[type="checkbox"]');
                                    if (checkbox) {
                                        checkbox.checked = false;
                                    }
                                });
                                
                                // 清空 selected_data widget
                                const selectedDataWidget = this.widgets.find(w => w.name === "selected_data");
                                if (selectedDataWidget) {
                                    selectedDataWidget.value = "[]";
                                    
                                    // 标记节点需要重新执行
                                    this.setDirtyCanvas(true, true);
                                }
                            }
                        }),
                        $el('input.search', {
                            placeholder: "🔎 输入关键词搜索动漫人物 ...",
                            oninput: async (e) => {
                                let value = e.target.value;
                                const data = await getAnimeCharacters(value, "");
                                list.innerHTML = '';
                                const groupedElements = getGroupedCharacterList(this, data, language);
                                list.append(...groupedElements);
                            }
                        })
                    ]),
                    list
                ]));

                // 初始化加载
                getAnimeCharacters().then(data => {
                    const groupedElements = getGroupedCharacterList(this, data, language);
                    list.append(...groupedElements);
                });

                // 可选：多选回填逻辑
            }
        }
    }
});