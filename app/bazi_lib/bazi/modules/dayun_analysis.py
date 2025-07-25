"""
大运分析模块 - 处理八字的大运分析
包含大运计算、大运与命局关系分析、大运吉凶评估等功能
"""

from typing import Dict, Any, List, Tuple, Optional

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from ..datas import *  # type: ignore
    from ..bazi_core import *  # type: ignore
    from ..common import *  # type: ignore
    from ..ganzhi import *  # type: ignore
    from ..data.zhi5 import zhi5  # type: ignore
except ImportError:
    try:
        from datas import *  # type: ignore
        from bazi_core import *  # type: ignore
        from common import *  # type: ignore
        from ganzhi import *  # type: ignore
        from data.zhi5 import zhi5  # type: ignore
    except ImportError:
        # 设置默认的大运相关数据
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 默认的十神数据
        ten_deities = {}
        for gan in Gan:
            ten_deities[gan] = {}
            for other_gan in Gan:
                ten_deities[gan][other_gan] = '比'  # 简化的十神关系
            for zhi in Zhi:
                ten_deities[gan][zhi] = '比'  # 简化的十神关系
        
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
        
        # 默认的地支藏干
        zhi5 = {}
        for zhi in Zhi:
            zhi5[zhi] = {zhi: 10}  # 简化的藏干
        
        # 默认的神煞计算函数
        def get_shens(gans, zhis, gan, zhi):
            return ""
        
        # 默认的其他函数
        def check_gan(gan, gans):
            return ""
        
        def yinyang(x):
            return '+' if x in ['甲', '丙', '戊', '庚', '壬', '子', '寅', '辰', '午', '申', '戌'] else '-'


class DayunAnalysisModule:
    """大运分析模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any], detail_info_data: Dict[str, Any],
                 shens_analysis_data: Dict[str, Any], zhi_relations_data: Dict[str, Any]):
        """
        初始化大运分析模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
            detail_info_data: 来自DetailInfoModule的详细信息数据
            shens_analysis_data: 来自ShensAnalysisModule的神煞分析数据
            zhi_relations_data: 来自ZhiRelationsModule的地支关系数据
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
        
        # 八字对象（用于精确计算）
        self.ba_object = self.time_info.get('ba_object')
        self.solar = self.time_info.get('solar')
        self.lunar = self.time_info.get('lunar')
        
        # 大运计算结果
        self.direction = 1          # 大运方向（1顺行，-1逆行）
        self.start_age = 0          # 起运年龄
        self.dayun_list = []        # 大运列表
        self.dayun_details = []     # 大运详细分析
        self.dayun_relationships = [] # 大运与命局关系
        self.dayun_evaluations = [] # 大运吉凶评估
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行大运分析计算"""
        self._calculate_dayun_direction()
        self._calculate_dayun_list()
        self._analyze_dayun_details()
        self._analyze_dayun_relationships()
        self._evaluate_dayun_fortune()

    def _calculate_dayun_direction(self):
        """计算大运方向和起运年龄"""
        if not self.gans or len(self.gans) < 1:
            return
        
        try:
            # 根据年干阴阳和性别确定大运方向
            year_gan = self.gans[0] if isinstance(self.gans, list) else self.gans.year
            year_gan_idx = Gan.index(year_gan)
            is_yang_year = (year_gan_idx % 2 == 0)
            
            # 男命阳年顺行，阴年逆行；女命相反
            if not self.is_female:
                self.direction = 1 if is_yang_year else -1
            else:
                self.direction = -1 if is_yang_year else 1
            
            # 使用lunar_python精确计算起运年龄
            if self.ba_object and not self.use_bazi_input:
                try:
                    yun = self.ba_object.getYun(not self.is_female)
                    if yun:
                        self.start_age = yun.getStartAge()
                    else:
                        self.start_age = 8  # 默认起运年龄
                except:
                    self.start_age = 8
            else:
                # 简化的起运年龄计算
                self.start_age = 8 if not self.is_female else 7
                
        except Exception as e:
            print(f"计算大运方向错误: {e}")
            self.direction = 1
            self.start_age = 8

    def _calculate_dayun_list(self):
        """计算大运列表"""
        if not self.gans or not self.zhis or len(self.gans) < 2 or len(self.zhis) < 2:
            return
        
        try:
            # 从月柱开始推大运
            month_gan = self.gans[1] if isinstance(self.gans, list) else self.gans.month
            month_zhi = self.zhis[1] if isinstance(self.zhis, list) else self.zhis.month
            
            gan_seq = Gan.index(month_gan)
            zhi_seq = Zhi.index(month_zhi)
            
            # 计算12步大运
            for i in range(12):
                gan_seq += self.direction
                zhi_seq += self.direction
                
                dayun_gan = Gan[gan_seq % 10]
                dayun_zhi = Zhi[zhi_seq % 12]
                dayun_ganzhi = dayun_gan + dayun_zhi
                
                age = self.start_age + i * 10
                
                self.dayun_list.append({
                    'step': i + 1,
                    'age': age,
                    'ganzhi': dayun_ganzhi,
                    'gan': dayun_gan,
                    'zhi': dayun_zhi
                })
                
        except Exception as e:
            print(f"计算大运列表错误: {e}")

    def _analyze_dayun_details(self):
        """分析大运详细信息"""
        for dayun in self.dayun_list:
            try:
                gan = dayun['gan']
                zhi = dayun['zhi']
                ganzhi = dayun['ganzhi']
                
                # 十神分析
                gan_shen = ten_deities.get(self.me, {}).get(gan, '--') if self.me in ten_deities else '--'
                zhi_shen = ten_deities.get(self.me, {}).get(zhi, '--') if self.me in ten_deities else '--'
                
                # 纳音分析
                nayin = nayins.get((gan, zhi), f"{ganzhi}纳音")
                
                # 阴阳性质
                gan_yinyang = yinyang(gan)
                zhi_yinyang = yinyang(zhi)
                
                # 与命局的重复关系
                is_repeat = (gan, zhi) in self.zhus if self.zhus else False
                repeat_mark = '*' if is_repeat else ' '
                
                # 地支藏干分析
                zhi_canggan = self._analyze_zhi_canggan(zhi)
                
                # 地支关系分析
                zhi_relations = self._analyze_zhi_relations_with_mingju(zhi)
                
                # 空亡分析
                empty_info = self._check_empty(zhi)
                
                # 夹拱分析
                jia_gong_info = self._analyze_jia_gong(gan, zhi)
                
                # 神煞分析
                shens_info = self._get_dayun_shens(gan, zhi)
                
                # 天干特殊检查
                gan_check = self._check_gan_special(gan)
                
                detail = {
                    'dayun_info': dayun,
                    'ten_gods': {
                        'gan_shen': gan_shen,
                        'zhi_shen': zhi_shen
                    },
                    'properties': {
                        'nayin': nayin,
                        'gan_yinyang': gan_yinyang,
                        'zhi_yinyang': zhi_yinyang,
                        'is_repeat': is_repeat,
                        'repeat_mark': repeat_mark
                    },
                    'zhi_analysis': {
                        'canggan': zhi_canggan,
                        'relations': zhi_relations,
                        'empty_info': empty_info
                    },
                    'special_analysis': {
                        'jia_gong': jia_gong_info,
                        'shens': shens_info,
                        'gan_check': gan_check
                    },
                    'formatted_line': self._format_dayun_line(dayun, gan_shen, zhi_shen, nayin, 
                                                            zhi_canggan, zhi_relations, empty_info, 
                                                            repeat_mark, jia_gong_info, shens_info, gan_check)
                }
                
                self.dayun_details.append(detail)
                
            except Exception as e:
                print(f"分析大运详情错误: {e}")
                # 添加简化的大运信息
                self.dayun_details.append({
                    'dayun_info': dayun,
                    'formatted_line': f"{dayun['age']:>2d}       {dayun['ganzhi']}"
                })

    def _analyze_zhi_canggan(self, zhi: str) -> str:
        """分析地支藏干"""
        if zhi not in zhi5:
            return ""
        
        canggan_parts = []
        for gan, score in zhi5[zhi].items():
            shen = ten_deities.get(self.me, {}).get(gan, '') if self.me in ten_deities else ''
            canggan_parts.append(f"{gan}{shen}")
        
        return '　'.join(canggan_parts)

    def _analyze_zhi_relations_with_mingju(self, zhi: str) -> str:
        """分析大运地支与命局的关系"""
        if not self.zhis or zhi not in zhi_atts:
            return ""
        
        relations = []
        
        for mingju_zhi in self.zhis:
            if not mingju_zhi:
                continue
            
            # 检查各种关系
            zhi_attr = zhi_atts[zhi]
            
            # 冲关系
            if zhi_attr.get('冲') == mingju_zhi:
                relations.append(f"冲:{mingju_zhi}")
            
            # 合关系
            he_list = zhi_attr.get('合', [])
            if isinstance(he_list, (list, tuple)) and mingju_zhi in he_list:
                relations.append(f"合:{mingju_zhi}")
            
            # 会关系
            hui_list = zhi_attr.get('会', [])
            if isinstance(hui_list, (list, tuple)) and mingju_zhi in hui_list:
                relations.append(f"会:{mingju_zhi}")
            
            # 刑关系
            if zhi_attr.get('刑') == mingju_zhi:
                relations.append(f"刑:{mingju_zhi}")
            
            # 害关系
            if zhi_attr.get('害') == mingju_zhi:
                relations.append(f"害:{mingju_zhi}")
            
            # 破关系（跳过，影响较小）
            # if zhi_attr.get('破') == mingju_zhi:
            #     relations.append(f"破:{mingju_zhi}")
        
        return '  '.join(relations)

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

    def _analyze_jia_gong(self, gan: str, zhi: str) -> str:
        """分析夹拱关系"""
        if not self.gans or not self.zhis:
            return ""
        
        jia_gong_parts = []
        
        try:
            # 检查天干相同的夹拱关系
            for i, mingju_gan in enumerate(self.gans):
                if gan == mingju_gan and i < len(self.zhis):
                    mingju_zhi = self.zhis[i]
                    if mingju_zhi:
                        zhi_diff = abs(Zhi.index(zhi) - Zhi.index(mingju_zhi))
                        
                        # 夹关系（相差2位）
                        if zhi_diff == 2:
                            jia_zhi = Zhi[(Zhi.index(zhi) + Zhi.index(mingju_zhi)) // 2]
                            jia_gong_parts.append(f"--夹：{jia_zhi}")
                        
                        # 拱关系（相差10位，即相差2位的反向）
                        elif zhi_diff == 10:
                            gong_zhi = Zhi[(Zhi.index(zhi) + Zhi.index(mingju_zhi)) % 12]
                            jia_gong_parts.append(f"--拱：{gong_zhi}")
            
            return '  '.join(jia_gong_parts)
            
        except Exception as e:
            print(f"夹拱分析错误: {e}")
            return ""

    def _get_dayun_shens(self, gan: str, zhi: str) -> str:
        """获取大运神煞"""
        try:
            if 'get_shens' in globals():
                return get_shens(self.gans, self.zhis, gan, zhi)
            else:
                return ""
        except:
            return ""

    def _check_gan_special(self, gan: str) -> str:
        """检查天干特殊情况"""
        try:
            if 'check_gan' in globals() and self.gans:
                return check_gan(gan, self.gans)
            else:
                return ""
        except:
            return ""

    def _format_dayun_line(self, dayun: Dict, gan_shen: str, zhi_shen: str, nayin: str,
                          zhi_canggan: str, zhi_relations: str, empty_info: str,
                          repeat_mark: str, jia_gong_info: str, shens_info: str, gan_check: str) -> str:
        """格式化大运行"""
        try:
            # 构建大运行，模仿原版格式
            # 格式：年龄  空格  干支  天干十神:天干属性  地支阴阳  地支十神  藏干信息  空亡  重复标记  纳音  地支关系  夹拱  神煞
            
            age = dayun['age']
            ganzhi = dayun['ganzhi']
            gan = dayun['gan']
            zhi = dayun['zhi']
            gan_yinyang = yinyang(gan)
            zhi_yinyang = yinyang(zhi)
            
            # 基本格式
            line = "{1:<4d}{2:<5s}{3} {15} {14} {13}  {4}:{5}{8}{6:{0}<6s}{12}{7}{8}{9} - {10:{0}<10s} {11}".format(
                chr(12288),  # 0: 全角空格
                age,         # 1: 年龄
                '',          # 2: 空格占位
                ganzhi,      # 3: 干支
                gan_shen,    # 4: 天干十神
                gan,         # 5: 天干
                gan_check,   # 6: 天干检查
                zhi,         # 7: 地支
                zhi_yinyang, # 8: 地支阴阳
                zhi_shen,    # 9: 地支十神
                zhi_canggan, # 10: 藏干信息
                zhi_relations, # 11: 地支关系
                empty_info,  # 12: 空亡标记
                repeat_mark, # 13: 重复标记
                nayin,       # 14: 纳音
                zhi_shen     # 15: 地支十神（重复用于格式对齐）
            )
            
            # 添加夹拱和神煞信息
            if jia_gong_info:
                line += jia_gong_info
            if shens_info:
                line += shens_info
            
            return line
            
        except Exception as e:
            print(f"格式化大运行错误: {e}")
            return f"{dayun['age']:>2d}       {dayun['ganzhi']}"

    def _analyze_dayun_relationships(self):
        """分析大运与命局的关系"""
        for i, detail in enumerate(self.dayun_details):
            try:
                dayun_info = detail['dayun_info']
                gan = dayun_info['gan']
                zhi = dayun_info['zhi']
                
                # 分析天干关系
                gan_relationships = self._analyze_gan_relationships(gan)
                
                # 分析地支关系
                zhi_relationships = self._analyze_zhi_relationships(zhi)
                
                # 分析整体影响
                overall_impact = self._evaluate_dayun_impact(gan, zhi, gan_relationships, zhi_relationships)
                
                relationship = {
                    'dayun_step': i + 1,
                    'age_range': f"{dayun_info['age']}-{dayun_info['age'] + 9}",
                    'gan_relationships': gan_relationships,
                    'zhi_relationships': zhi_relationships,
                    'overall_impact': overall_impact
                }
                
                self.dayun_relationships.append(relationship)
                
            except Exception as e:
                print(f"分析大运关系错误: {e}")

    def _analyze_gan_relationships(self, dayun_gan: str) -> Dict[str, Any]:
        """分析大运天干与命局天干的关系"""
        relationships = {
            'same_gans': [],      # 相同天干
            'he_gans': [],        # 合化天干
            'chong_gans': [],     # 冲克天干
            'sheng_gans': [],     # 相生天干
            'ke_gans': []         # 相克天干
        }
        
        if not self.gans:
            return relationships
        
        try:
            # 天干合化关系
            gan_he_pairs = {
                ('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')
            }
            
            # 天干相冲关系
            gan_chong_pairs = {
                ('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')
            }
            
            for i, mingju_gan in enumerate(self.gans):
                if not mingju_gan:
                    continue
                
                # 相同天干
                if dayun_gan == mingju_gan:
                    relationships['same_gans'].append((i, mingju_gan))
                
                # 合化关系
                if (dayun_gan, mingju_gan) in gan_he_pairs or (mingju_gan, dayun_gan) in gan_he_pairs:
                    relationships['he_gans'].append((i, mingju_gan))
                
                # 相冲关系
                if (dayun_gan, mingju_gan) in gan_chong_pairs or (mingju_gan, dayun_gan) in gan_chong_pairs:
                    relationships['chong_gans'].append((i, mingju_gan))
            
            return relationships
            
        except Exception as e:
            print(f"分析天干关系错误: {e}")
            return relationships

    def _analyze_zhi_relationships(self, dayun_zhi: str) -> Dict[str, Any]:
        """分析大运地支与命局地支的关系"""
        relationships = {
            'same_zhis': [],      # 相同地支
            'liu_he': [],         # 六合
            'liu_chong': [],      # 六冲
            'san_he': [],         # 三合
            'san_hui': [],        # 三会
            'liu_hai': [],        # 六害
            'san_xing': [],       # 三刑
            'xiang_po': []        # 相破
        }
        
        if not self.zhis:
            return relationships
        
        try:
            # 六合关系
            liu_he_pairs = [
                ('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                ('辰', '酉'), ('巳', '申'), ('午', '未')
            ]
            
            # 六冲关系
            liu_chong_pairs = [
                ('子', '午'), ('丑', '未'), ('寅', '申'),
                ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
            ]
            
            for i, mingju_zhi in enumerate(self.zhis):
                if not mingju_zhi:
                    continue
                
                # 相同地支
                if dayun_zhi == mingju_zhi:
                    relationships['same_zhis'].append((i, mingju_zhi))
                
                # 六合关系
                for he_pair in liu_he_pairs:
                    if (dayun_zhi, mingju_zhi) == he_pair or (mingju_zhi, dayun_zhi) == he_pair:
                        relationships['liu_he'].append((i, mingju_zhi))
                
                # 六冲关系
                for chong_pair in liu_chong_pairs:
                    if (dayun_zhi, mingju_zhi) == chong_pair or (mingju_zhi, dayun_zhi) == chong_pair:
                        relationships['liu_chong'].append((i, mingju_zhi))
            
            return relationships
            
        except Exception as e:
            print(f"分析地支关系错误: {e}")
            return relationships

    def _evaluate_dayun_impact(self, gan: str, zhi: str, gan_rel: Dict, zhi_rel: Dict) -> Dict[str, Any]:
        """评估大运的整体影响"""
        impact = {
            'favorable_score': 0,    # 有利分数
            'unfavorable_score': 0,  # 不利分数
            'overall_rating': 'neutral',  # 整体评级
            'key_influences': [],    # 关键影响
            'suggestions': []        # 建议
        }
        
        try:
            # 评估天干影响
            if gan_rel['he_gans']:
                impact['favorable_score'] += 2
                impact['key_influences'].append("天干合化，利于合作")
            
            if gan_rel['chong_gans']:
                impact['unfavorable_score'] += 2
                impact['key_influences'].append("天干相冲，易生冲突")
            
            # 评估地支影响
            if zhi_rel['liu_he']:
                impact['favorable_score'] += 3
                impact['key_influences'].append("地支六合，关系和谐")
            
            if zhi_rel['liu_chong']:
                impact['unfavorable_score'] += 3
                impact['key_influences'].append("地支六冲，变动较大")
            
            if zhi_rel['san_he'] or zhi_rel['san_hui']:
                impact['favorable_score'] += 4
                impact['key_influences'].append("形成合局，力量集中")
            
            # 计算整体评级
            net_score = impact['favorable_score'] - impact['unfavorable_score']
            if net_score >= 3:
                impact['overall_rating'] = 'very_favorable'
            elif net_score >= 1:
                impact['overall_rating'] = 'favorable'
            elif net_score <= -3:
                impact['overall_rating'] = 'very_unfavorable'
            elif net_score <= -1:
                impact['overall_rating'] = 'unfavorable'
            else:
                impact['overall_rating'] = 'neutral'
            
            # 生成建议
            if impact['overall_rating'] in ['favorable', 'very_favorable']:
                impact['suggestions'].append("此运利于发展，可积极进取")
            elif impact['overall_rating'] in ['unfavorable', 'very_unfavorable']:
                impact['suggestions'].append("此运需谨慎行事，避免冲动")
            else:
                impact['suggestions'].append("此运平稳，宜稳中求进")
            
            return impact
            
        except Exception as e:
            print(f"评估大运影响错误: {e}")
            return impact

    def _evaluate_dayun_fortune(self):
        """评估各大运的吉凶"""
        for i, detail in enumerate(self.dayun_details):
            try:
                dayun_info = detail['dayun_info']
                gan = dayun_info['gan']
                zhi = dayun_info['zhi']
                
                # 十神分析
                gan_shen = detail['ten_gods']['gan_shen']
                zhi_shen = detail['ten_gods']['zhi_shen']
                
                # 基于十神评估吉凶
                fortune_score = self._calculate_shen_score(gan_shen) + self._calculate_shen_score(zhi_shen)
                
                # 基于关系评估
                if i < len(self.dayun_relationships):
                    relationship = self.dayun_relationships[i]
                    overall_impact = relationship['overall_impact']
                    fortune_score += overall_impact['favorable_score'] - overall_impact['unfavorable_score']
                
                # 确定吉凶等级
                if fortune_score >= 6:
                    fortune_level = '大吉'
                elif fortune_score >= 3:
                    fortune_level = '吉'
                elif fortune_score >= 1:
                    fortune_level = '小吉'
                elif fortune_score <= -6:
                    fortune_level = '大凶'
                elif fortune_score <= -3:
                    fortune_level = '凶'
                elif fortune_score <= -1:
                    fortune_level = '小凶'
                else:
                    fortune_level = '平'
                
                evaluation = {
                    'dayun_step': i + 1,
                    'age_range': f"{dayun_info['age']}-{dayun_info['age'] + 9}",
                    'fortune_score': fortune_score,
                    'fortune_level': fortune_level,
                    'main_influences': self._get_main_influences(gan_shen, zhi_shen),
                    'recommendations': self._get_recommendations(fortune_level, gan_shen, zhi_shen)
                }
                
                self.dayun_evaluations.append(evaluation)
                
            except Exception as e:
                print(f"评估大运吉凶错误: {e}")

    def _calculate_shen_score(self, shen: str) -> int:
        """计算十神分数"""
        # 简化的十神吉凶评分
        shen_scores = {
            '比': 0, '劫': -1, '食': 2, '伤': 1, '财': 2, '才': 1,
            '官': 2, '杀': -1, '印': 2, '枭': 0, '--': 0
        }
        return shen_scores.get(shen, 0)

    def _get_main_influences(self, gan_shen: str, zhi_shen: str) -> List[str]:
        """获取主要影响"""
        influences = []
        
        # 基于天干十神
        gan_influences = {
            '财': '利于财运投资', '才': '偏财机遇', '官': '事业发展', '杀': '压力挑战',
            '印': '学习贵人', '枭': '偏门技能', '食': '表达创作', '伤': '变动创新',
            '比': '平稳发展', '劫': '竞争破财'
        }
        
        if gan_shen in gan_influences:
            influences.append(f"天干{gan_shen}神：{gan_influences[gan_shen]}")
        
        # 基于地支十神
        if zhi_shen in gan_influences:
            influences.append(f"地支{zhi_shen}神：{gan_influences[zhi_shen]}")
        
        return influences[:3]  # 最多3个主要影响

    def _get_recommendations(self, fortune_level: str, gan_shen: str, zhi_shen: str) -> List[str]:
        """获取建议"""
        recommendations = []
        
        # 基于吉凶等级
        if fortune_level in ['大吉', '吉']:
            recommendations.append("运势良好，可积极进取，把握机遇")
        elif fortune_level in ['大凶', '凶']:
            recommendations.append("运势不佳，宜谨慎保守，避免重大决策")
        else:
            recommendations.append("运势平稳，宜稳中求进，循序渐进")
        
        # 基于十神特点
        if gan_shen == '财' or zhi_shen == '财':
            recommendations.append("利于投资理财，但需量力而行")
        elif gan_shen == '官' or zhi_shen == '官':
            recommendations.append("利于事业发展，可争取晋升机会")
        elif gan_shen == '印' or zhi_shen == '印':
            recommendations.append("利于学习进修，可提升自身能力")
        
        return recommendations[:2]  # 最多2个建议

    def get_dayun_table_lines(self) -> List[str]:
        """获取大运表格行"""
        lines = []
        for detail in self.dayun_details:
            if 'formatted_line' in detail:
                lines.append(detail['formatted_line'])
        return lines

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的大运分析结果"""
        return {
            "basic_info": {
                "direction": self.direction,
                "start_age": self.start_age,
                "direction_desc": "顺行" if self.direction == 1 else "逆行"
            },
            "dayun_list": self.dayun_list,
            "dayun_details": self.dayun_details,
            "dayun_relationships": self.dayun_relationships,
            "dayun_evaluations": self.dayun_evaluations,
            "table_lines": self.get_dayun_table_lines(),
            "summary_stats": {
                "total_dayuns": len(self.dayun_list),
                "favorable_count": len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']]),
                "unfavorable_count": len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']]),
                "neutral_count": len([e for e in self.dayun_evaluations if e['fortune_level'] == '平'])
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取大运分析摘要"""
        favorable_count = len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']])
        unfavorable_count = len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']])
        
        return {
            "basic_summary": f"{self.start_age}岁起运，大运{'顺行' if self.direction == 1 else '逆行'}",
            "fortune_summary": f"吉运{favorable_count}步，凶运{unfavorable_count}步",
            "direction_summary": f"大运方向：{'顺行' if self.direction == 1 else '逆行'}，每步10年",
            "evaluation_summary": f"共计{len(self.dayun_list)}步大运，涵盖{len(self.dayun_list) * 10}年运势",
            "main_analysis": self._get_main_dayun_analysis()
        }

    def _get_main_dayun_analysis(self) -> str:
        """获取主要大运分析"""
        analysis_parts = []
        
        # 分析前几步大运
        if len(self.dayun_evaluations) >= 3:
            first_three = self.dayun_evaluations[:3]
            good_count = sum(1 for e in first_three if e['fortune_level'] in ['大吉', '吉', '小吉'])
            
            if good_count >= 2:
                analysis_parts.append("早年大运较佳，利于发展基础")
            elif good_count == 0:
                analysis_parts.append("早年大运一般，需要稳扎稳打")
            else:
                analysis_parts.append("早年大运有起伏，需要把握时机")
        
        # 分析中年大运
        if len(self.dayun_evaluations) >= 6:
            middle_three = self.dayun_evaluations[3:6]
            good_count = sum(1 for e in middle_three if e['fortune_level'] in ['大吉', '吉', '小吉'])
            
            if good_count >= 2:
                analysis_parts.append("中年大运兴旺，是事业黄金期")
            elif good_count == 0:
                analysis_parts.append("中年大运需谨慎，避免重大变动")
        
        # 分析晚年大运
        if len(self.dayun_evaluations) >= 9:
            late_three = self.dayun_evaluations[6:9]
            good_count = sum(1 for e in late_three if e['fortune_level'] in ['大吉', '吉', '小吉'])
            
            if good_count >= 2:
                analysis_parts.append("晚年大运安稳，享受人生")
            elif good_count == 0:
                analysis_parts.append("晚年大运需要保健，注意平安")
        
        return "；".join(analysis_parts) if analysis_parts else "大运整体平稳，各有起伏"

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的大运数据"""
        return {
            "大运概况": {
                "起运年龄": self.start_age,
                "大运方向": "顺行" if self.direction == 1 else "逆行",
                "总步数": len(self.dayun_list),
                "涵盖年限": f"{len(self.dayun_list) * 10}年"
            },
            "大运列表": [
                {
                    "步数": dayun['step'],
                    "年龄段": f"{dayun['age']}-{dayun['age'] + 9}岁",
                    "干支": dayun['ganzhi'],
                    "天干": dayun['gan'],
                    "地支": dayun['zhi']
                }
                for dayun in self.dayun_list
            ],
            "吉凶评估": [
                {
                    "年龄段": eval['age_range'] + "岁",
                    "吉凶": eval['fortune_level'],
                    "主要影响": eval['main_influences'],
                    "建议": eval['recommendations']
                }
                for eval in self.dayun_evaluations
            ],
            "运势统计": {
                "吉运步数": len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大吉', '吉', '小吉']]),
                "凶运步数": len([e for e in self.dayun_evaluations if e['fortune_level'] in ['大凶', '凶', '小凶']]),
                "平运步数": len([e for e in self.dayun_evaluations if e['fortune_level'] == '平'])
            },
            "重点分析": self._get_main_dayun_analysis()
        }


def test_dayun_analysis_module():
    """测试大运分析模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    from .detail_info import DetailInfoModule
    from .shens_analysis import ShensAnalysisModule
    from .zhi_relations import ZhiRelationsModule
    
    print("=== 大运分析模块测试 ===")
    
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
    
    print("2. 创建大运分析模块...")
    dayun_analysis = DayunAnalysisModule(core_data, basic_info_data, bazi_main_data, 
                                        detail_info_data, shens_analysis_data, zhi_relations_data)
    
    print("\n3. 大运分析结果：")
    result = dayun_analysis.get_result()
    
    print(f"   起运年龄: {result['basic_info']['start_age']}岁")
    print(f"   大运方向: {result['basic_info']['direction_desc']}")
    print(f"   大运总数: {result['summary_stats']['total_dayuns']}步")
    
    return result


if __name__ == "__main__":
    test_dayun_analysis_module() 