"""
流年分析模块 - 处理八字的流年分析
包含流年计算、流年与大运命局关系分析、流年吉凶评估等功能
"""

import datetime
from typing import Dict, Any, List, Tuple, Optional

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from ..datas import Gan, Zhi, ten_deities, zhi_atts, nayins, empties
    from ..bazi_core import check_gan  # type: ignore
    from ..common import yinyang  # type: ignore
    from ..ganzhi import get_shens  # type: ignore
    from ..data.zhi5 import zhi5  # type: ignore
except ImportError:
    try:
        from .datas import Gan, Zhi, ten_deities, zhi_atts, nayins, empties  # type: ignore
        from .bazi_core import check_gan  # type: ignore
        from .common import yinyang  # type: ignore
        from .ganzhi import get_shens  # type: ignore
        from .data.zhi5 import zhi5  # type: ignore
    except ImportError:
        # 设置默认的流年相关数据
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
        
        # 默认的地支关系
        zhi_atts = {}
        for zhi in Zhi:
            zhi_atts[zhi] = {
                '冲': '', '合': [], '会': [], '刑': '', '害': '', '破': ''
            }
        
        # 默认的纳音
        nayins = {}
        for gan in Gan:
            for zhi in Zhi:
                nayins[(gan, zhi)] = f"{gan}{zhi}纳音"
        
        # 默认的空亡
        empties = {}
        for gan in Gan:
            for zhi in Zhi:
                empties[(gan, zhi)] = [zhi]
        
        # 默认的地支藏干数据
        zhi5 = {}
        for zhi in Zhi:
            zhi5[zhi] = {zhi: 10}  # 简化的地支藏干数据
        
        # 默认的神煞计算函数
        def get_shens(gans, zhis, gan, zhi):
            return ""
        
        # 默认的其他函数
        def check_gan(gan, gans):
            return ""
        
        def yinyang(x):
            return '+' if x in ['甲', '丙', '戊', '庚', '壬', '子', '寅', '辰', '午', '申', '戌'] else '-'


class LiunianAnalysisModule:
    """流年分析模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any],
                 shens_analysis_data: Dict[str, Any], zhi_relations_data: Dict[str, Any],
                 dayun_analysis_data: Dict[str, Any]):
        """
        初始化流年分析模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
            detail_info_data: 来自DetailInfoModule的详细信息数据
            shens_analysis_data: 来自ShensAnalysisModule的神煞分析数据
            zhi_relations_data: 来自ZhiRelationsModule的地支关系数据
            dayun_analysis_data: 来自DayunAnalysisModule的大运分析数据
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
        self.use_bazi_input = self.input_params.get('use_bazi_input', False)
        
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
        
        # 大运信息
        self.dayun_list = dayun_analysis_data.get('dayun_list', [])
        self.start_age = dayun_analysis_data.get('basic_info', {}).get('start_age', 8)
        
        # 八字对象（用于精确计算）
        self.ba_object = self.time_info.get('ba_object')
        self.solar = self.time_info.get('solar')
        self.lunar = self.time_info.get('lunar')
        
        # 流年计算结果
        self.liunian_data = {}          # 流年数据字典 {年份: 流年信息}
        self.liunian_details = []       # 流年详细分析
        self.liunian_relationships = [] # 流年与大运命局关系
        self.liunian_evaluations = []   # 流年吉凶评估
        self.current_year = datetime.datetime.now().year  # 当前年份
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行流年分析计算"""
        self._calculate_liunian_range()
        self._calculate_liunian_details()
        self._analyze_liunian_relationships()
        self._evaluate_liunian_fortune()

    def _calculate_liunian_range(self):
        """计算流年范围"""
        # 计算从出生年开始的流年，通常计算未来50-100年
        birth_year = self.year
        end_year = birth_year + 100  # 计算100年的流年
        
        current_gan_idx = 0
        current_zhi_idx = 0
        
        # 找到出生年的干支位置
        for i, gan in enumerate(Gan):
            for j, zhi in enumerate(Zhi):
                if self._year_to_ganzhi(birth_year) == gan + zhi:
                    current_gan_idx = i
                    current_zhi_idx = j
                    break
        
        # 计算每年的干支
        for year in range(birth_year, end_year + 1):
            age = year - birth_year + 1
            
            # 计算该年的干支
            year_gan_idx = (current_gan_idx + (year - birth_year)) % 10
            year_zhi_idx = (current_zhi_idx + (year - birth_year)) % 12
            
            year_gan = Gan[year_gan_idx]
            year_zhi = Zhi[year_zhi_idx]
            year_ganzhi = year_gan + year_zhi
            
            # 确定对应的大运
            dayun_info = self._get_dayun_for_age(age)
            
            self.liunian_data[year] = {
                'year': year,
                'age': age,
                'ganzhi': year_ganzhi,
                'gan': year_gan,
                'zhi': year_zhi,
                'dayun_info': dayun_info
            }

    def _year_to_ganzhi(self, year: int) -> str:
        """将公历年份转换为干支"""
        # 简化的年份转干支算法
        # 实际应该使用更精确的算法，这里使用简化版本
        gan_idx = (year - 4) % 10
        zhi_idx = (year - 4) % 12
        return Gan[gan_idx] + Zhi[zhi_idx]

    def _get_dayun_for_age(self, age: int) -> Optional[Dict[str, Any]]:
        """根据年龄获取对应的大运信息"""
        if not self.dayun_list:
            return None
        
        for dayun in self.dayun_list:
            dayun_start_age = dayun['age']
            dayun_end_age = dayun_start_age + 9
            
            if dayun_start_age <= age <= dayun_end_age:
                return dayun
        
        return None

    def _calculate_liunian_details(self):
        """计算流年详细信息"""
        # 只计算关键年份的详细信息，避免数据过多
        key_years = self._get_key_years()
        
        for year in key_years:
            if year not in self.liunian_data:
                continue
            
            liunian_info = self.liunian_data[year]
            
            try:
                gan = liunian_info['gan']
                zhi = liunian_info['zhi']
                age = liunian_info['age']
                dayun_info = liunian_info['dayun_info']
                
                # 十神分析
                gan_shen = ten_deities.get(self.me, {}).get(gan, '--') if self.me in ten_deities else '--'
                zhi_shen = ten_deities.get(self.me, {}).get(zhi, '--') if self.me in ten_deities else '--'
                
                # 纳音分析
                nayin = nayins.get((gan, zhi), f"{gan}{zhi}纳音")
                
                # 与命局的重复关系
                is_repeat = (gan, zhi) in self.zhus if self.zhus else False
                repeat_mark = '*' if is_repeat else ' '
                
                # 地支藏干分析
                zhi_canggan = self._analyze_zhi_canggan(zhi)
                
                # 与大运和命局的关系
                relationships = self._analyze_liunian_relationships_detailed(gan, zhi, dayun_info)
                
                # 空亡分析
                empty_info = self._check_empty(zhi)
                
                # 神煞分析
                shens_info = self._get_liunian_shens(gan, zhi)
                
                detail = {
                    'liunian_info': liunian_info,
                    'ten_gods': {
                        'gan_shen': gan_shen,
                        'zhi_shen': zhi_shen
                    },
                    'properties': {
                        'nayin': nayin,
                        'is_repeat': is_repeat,
                        'repeat_mark': repeat_mark
                    },
                    'analysis': {
                        'zhi_canggan': zhi_canggan,
                        'relationships': relationships,
                        'empty_info': empty_info,
                        'shens_info': shens_info
                    },
                    'formatted_line': self._format_liunian_line(liunian_info, gan_shen, zhi_shen, 
                                                              nayin, zhi_canggan, relationships, 
                                                              empty_info, repeat_mark, shens_info)
                }
                
                self.liunian_details.append(detail)
                
            except Exception as e:
                print(f"计算流年详情错误: {e}")

    def _get_key_years(self) -> List[int]:
        """获取关键年份（当前年及前后几年）"""
        current_year = datetime.datetime.now().year
        key_years = []
        
        # 当前年前后10年
        for i in range(-10, 11):
            year = current_year + i
            if year in self.liunian_data:
                key_years.append(year)
        
        # 添加一些特殊年份（如整十岁的年份）
        birth_year = self.year
        for age in [20, 30, 40, 50, 60, 70, 80]:
            year = birth_year + age - 1
            if year in self.liunian_data and year not in key_years:
                key_years.append(year)
        
        return sorted(key_years)

    def _analyze_zhi_canggan(self, zhi: str) -> str:
        """分析地支藏干"""
        if zhi not in zhi5:
            return ""
        
        canggan_parts = []
        for gan, score in zhi5[zhi].items():
            shen = ten_deities.get(self.me, {}).get(gan, '') if self.me in ten_deities else ''
            canggan_parts.append(f"{gan}{shen}")
        
        return '　'.join(canggan_parts)

    def _analyze_liunian_relationships_detailed(self, liunian_gan: str, liunian_zhi: str, 
                                              dayun_info: Optional[Dict]) -> Dict[str, Any]:
        """分析流年与大运、命局的详细关系"""
        relationships = {
            'with_mingju': {'gan': [], 'zhi': []},
            'with_dayun': {'gan': [], 'zhi': []},
            'special_combinations': []
        }
        
        try:
            # 与命局的关系
            if self.gans and self.zhis:
                # 天干关系
                for i, mingju_gan in enumerate(self.gans):
                    if liunian_gan == mingju_gan:
                        relationships['with_mingju']['gan'].append(f"同{i}柱天干")
                
                # 地支关系
                for i, mingju_zhi in enumerate(self.zhis):
                    if liunian_zhi == mingju_zhi:
                        relationships['with_mingju']['zhi'].append(f"同{i}柱地支")
                    
                    # 六合六冲等关系
                    rel = self._get_zhi_relationship(liunian_zhi, mingju_zhi)
                    if rel:
                        relationships['with_mingju']['zhi'].append(f"{rel}{i}柱")
            
            # 与大运的关系
            if dayun_info:
                dayun_gan = dayun_info['gan']
                dayun_zhi = dayun_info['zhi']
                
                # 天干关系
                if liunian_gan == dayun_gan:
                    relationships['with_dayun']['gan'].append("同大运天干")
                
                # 地支关系
                if liunian_zhi == dayun_zhi:
                    relationships['with_dayun']['zhi'].append("同大运地支")
                
                rel = self._get_zhi_relationship(liunian_zhi, dayun_zhi)
                if rel:
                    relationships['with_dayun']['zhi'].append(f"{rel}大运")
            
            # 特殊组合（三合、三会等）
            special_combos = self._check_special_combinations(liunian_gan, liunian_zhi, dayun_info)
            relationships['special_combinations'] = special_combos
            
        except Exception as e:
            print(f"分析流年关系错误: {e}")
        
        return relationships

    def _get_zhi_relationship(self, zhi1: str, zhi2: str) -> str:
        """获取两个地支之间的关系"""
        # 六合关系
        liu_he_pairs = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]
        
        for he_pair in liu_he_pairs:
            if (zhi1, zhi2) == he_pair or (zhi2, zhi1) == he_pair:
                return '合'
        
        # 六冲关系
        liu_chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        
        for chong_pair in liu_chong_pairs:
            if (zhi1, zhi2) == chong_pair or (zhi2, zhi1) == chong_pair:
                return '冲'
        
        return ''

    def _check_special_combinations(self, liunian_gan: str, liunian_zhi: str, 
                                  dayun_info: Optional[Dict]) -> List[str]:
        """检查特殊组合"""
        combinations = []
        
        try:
            # 检查三合局
            san_he_groups = [
                ['申', '子', '辰'],  # 水局
                ['巳', '酉', '丑'],  # 金局
                ['寅', '午', '戌'],  # 火局
                ['亥', '卯', '未']   # 木局
            ]
            
            all_zhis = list(self.zhis) if self.zhis else []
            if dayun_info:
                all_zhis.append(dayun_info['zhi'])
            all_zhis.append(liunian_zhi)
            
            for group in san_he_groups:
                if all(zhi in all_zhis for zhi in group):
                    element = {'申子辰': '水', '巳酉丑': '金', '寅午戌': '火', '亥卯未': '木'}[''.join(group)]
                    combinations.append(f"三合{element}局")
            
            # 检查三会局
            san_hui_groups = [
                ['亥', '子', '丑'],  # 水会
                ['寅', '卯', '辰'],  # 木会
                ['巳', '午', '未'],  # 火会
                ['申', '酉', '戌']   # 金会
            ]
            
            for group in san_hui_groups:
                if all(zhi in all_zhis for zhi in group):
                    element = {'亥子丑': '水', '寅卯辰': '木', '巳午未': '火', '申酉戌': '金'}[''.join(group)]
                    combinations.append(f"三会{element}局")
            
        except Exception as e:
            print(f"检查特殊组合错误: {e}")
        
        return combinations

    def _check_empty(self, zhi: str) -> str:
        """检查空亡"""
        if not self.zhus or not empties:
            return chr(12288)  # 全角空格
        
        try:
            # 以日柱为基准检查空亡
            day_zhu = self.zhus[2] if len(self.zhus) > 2 else None
            if day_zhu and day_zhu in empties and zhi in empties[day_zhu]:
                return '空'
            else:
                return chr(12288)
        except:
            return chr(12288)

    def _get_liunian_shens(self, gan: str, zhi: str) -> str:
        """获取流年神煞"""
        try:
            if 'get_shens' in globals():
                return get_shens(self.gans, self.zhis, gan, zhi)
            else:
                return ""
        except:
            return ""

    def _format_liunian_line(self, liunian_info: Dict, gan_shen: str, zhi_shen: str, nayin: str,
                           zhi_canggan: str, relationships: Dict, empty_info: str, 
                           repeat_mark: str, shens_info: str) -> str:
        """格式化流年行 - 完全按照原版bazi.py格式"""
        try:
            year = liunian_info['year']
            age = liunian_info['age']
            ganzhi = liunian_info['ganzhi']
            gan = liunian_info['gan']
            zhi = liunian_info['zhi']
            dayun_info = liunian_info.get('dayun_info', {})
            
            # 获取十二长生
            changsheng = self._get_changsheng(zhi)
            
            # 天干关系分析（冲合关系）
            gan_relations = self._analyze_gan_relations(gan)
            
            # 地支详细关系分析
            zhi_relations = self._analyze_zhi_relations_detailed(zhi, dayun_info)
            
            # 构建完整格式：年龄 年份 干支 长生 纳音 * 天干十神:天干±关系 地支±长生 - 地支藏干 关系 神:神煞
            line = "{1:>3d} {2} {3} {4} {5}{6}    {7}:{8}{9}　　　　　　　{10}{11}{12} - {13} {14}".format(
                chr(12288),     # 0: 全角空格
                age,            # 1: 年龄
                year,           # 2: 年份
                ganzhi,         # 3: 干支
                changsheng,     # 4: 十二长生
                nayin,          # 5: 纳音
                repeat_mark,    # 6: 重复标记*
                gan_shen,       # 7: 天干十神
                gan,            # 8: 天干
                gan_relations,  # 9: 天干关系（冲合）
                zhi,            # 10: 地支
                yinyang(zhi),   # 11: 地支阴阳
                changsheng,     # 12: 地支长生
                zhi_canggan,    # 13: 地支藏干
                zhi_relations   # 14: 地支关系
            )
            
            # 添加神煞信息
            if shens_info:
                line += f"  神:{shens_info}"
            
            return line
            
        except Exception as e:
            print(f"格式化流年行错误: {e}")
            return f"{liunian_info['age']:>3d} {liunian_info['year']:<5d}{liunian_info['ganzhi']}"

    def _analyze_liunian_relationships(self):
        """分析流年与大运命局的关系"""
        key_years = self._get_key_years()
        
        for year in key_years:
            if year not in self.liunian_data:
                continue
            
            try:
                liunian_info = self.liunian_data[year]
                gan = liunian_info['gan']
                zhi = liunian_info['zhi']
                dayun_info = liunian_info['dayun_info']
                
                # 与命局关系
                mingju_relationships = self._analyze_relationships_with_mingju(gan, zhi)
                
                # 与大运关系
                dayun_relationships = self._analyze_relationships_with_dayun(gan, zhi, dayun_info)
                
                # 三才关系（命局-大运-流年）
                sancai_relationships = self._analyze_sancai_relationships(gan, zhi, dayun_info)
                
                relationship = {
                    'year': year,
                    'age': liunian_info['age'],
                    'mingju_relationships': mingju_relationships,
                    'dayun_relationships': dayun_relationships,
                    'sancai_relationships': sancai_relationships,
                    'overall_harmony': self._calculate_harmony_score(mingju_relationships, dayun_relationships)
                }
                
                self.liunian_relationships.append(relationship)
                
            except Exception as e:
                print(f"分析流年关系错误: {e}")

    def _analyze_relationships_with_mingju(self, liunian_gan: str, liunian_zhi: str) -> Dict[str, int]:
        """分析与命局的关系"""
        relationships = {
            'harmony_score': 0,
            'conflict_score': 0,
            'neutral_score': 0
        }
        
        if not self.gans or not self.zhis:
            return relationships
        
        try:
            # 分析天干关系
            for mingju_gan in self.gans:
                if liunian_gan == mingju_gan:
                    relationships['harmony_score'] += 1
                # 这里可以添加更多天干关系的判断
            
            # 分析地支关系
            for mingju_zhi in self.zhis:
                rel = self._get_zhi_relationship(liunian_zhi, mingju_zhi)
                if rel == '合':
                    relationships['harmony_score'] += 2
                elif rel == '冲':
                    relationships['conflict_score'] += 2
                else:
                    relationships['neutral_score'] += 1
            
        except Exception as e:
            print(f"分析与命局关系错误: {e}")
        
        return relationships

    def _analyze_relationships_with_dayun(self, liunian_gan: str, liunian_zhi: str, 
                                        dayun_info: Optional[Dict]) -> Dict[str, int]:
        """分析与大运的关系"""
        relationships = {
            'harmony_score': 0,
            'conflict_score': 0,
            'neutral_score': 0
        }
        
        if not dayun_info:
            return relationships
        
        try:
            dayun_gan = dayun_info['gan']
            dayun_zhi = dayun_info['zhi']
            
            # 天干关系
            if liunian_gan == dayun_gan:
                relationships['harmony_score'] += 2
            
            # 地支关系
            rel = self._get_zhi_relationship(liunian_zhi, dayun_zhi)
            if rel == '合':
                relationships['harmony_score'] += 3
            elif rel == '冲':
                relationships['conflict_score'] += 3
            else:
                relationships['neutral_score'] += 1
            
        except Exception as e:
            print(f"分析与大运关系错误: {e}")
        
        return relationships

    def _analyze_sancai_relationships(self, liunian_gan: str, liunian_zhi: str, 
                                    dayun_info: Optional[Dict]) -> Dict[str, Any]:
        """分析三才关系（命局-大运-流年）"""
        sancai = {
            'pattern': 'normal',
            'description': '',
            'strength': 0
        }
        
        try:
            # 这里可以实现复杂的三才关系分析
            # 暂时简化处理
            if dayun_info:
                sancai['description'] = f"流年{liunian_gan}{liunian_zhi}与大运{dayun_info['ganzhi']}的组合"
                sancai['strength'] = 1
            
        except Exception as e:
            print(f"分析三才关系错误: {e}")
        
        return sancai

    def _calculate_harmony_score(self, mingju_rel: Dict, dayun_rel: Dict) -> int:
        """计算和谐度分数"""
        total_harmony = mingju_rel['harmony_score'] + dayun_rel['harmony_score']
        total_conflict = mingju_rel['conflict_score'] + dayun_rel['conflict_score']
        
        return total_harmony - total_conflict

    def _evaluate_liunian_fortune(self):
        """评估流年吉凶"""
        key_years = self._get_key_years()
        
        for year in key_years:
            if year not in self.liunian_data:
                continue
            
            try:
                liunian_info = self.liunian_data[year]
                gan = liunian_info['gan']
                zhi = liunian_info['zhi']
                
                # 基于十神评估
                gan_shen = ten_deities.get(self.me, {}).get(gan, '--') if self.me in ten_deities else '--'
                zhi_shen = ten_deities.get(self.me, {}).get(zhi, '--') if self.me in ten_deities else '--'
                
                fortune_score = self._calculate_shen_score(gan_shen) + self._calculate_shen_score(zhi_shen)
                
                # 基于关系评估
                relationship = next((r for r in self.liunian_relationships if r['year'] == year), None)
                if relationship:
                    fortune_score += relationship['overall_harmony']
                
                # 确定吉凶等级
                if fortune_score >= 5:
                    fortune_level = '大吉'
                elif fortune_score >= 2:
                    fortune_level = '吉'
                elif fortune_score >= 1:
                    fortune_level = '小吉'
                elif fortune_score <= -5:
                    fortune_level = '大凶'
                elif fortune_score <= -2:
                    fortune_level = '凶'
                elif fortune_score <= -1:
                    fortune_level = '小凶'
                else:
                    fortune_level = '平'
                
                evaluation = {
                    'year': year,
                    'age': liunian_info['age'],
                    'fortune_score': fortune_score,
                    'fortune_level': fortune_level,
                    'main_influences': self._get_liunian_main_influences(gan_shen, zhi_shen),
                    'recommendations': self._get_liunian_recommendations(fortune_level, gan_shen, zhi_shen)
                }
                
                self.liunian_evaluations.append(evaluation)
                
            except Exception as e:
                print(f"评估流年吉凶错误: {e}")

    def _calculate_shen_score(self, shen: str) -> int:
        """计算十神分数"""
        shen_scores = {
            '比': 0, '劫': -1, '食': 2, '伤': 1, '财': 2, '才': 1,
            '官': 2, '杀': -1, '印': 2, '枭': 0, '--': 0
        }
        return shen_scores.get(shen, 0)

    def _get_liunian_main_influences(self, gan_shen: str, zhi_shen: str) -> List[str]:
        """获取流年主要影响"""
        influences = []
        
        gan_influences = {
            '财': '财运投资年', '才': '偏财机遇年', '官': '事业发展年', '杀': '压力挑战年',
            '印': '学习贵人年', '枭': '技能提升年', '食': '表达创作年', '伤': '变动创新年',
            '比': '稳定发展年', '劫': '竞争破财年'
        }
        
        if gan_shen in gan_influences:
            influences.append(gan_influences[gan_shen])
        
        if zhi_shen in gan_influences and zhi_shen != gan_shen:
            influences.append(f"地支{gan_influences[zhi_shen]}")
        
        return influences[:2]

    def _get_liunian_recommendations(self, fortune_level: str, gan_shen: str, zhi_shen: str) -> List[str]:
        """获取流年建议"""
        recommendations = []
        
        if fortune_level in ['大吉', '吉']:
            recommendations.append("流年运势佳，可积极行动")
        elif fortune_level in ['大凶', '凶']:
            recommendations.append("流年需谨慎，避免重大变动")
        else:
            recommendations.append("流年平稳，按部就班")
        
        if gan_shen == '财' or zhi_shen == '财':
            recommendations.append("利于投资理财")
        elif gan_shen == '官' or zhi_shen == '官':
            recommendations.append("利于事业晋升")
        
        return recommendations[:2]

    def get_liunian_table_lines(self, start_year: Optional[int] = None, 
                               end_year: Optional[int] = None) -> List[str]:
        """获取流年表格行"""
        lines = []
        
        if start_year is None:
            start_year = self.current_year - 5
        if end_year is None:
            end_year = self.current_year + 5
        
        for detail in self.liunian_details:
            liunian_info = detail['liunian_info']
            year = liunian_info['year']
            
            if start_year <= year <= end_year and 'formatted_line' in detail:
                lines.append(detail['formatted_line'])
        
        return lines

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的流年分析结果"""
        return {
            "basic_info": {
                "birth_year": self.year,
                "current_year": self.current_year,
                "calculated_years": len(self.liunian_data),
                "key_years_count": len(self.liunian_details)
            },
            "liunian_data": self.liunian_data,  # 返回完整的流年数据
            "liunian_details": self.liunian_details,
            "liunian_relationships": self.liunian_relationships,
            "liunian_evaluations": self.liunian_evaluations,
            "table_lines": self.get_liunian_table_lines(),
            "summary_stats": {
                "favorable_years": len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']]),
                "unfavorable_years": len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']]),
                "neutral_years": len([e for e in self.liunian_evaluations if e['fortune_level'] == '平'])
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取流年分析摘要"""
        favorable_count = len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']])
        unfavorable_count = len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']])
        
        return {
            "basic_summary": f"计算{len(self.liunian_data)}年流年，重点分析{len(self.liunian_details)}年",
            "fortune_summary": f"吉年{favorable_count}年，凶年{unfavorable_count}年",
            "current_year_summary": f"当前{self.current_year}年" + self._get_current_year_fortune(),
            "trend_summary": self._get_trend_summary(),
            "main_analysis": self._get_main_liunian_analysis()
        }

    def _get_current_year_fortune(self) -> str:
        """获取当前年份运势"""
        current_eval = next((e for e in self.liunian_evaluations if e['year'] == self.current_year), None)
        if current_eval:
            return f"运势{current_eval['fortune_level']}"
        else:
            return "运势待分析"

    def _get_trend_summary(self) -> str:
        """获取趋势摘要"""
        if len(self.liunian_evaluations) < 5:
            return "数据不足，无法分析趋势"
        
        recent_evals = sorted([e for e in self.liunian_evaluations if e['year'] >= self.current_year - 2], key=lambda x: x['year'])[:5]
        good_count = sum(1 for e in recent_evals if e['fortune_level'] in ['大吉', '吉', '小吉'])
        
        if good_count >= 4:
            return "近年运势上升趋势"
        elif good_count <= 1:
            return "近年运势需要谨慎"
        else:
            return "近年运势有起伏"

    def _get_main_liunian_analysis(self) -> str:
        """获取主要流年分析"""
        analysis_parts = []
        
        # 分析近期流年
        recent_years = [e for e in self.liunian_evaluations if self.current_year - 3 <= e['year'] <= self.current_year + 3]
        
        if recent_years:
            good_years = [e for e in recent_years if e['fortune_level'] in ['大吉', '吉', '小吉']]
            bad_years = [e for e in recent_years if e['fortune_level'] in ['大凶', '凶', '小凶']]
            
            if good_years:
                good_year_list = [str(e['year']) for e in good_years[:3]]
                analysis_parts.append(f"近期吉年：{','.join(good_year_list)}")
            
            if bad_years:
                bad_year_list = [str(e['year']) for e in bad_years[:3]]
                analysis_parts.append(f"近期需谨慎年份：{','.join(bad_year_list)}")
        
        return "；".join(analysis_parts) if analysis_parts else "流年运势平稳，各有起伏"

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的流年数据"""
        return {
            "流年概况": {
                "出生年": self.year,
                "当前年": self.current_year,
                "计算年数": len(self.liunian_data),
                "重点分析年数": len(self.liunian_details)
            },
            "近期流年": [
                {
                    "年份": eval['year'],
                    "年龄": eval['age'],
                    "吉凶": eval['fortune_level'],
                    "主要影响": eval['main_influences'],
                    "建议": eval['recommendations']
                }
                for eval in self.liunian_evaluations 
                if self.current_year - 5 <= eval['year'] <= self.current_year + 5
            ],
            "运势统计": {
                "吉年数": len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']]),
                "凶年数": len([e for e in self.liunian_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']]),
                "平年数": len([e for e in self.liunian_evaluations if e['fortune_level'] == '平'])
            },
            "当前年运势": {
                "年份": self.current_year,
                "运势": self._get_current_year_fortune(),
                "趋势": self._get_trend_summary()
            },
            "重点提示": self._get_main_liunian_analysis()
        }


    def _get_changsheng(self, zhi: str) -> str:
        """获取十二长生"""
        changsheng_map = {
            '子': '胎', '丑': '养', '寅': '长', '卯': '沐', '辰': '冠', '巳': '建',
            '午': '帝', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '绝'
        }
        return changsheng_map.get(zhi, '未知')
    
    def _analyze_gan_relations(self, liunian_gan: str) -> str:
        """分析流年天干与命局天干的关系"""
        relations = []
        
        if not self.gans:
            return ""
        
        try:
            # 天干合化关系
            gan_he_pairs = {
                ('甲', '己'): '合', ('乙', '庚'): '合', ('丙', '辛'): '合',
                ('丁', '壬'): '合', ('戊', '癸'): '合'
            }
            
            # 天干相冲关系  
            gan_chong_pairs = {
                ('甲', '庚'): '冲', ('乙', '辛'): '冲', ('丙', '壬'): '冲', ('丁', '癸'): '冲'
            }
            
            for mingju_gan in self.gans:
                if not mingju_gan:
                    continue
                
                # 检查合化关系
                if (liunian_gan, mingju_gan) in gan_he_pairs or (mingju_gan, liunian_gan) in gan_he_pairs:
                    relations.append(f"合{mingju_gan}")
                
                # 检查相冲关系
                elif (liunian_gan, mingju_gan) in gan_chong_pairs or (mingju_gan, liunian_gan) in gan_chong_pairs:
                    relations.append(f"冲{mingju_gan}")
            
            return ''.join(relations) if relations else ""
            
        except Exception as e:
            print(f"分析天干关系错误: {e}")
            return ""
    
    def _analyze_zhi_relations_detailed(self, liunian_zhi: str, dayun_info: Optional[Dict]) -> str:
        """分析流年地支的详细关系"""
        relations = []
        
        if not self.zhis or liunian_zhi not in zhi_atts:
            return ""
        
        try:
            zhi_attr = zhi_atts[liunian_zhi]
            
            # 与命局地支的关系
            for i, mingju_zhi in enumerate(self.zhis):
                if not mingju_zhi:
                    continue
                
                # 六合关系
                he_list = zhi_attr.get('合', [])
                if isinstance(he_list, (list, tuple)) and mingju_zhi in he_list:
                    relations.append(f"合:{mingju_zhi}")
                elif isinstance(he_list, str) and mingju_zhi == he_list:
                    relations.append(f"合:{mingju_zhi}")
                
                # 三会关系
                hui_list = zhi_attr.get('会', [])
                if isinstance(hui_list, (list, tuple)) and mingju_zhi in hui_list:
                    relations.append(f"会:{mingju_zhi}")
                elif isinstance(hui_list, str) and mingju_zhi == hui_list:
                    relations.append(f"会:{mingju_zhi}")
                
                # 六冲关系
                if zhi_attr.get('冲') == mingju_zhi:
                    relations.append(f"冲:{mingju_zhi}")
                
                # 六害关系
                if zhi_attr.get('害') == mingju_zhi:
                    relations.append(f"害:{mingju_zhi}")
                
                # 三刑关系
                if zhi_attr.get('刑') == mingju_zhi:
                    relations.append(f"刑:{mingju_zhi}")
                
                # 被刑关系
                if zhi_attr.get('被刑') == mingju_zhi:
                    relations.append(f"被刑:{mingju_zhi}")
                
                # 暗合关系
                if zhi_attr.get('暗') == mingju_zhi:
                    relations.append(f"暗:{mingju_zhi}")
                
                # 同柱关系
                if liunian_zhi == mingju_zhi:
                    relations.append(f"同{i}柱地支")
            
            # 与大运地支的关系
            if dayun_info:
                dayun_zhi = dayun_info.get('zhi', '')
                if dayun_zhi:
                    if liunian_zhi == dayun_zhi:
                        relations.append("同大运地支")
                    
                    # 检查与大运的冲合关系
                    if zhi_attr.get('冲') == dayun_zhi:
                        relations.append("冲大运")
                    
                    he_list = zhi_attr.get('合', [])
                    if isinstance(he_list, (list, tuple)) and dayun_zhi in he_list:
                        relations.append("合大运")
                    elif isinstance(he_list, str) and dayun_zhi == he_list:
                        relations.append("合大运")
            
            return '  '.join(relations)
            
        except Exception as e:
            print(f"分析地支关系错误: {e}")
            return ""


def test_liunian_analysis_module():
    """测试流年分析模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    from .shens_analysis import ShensAnalysisModule
    from .zhi_relations import ZhiRelationsModule
    from .dayun_analysis import DayunAnalysisModule
    
    print("=== 流年分析模块测试 ===")
    
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
    
    print("2. 创建流年分析模块...")
    liunian_analysis = LiunianAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                           detail_info_data, shens_analysis_data, zhi_relations_data,
                                           dayun_analysis_data)
    
    print("\n3. 流年分析结果：")
    result = liunian_analysis.get_result()
    
    print(f"   计算年数: {result['basic_info']['calculated_years']}年")
    print(f"   重点分析: {result['basic_info']['key_years_count']}年")
    print(f"   当前年份: {result['basic_info']['current_year']}年")
    
    return result


if __name__ == "__main__":
    test_liunian_analysis_module() 