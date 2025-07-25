"""
六亲分析模块 - 处理八字中的六亲关系分析
包含父母、兄弟姐妹、配偶、子女等亲属关系的分析和评估
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
        # 设置默认的六亲相关数据
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 默认的十神数据
        ten_deities = {}
        for gan in Gan:
            ten_deities[gan] = {}
            for other_gan in Gan:
                ten_deities[gan][other_gan] = '比'
            for zhi in Zhi:
                ten_deities[gan][zhi] = '比'
        
        # 默认的六亲对应关系
        def get_default_liuqin_mapping(is_female: bool = False):
            if is_female:
                return {
                    '才': '父亲', '财': '父亲', '印': '母亲', '枭': '偏印',
                    '官': '丈夫', '杀': '情夫', '劫': '兄弟', '比': '姐妹',
                    '食': '女儿', '伤': '儿子'
                }
            else:
                return {
                    '才': '父亲', '财': '妻子', '印': '母亲', '枭': '祖父',
                    '官': '女儿', '杀': '儿子', '劫': '姐妹', '比': '兄弟',
                    '食': '下属', '伤': '孙女'
                }


class LiuqinAnalysisModule:
    """六亲分析模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any],
                 shens_analysis_data: Dict[str, Any], zhi_relations_data: Dict[str, Any],
                 dayun_analysis_data: Dict[str, Any], liunian_analysis_data: Dict[str, Any]):
        """
        初始化六亲分析模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
            detail_info_data: 来自DetailInfoModule的详细信息数据
            shens_analysis_data: 来自ShensAnalysisModule的神煞分析数据
            zhi_relations_data: 来自ZhiRelationsModule的地支关系数据
            dayun_analysis_data: 来自DayunAnalysisModule的大运分析数据
            liunian_analysis_data: 来自LiunianAnalysisModule的流年分析数据
        """
        # 从各模块数据中提取信息
        self.input_params = core_data.get('input_params', {})
        self.time_info = core_data.get('time_info', {})
        self.bazi_info = core_data.get('bazi_info', {})
        
        # 基本参数
        self.year = self.input_params.get('year', 0)
        self.month = self.input_params.get('month', 0)
        self.day = self.input_params.get('day', 0)
        self.hour = self.input_params.get('hour', 0)
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
            # 备用数据提取
            self.gans = bazi_main_data.get('gans', [])
            self.zhis = bazi_main_data.get('zhis', [])
            self.me = bazi_main_data.get('me', '')
            self.zhus = bazi_main_data.get('zhus', [])
        
        # 十神信息
        if 'ten_gods' in bazi_main_data:
            ten_gods_data = bazi_main_data['ten_gods']
            self.gan_shens = ten_gods_data.get('gan_shens', [])
            self.zhi_shens = ten_gods_data.get('zhi_shens', [])
        else:
            self.gan_shens = bazi_main_data.get('gan_shens', [])
            self.zhi_shens = bazi_main_data.get('zhi_shens', [])
        
        # 五行分数
        self.scores = bazi_main_data.get('scores', {})
        self.gan_scores = bazi_main_data.get('gan_scores', {})
        
        # 六亲分析结果
        self.liuqin_mapping = {}        # 十神到六亲的映射
        self.liuqin_analysis = {}       # 各六亲的详细分析
        self.liuqin_statistics = {}     # 六亲统计信息
        self.liuqin_relationships = []  # 六亲关系评估
        self.liuqin_predictions = {}    # 六亲运势预测
        self.marriage_analysis = {}     # 婚姻专项分析
        self.children_analysis = {}     # 子女专项分析
        self.parents_analysis = {}      # 父母专项分析
        self.siblings_analysis = {}     # 兄弟姐妹专项分析
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行六亲分析计算"""
        self._setup_liuqin_mapping()
        self._analyze_liuqin_basic()
        self._analyze_liuqin_detailed()
        self._analyze_marriage()
        self._analyze_children()
        self._analyze_parents()
        self._analyze_siblings()
        self._analyze_liuqin_statistics()
        self._evaluate_liuqin_fortune()

    def _setup_liuqin_mapping(self):
        """设置六亲映射关系"""
        if self.is_female:
            # 女命的六亲映射
            self.liuqin_mapping = {
                '才': '父亲', '财': '父亲', '印': '母亲', '枭': '偏印',
                '官': '丈夫', '杀': '情夫', '劫': '兄弟', '比': '姐妹',
                '食': '女儿', '伤': '儿子'
            }
        else:
            # 男命的六亲映射
            self.liuqin_mapping = {
                '才': '父亲', '财': '妻子', '印': '母亲', '枭': '祖父',
                '官': '女儿', '杀': '儿子', '劫': '姐妹', '比': '兄弟',
                '食': '下属', '伤': '孙女'
            }

    def _analyze_liuqin_basic(self):
        """分析基本六亲情况"""
        # 分析四柱中的六亲分布
        pillar_names = ['年柱', '月柱', '日柱', '时柱']
        
        for i, (gan_shen, zhi_shen) in enumerate(zip(self.gan_shens, self.zhi_shens)):
            pillar_analysis = {
                'pillar': pillar_names[i],
                'position': i,
                'gan_shen': gan_shen,
                'zhi_shen': zhi_shen,
                'gan_liuqin': self.liuqin_mapping.get(gan_shen, '未知'),
                'zhi_liuqin': self.liuqin_mapping.get(zhi_shen, '未知'),
                'gan': self.gans[i] if i < len(self.gans) else '',
                'zhi': self.zhis[i] if i < len(self.zhis) else '',
                'analysis': self._analyze_pillar_liuqin(i, gan_shen, zhi_shen)
            }
            
            if pillar_names[i] not in self.liuqin_analysis:
                self.liuqin_analysis[pillar_names[i]] = []
            self.liuqin_analysis[pillar_names[i]] = pillar_analysis

    def _analyze_pillar_liuqin(self, position: int, gan_shen: str, zhi_shen: str) -> Dict[str, Any]:
        """分析单个柱的六亲情况"""
        analysis = {
            'favorable_aspects': [],
            'unfavorable_aspects': [],
            'relationship_quality': 'neutral',
            'strength': 'medium',
            'special_notes': []
        }
        
        # 根据位置分析
        if position == 0:  # 年柱 - 祖辈、父母
            analysis['primary_focus'] = '祖辈父母'
            if gan_shen in ['印', '枭']:
                analysis['favorable_aspects'].append('母亲关系良好')
                analysis['relationship_quality'] = 'good'
            elif gan_shen in ['才', '财']:
                analysis['favorable_aspects'].append('父亲关系良好')
                analysis['relationship_quality'] = 'good'
        
        elif position == 1:  # 月柱 - 兄弟姐妹、同辈
            analysis['primary_focus'] = '兄弟姐妹'
            if gan_shen in ['比', '劫']:
                analysis['favorable_aspects'].append('兄弟姐妹情深')
                analysis['relationship_quality'] = 'good'
            elif gan_shen in ['官', '杀']:
                analysis['unfavorable_aspects'].append('与兄弟姐妹有竞争')
                analysis['relationship_quality'] = 'challenging'
        
        elif position == 2:  # 日柱 - 自己和配偶
            analysis['primary_focus'] = '夫妻关系'
            if self.is_female:
                if zhi_shen in ['官', '杀']:
                    analysis['favorable_aspects'].append('婚姻宫有官杀，利于婚姻')
                    analysis['relationship_quality'] = 'good'
            else:
                if zhi_shen in ['财', '才']:
                    analysis['favorable_aspects'].append('婚姻宫有财星，利于婚姻')
                    analysis['relationship_quality'] = 'good'
        
        elif position == 3:  # 时柱 - 子女、晚辈
            analysis['primary_focus'] = '子女后代'
            if gan_shen in ['食', '伤']:
                analysis['favorable_aspects'].append('子女宫有食伤，利于生育')
                analysis['relationship_quality'] = 'good'
            elif gan_shen in ['官', '杀']:
                if self.is_female:
                    analysis['special_notes'].append('女命时柱官杀，子女有出息')
                else:
                    analysis['favorable_aspects'].append('男命时柱官杀，子女有出息')
        
        return analysis

    def _analyze_liuqin_detailed(self):
        """详细分析各类六亲"""
        # 统计各十神出现次数
        all_shens = self.gan_shens + self.zhi_shens
        shen_counts = Counter(all_shens)
        
        # 分析各类六亲的详细情况
        for shen, count in shen_counts.items():
            if shen == '--' or shen not in self.liuqin_mapping:
                continue
            
            liuqin = self.liuqin_mapping[shen]
            
            if liuqin not in self.liuqin_relationships:
                self.liuqin_relationships.append({
                    'liuqin_type': liuqin,
                    'corresponding_shen': shen,
                    'count': count,
                    'strength': self._evaluate_shen_strength(shen),
                    'quality': self._evaluate_relationship_quality(shen, count),
                    'positions': self._get_shen_positions(shen),
                    'detailed_analysis': self._get_detailed_liuqin_analysis(liuqin, shen, count),
                    'predictions': self._predict_liuqin_fortune(liuqin, shen),
                    'suggestions': self._get_liuqin_suggestions(liuqin, shen, count)
                })

    def _evaluate_shen_strength(self, shen: str) -> str:
        """评估十神的强度"""
        # 根据月令、得令、有根等因素评估
        if shen in ['印', '比']:
            return 'strong'
        elif shen in ['食', '伤', '财', '才']:
            return 'medium'
        elif shen in ['官', '杀']:
            return 'medium'
        else:
            return 'weak'

    def _evaluate_relationship_quality(self, shen: str, count: int) -> str:
        """评估六亲关系质量"""
        # 基于十神特性和数量评估
        if count == 0:
            return 'absent'
        elif count == 1:
            if shen in ['印', '官', '财', '食']:
                return 'good'
            else:
                return 'normal'
        elif count == 2:
            if shen in ['比', '劫']:
                return 'good'  # 比劫适中有助
            else:
                return 'normal'
        else:  # count >= 3
            if shen in ['印', '比', '劫']:
                return 'excessive'  # 过多可能不利
            else:
                return 'abundant'

    def _get_shen_positions(self, shen: str) -> List[str]:
        """获取十神在四柱中的位置"""
        positions = []
        pillar_names = ['年柱', '月柱', '日柱', '时柱']
        
        for i, (gan_shen, zhi_shen) in enumerate(zip(self.gan_shens, self.zhi_shens)):
            if gan_shen == shen:
                positions.append(f"{pillar_names[i]}天干")
            if zhi_shen == shen:
                positions.append(f"{pillar_names[i]}地支")
        
        return positions

    def _get_detailed_liuqin_analysis(self, liuqin: str, shen: str, count: int) -> Dict[str, Any]:
        """获取详细的六亲分析"""
        analysis = {
            'relationship_nature': '',
            'interaction_pattern': '',
            'emotional_bond': '',
            'practical_support': '',
            'potential_issues': [],
            'positive_aspects': []
        }
        
        # 根据六亲类型和十神特性分析
        if liuqin in ['父亲', '母亲']:
            analysis = self._analyze_parents_relationship(liuqin, shen, count)
        elif liuqin in ['妻子', '丈夫', '情夫']:
            analysis = self._analyze_spouse_relationship(liuqin, shen, count)
        elif liuqin in ['兄弟', '姐妹']:
            analysis = self._analyze_siblings_relationship(liuqin, shen, count)
        elif liuqin in ['儿子', '女儿', '孙女', '下属']:
            analysis = self._analyze_children_relationship(liuqin, shen, count)
        
        return analysis

    def _analyze_parents_relationship(self, liuqin: str, shen: str, count: int) -> Dict[str, Any]:
        """分析父母关系"""
        analysis = {
            'relationship_nature': '',
            'interaction_pattern': '',
            'emotional_bond': '',
            'practical_support': '',
            'potential_issues': [],
            'positive_aspects': []
        }
        
        if shen == '印':  # 正印 - 母亲
            analysis['relationship_nature'] = '正统慈爱的母子关系'
            analysis['emotional_bond'] = '深厚的情感纽带'
            analysis['practical_support'] = '母亲给予全面支持和庇护'
            analysis['positive_aspects'] = ['母爱深厚', '教育良好', '品德高尚']
            if count > 2:
                analysis['potential_issues'] = ['过度溺爱', '依赖性强', '缺乏独立性']
        
        elif shen == '枭':  # 偏印
            analysis['relationship_nature'] = '复杂的长辈关系'
            analysis['emotional_bond'] = '情感较为疏离'
            analysis['practical_support'] = '支持方式特殊或间接'
            analysis['positive_aspects'] = ['独特的教育方式', '培养特殊才能']
            analysis['potential_issues'] = ['关系疏远', '理解困难', '支持不稳定']
        
        elif shen in ['财', '才']:  # 财星 - 父亲
            analysis['relationship_nature'] = '务实的父子关系'
            analysis['emotional_bond'] = '通过物质表达关爱'
            analysis['practical_support'] = '经济支持和实用指导'
            analysis['positive_aspects'] = ['经济条件好', '实用教育', '事业指导']
            if count > 2:
                analysis['potential_issues'] = ['过分重视金钱', '情感表达不足']
        
        return analysis

    def _analyze_spouse_relationship(self, liuqin: str, shen: str, count: int) -> Dict[str, Any]:
        """分析配偶关系"""
        analysis = {
            'relationship_nature': '',
            'interaction_pattern': '',
            'emotional_bond': '',
            'practical_support': '',
            'potential_issues': [],
            'positive_aspects': []
        }
        
        if self.is_female:  # 女命看官杀为夫
            if shen == '官':
                analysis['relationship_nature'] = '正统和谐的夫妻关系'
                analysis['emotional_bond'] = '相敬如宾，感情稳定'
                analysis['practical_support'] = '丈夫有责任心，事业有成'
                analysis['positive_aspects'] = ['婚姻稳定', '丈夫可靠', '家庭和睦']
                if count > 1:
                    analysis['potential_issues'] = ['感情选择困难', '多角恋爱']
            
            elif shen == '杀':
                analysis['relationship_nature'] = '激情但不稳定的感情关系'
                analysis['emotional_bond'] = '感情激烈但多变'
                analysis['practical_support'] = '对方能力强但性格强势'
                analysis['positive_aspects'] = ['感情热烈', '对方有能力']
                analysis['potential_issues'] = ['关系不稳定', '争执较多', '控制欲强']
        
        else:  # 男命看财星为妻
            if shen == '财':
                analysis['relationship_nature'] = '传统和谐的夫妻关系'
                analysis['emotional_bond'] = '感情真挚，相互支持'
                analysis['practical_support'] = '妻子贤惠，善理家务'
                analysis['positive_aspects'] = ['妻子贤惠', '家庭和睦', '财运旺盛']
                if count > 1:
                    analysis['potential_issues'] = ['感情复杂', '多妻倾向']
            
            elif shen == '才':
                analysis['relationship_nature'] = '现实导向的婚姻关系'
                analysis['emotional_bond'] = '感情较为理性'
                analysis['practical_support'] = '经济互助，实用主义'
                analysis['positive_aspects'] = ['经济条件好', '实用主义']
                analysis['potential_issues'] = ['感情不够深厚', '过于现实']
        
        return analysis

    def _analyze_siblings_relationship(self, liuqin: str, shen: str, count: int) -> Dict[str, Any]:
        """分析兄弟姐妹关系"""
        analysis = {
            'relationship_nature': '',
            'interaction_pattern': '',
            'emotional_bond': '',
            'practical_support': '',
            'potential_issues': [],
            'positive_aspects': []
        }
        
        if shen == '比':
            analysis['relationship_nature'] = '和睦的同性手足关系'
            analysis['emotional_bond'] = '情同手足，相互理解'
            analysis['practical_support'] = '互相帮助，共同进退'
            analysis['positive_aspects'] = ['感情深厚', '相互支持', '团结一致']
            if count > 2:
                analysis['potential_issues'] = ['过度依赖', '缺乏独立性']
        
        elif shen == '劫':
            analysis['relationship_nature'] = '竞争性的手足关系'
            analysis['emotional_bond'] = '既亲近又竞争'
            analysis['practical_support'] = '有时合作有时竞争'
            analysis['positive_aspects'] = ['相互激励', '共同成长']
            analysis['potential_issues'] = ['竞争激烈', '利益冲突', '关系复杂']
        
        return analysis

    def _analyze_children_relationship(self, liuqin: str, shen: str, count: int) -> Dict[str, Any]:
        """分析子女关系"""
        analysis = {
            'relationship_nature': '',
            'interaction_pattern': '',
            'emotional_bond': '',
            'practical_support': '',
            'potential_issues': [],
            'positive_aspects': []
        }
        
        if shen == '食':
            analysis['relationship_nature'] = '温和的亲子关系'
            analysis['emotional_bond'] = '亲情温馨，沟通良好'
            analysis['practical_support'] = '子女孝顺，晚年有依靠'
            analysis['positive_aspects'] = ['子女孝顺', '关系和谐', '晚年幸福']
            if count == 0:
                analysis['potential_issues'] = ['子女缘薄', '生育困难']
        
        elif shen == '伤':
            analysis['relationship_nature'] = '活跃但复杂的亲子关系'
            analysis['emotional_bond'] = '感情丰富但多变'
            analysis['practical_support'] = '子女有才华但个性强'
            analysis['positive_aspects'] = ['子女聪明', '有才华', '个性独特']
            analysis['potential_issues'] = ['管教困难', '叛逆性强', '关系紧张']
        
        # 对于官杀看子女的情况
        elif shen in ['官', '杀']:
            if self.is_female:
                analysis['relationship_nature'] = '权威型的亲子关系'
                analysis['emotional_bond'] = '严格但关爱'
                analysis['practical_support'] = '子女有出息，成就较高'
                analysis['positive_aspects'] = ['子女有成就', '社会地位高']
            else:
                analysis['relationship_nature'] = '传统的父子关系'
                analysis['positive_aspects'] = ['子女有责任心', '事业有成']
        
        return analysis

    def _predict_liuqin_fortune(self, liuqin: str, shen: str) -> Dict[str, str]:
        """预测六亲运势"""
        predictions = {
            'early_years': '',
            'middle_years': '',
            'later_years': '',
            'overall_trend': ''
        }
        
        # 基于十神特性预测
        if shen in ['印', '比']:
            predictions['early_years'] = '早年关系良好，得到支持'
            predictions['middle_years'] = '中年关系稳定，相互扶持'
            predictions['later_years'] = '晚年情深，享受天伦'
            predictions['overall_trend'] = '整体关系和谐稳定'
        
        elif shen in ['财', '官']:
            predictions['early_years'] = '早年关系一般，需要磨合'
            predictions['middle_years'] = '中年关系改善，互相理解'
            predictions['later_years'] = '晚年关系融洽，相互依靠'
            predictions['overall_trend'] = '关系逐步改善，越来越好'
        
        elif shen in ['食', '伤']:
            predictions['early_years'] = '早年关系活跃，变化较多'
            predictions['middle_years'] = '中年关系复杂，需要沟通'
            predictions['later_years'] = '晚年关系趋于稳定'
            predictions['overall_trend'] = '关系多变但最终趋于稳定'
        
        else:
            predictions['overall_trend'] = '关系平稳，无特殊变化'
        
        return predictions

    def _get_liuqin_suggestions(self, liuqin: str, shen: str, count: int) -> List[str]:
        """获取六亲关系建议"""
        suggestions = []
        
        # 通用建议
        if count == 0:
            suggestions.append(f"缺少{liuqin}星，需要主动维护{liuqin}关系")
            suggestions.append("可通过五行调理来改善相关运势")
        elif count > 2:
            suggestions.append(f"{liuqin}星过多，需要平衡处理各种关系")
            suggestions.append("避免过度依赖或被过度依赖")
        
        # 具体建议
        if liuqin in ['父亲', '母亲']:
            suggestions.append("多关心父母健康，常回家看看")
            suggestions.append("在重大决策时可征求父母意见")
        
        elif liuqin in ['妻子', '丈夫']:
            suggestions.append("夫妻之间要多沟通，相互理解")
            suggestions.append("在事业和家庭之间找到平衡点")
        
        elif liuqin in ['兄弟', '姐妹']:
            suggestions.append("维护手足情谊，但要保持适当独立")
            suggestions.append("在利益面前要公平处理，避免争执")
        
        elif liuqin in ['儿子', '女儿']:
            suggestions.append("教育子女要宽严并济，因材施教")
            suggestions.append("培养子女独立能力，不要过度溺爱")
        
        return suggestions

    def _analyze_marriage(self):
        """专项分析婚姻情况"""
        self.marriage_analysis = {
            'marriage_star': '',
            'marriage_palace': '',
            'marriage_timing': '',
            'marriage_quality': '',
            'spouse_characteristics': {},
            'marriage_challenges': [],
            'marriage_suggestions': []
        }
        
        if self.is_female:
            # 女命看官杀为夫星
            official_count = self.gan_shens.count('官') + self.zhi_shens.count('官')
            kill_count = self.gan_shens.count('杀') + self.zhi_shens.count('杀')
            
            if official_count > 0:
                self.marriage_analysis['marriage_star'] = f"正官{official_count}个"
                self.marriage_analysis['marriage_quality'] = '婚姻稳定，丈夫可靠'
            elif kill_count > 0:
                self.marriage_analysis['marriage_star'] = f"七杀{kill_count}个"
                self.marriage_analysis['marriage_quality'] = '感情激烈，但需要磨合'
            else:
                self.marriage_analysis['marriage_star'] = '无明显夫星'
                self.marriage_analysis['marriage_quality'] = '婚姻缘分较薄，需主动争取'
            
            if official_count + kill_count > 1:
                self.marriage_analysis['marriage_challenges'].append('感情选择复杂，容易多角恋')
        
        else:
            # 男命看财星为妻星
            wealth_count = self.gan_shens.count('财') + self.zhi_shens.count('财')
            partial_wealth_count = self.gan_shens.count('才') + self.zhi_shens.count('才')
            
            if wealth_count > 0:
                self.marriage_analysis['marriage_star'] = f"正财{wealth_count}个"
                self.marriage_analysis['marriage_quality'] = '婚姻和谐，妻子贤惠'
            elif partial_wealth_count > 0:
                self.marriage_analysis['marriage_star'] = f"偏财{partial_wealth_count}个"
                self.marriage_analysis['marriage_quality'] = '婚姻现实，注重物质'
            else:
                self.marriage_analysis['marriage_star'] = '无明显妻星'
                self.marriage_analysis['marriage_quality'] = '婚姻缘分较薄，需主动争取'
            
            if wealth_count + partial_wealth_count > 1:
                self.marriage_analysis['marriage_challenges'].append('感情复杂，可能有多妻倾向')
        
        # 分析婚姻宫（日支）
        if len(self.zhi_shens) > 2:
            day_zhi_shen = self.zhi_shens[2]
            self.marriage_analysis['marriage_palace'] = f"婚姻宫为{day_zhi_shen}"
            
            if self.is_female and day_zhi_shen in ['官', '杀']:
                self.marriage_analysis['marriage_suggestions'].append('婚姻宫有官杀，利于婚姻')
            elif not self.is_female and day_zhi_shen in ['财', '才']:
                self.marriage_analysis['marriage_suggestions'].append('婚姻宫有财星，利于婚姻')
            elif day_zhi_shen in ['比', '劫']:
                self.marriage_analysis['marriage_challenges'].append('婚姻宫有比劫，配偶易被夺')
            elif day_zhi_shen in ['食', '伤']:
                self.marriage_analysis['marriage_challenges'].append('婚姻宫有食伤，配偶关系复杂')

    def _analyze_children(self):
        """专项分析子女情况"""
        self.children_analysis = {
            'children_star': '',
            'children_palace': '',
            'fertility': '',
            'children_quality': '',
            'children_relationship': '',
            'children_future': '',
            'children_suggestions': []
        }
        
        # 分析食伤为子女星
        food_count = self.gan_shens.count('食') + self.zhi_shens.count('食')
        hurt_count = self.gan_shens.count('伤') + self.zhi_shens.count('伤')
        
        if food_count > 0:
            self.children_analysis['children_star'] = f"食神{food_count}个"
            self.children_analysis['children_quality'] = '子女孝顺，关系和谐'
            self.children_analysis['fertility'] = '生育能力良好'
        
        if hurt_count > 0:
            self.children_analysis['children_star'] += f" 伤官{hurt_count}个"
            self.children_analysis['children_quality'] = '子女聪明但个性强'
            self.children_analysis['fertility'] = '生育能力强，但需注意教育'
        
        if food_count + hurt_count == 0:
            self.children_analysis['children_star'] = '无明显子女星'
            self.children_analysis['fertility'] = '子女缘分较薄'
            self.children_analysis['children_suggestions'].append('需要积极调理，改善子女运')
        
        # 分析时柱为子女宫
        if len(self.gan_shens) > 3 and len(self.zhi_shens) > 3:
            time_gan_shen = self.gan_shens[3]
            time_zhi_shen = self.zhi_shens[3]
            
            self.children_analysis['children_palace'] = f"子女宫：天干{time_gan_shen}，地支{time_zhi_shen}"
            
            if time_gan_shen in ['食', '伤'] or time_zhi_shen in ['食', '伤']:
                self.children_analysis['children_suggestions'].append('时柱有食伤，利于生育')
            elif time_gan_shen in ['官', '杀'] or time_zhi_shen in ['官', '杀']:
                self.children_analysis['children_suggestions'].append('时柱有官杀，子女有出息')
            elif time_gan_shen in ['印', '枭'] or time_zhi_shen in ['印', '枭']:
                self.children_analysis['children_suggestions'].append('时柱有印星，子女聪明好学')

    def _analyze_parents(self):
        """专项分析父母情况"""
        self.parents_analysis = {
            'father_star': '',
            'mother_star': '',
            'father_relationship': '',
            'mother_relationship': '',
            'parents_health': '',
            'parents_support': '',
            'parents_suggestions': []
        }
        
        # 分析印星为母亲
        seal_count = self.gan_shens.count('印') + self.zhi_shens.count('印')
        offset_count = self.gan_shens.count('枭') + self.zhi_shens.count('枭')
        
        if seal_count > 0:
            self.parents_analysis['mother_star'] = f"正印{seal_count}个"
            self.parents_analysis['mother_relationship'] = '母子关系深厚，母爱充沛'
        elif offset_count > 0:
            self.parents_analysis['mother_star'] = f"偏印{offset_count}个"
            self.parents_analysis['mother_relationship'] = '与母亲关系复杂，需要理解'
        else:
            self.parents_analysis['mother_star'] = '无明显母星'
            self.parents_analysis['mother_relationship'] = '与母亲缘分较薄'
        
        # 分析财星为父亲
        wealth_count = self.gan_shens.count('财') + self.zhi_shens.count('财')
        partial_wealth_count = self.gan_shens.count('才') + self.zhi_shens.count('才')
        
        if wealth_count > 0:
            self.parents_analysis['father_star'] = f"正财{wealth_count}个"
            self.parents_analysis['father_relationship'] = '父子关系稳定，父亲负责'
        elif partial_wealth_count > 0:
            self.parents_analysis['father_star'] = f"偏财{partial_wealth_count}个"
            self.parents_analysis['father_relationship'] = '与父亲关系较为疏远'
        else:
            self.parents_analysis['father_star'] = '无明显父星'
            self.parents_analysis['father_relationship'] = '与父亲缘分较薄'
        
        # 综合分析
        if seal_count + offset_count > 1:
            self.parents_analysis['parents_suggestions'].append('印星过多，需要培养独立性')
        if wealth_count + partial_wealth_count > 1:
            self.parents_analysis['parents_suggestions'].append('财星过多，注意与父亲的关系平衡')

    def _analyze_siblings(self):
        """专项分析兄弟姐妹情况"""
        self.siblings_analysis = {
            'siblings_star': '',
            'siblings_count': '',
            'siblings_relationship': '',
            'siblings_support': '',
            'siblings_competition': '',
            'siblings_suggestions': []
        }
        
        # 分析比劫为兄弟姐妹
        rob_count = self.gan_shens.count('比') + self.zhi_shens.count('比')
        compete_count = self.gan_shens.count('劫') + self.zhi_shens.count('劫')
        
        total_siblings = rob_count + compete_count
        
        if rob_count > 0:
            self.siblings_analysis['siblings_star'] = f"比肩{rob_count}个"
            self.siblings_analysis['siblings_relationship'] = '兄弟姐妹关系和睦'
        
        if compete_count > 0:
            self.siblings_analysis['siblings_star'] += f" 劫财{compete_count}个"
            self.siblings_analysis['siblings_relationship'] = '兄弟姐妹关系有竞争'
        
        if total_siblings == 0:
            self.siblings_analysis['siblings_star'] = '无明显兄弟姐妹星'
            self.siblings_analysis['siblings_count'] = '兄弟姐妹较少或关系疏远'
        elif total_siblings == 1:
            self.siblings_analysis['siblings_count'] = '兄弟姐妹适中，关系良好'
        elif total_siblings == 2:
            self.siblings_analysis['siblings_count'] = '兄弟姐妹较多，关系密切'
        else:
            self.siblings_analysis['siblings_count'] = '兄弟姐妹很多，关系复杂'
            self.siblings_analysis['siblings_suggestions'].append('比劫过多，需要保持独立性')
        
        # 分析月柱为兄弟姐妹宫
        if len(self.gan_shens) > 1 and len(self.zhi_shens) > 1:
            month_gan_shen = self.gan_shens[1]
            month_zhi_shen = self.zhi_shens[1]
            
            if month_gan_shen in ['比', '劫'] or month_zhi_shen in ['比', '劫']:
                self.siblings_analysis['siblings_support'] = '月柱有比劫，兄弟姐妹互相支持'
            elif month_gan_shen in ['官', '杀'] or month_zhi_shen in ['官', '杀']:
                self.siblings_analysis['siblings_competition'] = '月柱有官杀，与兄弟姐妹有竞争'

    def _analyze_liuqin_statistics(self):
        """分析六亲统计信息"""
        all_shens = self.gan_shens + self.zhi_shens
        shen_counts = Counter(all_shens)
        
        self.liuqin_statistics = {
            'total_liuqin_stars': 0,
            'strongest_liuqin': '',
            'weakest_liuqin': '',
            'balanced_assessment': '',
            'overall_liuqin_fortune': '',
            'distribution': {}
        }
        
        # 统计各类六亲星的数量
        liuqin_counts = {}
        for shen, count in shen_counts.items():
            if shen in self.liuqin_mapping:
                liuqin = self.liuqin_mapping[shen]
                if liuqin not in liuqin_counts:
                    liuqin_counts[liuqin] = 0
                liuqin_counts[liuqin] += count
        
        self.liuqin_statistics['distribution'] = liuqin_counts
        self.liuqin_statistics['total_liuqin_stars'] = sum(liuqin_counts.values())
        
        # 找出最强和最弱的六亲关系
        if liuqin_counts:
            self.liuqin_statistics['strongest_liuqin'] = max(liuqin_counts.keys(), key=lambda x: liuqin_counts[x])
            self.liuqin_statistics['weakest_liuqin'] = min(liuqin_counts.keys(), key=lambda x: liuqin_counts[x])
        
        # 评估整体六亲运势
        total_score = sum(self._score_liuqin_relationship(liuqin, count) for liuqin, count in liuqin_counts.items())
        
        if total_score >= 20:
            self.liuqin_statistics['overall_liuqin_fortune'] = '六亲关系整体良好，家庭和睦'
        elif total_score >= 10:
            self.liuqin_statistics['overall_liuqin_fortune'] = '六亲关系一般，需要主动维护'
        else:
            self.liuqin_statistics['overall_liuqin_fortune'] = '六亲关系较弱，需要积极改善'

    def _score_liuqin_relationship(self, liuqin: str, count: int) -> int:
        """为六亲关系打分"""
        base_score = min(count, 3) * 2  # 基础分数，最高6分
        
        # 根据六亲类型调整
        if liuqin in ['母亲', '父亲']:
            base_score += 2  # 父母关系更重要
        elif liuqin in ['妻子', '丈夫']:
            base_score += 3  # 配偶关系最重要
        elif liuqin in ['儿子', '女儿']:
            base_score += 1  # 子女关系重要
        
        # 过多的惩罚
        if count > 3:
            base_score -= (count - 3)
        
        return max(0, base_score)

    def _evaluate_liuqin_fortune(self):
        """评估六亲运势"""
        self.liuqin_predictions = {
            'marriage_fortune': self._predict_marriage_fortune(),
            'children_fortune': self._predict_children_fortune(),
            'parents_fortune': self._predict_parents_fortune(),
            'siblings_fortune': self._predict_siblings_fortune(),
            'overall_suggestions': self._get_overall_liuqin_suggestions()
        }

    def _predict_marriage_fortune(self) -> Dict[str, str]:
        """预测婚姻运势"""
        predictions = {
            'early_marriage': '一般',
            'middle_marriage': '一般',
            'late_marriage': '一般',
            'overall_trend': '平稳'
        }
        
        if self.is_female:
            official_count = self.gan_shens.count('官') + self.zhi_shens.count('官')
            if official_count > 0:
                predictions['overall_trend'] = '婚姻稳定，感情和睦'
        else:
            wealth_count = self.gan_shens.count('财') + self.zhi_shens.count('财')
            if wealth_count > 0:
                predictions['overall_trend'] = '婚姻幸福，妻子贤惠'
        
        return predictions

    def _predict_children_fortune(self) -> Dict[str, str]:
        """预测子女运势"""
        predictions = {
            'fertility': '一般',
            'children_success': '一般',
            'parent_child_relationship': '一般',
            'overall_trend': '平稳'
        }
        
        food_count = self.gan_shens.count('食') + self.zhi_shens.count('食')
        if food_count > 0:
            predictions['overall_trend'] = '子女孝顺，晚年幸福'
        
        return predictions

    def _predict_parents_fortune(self) -> Dict[str, str]:
        """预测父母运势"""
        predictions = {
            'father_relationship': '一般',
            'mother_relationship': '一般',
            'parents_health': '一般',
            'overall_trend': '平稳'
        }
        
        seal_count = self.gan_shens.count('印') + self.zhi_shens.count('印')
        if seal_count > 0:
            predictions['mother_relationship'] = '良好'
            predictions['overall_trend'] = '与母亲关系深厚'
        
        return predictions

    def _predict_siblings_fortune(self) -> Dict[str, str]:
        """预测兄弟姐妹运势"""
        predictions = {
            'sibling_support': '一般',
            'sibling_harmony': '一般',
            'mutual_help': '一般',
            'overall_trend': '平稳'
        }
        
        rob_count = self.gan_shens.count('比') + self.zhi_shens.count('比')
        if rob_count > 0:
            predictions['overall_trend'] = '兄弟姐妹关系和睦，互相支持'
        
        return predictions

    def _get_overall_liuqin_suggestions(self) -> List[str]:
        """获取整体六亲建议"""
        suggestions = [
            "维护家庭和睦，珍惜亲情",
            "在处理家庭关系时要公平公正",
            "适当时候要学会独立，不过度依赖",
            "重要决策时可征求家人意见",
            "定期与家人沟通，增进感情"
        ]
        
        # 根据具体情况添加建议
        if self.liuqin_statistics['total_liuqin_stars'] < 5:
            suggestions.append("六亲星较少，需要主动维护各种关系")
        elif self.liuqin_statistics['total_liuqin_stars'] > 10:
            suggestions.append("六亲星较多，要平衡处理各种关系")
        
        return suggestions

    def get_liuqin_table_lines(self) -> List[str]:
        """获取六亲分析表格行"""
        lines = []
        
        # 表头
        lines.append("天干六亲分析：")
        for i, gan in enumerate(['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']):
            if gan in ten_deities.get(self.me, {}):
                shen = ten_deities[self.me][gan]
                liuqin = self.liuqin_mapping.get(shen, '未知')
                
                # 计算该天干在四柱中的分布
                pillar_info = []
                if i < len(self.gan_shens):
                    for j, pillar_shen in enumerate(self.gan_shens):
                        if pillar_shen == shen:
                            pillar_info.append(f"第{j+1}柱")
                
                pillar_str = ','.join(pillar_info) if pillar_info else '无'
                score = self.gan_scores.get(gan, 0)
                
                line = f"{gan}:{shen} {liuqin} 分数:{score} 位置:{pillar_str}"
                lines.append(line)
            
            if (i + 1) % 5 == 0:  # 每5个换行
                lines.append("")
        
        return lines

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的六亲分析结果"""
        return {
            "liuqin_mapping": self.liuqin_mapping,
            "liuqin_analysis": self.liuqin_analysis,
            "liuqin_relationships": self.liuqin_relationships,
            "marriage_analysis": self.marriage_analysis,
            "children_analysis": self.children_analysis,
            "parents_analysis": self.parents_analysis,
            "siblings_analysis": self.siblings_analysis,
            "liuqin_statistics": self.liuqin_statistics,
            "liuqin_predictions": self.liuqin_predictions,
            "table_lines": self.get_liuqin_table_lines(),
            "summary_stats": {
                "total_relationships": len(self.liuqin_relationships),
                "strongest_liuqin": self.liuqin_statistics.get('strongest_liuqin', ''),
                "overall_fortune": self.liuqin_statistics.get('overall_liuqin_fortune', ''),
                "marriage_quality": self.marriage_analysis.get('marriage_quality', ''),
                "children_prospect": self.children_analysis.get('fertility', ''),
                "parents_relationship": f"父:{self.parents_analysis.get('father_relationship', '')} 母:{self.parents_analysis.get('mother_relationship', '')}"
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取六亲分析摘要"""
        return {
            "basic_summary": f"六亲分析：{self.liuqin_statistics['total_liuqin_stars']}个六亲星",
            "marriage_summary": f"婚姻：{self.marriage_analysis.get('marriage_quality', '一般')}",
            "children_summary": f"子女：{self.children_analysis.get('fertility', '一般')}",
            "parents_summary": f"父母关系：{self.parents_analysis.get('father_relationship', '一般')} / {self.parents_analysis.get('mother_relationship', '一般')}",
            "siblings_summary": f"兄弟姐妹：{self.siblings_analysis.get('siblings_relationship', '一般')}",
            "overall_assessment": self.liuqin_statistics.get('overall_liuqin_fortune', '六亲关系平稳'),
            "main_suggestions": "；".join(self.liuqin_predictions.get('overall_suggestions', [])[:3])
        }

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的六亲数据"""
        return {
            "六亲概况": {
                "性别": self.gender,
                "六亲星总数": self.liuqin_statistics['total_liuqin_stars'],
                "最强六亲": self.liuqin_statistics.get('strongest_liuqin', ''),
                "整体评估": self.liuqin_statistics.get('overall_liuqin_fortune', '')
            },
            "婚姻分析": {
                "婚姻星": self.marriage_analysis.get('marriage_star', ''),
                "婚姻质量": self.marriage_analysis.get('marriage_quality', ''),
                "婚姻宫": self.marriage_analysis.get('marriage_palace', ''),
                "主要挑战": self.marriage_analysis.get('marriage_challenges', []),
                "改善建议": self.marriage_analysis.get('marriage_suggestions', [])
            },
            "子女分析": {
                "子女星": self.children_analysis.get('children_star', ''),
                "生育能力": self.children_analysis.get('fertility', ''),
                "子女品质": self.children_analysis.get('children_quality', ''),
                "亲子关系": self.children_analysis.get('children_relationship', ''),
                "教育建议": self.children_analysis.get('children_suggestions', [])
            },
            "父母分析": {
                "父亲星": self.parents_analysis.get('father_star', ''),
                "母亲星": self.parents_analysis.get('mother_star', ''),
                "父子关系": self.parents_analysis.get('father_relationship', ''),
                "母子关系": self.parents_analysis.get('mother_relationship', ''),
                "孝亲建议": self.parents_analysis.get('parents_suggestions', [])
            },
            "兄弟姐妹": {
                "手足星": self.siblings_analysis.get('siblings_star', ''),
                "手足数量": self.siblings_analysis.get('siblings_count', ''),
                "关系性质": self.siblings_analysis.get('siblings_relationship', ''),
                "相处建议": self.siblings_analysis.get('siblings_suggestions', [])
            },
            "各柱六亲": [
                {
                    "柱位": analysis.get('pillar', ''),
                    "天干六亲": analysis.get('gan_liuqin', ''),
                    "地支六亲": analysis.get('zhi_liuqin', ''),
                    "关系质量": analysis.get('analysis', {}).get('relationship_quality', ''),
                    "主要特点": analysis.get('analysis', {}).get('primary_focus', '')
                }
                for analysis in [self.liuqin_analysis.get(pillar, {}) for pillar in ['年柱', '月柱', '日柱', '时柱']]
                if analysis
            ],
            "运势预测": {
                "婚姻运势": self.liuqin_predictions.get('marriage_fortune', {}),
                "子女运势": self.liuqin_predictions.get('children_fortune', {}),
                "父母运势": self.liuqin_predictions.get('parents_fortune', {}),
                "兄弟运势": self.liuqin_predictions.get('siblings_fortune', {})
            },
            "重点建议": self.liuqin_predictions.get('overall_suggestions', [])
        }


def test_liuqin_analysis_module():
    """测试六亲分析模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    from .shens_analysis import ShensAnalysisModule
    from .zhi_relations import ZhiRelationsModule
    from .dayun_analysis import DayunAnalysisModule
    from .liunian_analysis import LiunianAnalysisModule
    
    print("=== 六亲分析模块测试 ===")
    
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
    
    print("2. 创建六亲分析模块...")
    liuqin_analysis = LiuqinAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                          detail_info_data, shens_analysis_data, zhi_relations_data,
                                          dayun_analysis_data, liunian_analysis_data)
    
    print("\n3. 六亲分析结果：")
    result = liuqin_analysis.get_result()
    
    print(f"   六亲星总数: {result['summary_stats']['total_relationships']}")
    print(f"   最强六亲: {result['summary_stats']['strongest_liuqin']}")
    print(f"   整体评估: {result['summary_stats']['overall_fortune']}")
    
    return result


if __name__ == "__main__":
    test_liuqin_analysis_module() 