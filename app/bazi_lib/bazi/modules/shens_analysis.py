"""
神煞分析模块 - 处理八字中的各种吉神凶煞
包含年神、月神、日神、自身神煞的识别、分析和解释
"""

from typing import Dict, Any, List, Tuple, Optional, Set

try:
    from ..datas import *
    from ..bazi_core import *
    from ..common import *
except ImportError:
    try:
        from datas import *
        from bazi_core import *
        from common import *
    except ImportError:
        # 设置默认的神煞数据
        year_shens = {
            '孤辰': {"子": ["寅"], "丑": ["寅"], "寅": ["巳"], "卯": ["巳"], "辰": ["巳"], "巳": ["申"], 
                   "午": ["申"], "未": ["申"], "申": ["亥"], "酉": ["亥"], "戌": ["亥"], "亥": ["寅"]},
            '寡宿': {"子": ["戌"], "丑": ["戌"], "寅": ["丑"], "卯": ["丑"], "辰": ["丑"], "巳": ["辰"], 
                   "午": ["辰"], "未": ["辰"], "申": ["未"], "酉": ["未"], "戌": ["未"], "亥": ["戌"]},   
            '大耗': {"子": ["巳", "未"], "丑": ["午", "申"], "寅": ["未", "酉"], "卯": ["申", "戌"], 
                   "辰": ["酉", "亥"], "巳": ["戌", "子"], "午": ["亥", "丑"], "未": ["子", "寅"], 
                   "申": ["丑", "卯"], "酉": ["寅", "辰"], "戌": ["卯", "巳"], "亥": ["辰", "午"]},      
        }

        month_shens = {
            '天德': {"子": ["巳"], "丑": ["庚"], "寅": ["丁"], "卯": ["申"], "辰": ["壬"], "巳": ["辛"], 
                   "午": ["亥"], "未": ["甲"], "申": ["癸"], "酉": ["寅"], "戌": ["丙"], "亥": ["乙"]},
            '月德': {"子": ["壬"], "丑": ["庚"], "寅": ["丙"], "卯": ["甲"], "辰": ["壬"], "巳": ["庚"], 
                   "午": ["丙"], "未": ["甲"], "申": ["壬"], "酉": ["庚"], "戌": ["丙"], "亥": ["甲"]},
        }

        day_shens = { 
            '将星': {"子": ["子"], "丑": ["酉"], "寅": ["午"], "卯": ["卯"], "辰": ["子"], "巳": ["酉"], 
                   "午": ["午"], "未": ["卯"], "申": ["子"], "酉": ["酉"], "戌": ["午"], "亥": ["卯"]},      
            '华盖': {"子": ["辰"], "丑": ["丑"], "寅": ["戌"], "卯": ["未"], "辰": ["辰"], "巳": ["丑"], 
                   "午": ["戌"], "未": ["未"], "申": ["辰"], "酉": ["丑"], "戌": ["戌"], "亥": ["未"]}, 
            '驿马': {"子": ["寅"], "丑": ["亥"], "寅": ["申"], "卯": ["巳"], "辰": ["寅"], "巳": ["亥"], 
                   "午": ["申"], "未": ["巳"], "申": ["寅"], "酉": ["亥"], "戌": ["申"], "亥": ["巳"]},
            '劫煞': {"子": ["巳"], "丑": ["寅"], "寅": ["亥"], "卯": ["申"], "辰": ["巳"], "巳": ["寅"], 
                   "午": ["亥"], "未": ["申"], "申": ["巳"], "酉": ["寅"], "戌": ["亥"], "亥": ["申"]},
            '亡神': {"子": ["亥"], "丑": ["申"], "寅": ["巳"], "卯": ["寅"], "辰": ["亥"], "巳": ["申"], 
                   "午": ["巳"], "未": ["寅"], "申": ["亥"], "酉": ["申"], "戌": ["巳"], "亥": ["寅"]},    
            '桃花': {"子": ["酉"], "丑": ["午"], "寅": ["卯"], "卯": ["子"], "辰": ["酉"], "巳": ["午"], 
                   "午": ["卯"], "未": ["子"], "申": ["酉"], "酉": ["午"], "戌": ["卯"], "亥": ["子"]},        
        }

        g_shens = {
            '天乙': {"甲": ["未", "丑"], "乙": ["申", "子"], "丙": ["酉", "亥"], "丁": ["酉", "亥"], 
                   "戊": ["未", "丑"], "己": ["申", "子"], "庚": ["未", "丑"], "辛": ["寅", "午"], 
                   "壬": ["卯", "巳"], "癸": ["卯", "巳"]},
            '文昌': {"甲": ["巳"], "乙": ["午"], "丙": ["申"], "丁": ["酉"], "戊": ["申"], "己": ["酉"], 
                   "庚": ["亥"], "辛": ["子"], "壬": ["寅"], "癸": ["丑"]},   
            '阳刃': {"甲": ["卯"], "乙": [], "丙": ["午"], "丁": [], "戊": ["午"], "己": [], 
                   "庚": ["酉"], "辛": [], "壬": ["子"], "癸": []},     
            '红艳': {"甲": ["午"], "乙": ["午"], "丙": ["寅"], "丁": ["未"], "戊": ["辰"], "己": ["辰"], 
                   "庚": ["戌"], "辛": ["酉"], "壬": ["子"], "癸": ["申"]},       
        }

        # 神煞解释
        shens_infos = {
            '孤辰': "孤僻、孤独：月支容易不合群、容易30岁以后才结婚。女命官杀月干坐孤辰、独居概率大，时支则有阴道之心。",
            '寡宿': "类似孤辰，同柱有天月德没关系。男怕孤，女怕寡。",  
            '大耗': "意外破损，单独没关系。与桃花或驿马之类同柱则危险。",
            '天德': "先天有福，日干终生有福。忌讳冲克，不怕合。女命与夫星同干更佳。",
            '月德': "先天有福，日干终生有福。忌讳冲克，不怕合。女命与夫星同干更佳。",
            '将星': "有理想、气度、即从容不迫。",     
            '华盖': "有艺术、水准与命格相关。",
            '驿马': "多迁移、水准与命格相关。女驿马合贵人，终沦落风尘。",
            '劫煞': "与贵人同柱没关系、与亡神对冲。会三刑不佳，其他情况还好。为日主所克无大碍。",
            '亡神': "与贵人同柱没关系、与劫煞对冲。会三刑不佳，其他情况还好。为日主所克无大碍。",  
            '桃花': "凶居多、女正官坐桃花吉。", 
            '天乙': "后天解难、女命不适合多",
            '文昌': "诗书佳，未必有福，女命多参考李清照。",   
            '阳刃': "性格刚强，女命未必佳。",     
            '红艳': "爱得执著，不顾及地位差异。",  
        }

        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


class ShensAnalysisModule:
    """神煞分析模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any]):
        """
        初始化神煞分析模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
            detail_info_data: 来自DetailInfoModule的详细信息数据
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
        
        # 神煞分析结果
        self.year_shens_result = {}    # 年神煞
        self.month_shens_result = {}   # 月神煞
        self.day_shens_result = {}     # 日神煞
        self.self_shens_result = {}    # 自身神煞
        self.all_shens = set()         # 所有神煞
        self.shens_by_pillar = [[], [], [], []]  # 各柱的神煞
        self.special_combinations = []  # 特殊组合
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行神煞分析计算"""
        self._analyze_year_shens()
        self._analyze_month_shens()
        self._analyze_day_shens()
        self._analyze_self_shens()
        self._analyze_special_combinations()

    def _analyze_year_shens(self):
        """分析年神煞"""
        if not self.zhis or len(self.zhis) < 4:
            return
        
        year_zhi = self.zhis[0]
        
        for shen_name, shen_data in year_shens.items():
            if year_zhi in shen_data:
                target_zhis = shen_data[year_zhi]
                found_positions = []
                
                # 检查月、日、时支
                for i in range(1, 4):
                    if i < len(self.zhis) and self.zhis[i] in target_zhis:
                        found_positions.append(i)
                        self.shens_by_pillar[i].append(shen_name)
                        self.all_shens.add(shen_name)
                
                if found_positions:
                    self.year_shens_result[shen_name] = {
                        'base_zhi': year_zhi,
                        'target_zhis': target_zhis,
                        'found_positions': found_positions,
                        'found_zhis': [self.zhis[pos] for pos in found_positions],
                        'description': shens_infos.get(shen_name, ''),
                        'is_active': True
                    }

    def _analyze_month_shens(self):
        """分析月神煞"""
        if not self.zhis or len(self.zhis) < 2:
            return
        
        month_zhi = self.zhis[1]
        
        for shen_name, shen_data in month_shens.items():
            if month_zhi in shen_data:
                targets = shen_data[month_zhi]
                found_positions = []
                
                # 检查所有位置的干支
                for i in range(4):
                    # 检查天干
                    if i < len(self.gans) and self.gans[i] in targets:
                        found_positions.append(('gan', i))
                        self.shens_by_pillar[i].append(shen_name)
                        self.all_shens.add(shen_name)
                        # 日主有月德天德加强标记
                        if i == 2:  # 日主位置
                            self.shens_by_pillar[i].append(shen_name + "●")
                    
                    # 检查地支
                    if i < len(self.zhis) and self.zhis[i] in targets:
                        found_positions.append(('zhi', i))
                        self.shens_by_pillar[i].append(shen_name)
                        self.all_shens.add(shen_name)
                
                if found_positions:
                    self.month_shens_result[shen_name] = {
                        'base_zhi': month_zhi,
                        'targets': targets,
                        'found_positions': found_positions,
                        'description': shens_infos.get(shen_name, ''),
                        'is_active': True
                    }

    def _analyze_day_shens(self):
        """分析日神煞"""
        if not self.zhis or len(self.zhis) < 3:
            return
        
        day_zhi = self.zhis[2]
        
        for shen_name, shen_data in day_shens.items():
            if day_zhi in shen_data:
                target_zhis = shen_data[day_zhi]
                found_positions = []
                
                # 检查年、月、时支（不包括日支自身）
                for i in [0, 1, 3]:
                    if i < len(self.zhis) and self.zhis[i] in target_zhis:
                        found_positions.append(i)
                        self.shens_by_pillar[i].append(shen_name)
                        self.all_shens.add(shen_name)
                
                if found_positions:
                    self.day_shens_result[shen_name] = {
                        'base_zhi': day_zhi,
                        'target_zhis': target_zhis,
                        'found_positions': found_positions,
                        'found_zhis': [self.zhis[pos] for pos in found_positions],
                        'description': shens_infos.get(shen_name, ''),
                        'is_active': True
                    }

    def _analyze_self_shens(self):
        """分析自身神煞（以日主为基准）"""
        if not self.me or not self.zhis:
            return
        
        for shen_name, shen_data in g_shens.items():
            if self.me in shen_data:
                target_zhis = shen_data[self.me]
                if not target_zhis:  # 某些神煞对特定日主为空
                    continue
                    
                found_positions = []
                
                # 检查所有地支
                for i in range(len(self.zhis)):
                    if self.zhis[i] in target_zhis:
                        found_positions.append(i)
                        self.shens_by_pillar[i].append(shen_name)
                        self.all_shens.add(shen_name)
                
                if found_positions:
                    self.self_shens_result[shen_name] = {
                        'day_master': self.me,
                        'target_zhis': target_zhis,
                        'found_positions': found_positions,
                        'found_zhis': [self.zhis[pos] for pos in found_positions],
                        'description': shens_infos.get(shen_name, ''),
                        'is_active': True
                    }

    def _analyze_special_combinations(self):
        """分析特殊神煞组合"""
        # 天罗地网组合
        if '辰' in self.zhis and '巳' in self.zhis:
            self.special_combinations.append({
                'name': '地网',
                'elements': ['辰', '巳'],
                'description': '地网：地支辰巳。天罗：戌亥。天罗地网全凶。',
                'type': 'unfavorable'
            })
        
        if '戌' in self.zhis and '亥' in self.zhis:
            self.special_combinations.append({
                'name': '天罗',
                'elements': ['戌', '亥'],
                'description': '天罗：戌亥。地网：地支辰巳。天罗地网全凶。',
                'type': 'unfavorable'
            })
        
        # 桃花组合分析
        self._analyze_peach_blossom_combinations()
        
        # 贵人组合分析
        self._analyze_noble_combinations()

    def _analyze_peach_blossom_combinations(self):
        """分析桃花组合"""
        year_zhi = self.zhis[0] if self.zhis else ''
        day_zhi = self.zhis[2] if len(self.zhis) > 2 else ''
        
        # 桃花分类：墙里桃花（年月）、墙外桃花（日时）
        peach_blossoms = []
        
        # 子午卯酉桃花
        peach_map = {
            ('申', '子', '辰'): '酉',
            ('丑', '巳', '酉'): '午', 
            ('寅', '午', '戌'): '卯',
            ('亥', '卯', '未'): '子'
        }
        
        for combo, peach in peach_map.items():
            if any(zhi in combo for zhi in [year_zhi, day_zhi]):
                if peach in self.zhis:
                    peach_pos = self.zhis.index(peach)
                    peach_type = "墙里桃花" if peach_pos < 2 else "墙外桃花"
                    peach_blossoms.append({
                        'position': peach_pos,
                        'zhi': peach,
                        'type': peach_type,
                        'base_combo': combo
                    })
        
        if peach_blossoms:
            self.special_combinations.append({
                'name': '咸池桃花',
                'elements': peach_blossoms,
                'description': '墙里桃花，煞在年月；墙外桃花，煞在日时。',
                'type': 'mixed'
            })

    def _analyze_noble_combinations(self):
        """分析贵人组合"""
        # 天乙贵人组合
        if '天乙' in self.self_shens_result:
            tianyi_info = self.self_shens_result['天乙']
            if len(tianyi_info['found_positions']) >= 2:
                self.special_combinations.append({
                    'name': '天乙贵人组合',
                    'elements': tianyi_info['found_zhis'],
                    'description': '多个天乙贵人，后天解难能力强。',
                    'type': 'favorable'
                })
        
        # 天德月德同现
        has_tiande = '天德' in self.month_shens_result
        has_yuede = '月德' in self.month_shens_result
        if has_tiande and has_yuede:
            self.special_combinations.append({
                'name': '天月德合',
                'elements': ['天德', '月德'],
                'description': '天德月德同现，先天福德深厚。',
                'type': 'favorable'
            })

    def get_shens_table_lines(self) -> List[str]:
        """获取神煞表格行"""
        lines = []
        
        # 构建每柱的神煞字符串
        pillar_strs = []
        for i in range(4):
            if self.shens_by_pillar[i]:
                # 使用中文全角空格分隔
                shen_str = chr(12288).join(self.shens_by_pillar[i])
                pillar_strs.append(shen_str)
            else:
                pillar_strs.append('')
        
        # 只显示前两柱（年月）的神煞
        if pillar_strs[0] or pillar_strs[1]:
            line = "{1:{0}<15s}{2:{0}<15s}".format(chr(12288), pillar_strs[0], pillar_strs[1])
            lines.append(line)
        
        return lines

    def get_detailed_analysis(self) -> Dict[str, Any]:
        """获取详细的神煞分析"""
        analysis = {
            'summary': {
                'total_shens': len(self.all_shens),
                'year_shens_count': len(self.year_shens_result),
                'month_shens_count': len(self.month_shens_result),
                'day_shens_count': len(self.day_shens_result),
                'self_shens_count': len(self.self_shens_result),
                'special_combinations_count': len(self.special_combinations)
            },
            'by_category': {
                'year_shens': self.year_shens_result,
                'month_shens': self.month_shens_result,
                'day_shens': self.day_shens_result,
                'self_shens': self.self_shens_result
            },
            'by_pillar': {
                'year_pillar': self.shens_by_pillar[0],
                'month_pillar': self.shens_by_pillar[1],
                'day_pillar': self.shens_by_pillar[2],
                'time_pillar': self.shens_by_pillar[3]
            },
            'special_combinations': self.special_combinations,
            'favorable_shens': self._get_favorable_shens(),
            'unfavorable_shens': self._get_unfavorable_shens(),
            'neutral_shens': self._get_neutral_shens()
        }
        
        return analysis

    def _get_favorable_shens(self) -> List[str]:
        """获取吉神"""
        favorable = ['天德', '月德', '天乙', '文昌', '将星']
        return [shen for shen in self.all_shens if shen in favorable]

    def _get_unfavorable_shens(self) -> List[str]:
        """获取凶煞"""
        unfavorable = ['孤辰', '寡宿', '大耗', '劫煞', '亡神', '桃花']
        return [shen for shen in self.all_shens if shen in unfavorable]

    def _get_neutral_shens(self) -> List[str]:
        """获取中性神煞"""
        favorable = self._get_favorable_shens()
        unfavorable = self._get_unfavorable_shens()
        return [shen for shen in self.all_shens if shen not in favorable and shen not in unfavorable]

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的神煞分析结果"""
        return {
            "all_shens": list(self.all_shens),
            "shens_by_pillar": self.shens_by_pillar,
            "year_shens": self.year_shens_result,
            "month_shens": self.month_shens_result,
            "day_shens": self.day_shens_result,
            "self_shens": self.self_shens_result,
            "special_combinations": self.special_combinations,
            "detailed_analysis": self.get_detailed_analysis(),
            "table_lines": self.get_shens_table_lines(),
            "summary_stats": {
                "total_count": len(self.all_shens),
                "favorable_count": len(self._get_favorable_shens()),
                "unfavorable_count": len(self._get_unfavorable_shens()),
                "neutral_count": len(self._get_neutral_shens())
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取神煞分析摘要"""
        favorable_shens = self._get_favorable_shens()
        unfavorable_shens = self._get_unfavorable_shens()
        
        return {
            "total_summary": f"共发现{len(self.all_shens)}个神煞",
            "favorable_summary": f"吉神{len(favorable_shens)}个：{', '.join(favorable_shens) if favorable_shens else '无'}",
            "unfavorable_summary": f"凶煞{len(unfavorable_shens)}个：{', '.join(unfavorable_shens) if unfavorable_shens else '无'}",
            "special_summary": f"特殊组合{len(self.special_combinations)}个",
            "main_analysis": self._get_main_analysis_text()
        }

    def _get_main_analysis_text(self) -> str:
        """获取主要分析文本"""
        analysis_parts = []
        
        # 重要吉神分析
        if '天德' in self.all_shens or '月德' in self.all_shens:
            analysis_parts.append("命带天月德，先天福德深厚")
        
        if '天乙' in self.all_shens:
            analysis_parts.append("有天乙贵人，后天多得贵人相助")
        
        if '文昌' in self.all_shens:
            analysis_parts.append("带文昌星，利于学业文书")
        
        # 重要凶煞分析
        if '孤辰' in self.all_shens or '寡宿' in self.all_shens:
            analysis_parts.append("命带孤寡，易有孤独之象")
        
        if '桃花' in self.all_shens:
            analysis_parts.append("命带桃花，感情丰富但需注意异性关系")
        
        # 特殊组合
        for combo in self.special_combinations:
            if combo['type'] == 'unfavorable':
                analysis_parts.append(f"有{combo['name']}组合，需要注意")
            elif combo['type'] == 'favorable':
                analysis_parts.append(f"有{combo['name']}组合，较为有利")
        
        return "；".join(analysis_parts) if analysis_parts else "神煞平和，无特别突出之处"

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的神煞数据"""
        return {
            "神煞总览": {
                "总数": len(self.all_shens),
                "吉神": self._get_favorable_shens(),
                "凶煞": self._get_unfavorable_shens(),
                "中性": self._get_neutral_shens()
            },
            "各柱神煞": {
                "年柱": self.shens_by_pillar[0],
                "月柱": self.shens_by_pillar[1], 
                "日柱": self.shens_by_pillar[2],
                "时柱": self.shens_by_pillar[3]
            },
            "神煞详解": {
                shen: {
                    "类型": "吉神" if shen in self._get_favorable_shens() else "凶煞" if shen in self._get_unfavorable_shens() else "中性",
                    "解释": shens_infos.get(shen, "暂无详细解释")
                }
                for shen in self.all_shens
            },
            "特殊组合": [
                {
                    "名称": combo['name'],
                    "性质": combo['type'],
                    "说明": combo['description']
                }
                for combo in self.special_combinations
            ],
            "重点提示": self._get_main_analysis_text()
        }


def test_shens_analysis_module():
    """测试神煞分析模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    
    print("=== 神煞分析模块测试 ===")
    
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
    
    print("2. 创建神煞分析模块...")
    shens_analysis = ShensAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data)
    
    print("\n3. 神煞分析结果：")
    result = shens_analysis.get_result()
    
    print(f"   发现神煞总数: {len(result['all_shens'])}")
    print(f"   神煞列表: {', '.join(result['all_shens'])}")
    
    print("\n4. 各柱神煞分布：")
    pillar_names = ['年柱', '月柱', '日柱', '时柱']
    for i, shens in enumerate(result['shens_by_pillar']):
        if shens:
            print(f"   {pillar_names[i]}: {', '.join(shens)}")
    
    print("\n5. 神煞分类统计：")
    stats = result['summary_stats']
    print(f"   吉神: {stats['favorable_count']}个")
    print(f"   凶煞: {stats['unfavorable_count']}个")
    print(f"   中性: {stats['neutral_count']}个")
    
    print("\n6. 特殊组合：")
    for combo in result['special_combinations']:
        print(f"   {combo['name']}: {combo['description'][:50]}...")
    
    print("\n7. 摘要分析：")
    summary = shens_analysis.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n8. LLM友好数据样例：")
    llm_data = shens_analysis.get_llm_friendly_data()
    print(f"   神煞总览: {llm_data['神煞总览']}")
    print(f"   重点提示: {llm_data['重点提示']}")
    
    return result


if __name__ == "__main__":
    test_shens_analysis_module() 