"""
地支关系模块 - 处理八字中地支间的复杂关系
包含六合、六冲、三合局、三会局、六害、三刑、拱合等关系的识别和分析
"""

from typing import Dict, Any, List, Tuple, Optional, Set

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
        # 设置默认的地支关系数据
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 地支属性关系
        zhi_atts = {
            "子": {"冲": "午", "刑": "卯", "被刑": "卯", "合": ("申", "辰"), "会": ("亥", "丑"), '害': '未', '破': '酉', "六": "丑", "暗": ""},
            "丑": {"冲": "未", "刑": "戌", "被刑": "未", "合": ("巳", "酉"), "会": ("子", "亥"), '害': '午', '破': '辰', "六": "子", "暗": "寅"},
            "寅": {"冲": "申", "刑": "巳", "被刑": "申", "合": ("午", "戌"), "会": ("卯", "辰"), '害': '巳', '破': '亥', "六": "亥", "暗": "丑"},
            "卯": {"冲": "酉", "刑": "子", "被刑": "子", "合": ("未", "亥"), "会": ("寅", "辰"), '害': '辰', '破': '午', "六": "戌", "暗": "申"},
            "辰": {"冲": "戌", "刑": "辰", "被刑": "辰", "合": ("子", "申"), "会": ("寅", "卯"), '害': '卯', '破': '丑', "六": "酉", "暗": ""},
            "巳": {"冲": "亥", "刑": "申", "被刑": "寅", "合": ("酉", "丑"), "会": ("午", "未"), '害': '寅', '破': '申', "六": "申", "暗": ""},
            "午": {"冲": "子", "刑": "午", "被刑": "午", "合": ("寅", "戌"), "会": ("巳", "未"), '害': '丑', '破': '卯', "六": "未", "暗": "亥"},
            "未": {"冲": "丑", "刑": "丑", "被刑": "戌", "合": ("卯", "亥"), "会": ("巳", "午"), '害': '子', '破': '戌', "六": "午", "暗": ""},
            "申": {"冲": "寅", "刑": "寅", "被刑": "巳", "合": ("子", "辰"), "会": ("酉", "戌"), '害': '亥', '破': '巳', "六": "巳", "暗": "卯"},
            "酉": {"冲": "卯", "刑": "酉", "被刑": "酉", "合": ("巳", "丑"), "会": ("申", "戌"), '害': '戌', '破': '子', "六": "辰", "暗": ""},
            "戌": {"冲": "辰", "刑": "未", "被刑": "丑", "合": ("午", "寅"), "会": ("申", "酉"), '害': '酉', '破': '未', "六": "卯", "暗": ""},
            "亥": {"冲": "巳", "刑": "亥", "被刑": "亥", "合": ("卯", "未"), "会": ("子", "丑"), '害': '申', '破': '寅', "六": "寅", "暗": "午"},
        }

        # 六合关系
        zhi_6hes = {
            "子丑": "土", "寅亥": "木", "卯戌": "火", 
            "酉辰": "金", "申巳": "水", "未午": "土"
        }

        # 三合局
        zhi_hes = {
            "申子辰": "水", "巳酉丑": "金", "寅午戌": "火", "亥卯未": "木"
        }

        # 三会局
        zhi_huis = {
            "亥子丑": "水", "寅卯辰": "木", "巳午未": "火", "申酉戌": "金"
        }

        # 拱合关系
        gong_he = {
            "申辰": '子', "巳丑": '酉', "寅戌": '午', "亥未": '卯',
            "辰申": '子', "丑巳": '酉', "戌寅": '午', "未亥": '卯'
        }

        # 拱会关系
        gong_hui = {
            "亥丑": '子', "寅辰": '卯', "巳未": '午', "申戌": '酉',
            "丑亥": '子', "辰寅": '卯', "未巳": '午', "戌申": '酉'
        }

        # 六冲关系
        zhi_chongs = {
            ("子", "午"): "相冲", ("丑", "未"): "相冲", ("寅", "申"): "相冲",
            ("卯", "酉"): "相冲", ("辰", "戌"): "相冲", ("巳", "亥"): "相冲"
        }

        # 六害关系
        zhi_haies = {
            ("子", "未"): "子未害", ("丑", "午"): "丑午害", ("寅", "巳"): "寅巳害",
            ("卯", "辰"): "卯辰害", ("申", "亥"): "申亥害", ("酉", "戌"): "酉戌害"
        }

        # 三刑关系
        zhi_xings = {
            ("寅", "巳"): "寅刑巳 无恩之刑", ("巳", "申"): "巳刑申 无恩之刑", ("申", "寅"): "申刑寅 无恩之刑",
            ("未", "丑"): "未刑丑 持势之刑", ("丑", "戌"): "丑刑戌 持势之刑", ("戌", "未"): "戌刑未 持势之刑",
            ("子", "卯"): "子刑卯 无礼之刑", ("卯", "子"): "卯刑子 无礼之刑"
        }

        # 自刑
        zhi_zixings = ['辰', '午', '酉', '亥']

        # 相破关系
        zhi_poes = {
            ("子", "酉"): "相破", ("午", "卯"): "相破",
            ("辰", "丑"): "相破", ("戌", "未"): "相破"
        }


class ZhiRelationsModule:
    """地支关系模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any],
                 shens_analysis_data: Dict[str, Any]):
        """
        初始化地支关系模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
            detail_info_data: 来自DetailInfoModule的详细信息数据
            shens_analysis_data: 来自ShensAnalysisModule的神煞分析数据
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
            # 备用数据提取
            self.gans = bazi_main_data.get('gans', [])
            self.zhis = bazi_main_data.get('zhis', [])
            self.me = bazi_main_data.get('me', '')
            self.zhus = bazi_main_data.get('zhus', [])
        
        # 地支关系分析结果
        self.liu_he_relations = []      # 六合关系
        self.liu_chong_relations = []   # 六冲关系
        self.san_he_relations = []      # 三合局关系
        self.san_hui_relations = []     # 三会局关系
        self.liu_hai_relations = []     # 六害关系
        self.san_xing_relations = []    # 三刑关系
        self.zi_xing_relations = []     # 自刑关系
        self.xiang_po_relations = []    # 相破关系
        self.gong_he_relations = []     # 拱合关系
        self.gong_hui_relations = []    # 拱会关系
        
        # 相邻关系（只有相邻的才有力）
        self.adjacent_liu_he = [False, False, False, False]      # 相邻六合
        self.adjacent_liu_chong = [False, False, False, False]   # 相邻六冲
        self.adjacent_gan_he = [False, False, False, False]      # 相邻天干合
        self.adjacent_zhi_xing = [False, False, False, False]    # 相邻地支刑
        
        # 关系强度和影响
        self.relation_impacts = {}      # 各种关系的影响评估
        self.special_patterns = []      # 特殊格局
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行地支关系分析计算"""
        self._analyze_liu_he()
        self._analyze_liu_chong()
        self._analyze_san_he()
        self._analyze_san_hui()
        self._analyze_liu_hai()
        self._analyze_san_xing()
        self._analyze_zi_xing()
        self._analyze_xiang_po()
        self._analyze_gong_he()
        self._analyze_gong_hui()
        self._analyze_adjacent_relations()
        self._analyze_special_patterns()
        self._evaluate_relation_impacts()

    def _analyze_liu_he(self):
        """分析六合关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查六合关系
                he_key1 = zhi1 + zhi2
                he_key2 = zhi2 + zhi1
                
                if he_key1 in zhi_6hes or he_key2 in zhi_6hes:
                    element = zhi_6hes.get(he_key1, zhi_6hes.get(he_key2, ''))
                    is_adjacent = abs(i - j) == 1
                    
                    relation = {
                        'type': '六合',
                        'positions': (i, j),
                        'zhis': (zhi1, zhi2),
                        'element': element,
                        'is_adjacent': is_adjacent,
                        'strength': 'strong' if is_adjacent else 'weak',
                        'description': f"{zhi1}{zhi2}六合化{element}，{'力量较强' if is_adjacent else '力量较弱'}"
                    }
                    
                    self.liu_he_relations.append(relation)

    def _analyze_liu_chong(self):
        """分析六冲关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查六冲关系
                if (zhi1, zhi2) in zhi_chongs or (zhi2, zhi1) in zhi_chongs:
                    is_adjacent = abs(i - j) == 1
                    
                    relation = {
                        'type': '六冲',
                        'positions': (i, j),
                        'zhis': (zhi1, zhi2),
                        'is_adjacent': is_adjacent,
                        'strength': 'strong' if is_adjacent else 'weak',
                        'description': f"{zhi1}{zhi2}六冲，{'冲力较强' if is_adjacent else '冲力较弱'}"
                    }
                    
                    self.liu_chong_relations.append(relation)

    def _analyze_san_he(self):
        """分析三合局关系"""
        # 检查完整的三合局
        for he_combo, element in zhi_hes.items():
            he_zhis = list(he_combo)
            if all(zhi in self.zhis for zhi in he_zhis):
                positions = [self.zhis.index(zhi) for zhi in he_zhis]
                
                relation = {
                    'type': '三合局',
                    'positions': positions,
                    'zhis': he_zhis,
                    'element': element,
                    'strength': 'complete',
                    'description': f"{''.join(he_zhis)}三合{element}局"
                }
                
                self.san_he_relations.append(relation)
        
        # 检查半合局（两个地支的组合）
        for he_combo, element in zhi_hes.items():
            he_zhis = list(he_combo)
            for i in range(len(he_zhis)):
                for j in range(i + 1, len(he_zhis)):
                    zhi1, zhi2 = he_zhis[i], he_zhis[j]
                    if zhi1 in self.zhis and zhi2 in self.zhis:
                        pos1, pos2 = self.zhis.index(zhi1), self.zhis.index(zhi2)
                        
                        relation = {
                            'type': '半三合',
                            'positions': (pos1, pos2),
                            'zhis': (zhi1, zhi2),
                            'element': element,
                            'missing_zhi': [z for z in he_zhis if z not in [zhi1, zhi2]][0],
                            'strength': 'partial',
                            'description': f"{zhi1}{zhi2}半合{element}，缺{[z for z in he_zhis if z not in [zhi1, zhi2]][0]}"
                        }
                        
                        self.san_he_relations.append(relation)

    def _analyze_san_hui(self):
        """分析三会局关系"""
        # 检查完整的三会局
        for hui_combo, element in zhi_huis.items():
            hui_zhis = list(hui_combo)
            if all(zhi in self.zhis for zhi in hui_zhis):
                positions = [self.zhis.index(zhi) for zhi in hui_zhis]
                
                relation = {
                    'type': '三会局',
                    'positions': positions,
                    'zhis': hui_zhis,
                    'element': element,
                    'strength': 'complete',
                    'description': f"{''.join(hui_zhis)}三会{element}局"
                }
                
                self.san_hui_relations.append(relation)
        
        # 检查半会局
        for hui_combo, element in zhi_huis.items():
            hui_zhis = list(hui_combo)
            for i in range(len(hui_zhis)):
                for j in range(i + 1, len(hui_zhis)):
                    zhi1, zhi2 = hui_zhis[i], hui_zhis[j]
                    if zhi1 in self.zhis and zhi2 in self.zhis:
                        pos1, pos2 = self.zhis.index(zhi1), self.zhis.index(zhi2)
                        
                        relation = {
                            'type': '半三会',
                            'positions': (pos1, pos2),
                            'zhis': (zhi1, zhi2),
                            'element': element,
                            'missing_zhi': [z for z in hui_zhis if z not in [zhi1, zhi2]][0],
                            'strength': 'partial',
                            'description': f"{zhi1}{zhi2}半会{element}，缺{[z for z in hui_zhis if z not in [zhi1, zhi2]][0]}"
                        }
                        
                        self.san_hui_relations.append(relation)

    def _analyze_liu_hai(self):
        """分析六害关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查六害关系
                if (zhi1, zhi2) in zhi_haies or (zhi2, zhi1) in zhi_haies:
                    harm_desc = zhi_haies.get((zhi1, zhi2), zhi_haies.get((zhi2, zhi1), ''))
                    
                    relation = {
                        'type': '六害',
                        'positions': (i, j),
                        'zhis': (zhi1, zhi2),
                        'description': harm_desc,
                        'severity': self._evaluate_harm_severity(zhi1, zhi2)
                    }
                    
                    self.liu_hai_relations.append(relation)

    def _analyze_san_xing(self):
        """分析三刑关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查三刑关系
                if (zhi1, zhi2) in zhi_xings or (zhi2, zhi1) in zhi_xings:
                    xing_desc = zhi_xings.get((zhi1, zhi2), zhi_xings.get((zhi2, zhi1), ''))
                    
                    relation = {
                        'type': '三刑',
                        'positions': (i, j),
                        'zhis': (zhi1, zhi2),
                        'description': xing_desc,
                        'xing_type': self._get_xing_type(xing_desc)
                    }
                    
                    self.san_xing_relations.append(relation)

    def _analyze_zi_xing(self):
        """分析自刑关系"""
        zhi_counts = {}
        for i, zhi in enumerate(self.zhis):
            if zhi in zhi_zixings:
                if zhi not in zhi_counts:
                    zhi_counts[zhi] = []
                zhi_counts[zhi].append(i)
        
        for zhi, positions in zhi_counts.items():
            if len(positions) >= 2:
                relation = {
                    'type': '自刑',
                    'positions': positions,
                    'zhi': zhi,
                    'count': len(positions),
                    'description': f"{zhi}自刑，出现{len(positions)}次"
                }
                
                self.zi_xing_relations.append(relation)

    def _analyze_xiang_po(self):
        """分析相破关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查相破关系
                if (zhi1, zhi2) in zhi_poes or (zhi2, zhi1) in zhi_poes:
                    relation = {
                        'type': '相破',
                        'positions': (i, j),
                        'zhis': (zhi1, zhi2),
                        'description': f"{zhi1}{zhi2}相破"
                    }
                    
                    self.xiang_po_relations.append(relation)

    def _analyze_gong_he(self):
        """分析拱合关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查拱合关系
                gong_key1 = zhi1 + zhi2
                gong_key2 = zhi2 + zhi1
                
                if gong_key1 in gong_he or gong_key2 in gong_he:
                    target_zhi = gong_he.get(gong_key1, gong_he.get(gong_key2, ''))
                    if target_zhi not in self.zhis:  # 拱的地支不能在八字中出现
                        relation = {
                            'type': '拱合',
                            'positions': (i, j),
                            'zhis': (zhi1, zhi2),
                            'target_zhi': target_zhi,
                            'description': f"{zhi1}{zhi2}拱{target_zhi}"
                        }
                        
                        self.gong_he_relations.append(relation)

    def _analyze_gong_hui(self):
        """分析拱会关系"""
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 检查拱会关系
                gong_key1 = zhi1 + zhi2
                gong_key2 = zhi2 + zhi1
                
                if gong_key1 in gong_hui or gong_key2 in gong_hui:
                    target_zhi = gong_hui.get(gong_key1, gong_hui.get(gong_key2, ''))
                    if target_zhi not in self.zhis:  # 拱的地支不能在八字中出现
                        relation = {
                            'type': '拱会',
                            'positions': (i, j),
                            'zhis': (zhi1, zhi2),
                            'target_zhi': target_zhi,
                            'description': f"{zhi1}{zhi2}拱会{target_zhi}"
                        }
                        
                        self.gong_hui_relations.append(relation)

    def _analyze_adjacent_relations(self):
        """分析相邻关系（只有相邻的关系才有力）"""
        for i in range(3):
            zhi1, zhi2 = self.zhis[i], self.zhis[i + 1]
            
            # 相邻六合
            if zhi1 + zhi2 in zhi_6hes or zhi2 + zhi1 in zhi_6hes:
                self.adjacent_liu_he[i] = self.adjacent_liu_he[i + 1] = True
            
            # 相邻六冲
            if (zhi1, zhi2) in zhi_chongs or (zhi2, zhi1) in zhi_chongs:
                self.adjacent_liu_chong[i] = self.adjacent_liu_chong[i + 1] = True
            
            # 相邻地支刑
            if (zhi1, zhi2) in zhi_xings or (zhi2, zhi1) in zhi_xings:
                self.adjacent_zhi_xing[i] = self.adjacent_zhi_xing[i + 1] = True
        
        # 分析相邻天干合（需要天干数据）
        if len(self.gans) >= 4:
            gan_he_pairs = {
                ('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')
            }
            
            for i in range(3):
                gan1, gan2 = self.gans[i], self.gans[i + 1]
                if (gan1, gan2) in gan_he_pairs or (gan2, gan1) in gan_he_pairs:
                    self.adjacent_gan_he[i] = self.adjacent_gan_he[i + 1] = True

    def _analyze_special_patterns(self):
        """分析特殊格局"""
        # 天罗地网
        if '辰' in self.zhis and '巳' in self.zhis:
            self.special_patterns.append({
                'name': '地网',
                'elements': ['辰', '巳'],
                'description': '地网：地支辰巳。天罗：戌亥。天罗地网全凶。',
                'type': 'unfavorable'
            })
        
        if '戌' in self.zhis and '亥' in self.zhis:
            self.special_patterns.append({
                'name': '天罗',
                'elements': ['戌', '亥'],
                'description': '天罗：戌亥。地网：地支辰巳。天罗地网全凶。',
                'type': 'unfavorable'
            })
        
        # 四生、四败、四库全
        si_sheng = set(['寅', '申', '巳', '亥']) & set(self.zhis)
        si_bai = set(['子', '午', '卯', '酉']) & set(self.zhis)
        si_ku = set(['辰', '戌', '丑', '未']) & set(self.zhis)
        
        if len(si_sheng) == 4:
            self.special_patterns.append({
                'name': '四生全',
                'elements': list(si_sheng),
                'description': '四生全：寅申巳亥，主动变多迁移。',
                'type': 'neutral'
            })
        
        if len(si_bai) == 4:
            self.special_patterns.append({
                'name': '四败全',
                'elements': list(si_bai),
                'description': '四败全：子午卯酉，主桃花多情。',
                'type': 'mixed'
            })
        
        if len(si_ku) == 4:
            self.special_patterns.append({
                'name': '四库全',
                'elements': list(si_ku),
                'description': '四库全：辰戌丑未，主财库丰厚。',
                'type': 'favorable'
            })

    def _evaluate_relation_impacts(self):
        """评估各种关系的影响"""
        self.relation_impacts = {
            'favorable_relations': [],
            'unfavorable_relations': [],
            'neutral_relations': [],
            'resolution_relations': []  # 能够化解不利关系的关系
        }
        
        # 评估六合的积极影响
        for relation in self.liu_he_relations:
            if relation['is_adjacent']:
                self.relation_impacts['favorable_relations'].append({
                    'type': relation['type'],
                    'description': relation['description'],
                    'impact': 'strong_positive'
                })
        
        # 评估六冲的消极影响
        for relation in self.liu_chong_relations:
            if relation['is_adjacent']:
                self.relation_impacts['unfavorable_relations'].append({
                    'type': relation['type'],
                    'description': relation['description'],
                    'impact': 'strong_negative'
                })
        
        # 评估三合三会的积极影响
        for relation in self.san_he_relations + self.san_hui_relations:
            if relation['strength'] == 'complete':
                self.relation_impacts['favorable_relations'].append({
                    'type': relation['type'],
                    'description': relation['description'],
                    'impact': 'very_strong_positive'
                })
        
        # 评估刑害的消极影响
        for relation in self.san_xing_relations + self.liu_hai_relations:
            self.relation_impacts['unfavorable_relations'].append({
                'type': relation['type'],
                'description': relation['description'],
                'impact': 'negative'
            })

    def _evaluate_harm_severity(self, zhi1: str, zhi2: str) -> str:
        """评估六害的严重程度"""
        # 简化的害的严重程度评估
        severe_harms = [('子', '未'), ('丑', '午')]
        if (zhi1, zhi2) in severe_harms or (zhi2, zhi1) in severe_harms:
            return 'severe'
        else:
            return 'moderate'

    def _get_xing_type(self, xing_desc: str) -> str:
        """获取刑的类型"""
        if '无恩' in xing_desc:
            return '无恩之刑'
        elif '持势' in xing_desc:
            return '持势之刑'
        elif '无礼' in xing_desc:
            return '无礼之刑'
        else:
            return '其他刑'

    def get_relation_table_lines(self) -> List[str]:
        """获取地支关系表格行"""
        lines = []
        
        # 主要关系行（合冲）
        pillar_relations = ['', '', '', '']
        for i, zhi in enumerate(self.zhis):
            relations = []
            
            # 检查该位置的各种关系
            for relation in self.liu_he_relations:
                if i in relation['positions'] and relation['is_adjacent']:
                    relations.append('合')
            
            for relation in self.liu_chong_relations:
                if i in relation['positions'] and relation['is_adjacent']:
                    relations.append('冲')
            
            if relations:
                pillar_relations[i] = chr(12288).join(relations)
        
        if any(pillar_relations):
            line1 = "{1:{0}<15s}{2:{0}<15s}{3:{0}<15s}{4:{0}<15s}".format(
                chr(12288), *pillar_relations
            )
            lines.append(line1)
        
        # 次要关系行（刑害破）
        minor_relations = ['', '', '', '']
        for i, zhi in enumerate(self.zhis):
            relations = []
            
            for relation in self.san_xing_relations:
                if i in relation['positions']:
                    relations.append('刑')
            
            for relation in self.liu_hai_relations:
                if i in relation['positions']:
                    relations.append('害')
            
            for relation in self.xiang_po_relations:
                if i in relation['positions']:
                    relations.append('破')
            
            if relations:
                minor_relations[i] = chr(12288).join(relations)
        
        if any(minor_relations):
            line2 = "{1:{0}<15s}{2:{0}<15s}{3:{0}<15s}{4:{0}<15s}".format(
                chr(12288), *minor_relations
            )
            lines.append(line2)
        
        return lines

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的地支关系分析结果"""
        return {
            "liu_he_relations": self.liu_he_relations,
            "liu_chong_relations": self.liu_chong_relations,
            "san_he_relations": self.san_he_relations,
            "san_hui_relations": self.san_hui_relations,
            "liu_hai_relations": self.liu_hai_relations,
            "san_xing_relations": self.san_xing_relations,
            "zi_xing_relations": self.zi_xing_relations,
            "xiang_po_relations": self.xiang_po_relations,
            "gong_he_relations": self.gong_he_relations,
            "gong_hui_relations": self.gong_hui_relations,
            "adjacent_relations": {
                "liu_he": self.adjacent_liu_he,
                "liu_chong": self.adjacent_liu_chong,
                "gan_he": self.adjacent_gan_he,
                "zhi_xing": self.adjacent_zhi_xing
            },
            "special_patterns": self.special_patterns,
            "relation_impacts": self.relation_impacts,
            "table_lines": self.get_relation_table_lines(),
            "summary_stats": {
                "total_relations": self._count_total_relations(),
                "favorable_count": len(self.relation_impacts.get('favorable_relations', [])),
                "unfavorable_count": len(self.relation_impacts.get('unfavorable_relations', [])),
                "special_patterns_count": len(self.special_patterns)
            }
        }

    def _count_total_relations(self) -> int:
        """计算总关系数"""
        return (len(self.liu_he_relations) + len(self.liu_chong_relations) +
                len(self.san_he_relations) + len(self.san_hui_relations) +
                len(self.liu_hai_relations) + len(self.san_xing_relations) +
                len(self.zi_xing_relations) + len(self.xiang_po_relations) +
                len(self.gong_he_relations) + len(self.gong_hui_relations))

    def get_summary(self) -> Dict[str, str]:
        """获取地支关系分析摘要"""
        return {
            "total_summary": f"共发现{self._count_total_relations()}种地支关系",
            "he_chong_summary": f"六合{len(self.liu_he_relations)}个，六冲{len(self.liu_chong_relations)}个",
            "ju_summary": f"三合局{len([r for r in self.san_he_relations if r['strength'] == 'complete'])}个，三会局{len([r for r in self.san_hui_relations if r['strength'] == 'complete'])}个",
            "xing_hai_summary": f"三刑{len(self.san_xing_relations)}个，六害{len(self.liu_hai_relations)}个",
            "special_summary": f"特殊格局{len(self.special_patterns)}个",
            "main_analysis": self._get_main_analysis_text()
        }

    def _get_main_analysis_text(self) -> str:
        """获取主要分析文本"""
        analysis_parts = []
        
        # 分析有力的合冲关系
        strong_he = [r for r in self.liu_he_relations if r['is_adjacent']]
        strong_chong = [r for r in self.liu_chong_relations if r['is_adjacent']]
        
        if strong_he:
            analysis_parts.append(f"有{len(strong_he)}组相邻六合，利于和谐")
        
        if strong_chong:
            analysis_parts.append(f"有{len(strong_chong)}组相邻六冲，易生动荡")
        
        # 分析完整的合会局
        complete_he = [r for r in self.san_he_relations if r['strength'] == 'complete']
        complete_hui = [r for r in self.san_hui_relations if r['strength'] == 'complete']
        
        if complete_he:
            elements = [r['element'] for r in complete_he]
            analysis_parts.append(f"有{elements}三合局，力量集中")
        
        if complete_hui:
            elements = [r['element'] for r in complete_hui]
            analysis_parts.append(f"有{elements}三会局，方向明确")
        
        # 分析刑害关系
        if self.san_xing_relations:
            analysis_parts.append("有三刑关系，需注意人际摩擦")
        
        if self.liu_hai_relations:
            analysis_parts.append("有六害关系，易遇小人暗害")
        
        # 分析特殊格局
        for pattern in self.special_patterns:
            if pattern['type'] == 'unfavorable':
                analysis_parts.append(f"有{pattern['name']}格局，需要化解")
            elif pattern['type'] == 'favorable':
                analysis_parts.append(f"有{pattern['name']}格局，较为有利")
        
        return "；".join(analysis_parts) if analysis_parts else "地支关系平和，无特别突出之处"

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的地支关系数据"""
        return {
            "关系总览": {
                "总数": self._count_total_relations(),
                "有利关系": len(self.relation_impacts.get('favorable_relations', [])),
                "不利关系": len(self.relation_impacts.get('unfavorable_relations', [])),
                "特殊格局": len(self.special_patterns)
            },
            "主要关系": {
                "六合": [f"{r['zhis'][0]}{r['zhis'][1]}合化{r['element']}({'相邻' if r['is_adjacent'] else '不相邻'})" 
                        for r in self.liu_he_relations],
                "六冲": [f"{r['zhis'][0]}{r['zhis'][1]}相冲({'相邻' if r['is_adjacent'] else '不相邻'})" 
                        for r in self.liu_chong_relations],
                "三合局": [f"{r['description']}" for r in self.san_he_relations if r['strength'] == 'complete'],
                "三会局": [f"{r['description']}" for r in self.san_hui_relations if r['strength'] == 'complete']
            },
            "次要关系": {
                "三刑": [f"{r['zhis'][0]}{r['zhis'][1]}：{r['xing_type']}" for r in self.san_xing_relations],
                "六害": [f"{r['zhis'][0]}{r['zhis'][1]}相害" for r in self.liu_hai_relations],
                "相破": [f"{r['zhis'][0]}{r['zhis'][1]}相破" for r in self.xiang_po_relations],
                "自刑": [f"{r['zhi']}自刑{r['count']}个" for r in self.zi_xing_relations]
            },
            "拱合关系": {
                "拱合": [f"{r['zhis'][0]}{r['zhis'][1]}拱{r['target_zhi']}" for r in self.gong_he_relations],
                "拱会": [f"{r['zhis'][0]}{r['zhis'][1]}拱会{r['target_zhi']}" for r in self.gong_hui_relations]
            },
            "特殊格局": [
                {
                    "名称": pattern['name'],
                    "元素": pattern['elements'],
                    "性质": pattern['type'],
                    "说明": pattern['description']
                }
                for pattern in self.special_patterns
            ],
            "影响评估": {
                "有利影响": [r['description'] for r in self.relation_impacts.get('favorable_relations', [])],
                "不利影响": [r['description'] for r in self.relation_impacts.get('unfavorable_relations', [])],
                "化解建议": self._get_resolution_suggestions()
            },
            "重点提示": self._get_main_analysis_text()
        }

    def _get_resolution_suggestions(self) -> List[str]:
        """获取化解建议"""
        suggestions = []
        
        # 针对六冲的化解建议
        for relation in self.liu_chong_relations:
            if relation['is_adjacent']:
                suggestions.append(f"对于{relation['zhis'][0]}{relation['zhis'][1]}六冲，可通过合化来缓解")
        
        # 针对三刑的化解建议
        for relation in self.san_xing_relations:
            suggestions.append(f"对于{relation['description']}，需要通过贵人化解")
        
        return suggestions[:3]  # 只返回前3个建议


def test_zhi_relations_module():
    """测试地支关系模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    from .shens_analysis import ShensAnalysisModule
    
    print("=== 地支关系模块测试 ===")
    
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
    
    print("2. 创建地支关系模块...")
    zhi_relations = ZhiRelationsModule(core_data, basic_info_data, bazi_main_data, 
                                      detail_info_data, shens_analysis_data)
    
    print("\n3. 地支关系分析结果：")
    result = zhi_relations.get_result()
    
    print(f"   发现关系总数: {result['summary_stats']['total_relations']}")
    
    print("\n4. 各类关系统计：")
    print(f"   六合: {len(result['liu_he_relations'])}个")
    print(f"   六冲: {len(result['liu_chong_relations'])}个")
    print(f"   三合局: {len(result['san_he_relations'])}个")
    print(f"   三会局: {len(result['san_hui_relations'])}个")
    print(f"   六害: {len(result['liu_hai_relations'])}个")
    print(f"   三刑: {len(result['san_xing_relations'])}个")
    print(f"   特殊格局: {len(result['special_patterns'])}个")
    
    return result


if __name__ == "__main__":
    test_zhi_relations_module() 