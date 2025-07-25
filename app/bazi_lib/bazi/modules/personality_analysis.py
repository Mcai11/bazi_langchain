"""
性格分析模块 - 严格按照原版bazi.py的逻辑和输出格式
包含命宫分析、坐支分析、特殊组合、十神性格等传统命理分析
"""

from typing import Dict, Any, List, Tuple, Optional
from collections import Counter

try:
    from ..datas import *
    from ..bazi_core import *
    from ..common import *
    from ..ganzhi import *
except ImportError:
    try:
        from datas import *
        from bazi_core import *
        from common import *
        from ganzhi import *
    except ImportError:
        # 设置默认值
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 默认的命宫描述
        minggongs = {
            '子': '天贵星，志气不凡，富裕清吉',
            '丑': '天厄星，先难后易，离祖劳心',
            '寅': '天权星，聪明大器，中年有权',
            '卯': '天赦星，慷慨疏财，需要修心',
            '辰': '天如星，奔波劳碌，离祖成功',
            '巳': '天文星，文章振发，女命克夫',
            '午': '天福星，荣华吉命，女命孤独',
            '未': '天驿星，离乡背井，劳心劳力',
            '申': '天孤星，不利六亲，僧道之命',
            '酉': '天秘星，怪异多能，反复无常',
            '戌': '天艺星，多艺多能，清雅荣贵',
            '亥': '天寿星，心慈明悟，克己助人'
        }
        
        # 默认的日柱坐支描述
        rizhus = {}
        
        # 默认的格局
        ju = {}
        
        # 默认的十神逆向映射
        ten_deities = {}


class PersonalityAnalysisModule:
    """性格分析模块 - 严格按照原版bazi.py逻辑"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any],
                 shens_analysis_data: Dict[str, Any], zhi_relations_data: Dict[str, Any],
                 dayun_analysis_data: Dict[str, Any], liunian_analysis_data: Dict[str, Any],
                 liuqin_analysis_data: Dict[str, Any]):
        """
        初始化性格分析模块
        """
        # 从各模块数据中提取信息
        self.input_params = core_data.get('input_params', {})
        self.bazi_info = core_data.get('bazi_info', {})
        
        # 基本参数
        self.gender = self.input_params.get('gender', '男')
        self.is_female = self.input_params.get('is_female', False)
        
        # 八字信息
        if 'basic_bazi' in bazi_main_data:
            basic_bazi = bazi_main_data['basic_bazi']
            self.gans = basic_bazi.get('gans', [])
            self.zhis = basic_bazi.get('zhis', [])
            self.me = basic_bazi.get('me', '')
            self.zhus = basic_bazi.get('zhus', [])
        else:
            self.gans = bazi_main_data.get('gans', [])
            self.zhis = bazi_main_data.get('zhis', [])
            self.me = bazi_main_data.get('me', '')
            self.zhus = bazi_main_data.get('zhus', [])
        
        # 十神信息
        if 'ten_gods' in bazi_main_data:
            ten_gods_data = bazi_main_data['ten_gods']
            self.gan_shens = ten_gods_data.get('gan_shens', [])
            self.zhi_shens = ten_gods_data.get('zhi_shens', [])
            self.all_shens = ten_gods_data.get('all_shens', [])
        else:
            self.gan_shens = bazi_main_data.get('gan_shens', [])
            self.zhi_shens = bazi_main_data.get('zhi_shens', [])
            self.all_shens = bazi_main_data.get('shens', [])
        
        # 五行信息
        if 'wuxing_analysis' in bazi_main_data:
            wuxing_data = bazi_main_data['wuxing_analysis']
            self.scores = wuxing_data.get('scores', {})
            self.gan_scores = wuxing_data.get('gan_scores', {})
        else:
            self.scores = bazi_main_data.get('scores', {})
            self.gan_scores = bazi_main_data.get('gan_scores', {})
        
        # 强弱信息
        if 'strength_analysis' in bazi_main_data:
            strength_data = bazi_main_data['strength_analysis']
            self.is_weak = strength_data.get('is_weak', True)
            self.strong_score = strength_data.get('strong_score', 0)
        else:
            self.is_weak = bazi_main_data.get('weak', True)
            self.strong_score = bazi_main_data.get('strong', 0)
        
        # 地支关系信息
        self.zhi_relations_data = zhi_relations_data
        
        # 性格分析结果列表
        self.personality_lines = []
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行性格分析计算"""
        self._analyze_minggong()
        self._analyze_rizhu()
        self._analyze_special_combinations()
        self._analyze_special_formats()
        self._analyze_bijian()
        self._analyze_jiecai()
        self._analyze_yinxing()
        self._analyze_other_shens()

    def _analyze_minggong(self):
        """分析命宫"""
        if len(self.zhis) >= 4:
            try:
                # 计算命宫：月支 + 时支 - 6，然后取模12
                month_index = Zhi.index(self.zhis[1])
                hour_index = Zhi.index(self.zhis[3])
                minggong_index = (month_index + hour_index - 6) % 12
                minggong = Zhi[::-1][minggong_index]  # 逆序取值
                
                # 获取命宫描述
                try:
                    if minggong in minggongs:
                        description = minggongs[minggong]
                        self.personality_lines.append(f"{minggong} {description}")
                except NameError:
                    # 使用默认描述
                    default_minggongs = {
                        '子': '天贵星，志气不凡，富裕清吉',
                        '丑': '天厄星，先难后易，离祖劳心',
                        '寅': '天权星，聪明大器，中年有权',
                        '卯': '天赦星，慷慨疏财，需要修心',
                        '辰': '天如星，奔波劳碌，离祖成功',
                        '巳': '天文星，文章振发，女命克夫',
                        '午': '天福星，荣华吉命，女命孤独',
                        '未': '天驿星，离乡背井，劳心劳力',
                        '申': '天孤星，不利六亲，僧道之命',
                        '酉': '天秘星，怪异多能，反复无常',
                        '戌': '天艺星，多艺多能，清雅荣贵',
                        '亥': '天寿星，心慈明悟，克己助人'
                    }
                    if minggong in default_minggongs:
                        self.personality_lines.append(f"{minggong} {default_minggongs[minggong]}")
            except (ValueError, IndexError):
                pass

    def _analyze_rizhu(self):
        """分析日柱坐支"""
        if len(self.gans) >= 3 and len(self.zhis) >= 3:
            day_gan = self.gans[2]
            day_zhi = self.zhis[2]
            rizhu = day_gan + day_zhi
            
            try:
                if rizhu in rizhus:
                    self.personality_lines.append(f"坐：{rizhus[rizhu]}")
            except NameError:
                # 使用默认分析或基于十神的分析
                if len(self.zhi_shens) >= 3:
                    day_zhi_shen = self.zhi_shens[2]
                    if day_zhi_shen == '食':
                        self.personality_lines.append("坐：自坐食神，相敬相助，即使透枭也无事，不过心思不定，做事毅力不足，也可能假客气。专位容易发胖，有福。")
                    elif day_zhi_shen == '财':
                        self.personality_lines.append("坐：自坐财星，善于理财，注重物质")
                    elif day_zhi_shen == '官':
                        self.personality_lines.append("坐：自坐正官，品格端正，有责任心")
                    elif day_zhi_shen == '印':
                        self.personality_lines.append("坐：自坐正印，好学上进，依赖心强")
                    elif day_zhi_shen == '比':
                        self.personality_lines.append("坐：自坐比肩，自信独立，不易合作")
                    elif day_zhi_shen == '劫':
                        self.personality_lines.append("坐：自坐劫财，积极主动，破财伤妻")

    def _analyze_special_combinations(self):
        """分析特殊组合"""
        # 地网
        if '辰' in self.zhis and '巳' in self.zhis:
            self.personality_lines.append("地网：地支辰巳。天罗：戌亥。天罗地网全凶。")
        
        # 天罗
        if '戌' in self.zhis and '亥' in self.zhis:
            self.personality_lines.append("天罗：戌亥。地网：地支辰巳。天罗地网全凶。")

    def _analyze_special_formats(self):
        """分析特殊格局"""
        if len(self.zhus) >= 3:
            day_pillar = (self.gans[2], self.zhis[2])
            
            # 魁罡格
            kuigang_pillars = [('庚','辰'), ('庚','戌'), ('壬','辰'), ('戊','戌')]
            if day_pillar in kuigang_pillars:
                self.personality_lines.append("魁罡格：基础96，日主庚辰,庚戌,壬辰, 戊戌，重叠方有力。日主强，无刑冲佳。")
                self.personality_lines.append("魁罡四柱曰多同，贵气朝来在此中，日主独逢冲克重，财官显露祸无穷。魁罡重叠是贵人，天元健旺喜临身，财官一见生灾祸，刑煞俱全定苦辛。")
        
        if len(self.zhus) >= 4:
            hour_pillar = (self.gans[3], self.zhis[3])
            
            # 金神格
            jinshen_pillars = [('乙','丑'), ('己','巳'), ('癸','酉')]
            if hour_pillar in jinshen_pillars:
                self.personality_lines.append("金神格：基础97，时柱乙丑、己巳、癸酉。只有甲和己日，甲日为主，甲子、甲辰最突出。月支通金火2局为佳命。不通可以选其他格")
            
            # 六阴朝阳
            if self.me == '辛' and self.zhis[3] == '子':
                self.personality_lines.append("六阴朝阳格：基础98，辛日时辰为子。")
            
            # 六乙鼠贵
            if self.me == '乙' and self.zhis[3] == '子':
                self.personality_lines.append("六阴朝阳格：基础99，乙日时辰为子。忌讳午冲，丑合，不适合有2个子。月支最好通木局，水也可以，不适合金火。申酉大运有凶，午也不行。夏季为伤官。入其他格以格局论。")
        
        # 从格判断
        if self.scores and max(self.scores.values()) > 25:
            self.personality_lines.append("有五行大于25分，需要考虑专格或者从格。")
            self.personality_lines.append("从旺格：安居远害、退身避位、淡泊名利,基础94;从势格：日主无根。")

    def _analyze_bijian(self):
        """分析比肩"""
        if '比' in self.gan_shens:
            self.personality_lines.append("比：同性相斥。讨厌自己。老是想之前有没有搞错。没有持久性，最多跟你三五年。 散财，月上比肩，做事没有定性，不看重钱，感情不持久。不怀疑人家，人心很好。善意好心惹麻烦。年上问题不大。")
            
            # 年月天干并现
            if len(self.gan_shens) >= 2 and self.gan_shens[0] == '比' and self.gan_shens[1] == '比':
                self.personality_lines.append("比肩年月天干并现：不是老大，出身平常。女仪容端庄，有自己的思想；不重视钱财,话多不能守秘。30随以前是非小人不断。")
            
            # 月柱干支比肩
            if len(self.gan_shens) >= 2 and len(self.zhi_shens) >= 2:
                if self.gan_shens[1] == '比' and self.zhi_shens[1] == '比':
                    self.personality_lines.append("月柱干支比肩：争夫感情丰富。30岁以前钱不够花。")
            
            # 年干比
            if len(self.gan_shens) >= 1 and self.gan_shens[0] == '比':
                self.personality_lines.append("年干比：上面有哥或姐，出身一般。")
            
            # 比肩过多的分析
            all_shens = self.gan_shens + self.zhi_shens
            bi_count = all_shens.count('比')
            if bi_count > 2:
                self.personality_lines.append("----基51:天干2比")
                self.personality_lines.append("自我排斥，易后悔、举棋不定、匆促决定而有失；男倾向于群力，自己决策容易孤注一掷，小事谨慎，大事决定后不再重复考虑。")
                self.personality_lines.append("女有自己的思想、容貌佳，注意细节，喜欢小孩重过丈夫。轻视老公。对丈夫多疑心，容易吃醋冲动。")
                self.personality_lines.append("男不得女欢心.")
                self.personality_lines.append("难以保守秘密，不适合多言；")
                
                if '官' not in all_shens and '杀' not in all_shens:
                    self.personality_lines.append("基51: 比肩多，四柱无正官七杀，性情急躁。")
        
        # 时支比
        if len(self.zhi_shens) >= 4 and self.zhi_shens[3] == '比':
            self.personality_lines.append("时支比：子女为人公正倔强、行动力强，能得资产。")
        
        # 时柱比
        if len(self.gan_shens) >= 4 and len(self.zhi_shens) >= 4:
            if '比' in [self.gan_shens[3], self.zhi_shens[3]]:
                self.personality_lines.append("时柱比：与亲人意见不合。")
        
        # 比劫大于2
        all_shens = self.gan_shens + self.zhi_shens
        bijie_count = all_shens.count('比') + all_shens.count('劫')
        if bijie_count > 2:
            if self.gender == '男':
                self.personality_lines.append("比劫大于2，男：感情阻碍、事业起伏不定。")

    def _analyze_jiecai(self):
        """分析劫财"""
        if '劫' in self.gan_shens:
            self.personality_lines.append("劫财扶助，无微不至。劫财多者谦虚之中带有傲气。凡事先理情，而后情理。先细节后全局。性刚强、精明干练、女命不适合干透支藏。")
            self.personality_lines.append("务实，不喜欢抽象性的空谈。不容易认错，比较倔。有理想，但是不够灵活。不怕闲言闲语干扰。不顾及别人面子。")
            self.personality_lines.append("合作事业有始无终。太重细节。做小领导还是可以的。有志向，自信。杀或食透干可解所有负面。女命忌讳比劫和合官杀，多为任性引发困难之事。")
            
            # 年月天干并现
            if len(self.gan_shens) >= 2 and self.gan_shens[0] == '劫' and self.gan_shens[1] == '劫':
                self.personality_lines.append("劫年月天干并现：喜怒形于色，30岁以前大失败一次。过度自信，精明反被精明误。")
            
            # 月柱干支劫
            if len(self.gan_shens) >= 2 and len(self.zhi_shens) >= 2:
                if self.gan_shens[1] == '劫' and self.zhi_shens[1] == '劫':
                    self.personality_lines.append("月柱干支劫：与父亲无缘，30岁以前任性，早婚防分手，自我精神压力极其重。")
            
            # 劫财过多
            all_shens = self.gan_shens + self.zhi_shens
            jie_count = all_shens.count('劫')
            if jie_count > 2:
                self.personality_lines.append('----劫财过多, 婚姻不好')
            
            # 日坐劫财
            if len(self.zhi_shens) >= 3 and self.zhi_shens[2] == '劫':
                self.personality_lines.append("日坐劫财，透天干。在年父早亡，在月夫妻关系不好。比如财产互相防范；鄙视对方；自己决定，哪怕对方不同意；老夫少妻；身世有差距；斤斤计较；敢爱敢恨的后遗症")
                self.personality_lines.append("以上多针对女。男的一般有双妻。天干有杀或食可解。")
        
        # 同一柱中劫财、阳刃伤官
        shen_zhus = list(zip(self.gan_shens, self.zhi_shens))
        for gan_shen, zhi_shen in shen_zhus:
            if (gan_shen == '劫' and zhi_shen == '伤') or (gan_shen == '伤' and zhi_shen == '劫'):
                self.personality_lines.append("同一柱中，劫财、阳刃伤官都有，外表华美，富屋穷人，婚姻不稳定，富而不久；年柱不利家长，月柱不利婚姻，时柱不利子女。伤官的狂妄。")
                break
        
        # 月柱劫
        if len(self.gan_shens) >= 2 and len(self.zhi_shens) >= 2:
            if '劫' in [self.gan_shens[1], self.zhi_shens[1]]:
                self.personality_lines.append("月柱劫：容易孤注一掷，30岁以前难稳定。男早婚不利。")

    def _analyze_yinxing(self):
        """分析印星"""
        # 偏印分析
        if '枭' in self.gan_shens:
            self.personality_lines.append("----偏印在天干如成格：偏印在前，偏财(财次之)在后，有天月德就是佳命(偏印格在日时，不在月透天干也麻烦)。忌讳倒食，但是坐绝没有这能力。")
            self.personality_lines.append("经典认为：偏印不能扶身，要身旺；偏印见官杀未必是福；喜伤官，喜财；忌日主无根；   女顾兄弟姐妹；男六亲似冰")
            self.personality_lines.append("偏印格干支有冲、合、刑，地支是偏印的绝位也不佳。")
            
            # 偏印在年
            if len(self.gan_shens) >= 1 and self.gan_shens[0] == '枭':
                self.personality_lines.append("偏印在年：少有富贵家庭；有宗教素养，不喜享乐，第六感强。")

    def _analyze_other_shens(self):
        """分析其他十神"""
        # 官格分析
        all_shens = self.gan_shens + self.zhi_shens
        if '官' in all_shens:
            self.personality_lines.append("局 [] 格 ['官']")
            
            # 官格透比或劫
            if '比' in self.gan_shens or '劫' in self.gan_shens:
                self.personality_lines.append("官格透比或劫：故做清高或有洁癖的文人。")
            
            # 官独透成格
            guan_count = all_shens.count('官')
            if guan_count == 1 and '财' not in all_shens and '印' not in all_shens:
                self.personality_lines.append("官独透天干成格，四柱无财或印，为老实人。")
            
            # 正官多者
            if guan_count > 1:
                self.personality_lines.append("正官多者，虚名。为人性格温和，比较实在。做七杀看")
        
        # 食神分析
        if len(self.zhi_shens) >= 3 and self.zhi_shens[2] == '食':
            self.personality_lines.append("自坐食神，相敬相助，即使透枭也无事，不过心思不定，做事毅力不足，也可能假客气。专位容易发胖，有福。")

    def get_personality_lines(self) -> List[str]:
        """获取性格分析行"""
        return self.personality_lines

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的性格分析结果"""
        return {
            "personality_lines": self.personality_lines,
            "formatted_output": "\n".join(self.personality_lines),
            "summary_stats": {
                "total_lines": len(self.personality_lines),
                "has_minggong": any("天" in line and "星" in line for line in self.personality_lines),
                "has_rizhu": any("坐：" in line for line in self.personality_lines),
                "has_special": any("天罗地网" in line or "魁罡" in line or "金神" in line for line in self.personality_lines),
                "has_bijian": any("比" in line for line in self.personality_lines),
                "has_jiecai": any("劫财" in line for line in self.personality_lines),
                "has_gege": any("格" in line for line in self.personality_lines)
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取性格分析摘要"""
        return {
            "total_analysis": f"性格分析：共{len(self.personality_lines)}条",
            "main_features": "；".join(self.personality_lines[:3]) if self.personality_lines else "暂无分析",
            "special_patterns": "；".join([line for line in self.personality_lines if "格" in line or "天罗地网" in line]),
            "character_traits": "；".join([line for line in self.personality_lines if "劫财" in line or "比" in line])
        }

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的性格数据"""
        # 分类整理性格分析内容
        minggong_lines = [line for line in self.personality_lines if any(star in line for star in ['天贵星', '天厄星', '天权星', '天赦星', '天如星', '天文星', '天福星', '天驿星', '天孤星', '天秘星', '天艺星', '天寿星'])]
        rizhu_lines = [line for line in self.personality_lines if line.startswith("坐：")]
        special_lines = [line for line in self.personality_lines if any(keyword in line for keyword in ["天罗地网", "魁罡", "金神", "六阴朝阳", "六乙鼠贵", "从格"])]
        bijian_lines = [line for line in self.personality_lines if "比" in line and "劫" not in line]
        jiecai_lines = [line for line in self.personality_lines if "劫财" in line]
        yinxing_lines = [line for line in self.personality_lines if "偏印" in line or "正印" in line]
        gege_lines = [line for line in self.personality_lines if "格" in line and "魁罡" not in line]
        
        return {
            "性格分析总览": {
                "分析条数": len(self.personality_lines),
                "主要特征": self.personality_lines[:5] if len(self.personality_lines) >= 5 else self.personality_lines
            },
            "命宫分析": minggong_lines,
            "日柱坐支": rizhu_lines,
            "特殊格局": special_lines,
            "比肩性格": bijian_lines,
            "劫财性格": jiecai_lines,
            "印星性格": yinxing_lines,
            "格局性格": gege_lines,
            "完整分析": self.personality_lines
        }


def test_personality_analysis_module():
    """测试性格分析模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    from .shens_analysis import ShensAnalysisModule
    from .zhi_relations import ZhiRelationsModule
    from .dayun_analysis import DayunAnalysisModule
    from .liunian_analysis import LiunianAnalysisModule
    from .liuqin_analysis import LiuqinAnalysisModule
    
    print("=== 原版风格性格分析模块测试 ===")
    
    # 创建依赖数据
    print("1. 创建依赖数据...")
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    core_data = core.get_result()
    
    basic_info = BasicInfoModule(core_data)
    basic_info_data = basic_info.get_result()
    
    bazi_main = BaziMainModule(core_data, basic_info_data)
    bazi_main_data = bazi_main.get_result()
    
    detail_info = DetailInfoModule(core_data, basic_info_data, bazi_main_data)
    detail_info_data = detail_info.get_result()
    
    shens_analysis = ShensAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data)
    shens_analysis_data = shens_analysis.get_result()
    
    zhi_relations = ZhiRelationsModule(core_data, basic_info_data, bazi_main_data, 
                                      detail_info_data, shens_analysis_data)
    zhi_relations_data = zhi_relations.get_result()
    
    dayun_analysis = DayunAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                        detail_info_data, shens_analysis_data, zhi_relations_data)
    dayun_analysis_data = dayun_analysis.get_result()
    
    liunian_analysis = LiunianAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                           detail_info_data, shens_analysis_data, zhi_relations_data,
                                           dayun_analysis_data)
    liunian_analysis_data = liunian_analysis.get_result()
    
    liuqin_analysis = LiuqinAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                          detail_info_data, shens_analysis_data, zhi_relations_data,
                                          dayun_analysis_data, liunian_analysis_data)
    liuqin_analysis_data = liuqin_analysis.get_result()
    
    print("2. 创建性格分析模块...")
    personality_analysis = PersonalityAnalysisModule(
        core_data, basic_info_data, bazi_main_data, detail_info_data,
        shens_analysis_data, zhi_relations_data, dayun_analysis_data,
        liunian_analysis_data, liuqin_analysis_data
    )
    
    print("\n3. 原版风格性格分析结果：")
    lines = personality_analysis.get_personality_lines()
    for line in lines:
        print(line)
    
    return personality_analysis.get_result()


if __name__ == "__main__":
    test_personality_analysis_module() 