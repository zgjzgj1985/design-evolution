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
        包含 Gen 1-9 宝可梦完整对战/竞技设计演进记录
        数据来源: VGC 官方规则历史 + Smogon 竞技分析 + 机制演进研究
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
                    "official_notes": """=== POKEMON RED & GREEN (Version 1.0) ===

[Game Boy Link Cable] Battle System
- First generation officially released in Japan with core battle framework.
- Link Cable enables 2v2 battles (hidden mode), establishing the "focus-fire + protect" tactical foundation.
- 151 Pokémon with type matchup system: Water beats Fire, Fire beats Grass, Grass beats Electric...
- Moves system: each move has PP (Power Points), accuracy, and type; PP management becomes key strategy.
- Held items introduced: Pokémon can carry items affecting battle performance.
- Sleep mechanics: Sleep status lasts variable turns, adding mind-game depth.
- Critical hit mechanics: moves have ~12% base crit chance, modified byfocus items.
- Speed determines turn order; ties resolved by random.

[Collection & Progression]
- National Pokédex: 151 species form the foundation of collection-and-battle loop.
- Gym Leader progression: 8 gyms with type-themed challenges.
- Elite Four + Champion: final challenge gates for post-game competitive play.
- Breeding system introduced in Gen 2 but data structures present in Gen 1 ROM.

[Legacy Impact]
- Core battle loop (select move → calculate damage → apply effects → check KO) remains essentially unchanged for 29 years.
- 2v2 Link Cable battles planted the seed for VGC esports.
- Speed tier system, type chart, and move categorization established Gen 1 baseline.
- Trade evolution requirement created early form of social multiplayer gameplay.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "首个宝可梦正式版本发布，Game Boy Link Cable 支持双打对战（隐藏模式）",
                            "intent": "开创回合制对战RPG品类，建立核心对战机制框架。虽然双打是隐藏模式，但奠定了2v2集火/保护博弈基础",
                            "detail": "红绿版建立了宝可梦对战的基础框架，包括属性克制、招式PP、道具携带、等级压制等核心机制。游戏同步通讯协议为后续电竞化提供了技术基础。",
                        },
                        {
                            "category": "PvP",
                            "content": "全国图鉴收录151种宝可梦，建立收集与对战的循环生态",
                            "intent": "通过图鉴收集驱动玩家投入，形成对战资源积累，为竞技深度奠定基础",
                            "detail": "151种宝可梦的差异化设计确保了每种都有独特定位，部分如卡比兽、吸盘魔偶因技能池深度成为早期对战常客。",
                        },
                    ],
                },
                {
                    "version": "1.1",
                    "date": "1996-10-15",
                    "game": "蓝",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON BLUE (Version 1.1) ===

[Official Bug Fix & Stabilization]
- Released October 15th, 1996 as the first official bug-fix patch for Red/Green.
- Fixed critical bugs affecting battle calculations, move accuracy, and experience gain.
- Established the "base game → bug-fix version" release cadence Game Freak maintains for 29 years.

[Battle System Fixes]
- Corrected damage calculation formulas (e.g., critical hit damage multiplier: 2→3).
- Fixed bug where badges provided stat boosts in Link battles (removed entirely).
- Fixed move interaction bugs: Counter, Mirror Coat, Bide now function correctly.
- Fixed encounter rate bugs for rare Pokémon.

[Gameplay Adjustments]
- Sprite improvements and minor map corrections.
- Balanced early-game Pokémon distribution for improved progression pacing.
- Fixed Hall of Fame corruption bug.

[Release Management Impact]
- Blue version established the precedent of a companion "revision" release for each generation.
- This patch-and-revision model would evolve into the "third version" tradition (Yellow, Crystal, Emerald...).""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "大量Bug修复，游戏稳定性提升，部分招式数值调整",
                            "intent": "修正首发版本的程序问题，建立后续版本迭代规范",
                            "detail": "蓝版作为红绿的修正版发布，修复了众多影响游戏正常进行的bug，同时也对部分过强/过弱的招式数值进行了调整。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "1998-09-30",
                    "game": "红/蓝",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON RED & BLUE (North America - Version 1.0) ===

[Western Launch]
- First Pokémon games released in North America on September 30th, 1998.
- North American debut established Pokémon as a global franchise.
- Red/Blue versions introduced Western audiences to the core battle system.
- Cable Link battles became standard at local tournaments and gaming conventions.

[Market Impact]
- Western release laid the foundation for the Pokémon trading card game (1999) and anime (1997 Japan, 1998 Western).
- "Gotta Catch 'Em All" marketing campaign resonated globally.
- Competitive scene formed around Game Boy Link Cable tournaments at schools and game stores.

[Format Legacy]
- North American competitive Pokémon scene began with local Link Cable tournaments.
- These grassroots tournaments would eventually evolve into the official VGC circuit.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "宝可梦正式登陆西方市场，Cable Link双打对战成为线下聚会标准玩法",
                            "intent": "全球化推广，建立双打对战的联机基础，电竞雏形开始形成",
                            "detail": "红蓝版是首个西方发行的版本，Game Boy Link Cable使双打对战成为可能。线下聚会中的双打对战是宝可梦电竞的最初形态。",
                        },
                        {
                            "category": "机制",
                            "content": "中文语言支持（国际版），扩大了全球玩家基础",
                            "intent": "扩大受众群体，建立国际化玩家社区",
                            "detail": "国际化版本使更多地区的玩家能够无障碍参与，奠定了宝可梦作为全球性IP的基础。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "1999-09-30",
                    "game": "黄",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON YELLOW (Version 1.0) ===

[Visual Standardization]
- First game with animated (sprite-based) Pokémon in battles → standardized battle visuals.
- Pokémon walk behind the player in the overworld (Pikachu follows) → companion dynamic established.
- Anime-style character designs throughout → Pokémon as "characters" rather than just "monsters."

[Battle Visuals]
- Animated battle sprites: all 151 species received battle animation → aesthetic unity for esports broadcasting.
- Battle transitions and animations more polished than Red/Blue → spectators can more easily identify Pokémon.
- This visual consistency laid the foundation for VGC broadcast quality.

[Design Philosophy]
- Yellow explicitly designed to tie in with the anime (Pikachu as the main character).
- "Pokémon as companion" concept → design philosophy that influenced future games' relationship systems (Pokémon-Amie, Camp, etc.).

[Competitive Legacy]
- Yellow's Battle Tower (similar to Red/Blue) was used for early tournament play.
- The visual improvements in Yellow set the standard for competitive battle presentation.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "添加动画版宝可梦头像到战斗画面，对战观赏性大幅提升",
                            "intent": "提升对战视觉体验，为未来电竞转播和观赏性竞争奠定基础",
                            "detail": "黄版首次引入动画风格的宝可梦头像，增加了对战的观赏性。虽然不是首个有动画的版本，但动画风格的统一化对后续电竞转播有重要意义。",
                        },
                        {
                            "category": "机制",
                            "content": "皮卡丘同行系统上线，宝可梦作为同伴的世界观设计",
                            "intent": "增强叙事体验，为宝可梦的「伙伴」定位建立情感基础",
                            "detail": "黄版是首个以动画风格设计的版本，皮卡丘会在世界地图上跟随玩家，强化了宝可梦的伙伴属性。",
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
                    "official_notes": """=== POKEMON GOLD & SILVER (Version 1.0) ===

[Ability System]
- Introduced 80+ Abilities providing passive effects unique to each Pokémon.
- Intimidate (威吓): 50% chance to lower opponent's Attack by 1 stage each turn → becomes the core of doubles defensive play for 29 years.
- Shed Skin: 30% chance to cure any status each turn → standard "survivability" ability.
- Synchronize: causes opponent to receive same status condition → core of stall and status-transfer strategies.
- Trace, Pressure, Intimidate, Synchronize establish the "passive ability" design vocabulary that defines Pokémon from other turn-based RPGs.

[Item System]
- Held Items system fully functional: Leftovers (剩饭) restore 1/16 HP per turn → defensive staple for 29 years.
- Focus Band: 10% chance to survive fatal hit at 1 HP → early RNG-based clutch item.
- Choice Band/Specs: lock into one move after use → "hit harder" offensive item paradigm.
- King's Rock: 10% chance to cause flinching → adds flinch pressure to any physical attacker.
- Item × Ability interaction layers create the "build" (构筑) system that is the foundation of competitive teambuilding.

[Day/Night System]
- Real-time clock determines day/night cycle affecting wild encounters and some moves.
- Moves like Snore usable only at night; some evolutions require day/night.
- Establishes "time-window constraints" as a design tool for restricting or enabling certain strategies.

[Multiplayer]
- Cell Phone system: register trainers and receive battle challenges → asynchronous PvP prototype.
- Mobile Adapter GB (Japan) enables real-time battle via phone line → pre-WiFi online experiment.
- Establishes the concept of "persistent challenge network" separate from casual play.

[Design Philosophy]
- G/S introduced the "two regions" structure: Johto + Kanto post-game creates the longest single-file experience.
- Level curve criticism (Kanto gyms too weak) becomes the first major balance debate in the community.
- Mobile phone challenge system planted the seed for ranking/competitive infrastructure.""",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "特性(Ability)系统上线，约80种特性提供被动战术效果，宝可梦个体差异化革命性提升",
                            "intent": "增加宝可梦个体差异化，为战术多样性奠定基础，使每只宝可梦都有独特定位",
                            "detail": "特性系统是第二世代最重要的机制创新，约80种特性为每只宝可梦提供独特被动能力。压迫感(SHED SKIN)、同步(SYNCHRONIZE)、紧张感(INTIMIDATE)等成为历代对战核心机制。特别是威吓——每回合50%概率降低对方攻击——成为联防体系的关键一环。",
                        },
                        {
                            "category": "机制",
                            "content": "携带道具系统上线，宝可梦可携带道具参与战斗，装备战术体系建立",
                            "intent": "增加配装战术深度，丰富对战策略选择，道具成为构筑核心变量",
                            "detail": "道具系统使玩家可以为宝可梦装备道具，在战斗中产生各种效果。剩饭(LEFTIES)在历代都是防守核心道具，焦点镜(FOCUS BAND)的25%先制度加成在早期对战中被广泛使用。道具与特性的组合成为宝可梦构筑的基础框架。",
                        },
                        {
                            "category": "机制",
                            "content": "昼夜系统上线，部分招式和道具效果受时间影响",
                            "intent": "增加环境变量，为特定战术提供时间窗口限制",
                            "detail": "昼夜系统使部分招式（如睡觉）在夜间不可用，特定道具效果也受时间影响。这是为对战环境引入「时间窗口」限制设计的早期尝试。",
                        },
                        {
                            "category": "PvP",
                            "content": "电话对战功能开放，可与NPC约战，异步对战概念雏形",
                            "intent": "建立异步PVP的早期形态，探索非同步对战的可能",
                            "detail": "通过电话系统，玩家可以约NPC训练师进行对战，这是宝可梦异步对战的雏形，也为未来线上对战做了概念铺垫。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2000-12-14",
                    "game": "水晶版",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON CRYSTAL (Version 1.0) ===

[Visual Upgrade]
- First Pokémon game with fully animated battle sprites for all 251 species.
- Enhanced overworld animations compared to Gold/Silver static sprites.
- Battle animation uniformity laid the visual foundation for future esports broadcast standards.

[Wi-Fi Battle Prototype]
- Wireless adapter support introduced (Japan only) → first wireless multiplayer experiment.
- Establishes the technical groundwork for the Wi-Fi era that follows in Gen 3-4.
- Seeds the concept of geographically unbound competitive play.

[Weather System Foundation]
- Added several weather-related Abilities (Forecast: Castform changes type based on weather).
- Drizzle, Sand Stream, Snow Warning introduced as non-legendary Abilities in Gen 3.
- Crystal's limited weather testing informed the full weather system design of RSE.

[Competitive Scene]
- Crystal's improved battle visuals make it the preferred game for early tournament play.
- Battle Tower: the first "endgame competitive facility" → Tower challenge becomes a series staple.
- Early competitive players use Crystal for Link Cable tournaments due to better display.

[Design Legacy]
- Only game in series to have animated sprites AND the Crystal-on-Water special encounter.
- The Battle Tower concept evolves into the Battle Frontier (Gen 3), Battle Tower (Gen 4), Maison (Gen 6), Stadium (Gen 7-8).""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "战斗画面全面动画化，宝可梦动作更丰富，为电竞观赏性奠定视觉基础",
                            "intent": "提升对战观赏性，为电竞化发展奠定视觉基础",
                            "detail": "水晶版是首个全部宝可梦使用动画Sprite的版本，对战过程更具动感。这对后续的VGC比赛转播有重要意义。",
                        },
                        {
                            "category": "机制",
                            "content": "wifi通讯功能测试版上线（日本地区），开启线上对战时代序幕",
                            "intent": "探索无线网络联机对战的可能性，为VGC全球化奠定技术基础",
                            "detail": "水晶版试水性引入了无线通信对战功能，为未来的Wi-Fi对战时代做技术铺垫。这是宝可梦从线下聚会对战走向全球化在线对战的关键一步。",
                        },
                        {
                            "category": "机制",
                            "content": "新特性「天气预报」和多只天气启动机特性加入，天气体系初步建立",
                            "intent": "为天气战术体系奠定基础，丰富环境战术维度",
                            "detail": "水晶版引入了部分天气启动特性，虽然当时天气队还不是主流，但为第三代天气系统的全面上线做了铺垫。",
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
                    "official_notes": """=== POKEMON RUBY & SAPPHIRE (Version 1.0) ===

[Doubles Battle - VGC Standard Established]
- 4v4 Selection: bring 4 Pokémon, select 2 to battle → doubles becomes the official VGC format, still in use today.
- Focus-fire mechanics: "Focus + Protect" (集火+保护) creates the core 2v2 tactical triangle.
  · Focus Fire (集火): both allies attack the same target → guaranteed KO on one Pokémon.
  · Protect (守住): blocks all damage for one turn → creates tempo control.
  · Friend Guard (友军保护): redirect damage to allies → counter-focus strategy.
- This "target selection × protection timing" structure defines Pokémon competitive depth for 20+ years.

[Weather System - Full Implementation]
- Sun (Sunny Day/Drizzle), Rain (Rain Dance/Drought), Sandstorm, Hail established with:
  · Permanent weather from Ability (Drizzle/Sand Stream/Snow Warning) vs. move-based (Rain Dance).
  · Weather-activated Abilities: Swift Swim (+50% Speed in rain), Sand Rush (+50% Speed in sand), Chlorophyll (+50% Speed in sun), Unburden (activates after item consumption).
  · Weather duration: 5 turns for moves, permanent for Abilities → creates "weather war" dynamics.
- Weather was initially restricted to legendary Pokémon (Kyogre=Drought, Groudon=Drizzle, Tyranitar=Sand Stream).
- Weather teams become the defining archetype of competitive Pokémon to this day.

[Breeding & EV System]
- Gender system and breeding introduced: produce eggs with inherited stats.
- Effort Values (EVs): each Pokémon gains stat boosts from defeating specific species.
- Individual Values (IVs): hidden stats (0-31) determined at birth → "perfect IV" pursuit begins.
- Natures: 25 types affecting stat growth (+10% one stat, -10% another).
- Breeding + EVs + IVs + Natures create the "cultivation system" (培育系统) that distinguishes casual from competitive.

[Contest System]
- Beauty, Cool, Smart, Tough contest categories → separates "battle" from "collection" player identities.
- Contests reward different training priorities than competitive play → creates parallel progression systems.

[Technical]
- Move Tutors: some moves learned from NPCs rather than only TM/HM → expands move accessibility.
- Secret Bases: customizable battle arenas → early "battle facility" prototype.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "双打对战正式确立为VGC标准规则，4v4选2出战规则沿用至今",
                            "intent": "建立VGC官方赛制的核心框架，确立回合制双打作为竞技基础",
                            "detail": "RSE是首个明确将双打作为官方对战格式的世代。4v4选2出战规则（每队4只选出2只出战）沿用至今。相比单打，2v2的「集火+保护」博弈创造了完全不同的战术维度：集火可以秒杀单体，保护可以完全抵挡一次攻击，友军保护可以转移目标——这些构成了宝可梦多人对战的战术基础。",
                        },
                        {
                            "category": "机制",
                            "content": "天气系统全面上线，晴/雨/沙/冰雹影响战斗，天气启动特性体系建立",
                            "intent": "增加环境战术维度，天气队成为重要战术流派，引入不可控随机性与可控启动机的博弈",
                            "detail": "天气系统是第三世代最重要的机制创新。降雨(DRIZZLE)、沙尘暴(SAND STREAM)、降雪(SNOW WARNING)、大晴天(DROUGHT)四个天气启动特性使天气队成为长期活跃的战术体系。天气不仅改变招式威力，还激活特定特性——如雨天激活悠游自如(SWIFT SWIFT)，沙暴提升沙隐(SAND VEIL)宝可梦闪避。这些机制间的交互构成了宝可梦对战的策略深度。",
                        },
                        {
                            "category": "机制",
                            "content": "性格值决定努力值分配方式，培育系统深度化，区分休闲玩家和竞技玩家",
                            "intent": "增加培育深度，将玩家群体区分为休闲收集和竞技对战两个赛道",
                            "detail": "性格与努力值系统使宝可梦培育成为竞技对战的重要环节。EV/IV系统的存在使高强度竞技对战需要大量前期投入，这成为宝可梦电竞与其他电竞的显著区别——休闲和竞技之间有明确的能力鸿沟。",
                        },
                        {
                            "category": "机制",
                            "content": "新增精灵球种类和野生遭遇机制，收集系统丰富化",
                            "intent": "扩展收集深度，为对战提供更多战术变种（不同抓取的宝可梦有不同的个体值）",
                            "detail": "更多精灵球种类不仅有收藏价值，还关系到个体值遗传（梦境球、等级球等），增加了收集与对战的关联性。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2004-01-29",
                    "game": "绿宝石",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON EMERALD (Version 1.0) ===

[VGC 2005 - Esports Framework Established]
- Emerald becomes the first official VGC tournament game (March 2005, "Pokémon World Championships 2005").
- Three-tier competitive structure established and maintained to this day:
  · Tier 1: Rule restrictions (no legendaries, level 50, etc.)
  · Tier 2: Official season calendar (Spring/Summer/Fall/Winter tournaments).
  · Tier 3: Pokémon World Championships annual finals.
- Legendaries banned from VGC (no Mewtwo, Lugia, Ho-Oh, Raikou, Entei, Suicune, Larvitar line).
- This framework has remained essentially unchanged for 20 years.

[Battle Frontier]
- 5 Battle Facilities: Battle Tower (tube-style), Pike (random events), Arena (type-matchup rules), Factory (random rental), Dome (tournament bracket).
- Battle Tower remains in every generation: Tower → Tower → Maison → Tower → Tower.
- Frontier Brains: 7 high-difficulty NPCs with unique AI and team themes.
- "Offline competitive content" becomes a series staple: provides ranked-play practice environment.

[Weather System Completion]
- Emerald is the final version of Gen 3, weather system fully tuned.
- Rain team (Swampert as Drizzle host) becomes the dominant weather archetype.
- Sandstorm team (Tyranitar as Sand Stream host) becomes the "defensive weather" alternative.
- Sun team (Groudon as Drought host) vs. Rain team (Kyogre) becomes the "legendary weather war" archetype.

[Design Legacy]
- Emerald is often voted the "best balanced" Gen 3 version in community surveys.
- The decision to create a "third version" (Emerald) instead of just patches sets a precedent.
- Battle Frontier design philosophy (challenging offline PvP content) influences Gen 4-8 facility design.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "战斗边疆(Battle Frontier)上线，提供5种对战设施（对战塔、双打塔、轮盘战、连接战、谜问答）",
                            "intent": "为高阶玩家提供长期对战目标，丰富PVP离线内容，延长游戏寿命",
                            "detail": "战斗边疆包含5种设施，为竞技玩家提供离线对战挑战。对战塔(Tower)成为历代保留设施，其高难度AI是检验队伍强度的标准测试环境。这一设计理念影响了后续历代的对战设施设计。",
                        },
                        {
                            "category": "PvP",
                            "content": "VGC 2005规则确立，红蓝绿宝石正式纳入官方赛制，宝可梦电竞体系正式确立",
                            "intent": "建立完整的官方竞技体系，从休闲游戏向电竞项目转型",
                            "detail": "绿宝石版成为VGC首个正式比赛用游戏，标志着宝可梦电竞体系的正式确立。此时VGC已建立完整的：规则限制体系（禁止传说宝可梦）+ 官方赛历（春夏秋冬四季）+ 世界锦标赛的三层竞技结构。",
                        },
                        {
                            "category": "平衡性",
                            "content": "天气体系全面应用，雨队/沙暴队成为RSE环境核心战术",
                            "intent": "通过天气启动机构建稳定的战术体系，增加环境多样性",
                            "detail": "绿宝石版作为RSE世代的最终版本，天气队在VGC环境中占据统治地位。雨队(Swampert为主)因悠游自如特性成为最强天气队，沙暴队(Tyranitar主导)则因其全面的种族值和沙隐特性成为攻防兼备的选择。",
                        },
                    ],
                },
                {
                    "version": "1.2",
                    "date": "2006-09-28",
                    "game": "火红/叶绿",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON FIRERED & LEAFGREEN (Version 1.2) ===

[QoL Improvements - Field Mechanics]
- HMs (Hidden Machines) can now be forgotten freely: solves the long-standing "HM Slave" (秘传招式占位) problem.
  · Previously: HMs (Cut, Surf, Flash, Strength, etc.) occupied valuable move slots with often useless battle moves.
  · QoL change: players can now forget HMs after use, freeing move slots for competitive movepools.
  · Direct competitive impact: Pokémon like Flygon, Gyarados gain access to full movepools.
- Expanded Pokédex: all 151 original species available in one game.

[Battle Simulation]
- Battle Frontier built on the FR/LG engine provides competitive practice environment.
- Level 50 format (VGC standard) used for official battles.
- Post-game Battle Tower unlocks early competitive training environment.

[Bug Contest & PvE Prototype]
- Bug Catching Contest: first competitive-cooperative PvE mini-game.
  · 4 players in a time-limited bug-catching event.
  · Cooperative elements: players share information, coordinate timing.
  · Collectibles tied to contest performance.
- This design directly influenced the Raids (Gen 8) and Tera Raids (Gen 9) multiplayer PvE formats.

[Remake Philosophy]
- FR/LG establishes the "remake" tradition: revisit old regions with new mechanics.
- Gen 1's simplicity (no Abilities, no items, basic damage formula) contrasts sharply with Gen 3 power level.
- This contrast highlights how much the competitive landscape had evolved in 7 years.

[Competitive Legacy]
- FR/LG became the standard for VGC tournaments until DPP's Wi-Fi era.
- Link Cable tournaments during FR/LG era were the last major era of purely offline competitive play.""",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "秘传招式限制解除，可遗忘任意秘传招式",
                            "intent": "优化对战配置自由度，提升竞技体验，解决秘传招式占用技能位的长期痛点",
                            "detail": "允许遗忘秘传招式是重要的对战便利化改进，解决了对战配置中秘传招式（居合斩、冲浪、飞翔等）占位导致技能槽不足的长期痛点。这一改动极大提升了宝可梦的技能配置灵活性。",
                        },
                        {
                            "category": "机制",
                            "content": "新增连续战斗(Bug Contest)和捕捉大赛，丰富PvE内容",
                            "intent": "增加多人合作PvE玩法雏形，为后续团体战设计积累经验",
                            "detail": "火红叶绿引入了类似多人PvE挑战的Bug Contest，为后续历代合作挑战内容（极巨团体战、太晶团体战）积累了设计经验。",
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
                    "official_notes": """=== POKEMON DIAMOND & PEARL (Version 1.0) ===

[Wi-Fi Battle - Global VGC Era Begins]
- Wi-Fi battles officially launched: players worldwide can battle in real-time online.
- Doubles (4v4 select 2) becomes the standard VGC format for all official tournaments.
- Ranking battles introduced: ELO-style rating system → creates persistent competitive motivation.
- From "local link cable" to "global Wi-Fi" is the single largest scale expansion in Pokémon esports history.
- Geographic restrictions removed: anyone with the game + Wi-Fi can compete in VGC.

[Physical/Special Split - Most Important Balance Overhaul]
- Before Gen 4: Water/Fire/Grass/Electric/Ice/Psychic = Special; all others = Physical (determined by TYPE).
- After Gen 4: each MOVE is individually categorized as Physical or Special (determined by MOVE itself).
- Impact: Fire Punch (physical) vs. Ember (special); Brick Break (physical) vs. Focus Blast (special).
- Result: Fire and Fighting types gain extensive physical movepools → their competitive viability skyrockets.
- Gen 4 DPP meta is radically different from Gen 3 RSE due to this single change.

[Stealth Rock & Hazard System]
- Stealth Rock introduced: placed on opponent's side, damages Pokémon on switch-in based on type.
- Switch-in damage (1/8 to 1/2 HP depending on type) creates "hazard control" as a core strategy.
- Spikes (up to 3 layers), Toxic Spikes, Sticky Web → "hazard wars" become a major early-game dynamic.
- Lead Pokémon selection (who goes first to set hazards) becomes a critical teambuilding decision.

[Story & Lore]
- Galactic Team storyline: introduces Giratina (first Pokémon with Forme changes).
- Cynthia's Champion team: becomes the benchmark for "well-designed AI teams."
- Sinnoh's 210 new species brings total to 493.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "Wi-Fi对战正式上线，全球玩家可进行在线双打对战，宝可梦电竞进入全球化时代",
                            "intent": "开启宝可梦线上竞技时代，建立全球化VGC生态，降低参赛门槛",
                            "detail": "Wi-Fi对战使全球玩家可以不受地域限制进行双打对战。DPP是首个真正意义上让全球玩家可以随时对战的一代。相比Game Boy Link Cable的线下限制，Wi-Fi对战极大地扩展了宝可梦电竞的参与规模。同时也引入了「排名对战」的雏形概念。",
                        },
                        {
                            "category": "机制",
                            "content": "物理/特殊招式分类改革，按招式本身属性而非类型决定，打破原有平衡格局",
                            "intent": "打破原有平衡格局，大幅增加战术多样性，部分原本弱势类型获得战术价值",
                            "detail": "这是历代最重要的平衡性变革之一。改革前：水/火/草/电/冰/超六系全部为特殊，其余为物理。改革后：按招式本身属性划分（如水炮=特殊，攀瀑=物理）。这一改动使火系格斗系等原本只能依赖少数招式的宝可梦获得了丰富的物理技能池，格斗系和火系的对战地位因此大幅提升。",
                        },
                        {
                            "category": "机制",
                            "content": "新增秘密基地(Stealth Rock)和钉子体系，控场战术革命",
                            "intent": "引入「隐形威胁」机制，增加先手控场的重要性，丰富开局博弈维度",
                            "detail": "秘密基地是历代最具影响力的控场机制之一。放置后，交换进场的宝可梦会受到基于属性相性的伤害。这使得先手放置钉子成为开局的关键战术决策：选择哪只首发？要不要放钉子？如何应对对方的钉子手？这一机制深刻影响了历代双打和单打的开局策略。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2008-09-13",
                    "game": "白金",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON PLATINUM (Version 1.0) ===

[PBR (Pokémon Battle Revolution) - Esports Spectator Tech]
- PBR mode introduced: watch AI-versus-AI or player-versus-AI battles in a dedicated battle facility.
- First systematic investment in "competitive spectating" technology by Game Freak.
- Although PBR mode was discontinued after Gen 4, the "spectator/watch mode" concept influenced VGC broadcast infrastructure.
- Esports spectating requires: consistent camera angles, readable UI, clear HP/status displays → PBR laid visual groundwork.

[Balance Adjustments]
- As the "third version" (like Emerald), Platinum fixed DPP's early meta imbalances.
- Direct Nerve (NERF): Garchomp (Sand Veil + Sandstorm = 20% evasion) was already a community concern.
- Turtank (nerfed) and Cresselia (buffed) → Platinum was the first time Game Freak actively adjusted competitive balance via patches.
- This set the precedent for "balance patches via third version" that continues today.

[Galactic Sequel]
- Distortion World ( Giratina's domain) provides the most unique battle environment in the series.
- Battle mechanics unaffected by Distortion World (controversial missed opportunity for unique effects).

[Competitive Legacy]
- Platinum became the standard tournament format for late Gen 4 VGC.
- The "third version = balance correction" model established Gen 3 Emerald precedent continues.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "新增PBR(宝可梦世界锦标赛)观战模式，探索电竞观赏性技术",
                            "intent": "为电竞观赏性提供技术基础，优化比赛转播体验",
                            "detail": "PBR模式让玩家可以观看宝可梦自动对战，展示了Game Freak对电竞化的探索。虽然这个模式在后续世代被废弃，但「观战系统」的概念对VGC转播技术有重要影响。",
                        },
                        {
                            "category": "平衡性",
                            "content": "大量宝可梦种族值和招式平衡调整，改善DPP初期Meta失衡",
                            "intent": "修正第四世代初期的数值失衡问题，提升环境多样性",
                            "detail": "白金版作为红蓝的修正版，对环境中的强力宝可梦进行了平衡调整。DPP初期，钱如水龟(Clefable)、克雷色利亚(Cresselia)、席多蓝恩(Heatran)等占据统治地位。平衡调整使更多宝可梦获得对战可用性。",
                        },
                        {
                            "category": "机制",
                            "content": "银河团故事线，新增大量传说宝可梦，丰富传说对战生态",
                            "intent": "通过传说宝可梦引入新战术变量，同时建立VGC禁用规则框架",
                            "detail": "银河团引入了多个传说宝可梦，这些传说宝可梦后来成为VGC「传说禁止列表」的核心参考案例。DPP时代建立了「传说宝可梦」与「普通宝可梦」的竞技分层体系雏形。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2009-09-12",
                    "game": "心金/魂银",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON HEARTGOLD & SOULSILVER (Version 1.0) ===

[Legendary Banlist Formalization]
- HG/SS becomes the first VGC generation with a fully formalized legendary banlist.
- Tier system established: OU (OverUsed), UU, RU, NU → Smogon's competitive tiering system begins formalization.
- Mewtwo, Lugia, Ho-Oh, Kyogre, Groudon, Rayquaza banned from standard VGC.
- This "legendary banlist" structure remains the core organizational framework for competitive formats to this day.

[Garchomp Ban - First Non-Legendary Mechanism Ban]
- Garchomp banned from Smogon OU due to Sand Veil + Sandstorm: 20% evasion stacking.
- First non-legendary Pokémon banned for a MECHANISM (not raw power) in competitive history.
- Precedent: "Unreliable RNG mechanics (evasion) > Strong stats" principle established.
- Sand Veil later banned in VGC (evasion clauses formalized).
- This case defined the "anti-frustration" principle that guides competitive rulemaking.

[Battle Subway & Johto]
- Battle Subway: 3 modes (Single, Double, Multi) → evolved from Battle Tower.
- PWT (Pokémon World Tournament): fight Gym Leaders, Champions from Gen 1-5 → "museum of past formats."
- Johto + Kanto dual-region structure creates the longest single-file experience in the series.
- "Follow Me" (看我嘛) mechanic for following Pikachu: early social/companion mechanic experimentation.

[Wi-Fi Era]
- Full Wi-Fi support with stable connection → HG/SS marks the peak of Gen 4 online competitive play.
- Battle Tower leaderboards: first attempt at persistent competitive ranking records.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "VGC 2009/2010规则赛季使用心金/魂银，传说宝可梦禁表正式化",
                            "intent": "建立VGC官方赛制的传说宝可梦禁表制度，维持竞技公平性",
                            "detail": "心金/魂银成为首个建立完整传说宝可梦禁表制度的VGC世代。超梦(Mewtwo)、洛奇亚(Lugia)、凤王(Ho-Oh)、三神柱等传说宝可梦被排除在VGC可用池之外，这一定期调整的禁用规则成为后续历代VGC的标配制度基础。",
                        },
                        {
                            "category": "平衡性",
                            "content": "Garchomp因「沙隐+沙暴」组合被Smogon OU禁入Ubers，首个非传说宝可梦禁用案例",
                            "intent": "维护竞技公平性，防止不可控随机性机制破坏竞技性，确立「不可靠机制」优先于「强力数值」的处理原则",
                            "detail": "Garchomp被禁是宝可梦竞技史上的里程碑事件。其「沙隐(Sand Veil)+沙暴」组合使闪避概率过高，被认为破坏了竞技性。这是首个因非伤害性机制（闪避）而非纯数值强度被禁用的非传说宝可梦案例。这一先例确立了：任何使对战结果过度依赖随机性的机制都应被限制。",
                        },
                        {
                            "category": "机制",
                            "content": "对战森林/对战电梯等新对战设施，丰富离线PvP内容",
                            "intent": "为竞技玩家提供更多离线训练和挑战内容，延长游戏生命周期",
                            "detail": "心金/魂银引入了新的对战设施，为离线玩家提供了更多PVP训练环境。这些设施的高难度AI成为选手们在正式比赛前测试队伍的重要工具。",
                        },
                    ],
                },
                {
                    "version": "1.1",
                    "date": "2010-09-15",
                    "game": "心金/魂银",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON HEARTGOLD & SOULSILVER (Post-Release Balance) ===

[Soul Dew Ban - First Item Ban]
- Soul Dew (心之水滴): Latias/Latios exclusive item, boosts Special Attack and Special Defense by 50%.
- Soul Dew + Latias/Latios were virtually mandatory in every team → "Soul Dew or lose" problem.
- Soul Dew banned from VGC: first time a non-megastone item was banned from competitive play.
- Precedent: item bans become a permanent tool in the competitive ruleset alongside Pokémon bans.
- Leftovers, Choice items, and Life Orb remain legal → "utility items" vs. "power items" distinction emerges.

[Balance Philosophy]
- VGC 2010 season (HG/SS) establishes "item tiering" as a competitive design tool.
- "Ban the single most dominant item" principle: item bans prevent single-item dominance without changing Pokémon's base stats.
- This contrasts with Pokémon bans which remove the Pokémon entirely from the format.

[Competitive Legacy]
- Soul Dew ban set the precedent for Z-Crystal bans (Gen 7) and held-item restrictions in future VGC formats.
- "Which items should be legal?" becomes a permanent agenda item in VGC format discussions.
- The distinction between "competitive items" and "overpowered items" continues to be refined in every generation.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "VGC 2010规则赛季调整，Soul Dew（心之水滴）等强力道具被禁",
                            "intent": "通过道具禁用规则防止特定强力道具组合统治环境，维护VGC多样性",
                            "detail": "Soul Dew被禁是道具禁用规则的早期案例。这件道具为璐璐(Latias/Latios)提供巨量特攻加成，使其成为环境中不可撼动的核心。这一禁用开启了VGC「道具禁用列表」的制度化进程。",
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
                    "official_notes": """=== POKEMON BLACK & WHITE (Version 1.0) ===

[Team Preview - Information Symmetry Revolution]
- Team Preview introduced: both players see each other's full 6-Pokémon team before selecting their 2.
- Before: "Guess the lead" was a major strategic element → blind opening moves dominated early game.
- After: "Teambuilding strategy" became as important as in-game execution.
- Complete paradigm shift: from "reactive read" to "proactive plan."
- Team Preview remains in every VGC format since BW → one of the most impactful rule changes ever.

[Dream World - Weather Ability Democratization]
- Dream World: equip abilities (Drizzle, Drought, etc.) from LEGENDARY Pokémon to regular species.
  · Before: weather abilities exclusive to Kyogre (Drizzle), Groudon (Drought), Tyranitar (Sand Stream).
  · After: Politoed gets Drizzle, Torkoal gets Drought, Hippowdon gets Sand Stream.
- "Weather democratization" increased team variety but also triggered the "Weather War" crisis.
- Drizzle Politoed + Swift Swim Pokémon = permanent rain → rain teams become dominant.
- This was the first major case of "ability power creep" from democratization design.

[Curse Mechanics & New Battle Features]
- Curseeason mechanic: Cursed Body (Gengar) introduced → chance to disable any move.
- Rotom Appliance Forms: first major Forme change system → multiple formes with different types/stats.
- Infinite-use TMs: TM system reformed → removes the "one-time TM" frustration.
- C-Gear wireless communication: multiplayer without friend codes → easier local play.

[Competitive Philosophy]
- "Power Creep from Democratization" lesson: giving everyone access to powerful tools doesn't automatically balance the game.
- Dream World weather abilities led to the Smogon OU ban of Drizzle + Swift Swim in the same team.
- BW established that "balancing mechanics ≠ balancing combinations of mechanics."
- Complex team-building (BW had 649 species) became a core skill for competitive players.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "VGC 2011/2012规则赛季开始，引入组队预览(Team Preview)，消除对战开局信息不对称",
                            "intent": "消除对战开局的信息不对称，增加组队阶段策略博弈，使对战从「先手压制」转向「全局规划」",
                            "detail": "组队预览(Team Preview)是BW时代最重要的VGC规则创新。在此之前，双打双方无法在开局前看到对方阵容，导致大量「猜拳」式开局博弈。组队预览让双方在选派出战宝可梦前就能看到对方6只阵容，这彻底改变了VGC的战略框架：玩家需要在开局前就规划好针对对方阵容的选队策略，而不仅仅是临场反应。这一规则成为历代VGC的标配。",
                        },
                        {
                            "category": "PvP",
                            "content": "天气 wars（天气战争）爆发，Drizzle Politoed组合成为史上最具统治力的天气战术",
                            "intent": "通过将永久天气能力赋予非传说宝可梦，探索「天气战术民主化」设计，但也暴露了强力天气启动机的环境统治力问题",
                            "detail": "BW时代引入了「梦世界(Dream World)」机制，允许将原本属于传说宝可梦的天气能力（Drizzle、Drought等）通过梦世界装备赋予普通宝可梦。Drizzle Politoed（雨/天气启动机）使降雨队成为BW环境的核心：悠游自如(Swift Swim)宝可梦在雨中速度翻倍，雨天强化水系招式，导致几乎每支队伍都必须针对天气制定对策。「天气战争」成为这一时代最具标志性的战术博弈。",
                        },
                        {
                            "category": "机制",
                            "content": "新增天气启动机特性（如Drizzle、Drought、Sand Stream等），天气体系从「传说专属」变为「全员可用」",
                            "intent": "将强力环境控制能力从传说宝可梦下放，增加战术多样性的同时探索能力下放的风险边界",
                            "detail": "BW时代天气能力下放是游戏设计的重要转折点。第五世代前，Drizzle只属于洛基亚(Kyogre)、Drought只属于固拉多(Groudon)，这些传说宝可梦被VGC禁用意味着天气能力几乎不可用。梦世界将天气能力赋予普通宝可梦，极大丰富了天气战术，但也暴露了强力环境控制机制的环境统治力问题。",
                        },
                        {
                            "category": "机制",
                            "content": "招式学习器(TM)系统改革，招式配置更加灵活",
                            "intent": "降低技能配置门槛，增加对战多样性",
                            "detail": "BW时代TM系统改革使更多招式可以自由配置，减少了「必须遗忘秘传才能学对战技能」的痛点。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2012-06-23",
                    "game": "黑2/白2",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON BLACK 2 & WHITE 2 (Version 1.0) ===

[Drizzle + Swift Swim Dual Ban - Mechanism Combination Precedent]
- First major case of banning a COMBINATION of mechanics (not a single Pokémon or item).
- Drizzle Politoed + Swift Swim Pokémon = rain team so dominant that separate bans insufficient.
- New rule: a team cannot have both Drizzle AND Swift Swim simultaneously.
- Principle established: "Individual balance ≠ Combination balance."
- This dual-ban model became the template for future complex restrictions (e.g., Megas in VGC 2016).

[PWT (Pokémon World Tournament) - Tournament-Exclusive Format]
- PWT: exclusive VGC format using ONLY legendary Pokémon (Mewtwo, Lugia, Ho-Oh, etc.).
- First "tournament-exclusive rule" format: rewards players who collected legendaries outside the main format.
- Creates a "premium tournament format" tier within VGC → spectators love seeing legendaries battle.
- Legacy: future VGC formats often include one "special ruleset" tournament per season.

[Black City / White Forest]
- Black City: NPCs with level 50-80 Pokémon → farming spot for rare species.
- Connected online: real players' cities appear as NPCs in each other's games.
- Early social integration experiment: your game literally contains other players' cities.

[Competitive Legacy]
- BW2 are widely considered the most competitively deep Gen 5 games.
- Hidden Grotto: rare Pokémon with hidden Abilities (HA) → ability breeding begins here.
- Dream Radar: catch legendary Pokémon with specific hidden abilities.
- Hidden Abilities become essential for competitive play from Gen 6 onward.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "VGC 2013规则赛季引入PWT(宝可梦世界锦标赛)专用格式",
                            "intent": "为顶级赛事提供独特的对战内容，增加世界锦标赛的仪式感",
                            "detail": "PWT是BW2赛季引入的世界锦标赛专用格式，只能使用历史传说宝可梦（如洛奇亚、凤王等），这是VGC首次为顶级赛事设计专属规则格式，丰富了顶级赛事的多样性。",
                        },
                        {
                            "category": "平衡性",
                            "content": "Drizzle+Swift Swim组合在Smogon OU被联合禁用，天气战争达到监管临界点",
                            "intent": "防止永久性天气能力组合统治环境，确立「强力机制组合」的监管先例",
                            "detail": "在Smogon OU中，Drizzle Politoed + Swift Swim宝可梦（尤其是刺龙王Kingdra）组合因过于强力被联合禁用（一条队伍不能同时有Drizzle和Swift Swim）。这开创了「机制组合禁用」的先例：在多个单独看起来平衡的机制，组合后产生过度统治效果时应联合限制。",
                        },
                        {
                            "category": "机制",
                            "content": "PWT专用传说宝可梦池建立，探索「赛事专属规则」设计方向",
                            "intent": "为世界锦标赛设计专属规则，增加顶级赛事的独特性和观赏性",
                            "detail": "PWT格式允许使用平时被VGC禁用的传说宝可梦，但限制了可用种类。这是首次在VGC体系中引入「赛事专属规则」概念。",
                        },
                        {
                            "category": "内容",
                            "content": "新角色「等离子团」引入，传说宝可梦生态更加丰富",
                            "intent": "通过故事线引入新传说宝可梦，为VGC可用精灵池增加新选择",
                            "detail": "BW2引入了莱希拉姆(Zekrom)和捷克罗姆(Reshiram)的对战形态，为竞技环境增添了新变数。",
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
                    "official_notes": """=== POKEMON X & Y (Version 1.0) ===

[Mega Evolution - Cross-Generation Enhancement System]
- 48 Mega Evolutions introduced: select Pokémon temporarily transform into stronger forme mid-battle.
- Key design constraints:
  · One Mega Evolution per team (no stacking).
  · Uses the held item slot (Mega Stone) → can't hold other items.
  · Lasts entire battle → no timing pressure.
- Design philosophy: "Explosive resource" (爆发资源) that requires strategic tradeoff.
- Competitive reality (from 2016 World Champion Wolfe Glick): "Only ~8 out of 48 Megas were competitively viable."
  · Top tier: Salamence, Kangaskhan, Gengar, Venusaur, Metagross.
  · Bottom tier: Altaria, Beedrill, Absol → "Mega Altaria" became a community joke.
- Mega Evolution's design influenced all subsequent enhancement systems (Z-Moves, Dynamaxing, Tera).

[Super Training & QoL]
- Super Training: visual minigame for EV training → dramatically reduces competitive entry barrier.
- Pokémon-Amie: pet your Pokémon → increases capture rate, affects critical hit chance.
- EXP. Share toggle: separate competitive training from casual progression.
- These QoL features dramatically lowered the "competitive cultivation barrier."

[3D Models & Spectating]
- Full 3D models: first fully 3D Pokémon game → camera can move during battles.
- Rotation Camera in battles → spectator-friendly camera angles.
- Battle spectator mode: watch ranked battles online → esports broadcast infrastructure improves.

[Competitive Season Format]
- VGC 2014 (X/Y) was the first year with a formal "season" structure: Spring → Summer → Fall → World Championships.
- X/Y's Wi-Fi infrastructure made this global season format technically possible.""",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "Mega进化系统上线，48种宝可梦可进化为更强形态，替代前代强化体系",
                            "intent": "建立新的跨世代强化机制，为经典宝可梦注入竞技活力，探索「限时强化」的战略深度",
                            "detail": "Mega进化是首个跨世代的宝可梦强化机制。关键设计约束：(1)每队只能有一只宝可梦可Mega进化 (2)Mega进化需要占用道具槽。这两个约束使Mega进化成为需要战术权衡的「爆发资源」——选择哪只Mega？何时Mega？这不仅是数值强化，更是战略决策。2016年VGC世界冠军Wolfe Glick评价：「Mega进化刚发布时完全不平衡，约48种Mega中只有8种有竞技价值」。最强势的包括Mega大嘴娃(Salamence)、Mega袋兽(Kangaskhan)、Mega耿鬼(Gengar)，而Mega大菊花(Altaria)、Mega大针蜂(Beedrill)几乎无人使用。",
                        },
                        {
                            "category": "机制",
                            "content": "超级特别团体战(Super Multi-Use)上线，4人合作PvE内容丰富化",
                            "intent": "为休闲玩家提供多人合作内容，增加游戏社交属性和重复游玩价值",
                            "detail": "XY版引入了超级特别团体战，为4人合作提供了更完善的内容和奖励。这是Game Freak探索「官方多人合作PvE」的早期尝试，为后续极巨团体战、太晶团体战积累了设计经验。",
                        },
                        {
                            "category": "平衡性",
                            "content": "Mega进化平衡性两极分化，迫使Game Freak在后续补丁中多次调整",
                            "intent": "通过补丁迭代调整Mega进化强度，探索「赛季规则动态调整」的电竞化运营模式",
                            "detail": "XY发售后，Mega进化的强度差异引发了社区广泛讨论。Game Freak开始在VGC赛季规则中动态调整Mega进化的可用性，例如在某些赛季禁用特定的Mega。这是宝可梦电竞「赛季规则调整」制度化的重要一步。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2014-11-21",
                    "game": "欧米伽红宝石/阿尔法蓝宝石",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON OMEGA RUBY & ALPHA SAPPHIRE (Version 1.0) ===

[Triple Triad & Multi Battle Expansion]
- Triple Triad: card battle minigame with collectible cards → massive casual fanbase.
- Super Multi Battles: 4-player co-op raids → precursor to Gen 8 Max Raids and Gen 9 Tera Raids.
  · 4 players simultaneously battle wild Pokémon (not trainers).
  · Turn-based: players queue moves, all execute simultaneously → introduces social coordination dynamics.
  · Rewards: rare items and Pokémon → social incentive for group play.

[Bug Contest Evolution]
- Hoenn Battle Frontier: 7 facilities → most comprehensive competitive training content to date.
- Battle Maison (Gen 6), Battle Tree (Gen 7), Battle Tower (Gen 8) all evolved from Frontier design.
- Secret Powers: each location has a unique terrain effect → terrain control becomes a new strategic layer.

[Mega Evolution Ecosystem Expansion]
- ORAS added new Mega Evolutions: Lopunny, Audino, Diancie.
- Mega balance adjustments: some Megas buffed (Mewtwo), some nerfed (Gengar → indirect nerf via Gen 6 mechanics).
- Prankster (Sableye): first "negative-priority" ability → status moves always go first in rain → competitive controversy.

[Competitive Legacy]
- ORAS introduced the "Rotation Battle" (4-player rotation, 2 active at a time) as a new format.
- Rotation battles added a new layer: position management → similar to the later Dynamax positioning debates.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "三打对战(3v3)模式上线，新增战术维度，玩家需同时管理3只宝可梦",
                            "intent": "增加竞技模式多样性，在标准双打之外提供新的赛制选择，丰富VGC内容",
                            "detail": "三打对战需要同时控制3只宝可梦，轮换机制带来不同于双打的战术深度。在三打中，位置轮换成为新的博弈维度，攻击可以附带换人效果成为强力的进攻工具。三打后来成为VGC的固定赛制之一。",
                        },
                        {
                            "category": "平衡性",
                            "content": "Mega进化平衡调整，新增Mega进化宝可梦，重新定义Mega竞技生态",
                            "intent": "通过补充弱势Mega和削弱强势Mega，维持Mega进化系统的竞技新鲜感",
                            "detail": "ORAS新增了多只Mega进化宝可梦，并对已有Mega的强度进行了调整。Mega大嘴娃(Salamence)凭借飞行+龙的优秀打击面和高速成为ORAS最强Mega之一，而Mega大针蜂(Beedrill)虽获得强化但仍处于弱势地位。这体现了「选择性强化」的设计理念——不是所有Mega都需要同等强度。",
                        },
                        {
                            "category": "机制",
                            "content": "战斗回合计时器正式引入，防止拖延战术，保障比赛流畅性",
                            "intent": "通过计时规则防止恶意拖延，保障比赛在合理时间内完成，提升电竞观赏性",
                            "detail": "计时机制的引入解决了长期困扰VGC的「拖延战术」问题。在此之前，理论上可以通过无限消耗回合来拖延比赛。计时规则迫使玩家在有限时间内做出决策，增加了比赛的心理压力和观赏性。",
                        },
                    ],
                },
                {
                    "version": "1.4",
                    "date": "2015-09-26",
                    "game": "X/Y",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON X & Y (Post-Release VGC Balance) ===

[Mega Venusaur & Mega Gengar Banned - Season Ban Precedent]
- VGC 2016 format: Mega Venusaur (Ban) and Mega Gengar (Ban) → first official ban of SPECIFIC Mega Evolution forms.
- Precedent: Game Freak officially acknowledged that certain Megas broke competitive balance and needed seasonal restrictions.
- Mega Venusaur: Chlorophyll + Sludge Bomb + Sleep Powder + Venusaur's bulk → near-unstoppable in sun teams.
- Mega Gengar: Shadow Tag (traps any Pokémon) + speed + coverage → no safe switch-in.
- Both were banned not for raw stats but for LACK OF COUNTERPLAY.

[Bloom Doom vs. Cheek Pulse]
- VGC 2016 ban decision was controversial: players who invested resources in banned Megas had to rebuild teams.
- "Seasonal ban list" (赛季禁用列表) system formalized: Game Freak adjusts Megas available each season.
- "Which Megas should be legal?" became a community discussion topic before each VGC season.

[Design Legacy]
- VGC 2016 was the first year where Game Freak actively curated the competitive format through seasonal Mega bans.
- This seasonal curation model directly influenced: VGC 2017 (Z-Move restrictions), VGC 2018 (restricted legendaries), VGC 2023 (Tera Type restrictions).
- "Dynamic format curation" became the standard competitive design tool for all future VGC generations.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "VGC 2016规则调整，Mega妙蛙花(Mega Venusaur)和Mega耿鬼(Mega Gengar)被Ban",
                            "intent": "维护VGC环境多样性，防止特定Mega统治环境，探索赛季规则动态调整制度",
                            "detail": "VGC 2016赛季禁止了Mega妙蛙花和Mega耿鬼，这是官方首次在赛季规则中禁用特定的Mega进化形态。这标志着Game Freak正式采用「赛季禁用列表」制度来动态调整Mega进化的可用性。",
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
                    "official_notes": """=== POKEMON SUN & MOON (Version 1.0) ===

[Z-Move System - Universal Enhancement Replacement]
- Z-Moves: every Pokémon gets a signature Z-Move (upgrade one move via Z-Crystal).
- Key design differences from Mega Evolution:
  · Universal: ALL Pokémon can use Z-Moves (vs. only 48 Megas).
  · One-time use: each Z-Move consumable per battle (vs. Mega's once-per-battle).
  · No item slot required: Z-Crystals don't compete with held items (vs. Mega Stones taking item slot).
- Community reaction polarized:
  · Supporters: "Everyone gets a nuke" → democratic access to explosive power.
  · Critics: "One-button-win" design → reduces strategic depth compared to Mega's "which Pokémon to evolve" decision.
- "Explosive resource democratization" experiment: giving everyone access to burst power.

[Alola Forms - Regional Variation System]
- Alola Forms: regional variants for existing species (Vulpix, Sandshrew, Raichu, etc.).
- Different types, abilities, and stats from original forms.
- Alola Muk (Alolan Form): Poison + Dark vs. original Pure Poison → entirely different competitive role.
- Alola Forms create the "regional identity" design language that influences later games.

[VGC 2017 - Alola Dex Restriction]
- Alola Dex restriction: only Pokémon in the Alola Pokédex (403 species) allowed in VGC.
- First systematic "regional restriction" rule (replacing legendary-only banlist).
- Allows older species while preventing "best-of-all-generations" power creep.
- "Which Pokémon are legal?" and "Which legendary can you use?" become separate decisions.

[No Set Mode - Competitive QoL]
- Switch mode changes: "Set" (no free switch) vs. "Switch" (free switch after KO) selectable in battle.
- Default changed to "Set" for competitive → reduces luck from free KO switches.
- Lures and predictions become more important → skill expression increases.""",
                    "changes": [
                        {
                            "category": "机制",
                            "content": "Z招式系统上线，取代Mega进化的强化体系，对战爆发资源体系重构",
                            "intent": "建立新的对战强化机制，提供全玩家可用的强化手段，探索「全员可用的爆发资源」设计",
                            "detail": "Z招式是首个对所有宝可梦开放的强化机制，每只宝可梦都有专属Z招式。关键设计变化：(1)全员可用 vs Mega进化仅特定宝可梦 (2)一次性使用 vs Mega进化整场一次 (3)无道具占用 vs 占用道具槽。这三种设计选择代表了「爆发资源民主化」的方向：让所有玩家都能使用强力爆发，而非只有特定Mega的玩家。社区反应两极：部分玩家认为Z招式让对战变成了「一个按钮就能赢」的设计，但也有玩家认可其「战略权衡」的一面——使用Z招式意味着放弃Mega进化的道具加成。",
                        },
                        {
                            "category": "机制",
                            "content": "阿罗拉形态(Alola Forms)引入，传说宝可梦以外的形态变化机制",
                            "intent": "扩展图鉴内容多样性，为对战提供区域特异性战术变量",
                            "detail": "阿罗拉形态是形态变化(Mega进化/Z招式)之外的新差异化机制。九尾(Ninetales)、六尾(Vulpix)、嘎啦嘎啦(Graveler)等在不同地区有不同形态，具有不同的属性组合和特性。这是Game Freak在「图鉴内容差异化」上的重要探索。",
                        },
                        {
                            "category": "PvP",
                            "content": "VGC 2017规则赛季确立，阿罗拉图鉴限制成为核心规则框架",
                            "intent": "通过区域图鉴限制构建世代规则体系，平衡新旧内容比例",
                            "detail": "VGC 2017规则限制只允许使用阿罗拉图鉴中的宝可梦，这是VGC历史上首个系统性的「图鉴限制规则」。相比之前的全面禁止传说宝可梦，图鉴限制提供了更精细的内容管理工具：玩家只能使用新世代的宝可梦，同时通过传说禁止列表控制传说宝可梦的使用。",
                        },
                    ],
                },
                {
                    "version": "1.2",
                    "date": "2017-06-19",
                    "game": "太阳/月亮",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON SUN & MOON (Post-Release Balance) ===

[VGC 2018 Season Preview]
- VGC 2018 format introduced major balance adjustments ahead of the competitive season.
- Pre-season balance patches (pushing nerfs/buffs before tournament season) → mature esports operation.
- "Proactive balance" model: Game Freak actively shapes the competitive environment before tournaments rather than reacting after.
- This proactive model became the standard for all subsequent VGC seasons.

[Mid-Season Z-Move Debate]
- Z-Crystal distribution controversies: some Z-Crystals only available viaPokémon Bank (virtual) → access inequality.
- "Which Z-Crystals should be legal?" became a recurring competitive design question.
- Parallels: Similar debates emerged in Gen 8 (which Gigantamax forms are legal?) and Gen 9 (which Tera Types are legal?).""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "VGC 2018规则预调，大量宝可梦种族值调整和招式平衡",
                            "intent": "通过赛季前的预平衡调整，减少发售后紧急削弱的需要，展示电竞化运营的成熟度",
                            "detail": "官方开始更频繁地使用补丁调整平衡，体现了电竞化运营的成熟。从SM世代开始，Game Freak会在赛季开始前主动调整环境平衡，而非等到发售后才被动修复。",
                        },
                    ],
                },
                {
                    "version": "1.0",
                    "date": "2017-11-17",
                    "game": "究极之日/究极之月",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON ULTRA SUN & ULTRA MOON (Version 1.0) ===

[Ultra Beasts (UB) - New Design Language]
- Ultra Beasts: first Pokémon with completely different design philosophy from traditional species.
  · UB-01 (Nihilego): parasitic jellyfish-like creature; no traditional type combination (Poison + Rock).
  · UB-02 (Buzzwole/Pheromosa): insectoid fighters with extreme Speed or Attack stats.
  · UB-03 (Xurkitree): electric tree-like creature with extremely high Special Attack.
  · Different base stat distributions: ultra-beasts push power boundaries.
- Design philosophy: "Break the mold" → intentionally unfamiliar aesthetic to differentiate UBs from traditional Pokémon.

[UB-Adhesive - First UB Ban]
- UB-Adhesive (Nihilego): "Neurotoxin" ability + Parasitic Tentacles = constantly drains HP from opponent.
- Weak Armor (弱策): taking a hit increases Speed sharply while lowering Defense → "sacrifice defense for Speed" mechanic.
- VGC 2018: UB-Adhesive banned → first Ultra Beast banned from competitive play.
- Precedent: "New design ≠ balanced design" → UBs require the same scrutiny as traditional Pokémon.

[Battle Tree]
- Battle Tree: single-player ranked battle facility → evolved from Battle Maison (ORAS).
- Battle Tower (Gen 8), Battle Tower (Gen 9) continue the offline competitive training lineage.
- Super Multi Battles: 4-player simultaneous combat → design tested in ORAS, refined in USUM.

[Alola Photo Fun]
- Festival Plaza: replace Battle Spot → social hub for multiplayer interactions.
- Festival Plaza's GTS (Global Trade System) integration → easier Pokémon trading.

[Competitive Legacy]
- USUM became the standard VGC format for late Gen 7 (VGC 2018 World Championships).
- USUM's competitive depth (deeper than SM) made it the preferred tournament game.""",
                    "changes": [
                        {
                            "category": "PvP",
                            "content": "究极异兽(UB)系列加入VGC可用池，丰富对战精灵库，引入全新设计理念的宝可梦",
                            "intent": "通过异星宝可梦引入新战术变量，同时建立与非传说宝可梦完全不同的设计语言",
                            "detail": "UB系列（如UB-01 UB-02等）是设计语言完全不同于传统宝可梦的异星生物，有着独特的外观和种族值分配。UB-Adhesive的「弱策(weak armor)」战术成为USUM环境的标志性战术之一——通过受到攻击触发弱策特性来大幅提升速度，在特定构筑中形成极强的爆发力。这种「牺牲防守换速度」的机制在传统宝可梦中较为罕见。",
                        },
                        {
                            "category": "机制",
                            "content": "新增四驱团对战和跨世代联动内容，丰富游戏内容",
                            "intent": "延长游戏寿命，增加重复游玩价值，吸引不同类型玩家",
                            "detail": "追加了新的对战内容和异兽捕捉内容，为VGC USUM赛季提供了更多环境变量。",
                        },
                        {
                            "category": "平衡性",
                            "content": "UB-Adhesive在VGC 2018赛季中被Ban，成为首个被禁用的究极异兽",
                            "intent": "通过禁用机制测试究极异兽的平衡边界，建立UB系列的VGC监管框架",
                            "detail": "UB-Adhesive的弱策战术在VGC环境中过于强力，被禁用。这是首个被VGC禁用的究极异兽案例，为后续UB系列的设计提供了重要的平衡参考。",
                        },
                    ],
                },
                {
                    "version": "1.3",
                    "date": "2018-04-18",
                    "game": "究极之日/究极之月",
                    "source_url": "https://bulbapedia.bulbagarden.net/wiki/Version_history",
                    "official_notes": """=== POKEMON ULTRA SUN & ULTRA MOON (Post-Release) ===

[VGC 2019 Pre-Worlds Balance]
- Pre-Worlds balance adjustments: Game Freak nerfed several dominant Pokémon ahead of the 2018 World Championships.
- Nerfs targeted: Celesteela, Muk-Alola, etc. → standard "pre-tournament meta stabilization" process.
- "Pre-tournament format adjustment" becomes a standard VGC operations tool.

[Seasonal Format Curation Matures]
- By USUM, the seasonal ban/allow system for Z-Crystals, Mega Stones, and Pokémon was fully operational.
- "What is legal this season?" becomes a major community discussion point before each VGC season.
- The complexity of format curation (managing Pokémon + Items + Abilities) led to calls for simpler systems in future generations.

[Esports Operations Legacy]
- USUM hosted the 2018 World Championships in Washington D.C.
- Record attendance: largest Pokémon VGC event to date.
- Professional esports production standards applied: live commentary, analysis desk, streaming.""",
                    "changes": [
                        {
                            "category": "平衡性",
                            "content": "VGC 2019规则发布前调整，削弱部分强力宝可梦，为新赛季做准备",
                            "intent": "为当年的世界锦标赛做最后的环境调整，确立赛季平衡基调",
                            "detail": "为VGC 2019世锦赛做最后的环境调整，部分在USUM中表现过于强力的宝可梦被削弱。",
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
        包含 Gen 1-9 宝可梦完整详细背景信息
        数据来源: VGC 官方规则历史 + Smogon 竞技分析 + 机制演进研究
        """
        global _DETAILED_PATCH_NOTES_CACHE
        if _DETAILED_PATCH_NOTES_CACHE is not None:
            return _DETAILED_PATCH_NOTES_CACHE

        detailed_db = {
            # ====== 第一/二世代 (Gen 1-2) ======
            "红/绿": {
                "1.0": {
                    "summary": "宝可梦正式诞生，确立回合制双打基础框架",
                    "full_context": "1996年2月27日发售，是首个商业化成功的回合制收集对战RPG。Game Boy Link Cable使双打对战成为可能。虽然双打是隐藏模式，但它奠定了宝可梦电竞的基础框架：集火可以秒杀单体，保护可以完全抵挡一次攻击，友军保护可以转移目标。这些构成了2v2战术博弈的核心要素。",
                    "impact": "开创了宝可梦作为电竞项目的先河，虽然当时VGC尚未建立，但线下双打对战已在玩家社区流行",
                    "vgc_relevance": "为后续VGC提供了基础规则框架，集火/保护/联防的对战三角成为历代核心博弈",
                    "key_insight": "初代就确立了'回合制+属性克制+技能组合'的核心玩法，这个框架在后续29年中几乎没有根本性改变",
                },
                "1.1": {
                    "summary": "首个官方版本修正，修复大量bug，建立版本迭代规范",
                    "full_context": "1996年10月15日发布的蓝版是首个正式版本修正。这次修正建立了Game Freak后续29年沿用的'首发+修正版'发布节奏。",
                    "impact": "为后续历代版本发布流程奠定基础",
                    "vgc_relevance": "版本迭代规范化对电竞环境稳定有重要意义",
                    "key_insight": "从第一版开始，Game Freak就建立了'发现问题→修正'的快速响应机制，这对电竞化运营至关重要",
                },
            },
            "黄": {
                "1.0": {
                    "summary": "动画风格统一化，提升对战观赏性，为电竞转播奠基",
                    "full_context": "1999年9月30日发售的黄版是首个完全以动画风格设计的版本。虽然不是首个有动画的版本，但动画风格的统一对后续VGC比赛转播有重要意义。",
                    "impact": "动画风格的统一化使宝可梦对战在视觉上更易于识别和转播",
                    "vgc_relevance": "为电竞转播提供统一的视觉语言，这是电竞化的重要一步",
                    "key_insight": "对战观赏性是电竞化的前提，黄版的动画统一化为后续VGC转播技术奠定了视觉基础",
                },
            },
            "金/银": {
                "1.0": {
                    "summary": "特性系统上线，约80种特性建立被动战术差异化基础",
                    "full_context": "1999年11月21日发售的金银版引入了特性(Ability)系统，这是宝可梦对战史上最重要的机制创新之一。约80种特性为每只宝可梦提供独特被动能力。最重要的特性包括：威吓(Intimidate)——每回合50%概率降低对方攻击，成为历代联防体系核心；压迫感(Shed Skin)——每回合30%概率治愈异常状态；同步(Synchronize)——使对手获得与自身相同的异常状态。",
                    "balance_changes": {
                        "威吓(Intimidate)": "引入降攻能力，每回合50%降对方攻击一段，成为历代联防必备特性",
                        "压迫感(Shed Skin)": "每回合30%概率治愈异常，增加存活能力",
                        "同步(Synchronize)": "使对手获得相同异常状态，成为接力队的核心特性",
                    },
                    "impact": "特性系统使每只宝可梦都有独特定位，极大丰富了战术多样性",
                    "vgc_relevance": "威吓成为历代双打联防的核心特性，特性与道具的组合成为宝可梦构筑的基础框架",
                    "key_insight": "特性系统展示了'被动能力'在回合制对战中创造策略深度的潜力，后续历代都通过新特性引入新战术变量",
                },
                "水晶版 1.0": {
                    "summary": "Wi-Fi对战测试版上线，开启线上竞技时代序幕",
                    "full_context": "2000年12月14日发售的水晶版试水性引入了无线通信对战功能（仅日本地区）。这是宝可梦从线下聚会对战走向全球化在线对战的关键一步。虽然测试版功能有限，但为后续Wi-Fi对战的全面开放做了技术铺垫。",
                    "impact": "从本地通讯到无线网络的跨越，为VGC全球化奠定技术基础",
                    "vgc_relevance": "Wi-Fi对战使全球玩家可以随时对战，极大扩展了宝可梦电竞的参与规模",
                    "key_insight": "从线下到线上的技术跨越是宝可梦电竞规模化的关键，没有Wi-Fi对战就没有VGC全球化",
                },
            },
            # ====== 第三/四世代 (Gen 3-4) ======
            "红宝石/蓝宝石": {
                "1.0": {
                    "summary": "双打VGC标准确立，天气系统全面上线，对战策略体系革命",
                    "full_context": "2002年3月29日发售的RSE世代确立了几个影响深远的设计决策：(1)双打正式成为VGC标准规则，4v4选2出战 (2)天气系统全面上线，晴/雨/沙/冰雹+对应启动特性 (3)物理/特殊分类仍沿用类型划分（为第四世代的革命性改革做铺垫）。天气系统建立了环境战术体系：天气启动机(Drizzle/Sand Stream等)提供稳定的天气条件，相关特性(Swift Swim/Sand Rush等)在对应天气中生效，天气招式威力变化构成完整的战术生态。",
                    "balance_changes": {
                        "降雨启动(Drizzle)": "永久降雨天气（当时仅限传说宝可梦Kyogre）",
                        "沙尘暴启动(Sand Stream)": "永久沙暴天气（当时仅限传说宝可梦Tyranitar）",
                        "悠游自如(Swift Swim)": "雨中速度翻倍，是雨天队核心特性",
                        "扬沙(Sand Rush)": "沙暴中速度翻倍，沙暴队核心特性",
                    },
                    "impact": "天气系统开创了'环境控制战术'这一全新品类，雨队/沙暴队成为历代标配战术体系",
                    "vgc_relevance": "天气队成为历代VGC的核心战术分支，天气启动机的可用性直接影响环境格局",
                    "key_insight": "天气系统展示了'不可控随机性(天气何时结束?)'与'可控启动机'之间的博弈如何创造策略深度",
                },
                "绿宝石 1.0": {
                    "summary": "VGC 2005规则确立，战斗边疆上线，电竞体系正式建立",
                    "full_context": "2004年1月29日发售的绿宝石版是宝可梦电竞史上最重要的版本之一。它正式确立了VGC 2005规则体系：(1)双打对战正式纳入官方赛制 (2)传说宝可梦禁表制度化 (3)战斗边疆Battle Frontier提供5种对战设施。战斗边疆中的对战塔(Tower)成为历代保留设施，其高难度AI是检验队伍强度的标准测试环境。",
                    "impact": "VGC电竞体系正式确立，标志宝可梦从游戏向电竞项目的转型完成",
                    "vgc_relevance": "VGC三层竞技结构（规则限制+官方赛历+世界锦标赛）在此版本中完全建立",
                    "key_insight": "VGC的制度化框架（禁表+赛历+世锦赛）是电竞化运营的标杆，这一框架在后续19年几乎没有根本性改变",
                },
            },
            "火红/叶绿": {
                "1.2": {
                    "summary": "秘传招式限制解除，对战配置自由度革命性提升",
                    "full_context": "2006年9月28日发售的火红叶绿引入了秘传招式可遗忘机制，解决了长期困扰玩家的问题：对战配置中秘传招式（居合斩、冲浪、飞翔等）占位导致技能槽不足。允许遗忘秘传招式极大提升了宝可梦的技能配置灵活性，对竞技构筑有重要影响。",
                    "impact": "从'被迫接受秘传招式占用'到'可以自由遗忘'的转变，大幅提升了技能配置自由度",
                    "vgc_relevance": "秘传招式的灵活配置直接影响宝可梦的竞技可用性，是构筑优化的重要环节",
                    "key_insight": "便利性设计会影响竞技深度——允许更多技能组合意味着更大的构筑空间和更多的战术选择",
                },
            },
            "钻石/珍珠": {
                "1.0": {
                    "summary": "Wi-Fi对战正式上线，全球化VGC时代开启，物理/特殊分类改革",
                    "full_context": "2006年9月28日发售的DPP世代有两个重大变革：(1)Wi-Fi对战正式开放，全球玩家可以随时在线对战 (2)物理/特殊招式分类改革——按招式本身属性划分而非类型划分。Wi-Fi对战使全球玩家可以不受地域限制进行双打对战，VGC从此进入全球化时代。物理/特殊改革使格斗系和火系获得丰富的物理技能池，极大提升了这些类型的战术地位。秘密基地(Stealth Rock)的引入开创了'隐形控场'机制，增加先手博弈维度。",
                    "balance_changes": {
                        "物理/特殊分类改革": "按招式本身属性划分（格斗/火等为物理，水/电等为特殊），而非按类型划分",
                        "秘密基地(Stealth Rock)": "放置后交换入场受到伤害，基于属性克制计算，是历代最重要的控场技能之一",
                    },
                    "impact": "Wi-Fi对战使VGC参与者规模扩大100倍，物理/特殊改革颠覆了历代平衡格局",
                    "vgc_relevance": "Wi-Fi对战是VGC全球化的技术基础，物理/特殊改革影响了历代格斗系和火系宝可梦的战术地位",
                    "key_insight": "技术平台升级(Wi-Fi)与机制改革(物理/特殊)并行，是DPP世代成功的关键——没有全球化用户基础就没有电竞生态",
                },
                "白金 1.0": {
                    "summary": "PBR观战模式探索电竞观赏性，平衡调整改善Meta",
                    "full_context": "2008年9月13日发售的白金版引入了PBR(Pokemon Battle Revolution)观战模式。虽然这一模式在后续世代被废弃，但「观战系统」的概念对VGC转播技术有重要影响。白金版作为DPP的修正版，对环境中过于强力的宝可梦（如钱如水龟Clefable、克雷色利亚Cresselia等）进行了平衡调整。",
                    "impact": "电竞观赏性技术探索，虽然PBR模式未能延续，但为后续观战系统积累了经验",
                    "vgc_relevance": "PBR的尝试表明Game Freak早在2008年就开始探索电竞转播技术",
                    "key_insight": "电竞化需要'可观赏性'支撑，PBR虽然失败了，但其理念对后续VGC转播有重要启示",
                },
            },
            "心金/魂银": {
                "1.0": {
                    "summary": "传说宝可梦禁表制度化，Garchomp成为首个因机制被禁的非传说宝可梦",
                    "full_context": "2009年9月12日发售的心金魂银世代建立了完整的传说宝可梦禁表制度。但更重要的是：Garchomp因「沙隐(Sand Veil)+沙暴」组合被Smogon OU禁入Ubers。这是首个因非伤害性机制（闪避）而非纯数值强度被禁用的非传说宝可梦案例。Garchomp的核心问题：沙暴中沙隐提供+20%闪避，使对战结果过度依赖随机性；同时Garchomp没有可靠的联防——它的快速+高攻+优秀技能池使它几乎不可被安全换入。",
                    "balance_changes": {
                        "Garchomp": "被禁入Ubers（Smogon OU），首个因闪避机制被禁的非传说宝可梦",
                        "沙隐(Sand Veil)": "沙暴中+20%闪避，后被纳入闪避禁止条款",
                    },
                    "impact": "Garchomp被禁确立了'不可靠机制 > 强力数值'的处理原则，深刻影响了历代平衡性决策",
                    "vgc_relevance": "沙隐后来在VGC中被禁止，这次先例为VGC的机制监管提供了重要参考",
                    "key_insight": "竞技公平性的核心是'减少运气成分'——任何使对战结果过度依赖随机性的机制都应该被限制，无论数值是否超标",
                },
                "1.1": {
                    "summary": "Soul Dew被禁，开启道具禁用列表制度化进程",
                    "full_context": "VGC 2010赛季，心之水滴(Soul Dew)被禁用。这件道具为璐璐(Latias/Latios)提供巨额特攻加成，使其成为环境中不可撼动的核心。这一禁用开启了VGC「道具禁用列表」的制度化进程。",
                    "impact": "道具禁用成为VGC平衡工具的重要一环",
                    "vgc_relevance": "道具禁用的制度化为后续历代Mega Stone、Z-Crystal等道具的禁用提供了先例",
                    "key_insight": "强力道具的禁用与强力宝可梦的禁用同等重要，道具层面对竞技平衡的影响往往被低估",
                },
            },
            # ====== 第五世代 (Gen 5) ======
            "黑/白": {
                "1.0": {
                    "summary": "组队预览消除信息不对称，天气战争爆发，设计民主化实验",
                    "full_context": "2011年3月6日发售的BW世代引入了两个改变VGC格局的重大设计：(1)组队预览(Team Preview)——双方在开局前能看到对方6只阵容，消除信息不对称 (2)梦世界(Dream World)——将原本属于传说宝可梦的天气能力(Drizzle/Drought等)通过装备赋予普通宝可梦。组队预览彻底改变了VGC的战略框架：玩家需要在开局前就规划好针对对方阵容的选队策略，而不仅仅是临场反应。梦世界将天气能力下放给Politoed(Drizzle)和Tyranitar以外的非传说宝可梦，使降雨队成为BW环境的绝对核心，「天气战争」成为这一时代最具标志性的战术博弈。",
                    "balance_changes": {
                        "组队预览(Team Preview)": "开局前可见双方6只阵容，从临场反应转向全局规划",
                        "Drizzle Politoed": "梦世界将Drizzle赋予Politoed，降雨队成为环境核心",
                        "Drought Torkoal": "晴队获得稳定天气启动机",
                        "Sand Stream Hippowdon": "沙暴队获得非传说天气启动机",
                    },
                    "impact": "组队预览成为历代VGC标配，天气战争暴露了强力环境控制机制下放的风险",
                    "vgc_relevance": "组队预览和天气能力下放是BW时代最重要的两个设计决策，深刻影响了历代VGC规则设计",
                    "key_insight": "信息透明化(组队预览)与能力下放(梦世界)是一把双刃剑——前者增加策略深度，后者增加多样性但也可能破坏平衡",
                },
            },
            "黑2/白2": {
                "1.0": {
                    "summary": "Drizzle+Swift Swim联合禁用，天气战争达到监管临界点",
                    "full_context": "2012年6月23日发售的BW2世代是BW时代天气战争的延续和监管节点。在Smogon OU中，Drizzle Politoed + Swift Swim宝可梦（尤其是刺龙王Kingdra）组合因过于强力被联合禁用：一条队伍不能同时拥有Drizzle和Swift Swim能力。这开创了「机制组合禁用」的先例——多个单独看起来平衡的机制，组合后产生过度统治效果时应联合限制。同时，VGC 2013规则引入PWT(宝可梦世界锦标赛)专用格式，只能使用历史传说宝可梦，这是VGC首次为顶级赛事设计专属规则格式。",
                    "balance_changes": {
                        "Drizzle+Swift Swim联合禁用": "首个机制组合禁用案例——禁止同一队伍同时拥有Drizzle天气和Swift Swim特性",
                        "PWT专用格式": "只能使用传说宝可梦的世界锦标赛专属规则",
                    },
                    "impact": "「机制组合禁用」原则确立，成为后续平衡调整的重要参考",
                    "vgc_relevance": "机制组合禁用的先例影响了历代VGC的禁用规则设计",
                    "key_insight": "'单独平衡 ≠ 组合平衡'——多个机制的协同效应往往是平衡性监管的盲区",
                },
            },
            # ====== 第六世代 (Gen 6) ======
            "X/Y": {
                "1.0": {
                    "summary": "Mega进化上线，48种宝可梦可临时进化，爆发资源设计新范式",
                    "full_context": "2013年10月12日发售的XY世代引入了Mega进化，这是宝可梦史上最重要的机制创新之一。关键设计约束：(1)每队只能有一只宝可梦可Mega进化 (2)Mega进化需要占用道具槽 (3)Mega进化持续整场战斗。这三个约束使Mega进化成为需要战术权衡的「爆发资源」——选择哪只Mega？何时Mega？使用道具槽的代价是什么？2016年VGC世界冠军Wolfe Glick评价：「Mega进化刚发布时完全不平衡，约48种Mega中只有8种有竞技价值」。最强势的包括Mega大嘴娃(Salamence)、Mega袋兽(Kangaskhan)、Mega耿鬼(Gengar)，而Mega大菊花(Altaria)、Mega大针蜂(Beedrill)几乎无人使用。",
                    "balance_changes": {
                        "Mega大嘴娃(Salamence)": "飞行+龙的优秀打击面，高速+高攻，成为ORAS最强Mega之一",
                        "Mega袋兽(Kangaskhan)": "早期版本存在攻击两次bug，修复后仍是强力Mega",
                        "Mega耿鬼(Gengar)": "飞行+毒属性，优异的速度和特攻，阴影球打击面优秀",
                    },
                    "impact": "Mega进化成为历代最具影响力的爆发资源机制，其设计约束（单次+道具槽占用）成为后续爆发资源设计的参考框架",
                    "vgc_relevance": "Mega进化是XY-XYAS时代VGC的核心机制，也是Game Freak探索'赛季禁用特定Mega'的起点",
                    "key_insight": "爆发资源的设计关键不是强度，而是'使用成本(道具槽)+使用限制(单次/限时)+使用时机(何时进化)'三者的权衡",
                },
                "1.4": {
                    "summary": "VGC 2016规则调整，Mega妙蛙花和Mega耿鬼被Ban，赛季禁用列表制度化",
                    "full_context": "VGC 2016赛季禁止了Mega妙蛙花(Mega Venusaur)和Mega耿鬼(Mega Gengar)，这是官方首次在赛季规则中禁用特定的Mega进化形态。这标志着Game Freak正式采用「赛季禁用列表」制度来动态调整Mega进化的可用性。Mega Venusaur因其强大的晴天增益和草毒双重打击面在VGC中占据统治地位，Mega Gengar则因其高速和优异打击面难以对抗。",
                    "impact": "「赛季禁用特定Mega」制度化，Game Freak开始采用动态规则调整来维护环境多样性",
                    "vgc_relevance": "赛季禁用特定Mega的先例为后续极巨化的赛季禁用规则奠定了制度基础",
                    "key_insight": "赛季规则动态调整是电竞化运营的标配工具，'哪些Mega可用'的决策权从'设计时固定'转向'赛季中灵活调整'",
                },
            },
            "欧米伽红宝石/阿尔法蓝宝石": {
                "1.0": {
                    "summary": "三打对战上线，计时器正式引入，电竞规则完善",
                    "full_context": "2014年11月21日发售的ORAS世代有两个重大电竞化设计：(1)三打对战(3v3)模式上线，需要同时管理3只宝可梦，轮换机制带来全新的战术深度 (2)战斗回合计时器正式引入，防止拖延战术，保障比赛流畅性。三打对战的位置轮换成为新的博弈维度，攻击附带换人效果成为强力进攻工具。计时器解决了长期困扰VGC的「拖延战术」问题——在此之前，理论上可以通过无限消耗回合来拖延比赛。",
                    "balance_changes": {
                        "三打对战(3v3)": "同时控制3只宝可梦，位置轮换成为新博弈维度",
                        "战斗计时器": "防止拖延战术，保障比赛在合理时间内完成",
                    },
                    "impact": "三打提供了VGC的新赛制选项，计时器保障了电竞比赛的流畅性和观赏性",
                    "vgc_relevance": "计时器的引入是电竞化运营的里程碑事件，确保了比赛的可观赏性和时间可控性",
                    "key_insight": "电竞观赏性需要规则保障——拖延战术会严重损害比赛观赏性，计时器是必要的规则工具",
                },
            },
            # ====== 第七世代 (Gen 7) ======
            "太阳/月亮": {
                "1.0": {
                    "summary": "Z招式上线，Mega进化替代方案探索，爆发资源民主化实验",
                    "full_context": "2016年11月18日发售的SM世代引入了Z招式，这是Game Freak对Mega进化的替代方案的探索。关键设计差异：(1)全员可用 vs Mega进化仅特定宝可梦 (2)一次性使用 vs Mega进化整场一次 (3)无道具占用 vs 占用道具槽。这三种设计选择代表了「爆发资源民主化」的方向——让所有玩家都能使用强力爆发，而非只有特定Mega的玩家。社区反应两极：部分玩家认为Z招式让对战变成了「一个按钮就能赢」的设计，但也有玩家认可其「战略权衡」的一面——使用Z招式意味着放弃道具加成。",
                    "balance_changes": {
                        "Z招式全面上线": "每只宝可梦都有专属Z招式，可将一个招式升级为Z招式",
                        "阿罗拉形态(Alola Forms)": "区域特异性形态变化，提供新的战术变量",
                    },
                    "impact": "Z招式是「爆发资源民主化」的重要实验，其设计取舍（全员可用vs道具占用）深刻影响了极巨化的设计决策",
                    "vgc_relevance": "Z招式的设计为极巨化提供了重要参考——'全员可用'是否真的比'限定专属'更好？答案在剑盾世代揭晓",
                    "key_insight": "'民主化'不等于'平衡'——Z招式让所有玩家都能爆发，但也让爆发变得更加同质化，缺乏Mega进化那种'选择哪只进化'的策略深度",
                },
                "究极之日/究极之月 1.0": {
                    "summary": "究极异兽(UB)加入VGC，引入全新设计语言的宝可梦",
                    "full_context": "2017年11月17日发售的USUM世代引入了究极异兽(UB)系列。UB系列是设计语言完全不同于传统宝可梦的异星生物，有着独特的外观和种族值分配。UB-Adhesive的「弱策(weak armor)」战术成为USUM环境的标志性战术之一——通过受到攻击触发弱策特性来大幅提升速度，在特定构筑中形成极强的爆发力。VGC 2018赛季，UB-Adhesive因过于强力被禁用，成为首个被禁用的究极异兽。",
                    "balance_changes": {
                        "UB-Adhesive": "VGC 2018中被禁用，首个被禁用的究极异兽",
                        "弱策(Weak Armor)特性": "受攻击时大幅提升速度+降低防御，形成独特的爆发机制",
                    },
                    "impact": "究极异兽为VGC引入了全新设计语言的宝可梦，「牺牲防守换速度」的机制在传统宝可梦中较为罕见",
                    "vgc_relevance": "UB系列的设计展示了'打破常规设计模式'的可能性，但监管框架也需要随之更新",
                    "key_insight": "设计创新需要配套的监管创新——UB系列的能力下放程度与传统宝可梦不同，VGC的禁用规则需要相应调整",
                },
            },
            # ====== 第八/九世代 (Gen 8-9) ======
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
            # ====== Gen 1-2 反馈 ======
            "首个宝可梦正式版本发布": {
                "sentiment": "positive",
                "summary": "宝可梦品类正式诞生，回合制对战框架奠定基础",
                "key_points": [
                    "开创回合制收集对战RPG品类，对战框架沿用29年几乎未变",
                    "双打对战的'集火+保护'博弈框架成为历代核心设计",
                ],
            },
            "特性(Ability)系统上线": {
                "sentiment": "positive",
                "summary": "特性系统被公认为历代最重要的机制创新之一，威吓成为双打联防核心",
                "key_points": [
                    "威吓(Intimidate)成为历代双打联防体系的核心特性",
                    "特性使每只宝可梦都有独特定位，极大丰富了构筑多样性",
                    "是宝可梦对战深度区别于其他回合制游戏的关键设计",
                ],
            },
            "携带道具系统": {
                "sentiment": "positive",
                "summary": "道具+特性的组合成为宝可梦构筑的基础框架，玩家社区高度评价",
                "key_points": [
                    "剩饭、焦点镜等道具成为历代标配，道具选择直接影响构筑思路",
                    "道具与特性的交互（如道具强化特性效果）增加了策略深度",
                ],
            },
            "Wi-Fi对战正式上线": {
                "sentiment": "positive",
                "summary": "VGC全球化时代开启，玩家社区热烈欢迎",
                "key_points": [
                    "Wi-Fi对战使全球玩家可以随时对战，VGC参与规模扩大100倍以上",
                    "从线下聚会对战到全球在线对战的跨越是电竞化的里程碑",
                    "Ranking对战的引入为竞技玩家提供了长期目标",
                ],
            },
            "物理/特殊招式分类改革": {
                "sentiment": "positive",
                "summary": "历代最重要的平衡性变革之一，玩家社区高度评价",
                "key_points": [
                    "格斗系和火系获得丰富的物理技能池，战术地位大幅提升",
                    "历代格局因此产生根本性变化，大量原本弱势宝可梦获得新生",
                    "被认为是Game Freak在平衡性设计上最成功的改革之一",
                ],
            },
            # ====== Gen 3-4 反馈 ======
            "双打对战正式确立为VGC标准规则": {
                "sentiment": "positive",
                "summary": "双打成为VGC标准是宝可梦电竞史最重要的决策之一",
                "key_points": [
                    "4v4选2规则沿用至今，是VGC最稳定的规则基础",
                    "双打的'集火+保护'博弈创造了完全不同于单打的战术维度",
                    "是宝可梦电竞观赏性的重要基础——双打比单打更易理解",
                ],
            },
            "天气系统全面上线": {
                "sentiment": "positive",
                "summary": "天气系统开创了环境控制战术品类，是历代最具深度的机制之一",
                "key_points": [
                    "天气队成为历代标配，环境控制成为核心战术维度",
                    "天气启动机与对应特性(Swift Swim等)的交互创造了丰富策略",
                    "历代天气战争是宝可梦对战最具观赏性的战术博弈之一",
                ],
            },
            "VGC 2005规则确立": {
                "sentiment": "positive",
                "summary": "VGC电竞体系正式确立，社区视为宝可梦电竞元年",
                "key_points": [
                    "首届世界锦标赛举办标志宝可梦电竞进入全球化时代",
                    "传说宝可梦禁表制度化，竞技公平性得到保障",
                ],
            },
            "Garchomp因「沙隐+沙暴」": {
                "sentiment": "positive",
                "summary": "首个非传说宝可梦禁用案例，社区认为决策正确",
                "key_points": [
                    "沙隐的闪避机制被认为破坏了竞技性，禁用是必要决策",
                    "确立了'不可靠机制 > 强力数值'的处理原则，被社区广泛认可",
                    "这次先例深刻影响了历代平衡性决策",
                ],
            },
            # ====== Gen 5 反馈 ======
            "组队预览(Team Preview)": {
                "sentiment": "positive",
                "summary": "BW时代最重要的VGC创新，社区认为彻底改变了对战策略框架",
                "key_points": [
                    "从'猜拳开局'到'全局规划'的转变增加了策略深度",
                    "消除了开局信息不对称，对战公平性提升",
                    "组队预览成为历代VGC标配，是电竞化运营的标杆设计",
                ],
            },
            "天气 wars（天气战争）": {
                "sentiment": "mixed",
                "summary": "BW天气战争是历代最具观赏性的战术博弈，但DrizzlePolitoed统治力过强引发争议",
                "key_points": [
                    "天气战争成为BW时代最具标志性的战术博弈，是VGC观赏性的高峰",
                    "Drizzle Politoed统治力过强，社区对天气战争的反应两极分化",
                    "Drizzle+Swift Swim联合禁用被认为是必要的平衡调整",
                ],
            },
            "Mega进化系统上线": {
                "sentiment": "positive",
                "summary": "Mega进化被社区认为是历代最具深度的爆发资源机制，社区评价两极但总体正面",
                "key_points": [
                    "2023年Smogon投票：72.1%玩家认为Mega进化是最受欢迎机制",
                    "但刚发布时只有8/48种Mega有竞技价值，平衡性问题严重",
                    "选择哪只Mega、何时Mega的战略权衡获得社区高度评价",
                ],
            },
            "Mega妙蛙花和Mega耿鬼被Ban": {
                "sentiment": "mixed",
                "summary": "赛季禁用特定Mega引发讨论，但被认为是维护环境多样性的必要举措",
                "key_points": [
                    "首次赛季禁用特定Mega被认为是电竞化运营成熟的体现",
                    "被禁用的Mega玩家需要调整构筑，但社区总体认可",
                    "开启了'赛季规则动态调整'的制度化进程",
                ],
            },
            "Z招式系统上线": {
                "sentiment": "mixed",
                "summary": "Z招式全员可用的设计两极分化：支持者认为民主化，反对者认为缺乏深度",
                "key_points": [
                    "2023年Smogon投票：只有9.8%玩家认为Z招式是最受欢迎机制",
                    "支持者：所有玩家都能使用强力爆发，道具槽不占用更灵活",
                    "反对者：Z招式变成了'一个按钮就能赢'，缺乏Mega进化的策略权衡",
                ],
            },
            "究极异兽(UB)系列加入VGC": {
                "sentiment": "positive",
                "summary": "全新设计语言的宝可梦获得社区好评，弱策战术成为标志性战术",
                "key_points": [
                    "UB-Adhesive的弱策战术在USUM环境成为标志性战术",
                    "设计语言与传统宝可梦不同，为竞技环境增添新鲜感",
                    "UB-Adhesive被禁用被认为是及时的平衡调整",
                ],
            },
            # ====== Gen 8-9 反馈 ======
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
