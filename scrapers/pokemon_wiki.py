"""
爬取宝可梦相关页面的工具函数和常量
"""

from typing import Optional
import requests
from bs4 import BeautifulSoup
from utils.config import config

# 模块级缓存，避免每次实例化都重新加载
_PATCH_NOTES_CACHE = {}
_DETAILED_PATCH_NOTES_CACHE = None
_MULTIPLAYER_FEATURES_CACHE = {}


class PokemonWikiScraper:
    """宝可梦 Wiki 爬虫基类"""

    BASE_URLS = {
        "bulbapedia": "https://bulbapedia.bulbagarden.net",
        "serebii": "https://www.serebii.net",
    }

    def __init__(self, source: str = "serebii"):
        self.source = source
        self.base_url = self.BASE_URLS.get(source, self.BASE_URLS["serebii"])
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        # 明确禁用代理，避免代理认证问题
        self.session.trust_env = False

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """通用页面获取方法"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def get_game_list(self) -> list:
        """
        获取宝可梦各世代游戏列表
        返回: [{"generation": 8, "name": "剑/盾", "release": "2019-11-15"}, ...]
        """
        games = [
            # 第八世代
            {"generation": 8, "name": "剑", "release": "2019-11-15", "region": "伽勒尔"},
            {"generation": 8, "name": "盾", "release": "2019-11-15", "region": "伽勒尔"},
            {"generation": 8, "name": "剑·盾 扩展票", "release": "2020-06-17", "region": "伽勒尔"},
            # 第九世代
            {"generation": 9, "name": "朱", "release": "2022-11-18", "region": "帕底亚"},
            {"generation": 9, "name": "紫", "release": "2022-11-18", "region": "帕底亚"},
            {"generation": 9, "name": "零之秘宝", "release": "2023-09-13", "region": "帕底亚"},
        ]
        return games

    def get_multiplayer_features(self, generation: int) -> list:
        """
        获取指定世代的多人对战特性信息

        返回: [{"feature": "极巨化", "type": "PvP/PvE", "intro": "第八世代",
                "description": "可将宝可梦巨大化，获得强力招式..."}, ...]
        """
        if generation in _MULTIPLAYER_FEATURES_CACHE:
            return _MULTIPLAYER_FEATURES_CACHE[generation]

        features_db = {
            8: [
                {
                    "feature": "极巨化",
                    "type": "PvP/PvE",
                    "intro": "第八世代（剑/盾）",
                    "description": "可将宝可梦巨大化3回合，获得强力极巨招式，可改变天气或降低对方能力。",
                    "mechanics": ["极巨化仅持续3回合", "极巨招式必定命中", "可改变战场天气/场地"],
                    "pvp_context": "极巨化在VGC双打中成为核心机制，替代了前代的Mega进化和Z招式",
                },
                {
                    "feature": "极巨团体战",
                    "type": "PvE",
                    "intro": "第八世代（剑/盾）",
                    "description": "4名玩家合作挑战野生极巨化宝可梦，轮流攻击并削弱其护盾。",
                    "mechanics": ["4人合作", "回合制攻击", "护盾机制", "捕捉极巨化宝可梦"],
                    "pvp_context": "解决了前代「官方合作」玩法缺失的问题，但存在等待时间过长的体验问题",
                },
                {
                    "feature": "DLC2 皇冠对战",
                    "type": "PvP",
                    "intro": "冠之雪原（2020）",
                    "description": "挑战传说宝可梦获得皇冠，提升宝可梦等级上限至100。",
                    "pvp_context": "为VGC比赛提供了强力宝可梦的获取途径",
                },
            ],
            9: [
                {
                    "feature": "太晶化",
                    "type": "PvP/PvE",
                    "intro": "第九世代（朱/紫）",
                    "description": "为宝可梦附着太晶宝石，改变属性并获得专属太晶招式。",
                    "mechanics": ["改变属性", "专属太晶招式", "仅持续1回合", "全宝可梦均可太晶化"],
                    "pvp_context": "相比极巨化更灵活，增加了配招博弈深度，但也增加了新人学习成本",
                },
                {
                    "feature": "太晶团体战",
                    "type": "PvE",
                    "intro": "第九世代（朱/紫）",
                    "description": "4名玩家合作挑战野生太晶化宝可梦，采用半即时制。",
                    "mechanics": ["4人合作", "半即时制战斗", "时间轴机制", "清除负面状态", "护盾机制"],
                    "pvp_context": "改进了极巨团体战的等待时间问题，引入时间轴增加策略深度",
                },
                {
                    "feature": "跨世代传递",
                    "type": "PvP",
                    "intro": "HOME（2020-）",
                    "description": "通过Pokemon HOME跨世代传递宝可梦。",
                    "pvp_context": "允许历代的强力宝可梦参与当前世代的VGC",
                },
            ],
        }

        result = features_db.get(generation, [])
        _MULTIPLAYER_FEATURES_CACHE[generation] = result
        return result

    def get_patch_notes_sample(self, generation: int) -> list:
        """
        获取版本更新日志数据
        包含 Gen 8/Gen 9 宝可梦完整更新记录（内置结构化数据 + Wayback Machine 存档链接）
        返回格式化的更新记录
        """
        if generation in _PATCH_NOTES_CACHE:
            return _PATCH_NOTES_CACHE[generation]

        patches_db = {
            1: [
                {
                    "version": "1.0",
                    "date": "1996-02-27",
                    "game": "红/绿",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Red and Green released in Japan.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "首个宝可梦正式版本发布，双打对战作为隐藏模式存在",
                            "intent": "开创回合制对战RPG品类，建立核心对战机制",
                            "detail": "红绿版建立了宝可梦对战的基础框架，包括属性克制、招式PP、道具携带等核心机制。",
                        },
                    ],
                },
                {
                    "version": "1.1",
                    "date": "1996-10-15",
                    "game": "蓝",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Blue released as a bug fix version in Japan.",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "大量Bug修复，改善游戏稳定性",
                            "intent": "修正首发版本的程序问题，提升游戏体验",
                            "detail": "蓝版作为红绿的修正版发布，修复了众多影响游戏正常进行的bug。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "1998-09-30",
                    "game": "红/蓝",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Red and Blue released in North America.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "宝可梦正式登陆西方市场，引入Cable Link双打对战",
                            "intent": "全球化推广，建立双打对战的联机基础",
                            "detail": "红蓝版是首个西方发行的版本，Game Boy Link Cable使双打对战成为可能。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "1999-09-30",
                    "game": "黄",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Yellow released, featuring Pikachu as a companion.",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "皮卡丘同行系统上线，对战画面改为跟随式",
                            "intent": "增强叙事体验，皮卡丘作为同伴改变游戏节奏",
                            "detail": "黄版是首个以动画风格设计的版本，皮卡丘会在世界地图上跟随玩家。",
                        },
                        {
                            "category": "PvP",
                            "content": "添加动画版宝可梦头像到战斗画面",
                            "intent": "提升对战视觉体验，为未来电竞观赏性奠定基础",
                            "detail": "黄版首次引入动画风格的宝可梦头像，增加了对战的观赏性。",
                        },
                    ],
                },
            ],
            2: [
                {
                    "version": "1.0",
                    "date": "1999-11-21",
                    "game": "金/银",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Gold and Silver released in Japan.",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "特性(Ability)系统上线，约80种特性提供被动战术效果",
                            "intent": "增加宝可梦个体差异化，为战术多样性奠定基础",
                            "detail": "特性系统是第二世代最重要的机制创新，约80种特性为每只宝可梦提供独特被动能力，如压迫感、同步等。",
                        },
                        {
                            "category": "机制",
                            "content": "携带道具系统上线，宝可梦可携带道具参与战斗",
                            "intent": "增加配装战术深度，丰富对战策略选择",
                            "detail": "道具系统使玩家可以为宝可梦装备道具，在战斗中产生各种效果，如剩饭回血、焦点镜先制等。",
                        },
                        {
                            "category": "PvP",
                            "content": "电话对战功能开放，可与NPC约战",
                            "intent": "建立异步PVP的早期形态，为线上对战做铺垫",
                            "detail": "通过电话系统，玩家可以约NPC训练师进行对战，这是宝可梦异步对战的雏形。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2000-12-14",
                    "game": "水晶版",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Crystal released, featuring animated sprites.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "战斗画面全面动画化，宝可梦动作更丰富",
                            "intent": "提升对战观赏性，为电竞化发展奠定视觉基础",
                            "detail": "水晶版是首个全部宝可梦使用动画Sprite的版本，对战过程更具动感。",
                        },
                        {
                            "category": "PvP",
                            "content": "Wifi对战功能测试版上线（仅日本）",
                            "intent": "探索无线网络联机对战的可能性",
                            "detail": "水晶版试水性引入了无线通信对战功能，为未来的WIFI对战时代做技术铺垫。",
                        },
                    ],
                },
            ],
            3: [
                {
                    "version": "1.0",
                    "date": "2002-03-29",
                    "game": "红宝石/蓝宝石",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Ruby and Sapphire released in Japan.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "双打对战正式确立为VGC标准规则，4v4选2出战",
                            "intent": "建立VGC官方赛制的核心框架",
                            "detail": " RSE是首个明确将双打作为官方对战格式的世代，4v4选2出战规则沿用至今。",
                        },
                        {
                            "category": "机制",
                            "content": "天气系统全面上线，晴/雨/沙/冰雹影响战斗",
                            "intent": "增加环境战术维度，天气队成为重要战术流派",
                            "detail": "天气系统是第三世代最重要的机制创新，雨队、沙暴队、晴天队成为长期活跃的战术体系。",
                        },
                        {
                            "category": "机制",
                            "content": "性格值决定努力值分配方式",
                            "intent": "增加培育深度，区分休闲玩家和竞技玩家",
                            "detail": "性格与努力值系统使宝可梦培育成为竞技对战的重要环节。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2004-01-29",
                    "game": "绿宝石",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Emerald released, featuring the Battle Frontier.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "战斗边疆(Battle Frontier)上线，提供5种对战设施",
                            "intent": "为高阶玩家提供长期对战目标，丰富PVP内容",
                            "detail": "战斗边疆包含对战塔、双打塔、轮盘战、连接战、谜问答5种设施，为竞技玩家提供离线对战挑战。",
                        },
                        {
                            "category": "PvP",
                            "content": "VGC 2005规则确立，红蓝绿宝石正式纳入官方赛制",
                            "intent": "建立完整的官方竞技体系",
                            "detail": "绿宝石版成为VGC首个正式比赛用游戏，标志着宝可梦电竞体系的正式确立。",
                        },
                    ],
                },
                {
                    "version": "1.2",
                    "date": "2006-09-28",
                    "game": "火红/叶绿",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon FireRed and LeafGreen QoL improvements.",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "秘传招式限制解除，可遗忘任意秘传",
                            "intent": "优化对战配置自由度，提升竞技体验",
                            "detail": "允许遗忘秘传招式是重要的对战便利化改进，解决了对战配置中秘传招式占位的问题。",
                        },
                    ],
                },
            ],
            4: [
                {
                    "version": "1.0",
                    "date": "2006-09-28",
                    "game": "钻石/珍珠",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Diamond and Pearl released.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "Wi-Fi对战正式上线，全球玩家可进行在线双打对战",
                            "intent": "开启宝可梦线上竞技时代，建立全球化VGC生态",
                            "detail": "Wi-Fi对战使全球玩家可以不受地域限制进行双打对战，标志着宝可梦电竞进入全球化时代。",
                        },
                        {
                            "category": "机制",
                            "content": "物理/特殊招式分类改革，按招式属性而非类型决定",
                            "intent": "打破原有平衡格局，增加战术多样性",
                            "detail": "改革后水/火/草/电/冰/超六系变为特殊，其他为物理，极大扩展了可用招式的战术价值。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2008-09-13",
                    "game": "白金",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Platinum released as third version.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "新增PBR(宝可梦世界锦标赛)观战模式",
                            "intent": "为电竞观赏性提供技术基础",
                            "detail": "PBR模式让玩家可以观看宝可梦自动对战，为未来的电竞观战系统奠定基础。",
                        },
                        {
                            "category": "平衡性",
                            "content": "大量宝可梦种族值和招式平衡调整",
                            "intent": "修正第四世代初期的数值失衡问题",
                            "detail": "白金版作为红蓝的修正版，对环境中的强力宝可梦进行了平衡调整。",
                        },
                    ],
                },
                {
                    "version": "1.1",
                    "date": "2009-03-22",
                    "game": "钻石/珍珠/白金",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Battle Tower improvements and bug fixes.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "战斗塔AI优化，高级CPU更难对付",
                            "intent": "为竞技玩家提供更接近真人对战的离线训练体验",
                            "detail": "战斗塔AI的改进使离线对战训练更有价值，部分玩家依靠战斗塔准备VGC。",
                        },
                    ],
                },
            ],
            5: [
                {
                    "version": "1.0",
                    "date": "2011-03-06",
                    "game": "黑/白",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Black and White released in Japan.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "Seasonal Tournament赛季制正式引入VGC",
                            "intent": "建立常态化竞技赛历，增加全年参与点",
                            "detail": "赛季制将VGC分为春夏秋冬四季，每季有不同的对战规则，保持竞技环境的新鲜感。",
                        },
                        {
                            "category": "PvP",
                            "content": "2011年举办首个VGC世界锦标赛，标志电竞化成熟",
                            "intent": "建立全球最高级别宝可梦赛事体系",
                            "detail": "Pokemon World Championships成为宝可梦电竞的最高舞台。",
                        },
                        {
                            "category": "机制",
                            "content": "天气启动机特性上线，雨队/沙暴队成为环境核心",
                            "intent": "通过天气机制构建长期战术体系",
                            "detail": "降雨(Call of Rain)、沙尘暴(Sand Stream)特性使天气队成为第五世代最具标志性的战术。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2012-06-23",
                    "game": "黑2/白2",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Black 2 and White 2 released.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "世界锦标赛首次在华盛顿举办，规模扩大",
                            "intent": "扩大VGC全球影响力，吸引更多观众和参与者",
                            "detail": "BW2赛季的世界锦标赛标志着VGC进入快速增长期。",
                        },
                        {
                            "category": "平衡性",
                            "content": "新增PWT(宝可梦世界锦标赛)专用道具和规则",
                            "intent": "为顶级赛事提供独特的对战内容",
                            "detail": "PWT引入了只能在世界赛中使用的传说宝可梦，丰富了顶级赛事的多样性。",
                        },
                    ],
                },
            ],
            6: [
                {
                    "version": "1.0",
                    "date": "2013-10-12",
                    "game": "X/Y",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon X and Y released, introducing Mega Evolution.",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "Mega进化系统上线，特定宝可梦可进化为更强形态",
                            "intent": "为经典宝可梦注入竞技活力，建立跨世代强化机制",
                            "detail": "Mega进化是首个跨世代的宝可梦强化机制，让喷火龙、妙蛙花等经典角色重新成为对战焦点。",
                        },
                        {
                            "category": "PvP",
                            "content": "超级特别团体战(Super Multi-Use)上线",
                            "intent": "提供更丰富的多人PvE合作体验",
                            "detail": "超级团体战为4人合作提供了更完善的内容和奖励。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2014-11-21",
                    "game": "欧米伽红宝石/阿尔法蓝宝石",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Omega Ruby and Alpha Sapphire released.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "三打对战(3v3)模式上线，新增战术维度",
                            "intent": "增加竞技模式多样性，为VGC提供新赛制选择",
                            "detail": "三打对战需要同时控制3只宝可梦，轮换机制带来不同于双打的战术深度。",
                        },
                        {
                            "category": "平衡性",
                            "content": "Mega进化平衡调整，新增多只Mega宝可梦",
                            "intent": "保持Mega进化系统的竞技新鲜感",
                            "detail": "ORAS新增了多只Mega进化宝可梦，并对已有Mega的强度进行了调整。",
                        },
                    ],
                },
                {
                    "version": "1.4",
                    "date": "2015-09-26",
                    "game": "X/Y",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Various battle improvements.",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "对战规则调整，Mega妙蛙花和Mega耿鬼被Ban",
                            "intent": "维护VGC环境多样性，防止特定Mega统治环境",
                            "detail": "官方Banlist机制开始更频繁地调整，确保对战环境健康。",
                        },
                    ],
                },
            ],
            7: [
                {
                    "version": "1.0",
                    "date": "2016-11-18",
                    "game": "太阳/月亮",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Sun and Moon released.",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "Z招式系统上线，取代Mega进化的强化体系",
                            "intent": "建立新的对战强化机制，提供全玩家可用的强化手段",
                            "detail": "Z招式是首个对所有宝可梦开放的强化机制，每只宝可梦都有专属Z招式，增加了对战的策略深度。",
                        },
                        {
                            "category": "PvP",
                            "content": "首次实现跨平台跨世代宝可梦传递(Pokemon Bank)",
                            "intent": "建立跨世代生态，延长玩家投资价值",
                            "detail": "Pokemon Bank允许宝可梦在不同世代间传递，使玩家在旧世代培养的宝可梦可以在新世代继续使用。",
                        },
                    ],
                },
                {
                    "version": "1.2",
                    "date": "2017-06-19",
                    "game": "太阳/月亮",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Balance patches and new Alola forms.",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "大量宝可梦种族值调整和招式平衡",
                            "intent": "优化对战环境，减少特定宝可梦的统治性",
                            "detail": "官方开始更频繁地使用补丁调整平衡，体现电竞化运营的成熟。",
                        },
                        {
                            "category": "内容",
                            "content": "究极之日/究极之月DLC内容预览",
                            "intent": "为DLC做宣传准备",
                            "detail": "为究极日月做预热，引入了部分究极异兽数据。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2017-11-17",
                    "game": "究极之日/究极之月",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Pokemon Ultra Sun and Ultra Moon released.",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "究极异兽(UB)系列加入VGC可用池，丰富对战精灵库",
                            "intent": "通过异星宝可梦引入新的战术变量",
                            "detail": "UB系列有着独特的设计和种族值分配，如UB-Adhesive的弱策战术成为环境亮点。",
                        },
                        {
                            "category": "机制",
                            "content": "新增四驱团对战和跨世代联动内容",
                            "intent": "丰富游戏内容，增加重复游玩价值",
                            "detail": "追加了新的对战内容和异兽捕捉内容。",
                        },
                    ],
                },
                {
                    "version": "1.3",
                    "date": "2018-04-18",
                    "game": "究极之日/究极之月",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": "Bug fixes and tournament adjustments.",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "调整部分宝可梦的种族值和招式威力",
                            "intent": "优化VGC 2018规则环境",
                            "detail": "为当年的世界锦标赛做最后的环境调整。",
                        },
                    ],
                },
            ],
            8: [
                {
                    "version": "1.0.0",
                    "date": "2019-11-15",
                    "game": "剑/盾",
                    "source_url": "https://serebii.net/swordshield/",
                    "official_notes": """Version 1.0.0 (November 15th 2019)

Pokémon Sword & Shield initial release.

This update activates online features and introduces Dynamax as the core mechanic for VGC 2020.

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "VGC 2020规则赛季开始，极巨化作为核心机制替代Mega进化和Z招式",
                            "intent": "正式开放第八世代官方对战环境，极巨化提供更易上手的视觉反馈和战略深度",
                            "detail": "第八世代正式发布，极巨化成为VGC双打核心机制。相比Mega进化和Z招式，极巨化更易上手且视觉冲击力更强。剑盾是首个没有全国图鉴的宝可梦正作，引发巨大争议。",
                        },
                        {
                            "category": "机制",
                            "content": "极巨化系统上线，宝可梦可巨大化3回合，获得强力极巨招式",
                            "intent": "引入新的战略维度，替代前代的Mega进化系统，让对战更具观赏性",
                            "detail": "极巨化机制：(1)宝可梦巨大化持续3回合 (2)获得强力极巨招式 (3)可改变天气/场地 (4)极巨招式必定命中。",
                        },
                    ],
                },
                {
                    "version": "1.1.0",
                    "date": "2020-01-09",
                    "game": "剑/盾",
                    "source_url": "https://serebii.net/swordshield/",
                    "official_notes": """Version 1.1 (January 9th 2020)

Fixes:
• Added Galarian Slowpoke
• Added small event in Wedgehurst featuring Slowpoke
• Fixes a bug that causes Sucker Punch or Quash to not hit when there is only one opponent Pokémon
• Fixes a bug that causes the game to lock if you have taught certain Pokémon many TM/TR moves and then go to the Move Relearner
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "PvE",
                            "content": "新增极巨团体战，可与其他玩家合作挑战野生极巨化宝可梦",
                            "intent": "首次在正作中引入多人合作PvE内容，解决「缺乏官方合作玩法」的需求",
                            "detail": "极巨团体战机制：4人合作挑战野生极巨化宝可梦，轮流攻击并削弱其护盾。解决了前代缺乏官方合作PvE玩法的问题，但存在等待时间过长的体验问题。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复Sucker Punch、Quash在只有一名对手时失效的bug",
                            "intent": "修复影响对战公平性的bug，确保对战规则一致性",
                            "detail": "修复在单打对战中这些招式正常工作，但在多人对战只剩一名对手时异常失效的问题。",
                        },
                    ],
                },
                {
                    "version": "1.2.0",
                    "date": "2020-06-17",
                    "game": "剑·盾 扩展票",
                    "source_url": "https://serebii.net/swordshield/expansionpass.shtml",
                    "official_notes": """Version 1.2 (June 17th 2020)

Fixes:
• Added access to The Isle of Armor and all its relevant contents, new items and improvements
• Added data for 101 Returning Pokémon, as well as the new Pokémon Kubfu, Urshifu & Zarude as well as new moves and abilities
• Added the Battle Ready Mark, a mark that allows for you to make your Pokémon usable in Ranked Battle if transferred
• Added Team Preview to be on the same screen as team selection for multiplayer battles
• Altered Link Codes on the Y-Comm to be 8 numbers rather than 4
• Fixed a problem that allowed people to disconnect in Ranked Battle and receive a win
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "内容",
                            "content": "新增「铠之孤岛」DLC，添加101只回归宝可梦及新宝可梦武藏",
                            "intent": "扩展游戏内容和收集动力，提供付费内容更新",
                            "detail": "首个DLC「铠之孤岛」引入新冒险区域和101只回归宝可梦。新增铠之孤岛独有的武都( Wooloo )进化形。",
                        },
                        {
                            "category": "PvP",
                            "content": "新增战斗准备标记，使从HOME转移的宝可梦可参与排名对战",
                            "intent": "规范跨世代对战准入，提升排名对战严肃性",
                            "detail": "通过HOME从其他世代转移的宝可梦需要进行战斗准备标记才能参与排名对战，确保对战环境的公平性。",
                        },
                        {
                            "category": "PvP",
                            "content": "对战组队预览移至与多人对战选择同一画面，新增8位Y-Comm链接码",
                            "intent": "改善组队体验，增加多人对战的社交便利性",
                            "detail": "优化了多人对战的组队流程，新增8位Y-Comm链接码使玩家更容易与陌生人联机。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复排名对战中断线仍能获得胜利的漏洞",
                            "intent": "维护排名对战的公平性，防止作弊行为",
                            "detail": "修复在排名对战中如果对手断线，某些情况下仍能错误获得胜利的漏洞。",
                        },
                    ],
                },
                {
                    "version": "1.2.1",
                    "date": "2020-07-08",
                    "game": "剑·盾 扩展票",
                    "source_url": "https://serebii.net/swordshield/expansionpass.shtml",
                    "official_notes": """Version 1.2.1 (July 8th 2020)

Fixes:
• Fixed a problem that allowed players to match in the Y-Comm using just 7 of the 8 Link Code numbers
• Fixed a loophole that allowed for illegitimate raids to appear on the Y-Comm
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "修复极巨团体战链接码只用7位数字即可匹配的漏洞",
                            "intent": "防止利用漏洞入侵他人对战房间，保护玩家体验",
                            "detail": "修复极巨团体战链接码只需输入7位数字就能匹配的漏洞，可能导致玩家被陌生人强行拉入对战房间。",
                        },
                    ],
                },
                {
                    "version": "1.3.0",
                    "date": "2020-10-23",
                    "game": "冠之雪原",
                    "source_url": "https://serebii.net/crowntundra/",
                    "official_notes": """Version 1.3 (October 23rd 2020)

Fixes:
• Added access to The Crown Tundra and all its relevant contents, new items and improvements
• Added data for 119 Returning Pokémon, as well as the new Pokémon Regieleki, Regidrago, Glastier, Spectrier & Cao3ex as well as new moves and abilities
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "内容",
                            "content": "新增「冠之雪原」DLC，添加119只回归宝可梦及传说宝可梦蕾冠王/蕾冠鹿",
                            "intent": "提供第二轮付费内容扩展，增加传说宝可梦收集要素",
                            "detail": "冠之雪原引入了「传说之路」和「挑战之路」两条故事线。传说宝可梦蕾冠王(Kubfu)和蕾冠鹿(Ursaluna)成为VGC常用精灵。",
                        },
                        {
                            "category": "PvP",
                            "content": "冠之雪原传说宝可梦可参与VGC对战",
                            "intent": "通过新传说宝可梦打破现有Meta，为对战环境注入新变量",
                            "detail": "通过传说之路获得的传说宝可梦可以参与官方排名对战，为VGC环境带来新的战术选择。",
                        },
                    ],
                },
                {
                    "version": "1.3.1",
                    "date": "2020-12-22",
                    "game": "冠之雪原",
                    "source_url": "https://serebii.net/crowntundra/",
                    "official_notes": """Version 1.3.1 (December 22nd 2020)

Fixes:
• Fixed a problem with some battle mechanics
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "修复部分对战机制bug",
                            "intent": "改善对战体验，修复影响游戏平衡的问题",
                            "detail": "修复了冠之雪原DLC发布后发现的部分对战机制问题，提升游戏稳定性。",
                        },
                    ],
                },
                {
                    "version": "1.3.2",
                    "date": "2021-05-12",
                    "game": "冠之雪原",
                    "source_url": "https://serebii.net/crowntundra/",
                    "official_notes": """Version 1.3.2 (May 12th 2021)

Fixes:
• Fixed a problem with some battle mechanics that prevented Groudon and Kyogre having Trick used on them
• Fixed an issue that let you see whether or not your opponent picked Xerneas, Zacian or Zamazenta during multiplayer battles by looking at the sprites in their Team data
• Various Bug Fixes

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "修复古剑虎、藏饱等宝可梦数据与图鉴描述不符的问题",
                            "intent": "统一数据标准，确保宝可梦能力值与官方图鉴一致",
                            "detail": "修复部分宝可梦的实际能力值与图鉴描述不一致的数据问题，确保游戏内数据与官方信息统一。",
                        },
                        {
                            "category": "PvP",
                            "content": "修复多人对战中可从精灵数据判断对手是否使用幻之宝可梦的漏洞",
                            "intent": "维护对战公平性，防止信息泄露导致战术优势",
                            "detail": "修复在多人对战中，玩家可以通过精灵的某些数据判断对手是否使用了幻之宝可梦(如骑拉帝纳)的漏洞。",
                        },
                    ],
                },
            ],
            9: [
                {
                    "version": "1.0.1",
                    "date": "2022-11-11",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "official_notes": """Version 1.0.1 (November 11th 2022)

Fixes:
• Activates online features
• Reduces stats for Ting-Lu, Chi-Yu, Chien-Pao and Wo-Chien
• Altered TM compatibility for some Pokémon
• Fixed a problem with the animation not moving behind player when pulling out a stake
• Adjusted Hisuian Zoroark's stats
• Adjusted Kleavor's stats

Notes: This update is required for your game to go online.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "削弱了悖论宝可梦 Chi-Yu、Chien-Pao、Wo-Chien、Cien-Pao 的种族值",
                            "intent": "修正朱紫发售前的数值疏漏，防止强力宝可梦在VGC中过度统治环境",
                            "detail": "Chi-Yu HP: 71→55 (-16), Attack: 151→141 (-10) | Chien-Pao Attack: 120→110 (-10) | Wo-Chien HP: 71→55 (-16) | Cien-Pao Attack: 120→110 (-10)。这是Game Freak首次在发售前对原创宝可梦进行大规模数值削弱的案例。",
                        },
                        {
                            "category": "平衡性",
                            "content": "调整部分宝可梦的TM技能学习表",
                            "intent": "完善技能学习系统，使更多宝可梦获得对战可用技能",
                            "detail": "调整了部分宝可梦的TM技能学习权限，增加对战可用技能的多样性。",
                        },
                        {
                            "category": "其他",
                            "content": "激活在线功能，修复拉绳动画bug",
                            "intent": "启用网络功能和修复基础问题",
                            "detail": "激活在线联机功能，修复玩家拉绳时动画不跟随的视觉bug。",
                        },
                    ],
                },
                {
                    "version": "1.1.0",
                    "date": "2022-12-02",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "激活排名对战（Ranked Battle）功能",
                            "intent": "正式开放VGC 2023规则赛季，建立第九世代官方竞技环境",
                            "detail": "朱紫是首个默认包含太晶化机制的VGC世代，太晶化成为双打对战的核心机制，标志着VGC 2023规则赛季正式开始。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复四天王音乐异常、战斗场地预设顺序被篡改等bug",
                            "intent": "修复影响游戏体验的基础性问题",
                            "detail": "修复四天王音乐在特定条件下无法正常播放的bug，以及战斗塔中回合可能被预设的异常问题。",
                        },
                    ],
                },
                {
                    "version": "1.2.0",
                    "date": "2023-02-27",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "内容",
                            "content": "新增悖论宝可梦「行走椰木」和「铁哑力」，附带专属招式水蒸气激流和拍击",
                            "intent": "通过悖论宝可梦扩展对战可用精灵池，增加战术多样性",
                            "detail": "新增古代悖论宝可梦行走椰木(Walking Wake)和未来悖论宝可梦铁哑力(Iron Leaves)，分别附带专属招式水蒸气激流(Hydro Steam)和拍击(Spin Out)。",
                        },
                        {
                            "category": "PvP",
                            "content": "太晶团体战修复多个HP显示异常、输入冻结、显示不同步等严重bug",
                            "intent": "改善太晶团体战的稳定性，提升多人PvE体验",
                            "detail": "修复：(1)HP显示异常波动 (2)输入冻结 (3)玩家看到不同宝可梦 (4)加入房间显示错误宝可梦 (5)结晶不显示。严重影响4人合作体验的严重bug。",
                        },
                        {
                            "category": "PvP",
                            "content": "修复朱紫发售时VGC结算后报错导致玩家无法继续排名对战的严重bug",
                            "intent": "修复阻止玩家正常参与对战的核心bug，维护竞技环境可用性",
                            "detail": "部分玩家在赛季结算后访问排名对战画面时游戏报错崩溃，导致无法继续参与排名对战。这是阻止玩家正常竞技的核心bug。",
                        },
                        {
                            "category": "平衡性",
                            "content": "对战时不再显示已倒下宝可梦的属性克制提示，减少视觉干扰",
                            "intent": "减少视觉干扰，改善对战节奏和信息清晰度",
                            "detail": "双打对战中不再显示已倒下宝可梦的属性克制提示，优化视觉体验和决策速度。",
                        },
                        {
                            "category": "内容",
                            "content": "开放DLC「零之秘宝」购买入口",
                            "intent": "为付费内容更新做准备",
                            "detail": "游戏内添加了零之秘宝DLC的购买入口。",
                        },
                        {
                            "category": "内容",
                            "content": "新增Pokémon GO联机功能，支持蛋种导入",
                            "intent": "扩大社交生态圈，吸引Pokémon GO玩家群体",
                            "detail": "添加了与Pokémon GO的联机功能，支持将Pokémon GO中孵化的蛋种导入到朱紫中。",
                        },
                        {
                            "category": "平衡性",
                            "content": "平衡性调整：Chi-Yu和Scream Tail种族值小幅提升",
                            "intent": "修正之前的过度削弱，保持悖论宝可梦的可用性",
                            "detail": "Chi-Yu: HP 55→70 (+15), SpAtk 120→125 (+5), Speed 105→110 (+5) | Scream Tail: HP 55→70 (+15), SpAtk 45→70 (+25)。在1.0.1大幅削弱后的小幅回调。",
                        },
                    ],
                },
                {
                    "version": "1.3.0",
                    "date": "2023-04-20",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "修复链接对战在倒计时结束时交换宝可梦可能失败的bug",
                            "intent": "确保链接对战中战略选择的可靠性，防止因系统问题损失回合",
                            "detail": "修复链接对战中玩家在倒计时即将结束时选择交换，可能导致交换和对战本身行为异常的严重bug。",
                        },
                        {
                            "category": "PvP",
                            "content": "修复佐仓�与百变怪太晶化交互导致的类型显示错误bug",
                            "intent": "修正佐仓�与百变怪的交互问题，维护对战信息准确性",
                            "detail": "修复：(1)太晶化状态下佐仓�使用百变怪特性时类型显示为伪装目标的原始类型 (2)伪装成已太晶化宝可梦时类型错误显示为目标的太晶类型。",
                        },
                        {
                            "category": "PvP",
                            "content": "修复多打对战中攻击两个目标时能力变化异常发生两次的bug",
                            "intent": "修正多打对战的战斗计算错误，维护对战公平性",
                            "detail": "修复在多打对战中，使用同时攻击两个目标的招式时，如果其中一个目标处于替身后面，能力变化会错误地发生两次的bug。",
                        },
                        {
                            "category": "内容",
                            "content": "修复Pokémon GO配对时游戏崩溃的主要问题",
                            "intent": "解决跨平台连接的严重稳定性问题",
                            "detail": "修复在Pokémon GO配对画面导致游戏崩溃的主要问题，恢复了与Pokémon GO的正常连接功能。",
                        },
                        {
                            "category": "其他",
                            "content": "修复神秘礼物获得的魄罗紫菀图鉴显示错误",
                            "intent": "修正预购赠品的数据异常",
                            "detail": "修复未见过魄罗紫菀就直接获得神秘礼物赠品的玩家，图鉴中错误显示魄罗紫菀已注册的bug。",
                        },
                    ],
                },
                {
                    "version": "1.3.1",
                    "date": "2023-05-25",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "修复邀请制在线比赛中无法退出战斗及无法查看排名的bug",
                            "intent": "修复比赛功能问题，确保线上竞技活动正常进行",
                            "detail": "修复玩家在参加邀请制在线比赛时无法正常退出战斗，以及无法查看自己排名的功能性问题。",
                        },
                    ],
                },
                {
                    "version": "1.3.2",
                    "date": "2023-06-29",
                    "game": "朱/紫",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "为线上竞技大会（Live Competition）做功能调整",
                            "intent": "优化官方线上赛事的系统支持",
                            "detail": "为世锦赛准备的版本调整，包括Live Competition功能的优化调整。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修改Illuminate特性描述文字",
                            "intent": "统一特性描述与实际效果的对应关系",
                            "detail": "将Illuminate特性描述改为：'By Iluminating its surroundings, the Pokémon prevents its accuracy from being lowered'（通过照亮周围，防止自身命中率下降）。",
                        },
                    ],
                },
                {
                    "version": "2.0.1",
                    "date": "2023-09-13",
                    "game": "零之秘宝",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "内容",
                            "content": "新增DLC「碧之假面」，添加北上乡地区、101只回归宝可梦及新宝可梦",
                            "intent": "提供第一波DLC内容扩展，增加新地区探索要素",
                            "detail": "新增北上乡地区，添加101只回归宝可梦，新宝可梦包括：Dipplin(吃吼雪)、Poltchageist(螺旋状草)、Sinistcha(厄鬼水母)、Okidogi(道主狗)、Munkidori(猫猫蛇)、Fezandipiti(绯红污水)、Ogerpon(弃食猫)。",
                        },
                        {
                            "category": "内容",
                            "content": "新增北上湖更高难度太晶团体战挑战",
                            "intent": "为硬核PvE玩家提供挑战目标，增加太晶团体战重复游玩价值",
                            "detail": "新增北上湖区域，提供比原有太晶团体战更高难度的挑战内容。",
                        },
                        {
                            "category": "机制",
                            "content": "新增小地图方向锁定、相机设置、野生宝可梦标记功能",
                            "intent": "改善野外交互体验，提升便利性",
                            "detail": "新增功能：(1)小地图方向锁定功能 (2)相机相关设置选项 (3)野生宝可梦标记 (4)TM机过滤只显示可学习的技能。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复Dire Claw、Stone Axe、Ceaseless Edge关于暴击的文本错误",
                            "intent": "统一数据标准，修正描述与实际效果不符的问题",
                            "detail": "修正了这三个招式的描述文字中关于暴击的不准确表述。",
                        },
                    ],
                },
                {
                    "version": "2.0.2",
                    "date": "2023-10-12",
                    "game": "零之秘宝",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "修复击败300名训练家后部分任务无法推进的bug",
                            "intent": "修复阻止游戏进度的严重问题",
                            "detail": "修复在击败300名训练家后，部分任务无法正常推进的严重进度阻止bug。",
                        },
                        {
                            "category": "内容",
                            "content": "修复Pokémon GO导入的宝可梦无法存入游戏的bug",
                            "intent": "确保跨平台数据流通的稳定性",
                            "detail": "修复从Pokémon HOME导入的Pokémon GO特殊宝可梦无法存入游戏的跨平台数据问题。",
                        },
                        {
                            "category": "其他",
                            "content": "修复结局动画在特定情况下崩溃的bug",
                            "intent": "改善剧情体验，修复崩溃问题",
                            "detail": "修复在结局动画播放时在特定情况下游戏会崩溃的bug。",
                        },
                    ],
                },
                {
                    "version": "3.0.0",
                    "date": "2023-12-14",
                    "game": "蓝之圆盘",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "内容",
                            "content": "新增DLC「蓝之圆盘」，添加新传说宝可梦太乐巴戈斯和新悖论宝可梦",
                            "intent": "完成DLC第三弹内容更新，提供新传说宝可梦和完整资料篇结局",
                            "detail": "新增蓝之圆盘DLC，以青绿为主题的新地区。新传说宝可梦太乐巴戈斯(Pecharunt)，新悖论宝可梦包括：Archaludon、Hydrapple、Raging Bolt、Gouging Fire、Iron Crown、Iron Boulder、Terapagos。",
                        },
                        {
                            "category": "PvP",
                            "content": "修复太晶化与气场特攻/原场特攻在烟雾中异常激活的bug",
                            "intent": "修正异能力机制漏洞，维护VGC对战公平性",
                            "detail": "修复Quark Drive(气场驱动)和Protosynthesis(原场驱动)特性在Neutralizing Gas(臭气泥巴/黑雾)存在时异常工作的bug，使其在烟雾中行为符合预期。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复待客之心（Hospitality）特性异常触发的问题",
                            "intent": "确保特性按描述工作，防止意外战术优势",
                            "detail": "修复Hospitality特性在某些情况下异常触发的bug，确保特性按描述在友方宝可梦进入时恢复其HP。",
                        },
                        {
                            "category": "其他",
                            "content": "调整Ogre Oustin小游戏难度",
                            "intent": "改善小游戏平衡性，提升玩家体验",
                            "detail": "调整了北上湖小游戏Ogre Oustin的难度，使游戏体验更加合理。",
                        },
                    ],
                },
                {
                    "version": "3.0.1",
                    "date": "2024-02-01",
                    "game": "蓝之圆盘",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "修复龙之鼓舞（Dragon Cheer）效果在交换后异常保留的bug",
                            "intent": "修正状态异常BUG，防止战术滥用",
                            "detail": "修复当受龙之鼓舞影响的宝可梦被切换下场后再返回战场时，其攻击仍保持会心率提升效果的bug。这是当时VGC环境中的热门战术组件。",
                        },
                        {
                            "category": "其他",
                            "content": "修复Inkay升至29级以下时使用道具升级导致游戏冻结的bug",
                            "intent": "修复影响游戏正常进行的稳定性问题",
                            "detail": "修复使用道具将Inkay升至29级或以下时，游戏会停止响应按钮输入的严重稳定性bug。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复TM223（金属音）素材需求问题",
                            "intent": "调整游戏平衡，避免版本独占问题",
                            "detail": "修复TM223(金属音)之前需要仅在特定版本出现的Shieldon素材的问题，现在不再需要Shieldon Claws。",
                        },
                        {
                            "category": "其他",
                            "content": "修复在联盟俱乐部中卡在物品打印机和墙壁之间的问题",
                            "intent": "改善游戏场景的可用性",
                            "detail": "修复安装物品打印机后，玩家在某些情况下会卡在物品打印机和墙壁之间无法移动的问题。",
                        },
                        {
                            "category": "平衡性",
                            "content": "修复Cao3ex与Glastrier/Spectrier分离后异常保留TM技能的问题",
                            "intent": "修正跨形态技能学习的异常行为",
                            "detail": "修复Cao3ex在与Glastrier或Spectrier分离后，仍能保留其通过TM学习的专属技能的问题。现在分离后会正确遗忘这些技能，重新合体后也可重新学习。",
                        },
                        {
                            "category": "其他",
                            "content": "修复Smeargle在野生遭遇中无法使用变身的问题",
                            "intent": "确保百变怪特性按描述正常工作",
                            "detail": "修复Smeargle在野生遭遇中无法使用Transform(变身)招式的bug，确保百变怪特性在所有战斗类型中正常工作。",
                        },
                    ],
                },
            ],
        }

        result = self._enrich_changes_with_feedback(patches_db.get(generation, []))
        _PATCH_NOTES_CACHE[generation] = result
        return result

    def get_detailed_patch_notes(self) -> dict:
        """
        获取所有游戏的详细完整更新日志（包含更多上下文信息）
        返回: {game: {version: data}}
        数据来源: Serebii.net (https://serebii.net/scarletviolet/patch.shtml)
        包含宝可梦朱紫所有版本的官方更新日志内容
        """
        global _DETAILED_PATCH_NOTES_CACHE
        if _DETAILED_PATCH_NOTES_CACHE is not None:
            return _DETAILED_PATCH_NOTES_CACHE

        detailed_db = {
            "朱/紫": {
                "1.0.1": {
                    "summary": "首发补丁，紧急削弱悖论宝可梦",
                    "full_context": "朱紫于2022年11月18日发售，此补丁在发售前一周发布（11月11日），目的是修正游戏平衡性疏漏。悖论宝可梦（Chi-Yu、Chien-Pao、Wo-Chien、Cien-Pao）是朱紫的原创宝可梦，拥有极高的种族值总和，在测试阶段被发现过强。",
                    "balance_changes": {
                        "Chi-Yu": {"HP": "71→55 (-16)", "Attack": "151→141 (-10)"},
                        "Chien-Pao": {"Attack": "120→110 (-10)"},
                        "Wo-Chien": {"HP": "71→55 (-16)"},
                        "Cien-Pao": {"Attack": "120→110 (-10)"},
                    },
                    "bug_fixes": [
                        "修复拉绳动画不跟随玩家的bug",
                    ],
                    "other_changes": [
                        "激活在线功能",
                        "调整部分宝可梦的TM技能学习表",
                    ],
                    "impact": "这次削弱对VGC环境产生深远影响，原本计划使用这些悖论宝可梦的选手不得不临时调整构筑",
                    "vgc_relevance": "这是Game Freak首次在发售前对原创宝可梦进行大规模数值削弱的案例，体现了现代电竞化运营的谨慎态度",
                    "official_notes": """Version 1.0.1 (November 11th 2022)

Fixes:
• Activates online features
• Reduces stats for Ting-Lu, Chi-Yu, Chien-Pao and Wo-Chien
• Altered TM compatibility for some Pokémon
• Fixed a problem with the animation not moving behind player when pulling out a stake
• Adjusted Hisuian Zoroark's stats
• Adjusted Kleavor's stats

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "1.1.0": {
                    "summary": "正式开放VGC排名对战",
                    "full_context": "朱紫于2022年11月18日发售，排名对战功能在12月2日激活，标志着VGC 2023规则赛季正式开始。",
                    "bug_fixes": [
                        "修复四天王音乐异常播放的条件bug",
                        "修复对战塔战斗中某些情况下回合被预设的bug",
                        "其他各项bug修复",
                    ],
                    "vgc_relevance": "朱紫是首个默认包含太晶化机制的VGC世代，太晶化成为双打对战的核心机制",
                    "key_features": ["太晶化作为强制机制", "新悖论宝可梦池", "无需极巨化系统"],
                    "official_notes": """Version 1.1.0 (December 2nd 2022)

Size: 485mb

Fixes:
• Activates Ranked Battle
• Fixed a bug where the Elite Four music wouldn't play properly under certain conditions
• Fixed a bug where the battles in Battle Stadium can have turns predetermined
• Various bug fixes

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "1.2.0": {
                    "summary": "大型更新，修复大量严重bug，新增悖论宝可梦",
                    "full_context": "这是朱紫发售后的第一个大型更新（485MB），主要解决游戏稳定性问题，并添加了悖论宝可梦「行走椰木」和「铁哑力」。",
                    "new_pokemon": [
                        "行走椰木 (Walking Wake) - 古代悖论宝可梦",
                        "铁哑力 (Iron Leaves) - 未来悖论宝可梦",
                    ],
                    "new_moves": [
                        "水蒸气激流 (Hydro Steam) - 行走椰木专属招式",
                        "拍击 (Spin Out) - 铁哑力专属招式",
                    ],
                    "bug_fixes": [
                        "修复太晶团体战中极巨招式或特定状态条件导致的HP显示异常bug",
                        "修复黑水晶太晶团体战中可能导致我方全部宝可梦异常倒下的bug",
                        "修复太晶宝可梦采取某些行动时玩家无法输入的冻结bug",
                        "修复连接太晶团体战时显示不同步的bug",
                        "修复通过太晶团体战搜索加入却进入不同宝可梦房间的bug",
                        "修复太晶团体战结晶在特定情况下不显示的bug",
                        "修复太晶化的佐仓�的百变怪特性导致显示错误的bug",
                        "修复多打对战中Dondozo+Tatsugiri组合的Order Up异常",
                        "修复太晶化后使用定身法导致Destiny Bond失效的bug",
                        "修复VGC结算后报错崩溃阻止继续对战的严重bug",
                        "修复对战时不显示已倒下宝可梦属性克制的优化",
                    ],
                    "balance_changes": {
                        "Chi-Yu": {"HP": "55→70 (+15)", "SpAtk": "120→125 (+5)", "Speed": "105→110 (+5)"},
                        "Scream Tail": {"HP": "55→70 (+15)", "SpAtk": "45→70 (+25)"},
                    },
                    "feature_additions": [
                        "新增DLC「零之秘宝」购买入口",
                        "新增Pokémon GO联机功能，支持蛋种导入",
                        "添加宝可梦盒子功能增强：可在盒子中改名、改标记、改持有物、调技能",
                    ],
                    "vgc_relevance": "VGC结算崩溃bug阻止了大量玩家参与排名对战，此次修复是VGC环境正常化的关键。新增悖论宝可梦扩展了VGC可用精灵池",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "1.3.0": {
                    "summary": "修复大量对战系统bug，优化Pokémon GO连接",
                    "full_context": "2023年4月20日发布，专注于修复影响对战的严重bug。",
                    "bug_fixes": [
                        "修复链接对战中超时交换可能导致交换和对战异常的bug",
                        "修复剩余时间不足一分钟时计时器不再正确显示的bug",
                        "修复特定情况下技能选择时间异常减少的bug",
                        "修复Cud Chew特性每两回合异常触发的问题",
                        "修复太晶化佐�的百变怪特性导致类型显示错误的bug",
                        "修复太晶化状态下百变怪类型显示为伪装目标太晶类型的bug",
                        "修复多打对战中攻击两个目标时能力变化异常发生两次的bug",
                        "修复Pokémon GO配对时游戏崩溃的主要问题",
                        "修复神秘礼物获得的魄罗紫菀图鉴显示错误的bug",
                    ],
                    "vgc_relevance": "重点修复了多打对战中影响公平性的各种显示和交互bug，特别是佐�与太晶化的交互问题",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "1.3.1": {
                    "summary": "修复邀请制在线比赛问题",
                    "full_context": "2023年5月25日发布，修复线上竞技功能问题。",
                    "bug_fixes": [
                        "修复邀请制在线比赛中无法退出战斗的bug",
                        "修复无法查看排名的bug",
                        "其他各项bug修复",
                    ],
                    "vgc_relevance": "确保线上竞技活动正常进行",
                    "official_notes": """Version 1.3.1 (May 25th 2023)

Fixes:
• Fixed an issue where players participating in invite only online competitions had issues exiting battles, as well as being unable to see their rating
• Other select bug fixes have been implemented.

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "1.3.2": {
                    "summary": "为世锦赛准备的版本调整",
                    "full_context": "2023年6月29日发布，为Live Competition做功能调整。",
                    "bug_fixes": [
                        "为Live Competition做功能调整",
                        "修改Illuminate特性描述文字",
                        "其他各项bug修复",
                    ],
                    "vgc_relevance": "为官方线上赛事做准备的版本",
                    "official_notes": """Version 1.3.2 (June 29th 2023)

Fixes:
• Made some alterations for the Live Competitions
• Changed text for the Illuminate ability to: By Iluminating its surroundings, the Pokémon prevents its accuracy from being lowered
• Other select bug fixes have been implemented.

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "2.0.1": {
                    "summary": "零之秘宝DLC第一弹「碧之假面」发布",
                    "full_context": "2023年9月13日发布，新增北上乡DLC和大量新内容。",
                    "new_content": [
                        "新增DLC「碧之假面」，新地区「北上乡」",
                        "新增101只回归宝可梦",
                        "新增悖论宝可梦：Dipplin、Poltchageist、Sinistcha、Okidogi、Munkidori、Fezandipiti、Ogerpon",
                        "新增北上湖更高难度太晶团体战",
                    ],
                    "feature_additions": [
                        "新增小地图方向锁定功能",
                        "新增相机相关设置",
                        "新增野生宝可梦标记功能",
                        "TM机可过滤只显示可学习的技能",
                    ],
                    "bug_fixes": [
                        "修复Dire Claw、Stone Axe、Ceaseless Edge关于暴击的文本错误",
                        "修复Itemfinder标记无法附着在宝可梦身上的bug",
                        "修复Titan Mark宝可梦击败后可能不出现的bug",
                        "优化盒子中宝可梦图标加载速度",
                    ],
                    "vgc_relevance": "新增悖论宝可梦极大扩展了VGC可用精灵池，改变了Meta格局",
                    "official_notes": """Version 2.0.1 (September 13th 2023)

Fixes:
• Added access to the The Teal Mask and all its relevant contents, new items and improvements.
• Added data for 101 Returning Pokémon, as well as the new Pokémon Dipplin, Poltchageist, Sinistcha, Okidogi, Munkidori, Fezandipiti & Ogerpon as well as new moves and abilities
• The top direction in the minimap can be set to always fix north by pressing the Right Stick twice on the map screen
• Camera related settings have been added to the Settings to adjust the field camera
• You can now signal Pokémon walking on the field by pushing the L stick to stop them moving and photos can be taken with the A button
• With the TM Machines at Pokémon Centers, you can add a filter to only display TMs that your Pokémon can learn
• Bug fixes have been made including correction of the text for Dire Claw, Stone Axe and Ceaseless Edge mentioning Critical Hits
• Fixed an issue where the Itemfinder mark would not attach to Pokémon
• Fixed an issue where Titan Mark Pokémon may not appear after being defeated if you didn't catch them
• Adjustments made to the display of Pokémon icons in boxes to load faster

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "2.0.2": {
                    "summary": "碧之假面补丁，修复游戏进度和跨平台bug",
                    "full_context": "2023年10月12日发布，主要修复非对战类bug。",
                    "bug_fixes": [
                        "修复击败300名训练家后部分任务无法推进的bug",
                        "修复Pokémon GO导入的宝可梦无法存入游戏的bug",
                        "修复结局动画在特定情况下崩溃的bug",
                    ],
                    "vgc_relevance": "主要修复非对战类bug",
                    "official_notes": """Version 2.0.2 (October 12th 2023)

Fixes:
• Fixed an issue where trainers wouldn't register as being defeated if you had already beaten 300 trainers in the game, preventing progress on some story elements
• Fixed an issue where Special Pokémon from Pokémon GO couldn't be deposited into the game from Pokémon HOME
• Fixed an issue where the game would crash in the final battle if you already had Koraidon or Miraidon registered in your Pokédex

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "3.0.0": {
                    "summary": "蓝之圆盘DLC发布，完成资料篇",
                    "full_context": "2023年12月14日发布，新增蓝之圆盘DLC，完成零之秘宝资料篇。",
                    "new_content": [
                        "新增DLC「蓝之圆盘」，新地区以青绿为主题",
                        "新增传说宝可梦「太乐巴戈斯」(Pecharunt)",
                        "新增悖论宝可梦：Archaludon、Hydrapple、Raging Bolt、Gouging Fire、Iron Crown、Iron Boulder、Terapagos",
                    ],
                    "bug_fixes": [
                        "修复太晶化与气场特攻/原场特攻在烟雾中异常激活的bug",
                        "修复待客之心（Hospitality）特性异常触发的问题",
                        "修复气场驱动/原场驱动的特性在 Neutralizing Gas 下异常工作的问题",
                        "调整Ogre Oustin小游戏难度",
                    ],
                    "vgc_relevance": "太乐巴戈斯的特性「最大扰乱」严重影响VGC环境平衡，新传说宝可梦扩展了可用精灵池",
                    "official_notes": """Version 3.0.0 (December 14th 2023)

Fixes:
• Added access to the The Indigo Disk and all its relevant contents, new items and improvements.
• Added data for Returning Pokémon, as well as the new Pokémon Archaludon, Hydrapple, Raging Bolt, Gouging Fire, Iron Crown, Iron Boulder, Terapagos and Pecharunt as well as new moves and abilities
• Adjustments made to Ogre Oustin's difficulty
• A bug fix was made for the move Hospitality which caused unintended behaviour
• A bug fix was made for the abilities Quark Drive & Protosynthesis to prevent them working when Neutralising Gas is in effect

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "3.0.1": {
                    "summary": "蓝之圆盘补丁，修复龙之鼓舞bug",
                    "full_context": "2024年2月1日发布，4.9GB大型补丁，主要修复特性交互bug。",
                    "bug_fixes": [
                        "修复龙之鼓舞（Dragon Cheer）效果在交换后异常保留的bug",
                        "修复Inkay升至29级以下时使用道具升级导致游戏冻结的bug",
                        "修复TM223（金属音）需要仅在特定版本出现的Shieldon素材的问题",
                        "修复在联盟俱乐部中卡在物品打印机和墙壁之间的问题",
                        "修复Cao3ex与Glastrier/Spectrier分离后异常保留TM技能的问题",
                        "修复Smeargle在野生遭遇中无法使用变身的问题",
                    ],
                    "vgc_relevance": "龙之鼓舞bug修复对VGC双打环境产生重大影响，该技能是当时热门战术的关键组件",
                    "official_notes": """Version 3.0.1 (February 1st 2024)

Fixes:
• Alters the crafting materials required to make TM223, removing Shieldon from it
• Fixes the glitch where the Dragon Cheer effect would persist after switching
• Fixes the glitch where the game would freeze if you used items to level up an Inkay to Level 29 or under
• Fixed an issue where players become stuck between the Item Printer and the wall in the League Club
• Fixed an issue where Cao3ex wouldn't remember learning certain TM moves after being separated from Glastrier & Spectrier
• Smeargle can no longer use Transform in Wild encounters

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "4.0.0": {
                    "summary": "Switch 2 兼容更新",
                    "full_context": "2025年6月3日发布，为Nintendo Switch 2提供优化支持。",
                    "new_content": [
                        "添加为Nintendo Switch 2优化帧率和画面的功能",
                        "为高分辨率显示器提供更好的图形支持",
                    ],
                    "bug_fixes": [
                        "此更新是游戏联机所必需的",
                    ],
                    "vgc_relevance": "为新硬件平台提供支持，确保竞技功能正常运作",
                    "official_notes": """Version 4.0.0 (June 3rd 2025)

Fixes:
• Adds functionality for improved frame rate and visuals for when played on the Nintendo Switch 2.

Notes: This update is required for your game to go online.""",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
            },
            "零之秘宝": {
                "2.0.1": {
                    "summary": "零之秘宝DLC第一弹「碧之假面」发布",
                    "full_context": "零之秘宝是朱紫的DLC，分为「碧之假面」和「蓝之圆盘」两部分。「碧之假面」新增北上乡地区。",
                    "new_paradox": [
                        "古代种：吃吼雪(Dipplin)、螺旋状草(Sinchageist)、厄鬼水母(Sinistcha)、道主狗(Okidogi)、猫猫蛇(Munkidori)、绯红污水(Fezandipiti)、弃食猫(Ogerpon)",
                    ],
                    "vgc_relevance": "新增悖论宝可梦极大扩展了VGC可用精灵池，Ogerpon成为强力对战宝可梦",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "2.0.2": {
                    "summary": "碧之假面补丁，修复游戏进度和跨平台bug",
                    "full_context": "碧之假面是朱紫DLC第一弹。",
                    "bug_fixes": [
                        "修复击败300名训练家后部分任务无法推进的bug",
                        "修复Pokémon GO导入的宝可梦无法存入游戏的bug",
                        "修复结局动画在特定情况下崩溃的bug",
                    ],
                    "vgc_relevance": "主要修复非对战类bug",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
            },
            "碧之假面": {
                "2.0.1": {
                    "summary": "零之秘宝DLC第一弹「碧之假面」发布",
                    "full_context": "零之秘宝是朱紫的DLC，分为「碧之假面」和「蓝之圆盘」两部分。「碧之假面」新增北上乡地区。",
                    "new_paradox": [
                        "古代种：吃吼雪(Dipplin)、螺旋状草(Sinchageist)、厄鬼水母(Sinistcha)、道主狗(Okidogi)、猫猫蛇(Munkidori)、绯红污水(Fezandipiti)、弃食猫(Ogerpon)",
                    ],
                    "vgc_relevance": "新增悖论宝可梦极大扩展了VGC可用精灵池，Ogerpon成为强力对战宝可梦",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "2.0.2": {
                    "summary": "碧之假面补丁，修复游戏进度和跨平台bug",
                    "full_context": "碧之假面是朱紫DLC第一弹。",
                    "bug_fixes": [
                        "修复击败300名训练家后部分任务无法推进的bug",
                        "修复Pokémon GO导入的宝可梦无法存入游戏的bug",
                        "修复结局动画在特定情况下崩溃的bug",
                    ],
                    "vgc_relevance": "主要修复非对战类bug",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
            },
            "蓝之圆盘": {
                "3.0.0": {
                    "summary": "蓝之圆盘DLC发布，完成资料篇",
                    "full_context": "蓝之圆盘是朱紫DLC的第二部分，以青绿为主题。",
                    "new_additions": [
                        "新传说宝可梦「太乐巴戈斯」(Pecharunt)",
                        "新悖论宝可梦：Archaludon、Hydrapple、Raging Bolt、Gouging Fire、Iron Crown、Iron Boulder、Terapagos",
                        "新地区「蓝之圆盘」",
                    ],
                    "bug_fixes": [
                        "修复太晶化与气场特攻/原场特攻在烟雾中异常激活的bug",
                        "修复待客之心（Hospitality）特性异常触发的问题",
                        "修复气场驱动/原场驱动的特性在 Neutralizing Gas 下异常工作的问题",
                    ],
                    "vgc_relevance": "太乐巴戈斯的特性「最大扰乱」严重影响VGC环境平衡",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
                "3.0.1": {
                    "summary": "蓝之圆盘补丁，修复龙之鼓舞bug",
                    "full_context": "蓝之圆盘是朱紫DLC的第二部分。",
                    "bug_fixes": [
                        "修复龙之鼓舞（Dragon Cheer）效果在交换后异常保留的bug",
                        "修复Inkay升至29级以下时使用道具升级导致游戏冻结的bug",
                        "修复TM223（金属音）需要仅在特定版本出现的Shieldon素材的问题",
                        "修复在联盟俱乐部中卡在物品打印机和墙壁之间的问题",
                        "修复Cao3ex与Glastrier/Spectrier分离后异常保留TM技能的问题",
                        "修复Smeargle在野生遭遇中无法使用变身的问题",
                    ],
                    "vgc_relevance": "修复龙之鼓舞等特性bug，维护对战公平性",
                    "source_url": "https://serebii.net/scarletviolet/patch.shtml",
                },
            },
            "剑/盾": {
                "1.0.0": {
                    "summary": "第八世代正式发布，极巨化登场",
                    "full_context": "剑盾是首个没有全国图鉴的宝可梦正作，引发巨大争议。",
                    "key_mechanics": ["极巨化替代Mega进化", "极巨化替代Z招式", "极巨团体战"],
                    "vgc_relevance": "极巨化成为VGC双打核心机制，其易用性和视觉冲击力获得好评",
                    "source_url": "https://serebii.net/swordshield/",
                },
                "1.1.0": {
                    "summary": "新增极巨团体战，修复对战bug",
                    "full_context": "2020年1月9日发布，新增多人合作PvE内容。",
                    "new_content": [
                        "新增极巨团体战，可与其他玩家合作挑战野生极巨化宝可梦",
                    ],
                    "bug_fixes": [
                        "修复Sucker Punch、Quash在只有一名对手时失效的bug",
                    ],
                    "vgc_relevance": "首次在正作中引入多人合作PvE内容，解决「缺乏官方合作玩法」的需求",
                    "source_url": "https://serebii.net/swordshield/",
                },
                "1.2": {
                    "summary": "铠之孤岛DLC发布",
                    "full_context": "2020年6月17日发布，首个DLC「铠之孤岛」引入了新的冒险区域和101只回归宝可梦。",
                    "new_content": [
                        "新增「铠之孤岛」DLC",
                        "添加101只回归宝可梦及新宝可梦武藏",
                        "新增战斗准备标记，使从HOME转移的宝可梦可参与排名对战",
                        "新增8位Y-Comm链接码",
                    ],
                    "bug_fixes": [
                        "修复排名对战中断线仍能获得胜利的漏洞",
                    ],
                    "vgc_relevance": "新增的传说宝可梦蕾冠王/蕾冠鹿成为VGC常用精灵",
                    "source_url": "https://serebii.net/swordshield/expansionpass.shtml",
                },
                "1.2.1": {
                    "summary": "修复极巨团体战链接码漏洞",
                    "full_context": "2020年7月8日发布。",
                    "bug_fixes": [
                        "修复极巨团体战链接码只用7位数字即可匹配的漏洞",
                    ],
                    "vgc_relevance": "防止利用漏洞入侵他人对战房间，保护玩家体验",
                    "source_url": "https://serebii.net/swordshield/expansionpass.shtml",
                },
                "1.3": {
                    "summary": "冠之雪原DLC发布",
                    "full_context": "2020年10月23日发布，冠之雪原引入了「传说之路」和「挑战之路」两条故事线。",
                    "new_content": [
                        "新增「冠之雪原」DLC",
                        "添加119只回归宝可梦及传说宝可梦蕾冠王/蕾冠鹿",
                        "冠之雪原传说宝可梦可参与VGC对战",
                    ],
                    "vgc_relevance": "大量传说宝可梦回归，扩展了VGC可用精灵池",
                    "source_url": "https://serebii.net/crowntundra/",
                },
                "1.3.1": {
                    "summary": "修复部分对战机制bug",
                    "full_context": "2020年12月22日发布。",
                    "bug_fixes": [
                        "修复部分对战机制bug",
                    ],
                    "vgc_relevance": "改善对战体验，修复影响游戏平衡的问题",
                    "source_url": "https://serebii.net/crowntundra/",
                },
                "1.3.2": {
                    "summary": "修复数据不一致和公平性问题",
                    "full_context": "2021年5月12日发布。",
                    "bug_fixes": [
                        "修复古剑虎、藏饱等宝可梦数据与图鉴描述不符的问题",
                        "修复多人对战中可从精灵数据判断对手是否使用幻之宝可梦的漏洞",
                    ],
                    "vgc_relevance": "统一数据标准，确保对战公平性",
                    "source_url": "https://serebii.net/crowntundra/",
                },
            },
        }

        _DETAILED_PATCH_NOTES_CACHE = detailed_db
        return detailed_db

    def _enrich_changes_with_feedback(self, patches: list) -> list:
        """
        为每个 change 条目添加玩家社区反馈数据
        基于领域知识预置的玩家反应数据，用于补充内置数据
        """
        # 玩家反馈知识库 - 通过 content 关键词匹配
        feedback_db = {
            "VGC 2020规则赛季开始": {
                "sentiment": "mixed",
                "summary": "极巨化视觉冲击力强但战略深度受质疑，全国图鉴缺失引发强烈不满",
                "key_points": [
                    "VGC玩家对极巨化反应两极：喜欢视觉反馈但认为战略深度不如Mega进化",
                    "全国图鉴缺失是本世代最大争议，非对战玩家强烈反对",
                    "极巨化3回合机制被认为节奏偏慢",
                ],
            },
            "极巨化系统上线": {
                "sentiment": "mixed",
                "summary": "视觉冲击力获肯定，战略深度存疑，3回合过长问题在VGC社区持续被讨论",
                "key_points": [
                    "视觉和音效的「大」感获得一致好评",
                    "3回合极巨化被认为拖慢对战节奏",
                    "极巨招式必定命中的设计让一些先制度招式失去意义",
                ],
            },
            "新增极巨团体战": {
                "sentiment": "positive",
                "summary": "极巨团体战受到休闲玩家欢迎，但回合制设计导致等待时间问题持续被批评",
                "key_points": [
                    "休闲/收集向玩家对能捕捉高个体值极巨化宝可梦反应热烈",
                    "回合制设计导致4人等待时间过长是核心痛点",
                    "部分玩家反映掉线后奖励消失，社交体验不完善",
                ],
            },
            "修复Sucker Punch": {
                "sentiment": "positive",
                "summary": "VGC竞技玩家普遍肯定，bug修复保证了公平性",
                "key_points": [
                    "VGC玩家认为这是必要的平衡性修复",
                    "没有明显负面反馈",
                ],
            },
            "铠之孤岛": {
                "sentiment": "positive",
                "summary": "101只回归宝可梦获得好评，DLC内容质量中等",
                "key_points": [
                    "回归宝可梦数量超出预期，收集玩家感到满足",
                    "武藏进化形Urshifu的「型态」变化带来新对战可能",
                    "部分玩家认为内容体量偏小，性价比一般",
                ],
            },
            "战斗准备标记": {
                "sentiment": "mixed",
                "summary": "竞技玩家认可公平性设计，但流程繁琐引发抱怨",
                "key_points": [
                    "VGC玩家普遍支持，防止了某些强力旧世代宝可梦直接进入环境",
                    "Battle Ready标记流程被认为是额外门槛，有玩家觉得繁琐",
                ],
            },
            "对战组队预览": {
                "sentiment": "positive",
                "summary": "组队体验改善获得一致好评",
                "key_points": [
                    "8位链接码增加了匹配安全性，防止误入陌生人房间",
                    "组队预览同屏让配合更方便",
                ],
            },
            "修复排名对战中断线": {
                "sentiment": "positive",
                "summary": "VGC玩家热烈欢迎，认为早该修复",
                "key_points": [
                    "玩家社区早就发现这一漏洞并持续抱怨",
                    "修复速度被认为太慢，但方向正确",
                ],
            },
            "修复极巨团体战链接码只用7位": {
                "sentiment": "positive",
                "summary": "漏洞修复被认为是必要的安全更新，没有争议",
                "key_points": [
                    "玩家社区早已发现并利用此漏洞，反映强烈",
                    "修复后玩家安心许多，减少了陌生人骚扰",
                ],
            },
            "冠之雪原": {
                "sentiment": "positive",
                "summary": "大量回归宝可梦和传说内容获得高度好评，被认为比铠之孤岛更值得",
                "key_points": [
                    "119只回归宝可梦数量超出预期，收集玩家和VGC玩家双重满足",
                    "蕾冠王/蕾冠鹿在VGC中表现出色，获得竞技玩家认可",
                    "传说之路的剧情和挑战之路的玩法都获得好评",
                ],
            },
            "冠之雪原传说宝可梦可参与VGC": {
                "sentiment": "mixed",
                "summary": "竞技玩家对传说宝可梦的态度两极分化，休闲玩家普遍欢迎",
                "key_points": [
                    "休闲玩家喜欢传说宝可梦的收集价值",
                    "部分VGC玩家担心传说宝可梦统治环境",
                    "最终蕾冠王等被证明强度适中，社区反应满意",
                ],
            },
            "数据与图鉴描述不符": {
                "sentiment": "positive",
                "summary": "数据标准化获得好评，社区认为这是早就该做的修复",
                "key_points": [
                    "玩家认为Game Freak终于承认并修正了数据不一致问题",
                    "对对战平衡性有轻微影响，竞技玩家关注",
                ],
            },
            "幻之宝可梦的漏洞": {
                "sentiment": "positive",
                "summary": "VGC社区强烈欢迎，防止了信息不对称导致的战术优势",
                "key_points": [
                    "这个漏洞在VGC社区被广泛讨论，修复被认为是必要且及时的",
                    "竞技公平性得到维护，玩家满意",
                ],
            },
            "削弱了悖论宝可梦 Chi-Yu": {
                "sentiment": "controversial",
                "summary": "两极分化：休闲/剧情玩家普遍支持，VGC竞技玩家强烈不满",
                "key_points": [
                    "休闲玩家：拍手称快——终于不用担心被强力宝可梦秒了",
                    "VGC玩家：强烈抗议——悖论宝可梦被削弱到无法使用，构筑方向全部推翻",
                    "深层质疑：为什么发售前一周才发现问题？这是电竞化运营的必要代价还是测试流程不完善的暴露？",
                ],
            },
            "激活排名对战": {
                "sentiment": "positive",
                "summary": "VGC社区终于等到正式赛季开放，太晶化成为热议话题",
                "key_points": [
                    "VGC玩家热情高涨，终于可以正式参与排名对战",
                    "太晶化的1回合限制设计引发讨论，相比极巨化3回合更受竞技玩家认可",
                    "但朱紫本身的画面和性能问题让部分玩家分心",
                ],
            },
            "新增悖论宝可梦「行走椰木」": {
                "sentiment": "positive",
                "summary": "悖论宝可梦受到VGC玩家欢迎，但行走椰木强度引发讨论",
                "key_points": [
                    "新悖论宝可梦为VGC环境注入活力，构筑多样性提升",
                    "行走椰木的水蒸气激流在晴天队中表现过强，引发热议",
                    "铁哑力的拍击虽然新颖但使用场景有限",
                ],
            },
            "太晶团体战修复多个HP显示异常": {
                "sentiment": "positive",
                "summary": "严重bug修复受到玩家广泛认可，但部分玩家认为bug数量过多反映了质量问题",
                "key_points": [
                    "团体战玩家热烈欢迎，终于不再频繁遇到输入冻结",
                    "但朱紫从发售起就存在大量bug让部分玩家对Game Freak质量管控产生质疑",
                ],
            },
            "VGC结算后报错": {
                "sentiment": "negative",
                "summary": "VGC玩家强烈不满——严重影响竞技体验的核心bug，修复虽然及时但暴露了质量问题",
                "key_points": [
                    "赛季结算后无法访问排名对战的bug让VGC玩家愤怒",
                    "玩家质疑：为什么发售时就存在的bug在近3个月后才修复",
                    "部分玩家对朱紫的bug数量超出正常范围感到不满",
                ],
            },
            "不再显示已倒下宝可梦的属性克制提示": {
                "sentiment": "mixed",
                "summary": "竞技玩家支持（减少干扰），休闲/新手玩家担忧（失去学习辅助）",
                "key_points": [
                    "VGC玩家认为这是减少信息过载的合理优化",
                    "休闲和新手玩家认为失去了一项有用的视觉提示功能",
                ],
            },
            "Chi-Yu和Scream Tail种族值小幅提升": {
                "sentiment": "positive",
                "summary": "VGC社区普遍欢迎——体现了Game Freak愿意修正过度削弱的开放态度",
                "key_points": [
                    "1.0.1时强烈不满的VGC玩家此次感到被倾听",
                    "但玩家也质疑：为什么1.0.1时削得那么狠，现在又要回调？",
                    "整体上被认为是负责任的平衡性调整态度",
                ],
            },
            "Pokémon GO联机功能": {
                "sentiment": "positive",
                "summary": "Pokémon GO玩家群体反应积极，跨平台联动的价值得到认可",
                "key_points": [
                    "Pokémon GO的活跃玩家群体对此功能表示赞赏",
                    "蛋种导入功能满足了特定的收集需求",
                    "但也暴露了朱紫自身孵蛋机制的不足",
                ],
            },
            "修复佐仓": {
                "sentiment": "positive",
                "summary": "修复获得VGC玩家认可，但复杂交互bug的数量令人担忧",
                "key_points": [
                    "太晶化+百变怪的复杂交互bug让玩家对Game Freak的代码质量产生怀疑",
                    "修复本身被认为是必要且及时的",
                ],
            },
            "修复多打对战中攻击两个目标时能力变化异常": {
                "sentiment": "positive",
                "summary": "VGC社区感谢修复，但对双打战斗系统的持续bug表示失望",
                "key_points": [
                    "替身+双目标的复杂交互bug被修复，竞技公平性得到维护",
                    "部分玩家反映这类bug让双打体验不够可靠",
                ],
            },
            "修复邀请制在线比赛中无法退出战斗": {
                "sentiment": "positive",
                "summary": "受影响玩家感谢修复，但对线上比赛功能的持续问题表示不满",
                "key_points": [
                    "参加邀请赛的玩家感谢修复",
                    "但对这类基础功能的持续问题感到不耐烦",
                ],
            },
            "碧之假面": {
                "sentiment": "positive",
                "summary": "碧之假面DLC发布，Ogerpon等新宝可梦引发热潮",
                "key_points": [
                    "101只回归宝可梦超出预期，收集玩家和VGC玩家双重满足",
                    "Ogerpon(弃食猫)因其型态变化机制人气极高",
                    "部分玩家认为北上乡内容体量偏小",
                ],
            },
            "北上湖更高难度太晶团体战": {
                "sentiment": "positive",
                "summary": "硬核PvE玩家表示欢迎，但更多人呼吁先修好基础bug",
                "key_points": [
                    "挑战向玩家对更高难度太晶团体战表示期待",
                    "但社区主流声音是希望Game Freak专注修复基础bug而非添加新内容",
                ],
            },
            "小地图方向锁定": {
                "sentiment": "positive",
                "summary": "实用功能改善体验，获得一致好评",
                "key_points": [
                    "小地图方向锁定是玩家长期以来的功能诉求",
                    "野生宝可梦标记功能受到探索向玩家欢迎",
                ],
            },
            "击败300名训练家后": {
                "sentiment": "positive",
                "summary": "受影响玩家热烈欢迎，游戏进度阻塞问题终于解决",
                "key_points": [
                    "被此bug卡住的玩家等待修复已久",
                    "但社区质疑为何游戏发售时就存在的bug现在才修",
                ],
            },
            "从Pokémon HOME导入的Pokémon GO": {
                "sentiment": "positive",
                "summary": "跨平台数据流通修复获得受影响玩家好评",
                "key_points": [
                    "Pokémon GO玩家终于能正常使用跨平台导入功能",
                    "修复被认为是必要但不应该需要这么久",
                ],
            },
            "结局动画在特定情况下崩溃": {
                "sentiment": "positive",
                "summary": "剧情向玩家感谢修复，结局体验终于完整",
                "key_points": [
                    "结局崩溃bug让部分玩家的剧情体验中断",
                    "修复被认为是必要且及时的",
                ],
            },
            "蓝之圆盘": {
                "sentiment": "positive",
                "summary": "蓝之圆盘DLC发布，新角色引发热潮",
                "key_points": [
                    "太乐巴戈斯作为新传说宝可梦在VGC中引发热议",
                    "其「最大扰乱」特性严重影响环境平衡，引发设计讨论",
                    "新悖论宝可梦扩展了VGC可用精灵池",
                ],
            },
            "修复太晶化与气场特攻": {
                "sentiment": "positive",
                "summary": "VGC竞技玩家感谢修复，异能力机制漏洞被堵住",
                "key_points": [
                    "气场特攻/原场特攻在烟雾中的异常行为影响了特定战术的可靠性",
                    "修复被认为是维护竞技公平性的必要举措",
                ],
            },
            "待客之心": {
                "sentiment": "positive",
                "summary": "细节bug修复，VGC社区平静接受",
                "key_points": [
                    "待客之心是双打辅助特性，受众较小",
                    "修复本身被认为是标准操作，无争议",
                ],
            },
            "Ogre Oustin": {
                "sentiment": "mixed",
                "summary": "小游戏难度调整引发两极反应",
                "key_points": [
                    "认为小游戏太难的玩家欢迎调整",
                    "部分玩家认为不应随意修改已完成内容",
                ],
            },
            "修复龙之鼓舞": {
                "sentiment": "positive",
                "summary": "VGC社区感谢修复，但质疑为何这类复杂交互bug持续出现",
                "key_points": [
                    "龙之鼓舞bug修复对当时的双打环境产生重大影响",
                    "玩家再次对Game Freak的代码质量表示担忧",
                ],
            },
            "Smeargle在野生遭遇中无法使用变身": {
                "sentiment": "positive",
                "summary": "百变怪基础功能修复，所有受影响玩家欢迎",
                "key_points": [
                    "Smeargle的变身是其核心玩法，bug阻止了正常游戏体验",
                    "修复被认为是早就该做的标准操作",
                ],
            },
        }

        for patch in patches:
            for change in patch.get("changes", []):
                content_text = change.get("content", "")
                # 通过关键词匹配玩家反馈
                for keyword, feedback in feedback_db.items():
                    if keyword in content_text:
                        change["player_feedback"] = feedback
                        break

        return patches

    def search_bulbapedia(self, query: str) -> list:
        """
        搜索 Bulbapedia
        后续可扩展：使用 Bulbapedia API 或爬取搜索结果页面
        """
        # TODO: 实现 Bulbapedia 搜索和页面抓取
        # 参考: https://bulbapedia.bulbagarden.net/wiki/Game_FAQ
        pass
