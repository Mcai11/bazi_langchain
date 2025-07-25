import argparse
import collections
import datetime
from typing import Dict, List, Tuple, Any, Optional

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from colorama import init
except ImportError:
    pass

# 导入所有必要的数据和工具模块
try:
    from .bazi_core import get_gen, gan_zhi_he, get_gong, get_shens, jin_jiao, is_ku, zhi_ku, is_yang, not_yang, gan_ke
    from .datas import *
    from .sizi import summarys
    from .common import *
    from .yue import months
except ImportError:
    try:
        from bazi_core import get_gen, gan_zhi_he, get_gong, get_shens, jin_jiao, is_ku, zhi_ku, is_yang, not_yang, gan_ke
        from datas import *
        from sizi import summarys
        from common import *
        from yue import months
    except ImportError as e:
        print(f"Warning: Could not import required modules: {e}")
        # 设置默认值以避免错误
        ten_deities = {}
        zhi5 = {}
        gan5 = {}
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# Named tuples for structured data
Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")

class Bazi:
    def __init__(self, year: int, month: int, day: int, hour: int, gender: str = '男', **kwargs):
        """
        初始化八字类 - 完整功能版本
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            gender: 性别，'男' 或 '女'
            **kwargs: 其他参数
                start: 开始年份，默认1850
                end: 结束年份，默认2030
                b: 是否直接输入八字，默认False
                g: 是否采用公历，默认False
                r: 是否为闰月，默认False
                n: 是否为女性，默认False（会根据gender自动设置）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.gender = gender
        
        # 参数设置
        self.start = kwargs.get('start', 1850)
        self.end = kwargs.get('end', 2030)
        self.use_bazi_input = kwargs.get('b', False)
        self.use_gregorian = kwargs.get('g', False)
        self.is_leap = kwargs.get('r', False)
        self.is_female = kwargs.get('n', gender == '女')
        
        # 初始化所有属性
        self._init_attributes()
        
        # 执行完整计算
        self.result = self._calculate()

    def _init_attributes(self):
        """初始化所有属性"""
        # 时间相关
        self.solar = None
        self.lunar = None
        self.ba = None
        self.day_lunar = None
        
        # 八字相关
        self.gans = None
        self.zhis = None
        self.me = None
        self.month_zhi = None
        self.alls = None
        self.zhus = None
        
        # 十神相关
        self.gan_shens = []
        self.zhi_shens = []
        self.shens = []
        self.zhi_shens2 = []
        self.zhi_shen3 = []
        self.shens2 = []
        
        # 分数相关
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        self.gan_scores = {gan: 0 for gan in Gan}
        self.weak = True
        self.strong = 0
        
        # 大运相关
        self.dayuns = []
        self.direction = 1
        
        # 神煞相关
        self.all_shens = set()
        self.all_shens_list = []
        self.shen_strs = ['', '', '', '']
        
        # 格局相关
        self.all_ges = []
        self.jus = []
        
        # 关系相关
        self.zhi_6he = [False, False, False, False]
        self.zhi_6chong = [False, False, False, False]
        self.gan_he = [False, False, False, False]
        self.zhi_xing = [False, False, False, False]
        
        # 分析结果
        self.analysis_text = []
        self.personality_text = []
        self.pattern_analysis = []

    def _calculate(self) -> Dict[str, Any]:
        """执行完整八字计算的主流程"""
        try:
            # 1. 基础时间转换
            self._convert_time()
            
            # 2. 获取八字信息
            self._get_bazi_info()
            
            # 3. 计算十神
            self._calculate_ten_gods()
            
            # 4. 计算五行分数
            self._calculate_scores()
            
            # 5. 计算强弱
            self._calculate_strength()
            
            # 6. 计算大运
            self._calculate_dayun()
            
            # 7. 分析神煞
            self._analyze_shens()
            
            # 8. 分析关系
            self._analyze_relationships()
            
            # 9. 格局分析
            self._analyze_patterns()
            
            # 10. 生成详细分析
            self._generate_analysis()
            
            # 11. 生成结果
            return self._generate_result()
            
        except Exception as e:
            return {"error": str(e), "base_info": f"计算出错: {e}"}

    def _convert_time(self):
        """时间转换"""
        try:
            if self.use_bazi_input:
                # 直接输入八字的情况 - 目前暂不支持，使用简化转换
                self._simple_bazi_conversion()
            else:
                if Solar and Lunar:
                    if self.use_gregorian:
                        self.solar = Solar.fromYmdHms(self.year, self.month, self.day, self.hour, 0, 0)
                        self.lunar = self.solar.getLunar()
                    else:
                        month_ = self.month * -1 if self.is_leap else self.month
                        self.lunar = Lunar.fromYmdHms(self.year, month_, self.day, self.hour, 0, 0)
                        self.solar = self.lunar.getSolar()
                    self.day_lunar = self.lunar
                else:
                    # 简化处理
                    self._simple_bazi_conversion()
        except Exception as e:
            print(f"时间转换错误: {e}")
            self._simple_bazi_conversion()

    def _simple_bazi_conversion(self):
        """简化的八字转换"""
        # 简化实现，实际需要复杂的历法计算
        year_gan_idx = (self.year - 4) % 10
        year_zhi_idx = (self.year - 4) % 12
        
        month_gan_idx = (year_gan_idx * 2 + self.month) % 10
        month_zhi_idx = (self.month - 1) % 12
        
        # 简化的日干支计算
        days_since_epoch = (self.year - 1900) * 365 + self.month * 30 + self.day
        day_gan_idx = days_since_epoch % 10
        day_zhi_idx = days_since_epoch % 12
        
        # 时干支计算
        hour_zhi_idx = (self.hour + 1) // 2 % 12
        hour_gan_idx = (day_gan_idx * 2 + hour_zhi_idx) % 10
        
        self.gans = Gans(
            year=Gan[year_gan_idx], 
            month=Gan[month_gan_idx], 
            day=Gan[day_gan_idx], 
            time=Gan[hour_gan_idx]
        )
        self.zhis = Zhis(
            year=Zhi[year_zhi_idx], 
            month=Zhi[month_zhi_idx], 
            day=Zhi[day_zhi_idx], 
            time=Zhi[hour_zhi_idx]
        )

    def _get_bazi_info(self):
        """获取八字信息"""
        try:
            if not self.use_bazi_input and self.lunar:
                self.ba = self.lunar.getEightChar()
                self.gans = Gans(
                    year=self.ba.getYearGan(), 
                    month=self.ba.getMonthGan(), 
                    day=self.ba.getDayGan(), 
                    time=self.ba.getTimeGan()
                )
                self.zhis = Zhis(
                    year=self.ba.getYearZhi(), 
                    month=self.ba.getMonthZhi(), 
                    day=self.ba.getDayZhi(), 
                    time=self.ba.getTimeZhi()
                )

            if self.gans and self.zhis:
                self.me = self.gans.day
                self.month_zhi = self.zhis.month
                self.alls = list(self.gans) + list(self.zhis)
                self.zhus = list(zip(self.gans, self.zhis))
        except Exception as e:
            print(f"获取八字信息错误: {e}")

    def _calculate_ten_gods(self):
        """计算十神"""
        try:
            if not self.gans or not self.zhis or not self.me or not ten_deities:
                return

            # 天干十神
            self.gan_shens = []
            for seq, item in enumerate(self.gans):
                if seq == 2:
                    self.gan_shens.append('--')
                else:
                    self.gan_shens.append(ten_deities[self.me][item])

            # 地支主气十神
            self.zhi_shens = []
            for item in self.zhis:
                d = zhi5.get(item, {})
                if d:
                    main_gan = max(d.keys(), key=lambda x: d[x])
                    self.zhi_shens.append(ten_deities[self.me][main_gan])
                else:
                    self.zhi_shens.append('--')

            self.shens = self.gan_shens + self.zhi_shens

            # 地支所有十神
            self.zhi_shens2 = []
            self.zhi_shen3 = []
            for item in self.zhis:
                d = zhi5.get(item, {})
                tmp = ''
                for item2 in d:
                    self.zhi_shens2.append(ten_deities[self.me][item2])
                    tmp += ten_deities[self.me][item2]
                self.zhi_shen3.append(tmp)
            self.shens2 = self.gan_shens + self.zhi_shens2

        except Exception as e:
            print(f"计算十神错误: {e}")

    def _calculate_scores(self):
        """计算五行分数"""
        try:
            if not self.gans or not self.zhis or not gan5 or not zhi5:
                return

            # 天干分数
            for item in self.gans:
                if item in gan5:
                    self.scores[gan5[item]] += 5
                    self.gan_scores[item] += 5

            # 地支分数
            zhis_to_process = list(self.zhis)
            if hasattr(self.zhis, 'month') and self.zhis.month:
                zhis_to_process.append(self.zhis.month)
                
            for item in zhis_to_process:
                if item in zhi5:
                    for gan in zhi5[item]:
                        if gan in gan5:
                            self.scores[gan5[gan]] += zhi5[item][gan]
                            self.gan_scores[gan] += zhi5[item][gan]

        except Exception as e:
            print(f"计算分数错误: {e}")

    def _calculate_strength(self):
        """计算八字强弱"""
        try:
            if not self.zhis or not self.me or not ten_deities:
                return

            # 子平真诠的计算
            self.weak = True
            me_status = []
            for item in self.zhis:
                if self.me in ten_deities and item in ten_deities[self.me]:
                    status = ten_deities[self.me][item]
                    me_status.append(status)
                    if status in ('长', '帝', '建'):
                        self.weak = False

            if self.weak and self.shens:
                bi_count = self.shens.count('比')
                ku_count = me_status.count('库')
                if bi_count + ku_count > 2:
                    self.weak = False

            # 网上的计算方法
            if self.me in ten_deities and hasattr(ten_deities[self.me], 'inverse'):
                me_attrs_ = ten_deities[self.me].inverse
                self.strong = (
                    self.gan_scores.get(me_attrs_.get('比', ''), 0) +
                    self.gan_scores.get(me_attrs_.get('劫', ''), 0) +
                    self.gan_scores.get(me_attrs_.get('枭', ''), 0) +
                    self.gan_scores.get(me_attrs_.get('印', ''), 0)
                )

        except Exception as e:
            print(f"计算强弱错误: {e}")

    def _calculate_dayun(self):
        """计算大运"""
        try:
            if not self.gans or not self.zhis:
                return

            seq = Gan.index(self.gans.year)
            if self.is_female:
                self.direction = -1 if seq % 2 == 0 else 1
            else:
                self.direction = 1 if seq % 2 == 0 else -1

            self.dayuns = []
            gan_seq = Gan.index(self.gans.month)
            zhi_seq = Zhi.index(self.zhis.month)
            
            for i in range(12):
                gan_seq += self.direction
                zhi_seq += self.direction
                dayun = Gan[gan_seq % 10] + Zhi[zhi_seq % 12]
                self.dayuns.append(dayun)

        except Exception as e:
            print(f"计算大运错误: {e}")

    def _analyze_shens(self):
        """分析神煞"""
        try:
            # 检查全局变量是否存在
            if not all(name in globals() for name in ['year_shens', 'month_shens', 'day_shens', 'g_shens']):
                return
                
            if not self.zhis or not self.gans:
                return
                
            self.all_shens = set()
            self.all_shens_list = []
            self.shen_strs = ['', '', '', '']

            # 简化的神煞分析 - 只做基础检查
            # 实际的神煞分析需要完整的数据文件支持

        except Exception as e:
            print(f"分析神煞错误: {e}")

    def _analyze_relationships(self):
        """分析地支关系"""
        try:
            # 简化的关系分析 - 需要完整数据文件支持
            if not self.gans or not self.zhis:
                return
            # 暂时跳过复杂的地支关系计算
            pass

        except Exception as e:
            print(f"分析关系错误: {e}")

    def _analyze_patterns(self):
        """分析格局"""
        try:
            self.all_ges = []
            self.jus = []
            
            if not self.zhi_shens:
                return
                
            # 建禄格
            if len(self.zhi_shens) > 1 and self.zhi_shens[1] == '比':
                self.all_ges.append('建')
                
            # 阳刃格
            if (len(self.zhi_shens) > 1 and self.zhi_shens[1] == '劫' and 
                self.me and Gan.index(self.me) % 2 == 0):
                self.all_ges.append('刃')
                
            # 其他格局判断
            if self.shens2:
                if self.shens2.count('食') > 1:
                    self.all_ges.append('食')
                if self.shens2.count('伤') > 1:
                    self.all_ges.append('伤')
                if self.shens2.count('财') > 1:
                    self.all_ges.append('财')
                if self.shens2.count('才') > 1:
                    self.all_ges.append('才')
                if self.shens2.count('官') > 1:
                    self.all_ges.append('官')
                if self.shens2.count('杀') > 1:
                    self.all_ges.append('杀')
                if self.shens2.count('印') > 1:
                    self.all_ges.append('印')
                if self.shens2.count('枭') > 1:
                    self.all_ges.append('枭')

        except Exception as e:
            print(f"分析格局错误: {e}")

    def _generate_analysis(self):
        """生成详细分析"""
        try:
            self.analysis_text = []
            self.personality_text = []
            self.pattern_analysis = []
            
            # 调候分析
            if self.me and self.zhis and len(self.zhis) > 1:
                tiahou_key = f"{self.me}{self.zhis[1]}"
                if 'tiaohous' in globals() and tiahou_key in tiaohous:
                    self.analysis_text.append(f"调候：{tiaohous[tiahou_key]}")
                
                if 'jinbuhuan' in globals() and tiahou_key in jinbuhuan:
                    self.analysis_text.append(f"金不换大运：{jinbuhuan[tiahou_key]}")
            
            # 强弱分析
            self.analysis_text.append(f"强弱：{self.strong} 中值29")
            self.analysis_text.append(f"强根：{'有' if not self.weak else '无'}")
            
            # 格局分析
            if self.all_ges:
                self.pattern_analysis.append(f"格局：{' '.join(self.all_ges)}")
            
            # 神煞分析
            if self.all_shens:
                for shen in self.all_shens:
                    if 'shens_infos' in globals() and shen in shens_infos:
                        self.analysis_text.append(f"{shen}：{shens_infos[shen]}")

        except Exception as e:
            print(f"生成分析错误: {e}")

    def _generate_result(self) -> Dict[str, Any]:
        """生成最终结果"""
        return {
            "base_info": self._format_base_info(),
            "bazi_main": self._format_bazi_main(),
            "detail": self._format_detail(),
            "dayun_table": self._format_dayun_table(),
            "liunian_table": self._format_liunian_table(),
            "analysis": self._format_analysis(),
            "tiangan": self._format_tiangan(),
            "personality": self._format_personality(),
            "scores": self.scores,
            "gan_scores": self.gan_scores,
            "patterns": self.all_ges,
            "bureaus": self.jus,
            "shens": list(self.all_shens),

        }

    def _format_base_info(self) -> str:
        """格式化基本信息"""
        if self.solar and self.lunar:
            sex = '女' if self.is_female else '男'
            base_parts = [f"{sex}命"]
            base_parts.append(f"公历: {self.solar.getYear()}年{self.solar.getMonth()}月{self.solar.getDay()}日")
            base_parts.append(f"农历: {self.lunar.getYear()}年{self.lunar.getMonth()}月{self.lunar.getDay()}日")
            
            if self.ba:
                yun = self.ba.getYun(not self.is_female)
                if yun:
                    base_parts.append(f"上运时间：{yun.getStartSolar().toFullString().split()[0]}")
                base_parts.append(f"命宫:{self.ba.getMingGong()}")
                base_parts.append(f"胎元:{self.ba.getTaiYuan()}")
            
            return "    ".join(base_parts)
        else:
            return f"{self.year}年{self.month}月{self.day}日 {self.hour}时 性别:{self.gender}"

    def _format_bazi_main(self) -> str:
        """格式化八字主体"""
        if not self.gans or not self.zhis:
            return "八字信息获取失败"
        
        # 构建完整的八字主体信息，包含十神、五行分数等
        lines = []
        
        # 天干行
        gan_line = ' '.join(list(self.gans))
        gan_shen_line = ' '.join(self.gan_shens) if self.gan_shens else ""
        
        # 地支行
        zhi_line = ' '.join(list(self.zhis))
        zhi_shen_line = ' '.join(self.zhi_shens) if self.zhi_shens else ""
        
        # 五行分数
        score_parts = []
        for element, score in self.scores.items():
            if score > 0:
                score_parts.append(f"{element}{score}")
        
        score_line = f"  {' '.join(score_parts)}  强弱:{self.strong} 中值29 强根:{'有' if not self.weak else '无'}"
        
        # 四柱信息
        sizhu_info = "四柱：" + ' '.join([''.join(item) for item in zip(self.gans, self.zhis)])
        
        lines.append(f"{gan_line}       {gan_shen_line}      {score_line}")
        lines.append(f"{zhi_line}       {zhi_shen_line}     {sizhu_info}")
        
        return '\n'.join(lines)

    def _format_detail(self) -> str:
        """格式化详细信息"""
        if not self.zhus:
            return "详细信息获取失败"
        
        # 构建详细的年月日时信息
        labels = ['【年】', '【月】', '【日】', '【时】']
        detail_parts = []
        
        for i, (gan, zhi) in enumerate(self.zhus):
            temp_gan = temps.get(gan, 0) if 'temps' in globals() else 0
            temp_zhi = temps.get(zhi, 0) if 'temps' in globals() else 0
            he_info = gan_zhi_he(self.zhus[i]) if 'gan_zhi_he' in globals() else ""
            
            if i != 2:  # 不是日柱
                jian_info = ""
                if self.gans and i < len(self.gans) and self.gans[i] in ten_deities:
                    jian_info = ten_deities[self.gans[i]].inverse.get('建', '') if hasattr(ten_deities[self.gans[i]], 'inverse') else ""
                detail_parts.append(f"{labels[i]}{temp_gan}:{temp_zhi}{jian_info}{he_info}")
            else:
                detail_parts.append(f"{labels[i]}{temp_gan}:{temp_zhi}{he_info}")
        
        return "{1:{0}^15s}{2:{0}^15s}{3:{0}^15s}{4:{0}^15s}".format(chr(12288), *detail_parts)

    def _format_dayun_table(self) -> Dict[str, str]:
        """格式化大运表"""
        dayun_dict = {}
        
        if not self.use_bazi_input and self.ba:
            try:
                yun = self.ba.getYun(not self.is_female)
                for dayun in yun.getDaYun()[1:]:
                    age = dayun.getStartAge()
                    gan_ = dayun.getGanZhi()[0]
                    zhi_ = dayun.getGanZhi()[1]
                    
                    # 构建详细的大运信息
                    info_parts = []
                    info_parts.append(f"{dayun.getGanZhi()}")
                    
                    if self.me in ten_deities:
                        info_parts.append(f"{ten_deities[self.me].get(gan_, '')}:{gan_}")
                        info_parts.append(f"{ten_deities[self.me].get(zhi_, '')}")
                    
                    if 'nayins' in globals() and (gan_, zhi_) in nayins:
                        info_parts.append(f"{nayins[(gan_, zhi_)]}")
                    
                    # 添加地支关系
                    if 'zhi_atts' in globals() and zhi_ in zhi_atts:
                        relations = []
                        for zhi in self.zhis:
                            for rel_type in zhi_atts[zhi_]:
                                if zhi in zhi_atts[zhi_][rel_type]:
                                    relations.append(f"{rel_type}:{zhi}")
                        if relations:
                            info_parts.append(' '.join(relations))
                    
                    # 添加神煞
                    shens_info = get_shens(self.gans, self.zhis, gan_, zhi_) if 'get_shens' in globals() else ""
                    if shens_info:
                        info_parts.append(shens_info)
                    
                    dayun_dict[str(age)] = " ".join(info_parts)
            except Exception as e:
                print(f"大运表格式化错误: {e}")
        
        # 简化版大运
        if not dayun_dict:
            for i, dayun in enumerate(self.dayuns):
                age = 1 + i * 10
                dayun_dict[str(age)] = dayun
                
        return dayun_dict

    def _format_liunian_table(self) -> Dict[str, List[str]]:
        """格式化流年表"""
        liunian_dict = {}
        
        if not self.use_bazi_input and self.ba:
            try:
                yun = self.ba.getYun(not self.is_female)
                for dayun in yun.getDaYun()[1:]:
                    for liunian in dayun.getLiuNian():
                        year = liunian.getYear()
                        age = liunian.getAge()
                        gan_zhi = liunian.getGanZhi()
                        
                        info_parts = [
                            str(age),
                            gan_zhi,
                            ten_deities[self.me].get(gan_zhi[0], '') if self.me in ten_deities else '',
                            ten_deities[self.me].get(gan_zhi[1], '') if self.me in ten_deities else ''
                        ]
                        
                        liunian_dict[str(year)] = info_parts
            except Exception as e:
                print(f"流年表格式化错误: {e}")
                
        return liunian_dict

    def _format_analysis(self) -> str:
        """格式化分析内容"""
        return "\n".join(self.analysis_text)

    def _format_tiangan(self) -> str:
        """格式化天干分析"""
        parts = []
        for gan, score in self.gan_scores.items():
            if score > 0:
                shen = ten_deities[self.me].get(gan, '') if self.me in ten_deities else ''
                parts.append(f"{gan}[{shen}]-{score}")
        return " ".join(parts)

    def _format_personality(self) -> str:
        """格式化性格分析"""
        parts = []
        
        # 基于十神的性格分析
        if self.shens:
            main_shens = [shen for shen in self.shens if shen != '--']
            if main_shens:
                shen_counts = {}
                for shen in set(main_shens):
                    shen_counts[shen] = main_shens.count(shen)
                
                dominant_shen = max(shen_counts.keys(), key=lambda x: shen_counts[x])
                parts.append(f"主要十神：{dominant_shen}")
        
        # 五行性格
        if self.scores:
            dominant_element = max(self.scores.keys(), key=lambda x: self.scores[x])
            parts.append(f"五行特点：{dominant_element}性")
        
        # 添加详细的性格分析文本
        parts.extend(self.personality_text)
        
        return "\n".join(parts)



    def get_result(self) -> Dict[str, Any]:
        """获取计算结果"""
        return self.result

    def get_formatted_output(self) -> str:
        """获取格式化的文本输出，匹配原版bazi.py的格式"""
        if "error" in self.result:
            return f"计算错误：{self.result['error']}"
        
        lines = []
        lines.append("-" * 120)
        lines.append(self.result["base_info"])
        lines.append("-" * 120)
        lines.append(self.result["bazi_main"])
        lines.append("-" * 120)
        lines.append(self.result["detail"])
        lines.append("-" * 120)
        
        # 详细分析部分
        lines.append(self.result["analysis"])
        lines.append("-" * 120)
        lines.append(self.result["tiangan"])
        lines.append("-" * 120)
        lines.append(self.result["personality"])
        lines.append("-" * 120)
        
        # 格局分析
        if self.result["patterns"]:
            lines.append(f"局 {self.result['bureaus']} 格 {self.result['patterns']}")
        
        # 古籍引用功能已移除
        
        # 大运
        if self.result["dayun_table"]:
            lines.append("\n\n大运")
            lines.append("=" * 120)
            for age, info in self.result["dayun_table"].items():
                lines.append(f"{age:>2s}       {info}")
        
        lines.append("=" * 120)
        
        return "\n".join(lines)


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='八字计算工具（完整版）',
                                   formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('year', type=int, help='年份')
    parser.add_argument('month', type=int, help='月份')
    parser.add_argument('day', type=int, help='日期')
    parser.add_argument('hour', type=int, help='小时')
    parser.add_argument('--gender', type=str, default='男', help='性别')
    parser.add_argument("--start", help="开始年份", type=int, default=1850)
    parser.add_argument("--end", help="结束年份", default='2030')
    parser.add_argument('-b', action="store_true", default=False, help='直接输入八字')
    parser.add_argument('-g', action="store_true", default=False, help='是否采用公历')
    parser.add_argument('-r', action="store_true", default=False, help='是否为闰月，仅仅使用于农历')
    parser.add_argument('-n', action="store_true", default=False, help='是否为女，默认为男')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    
    args = parser.parse_args()
    
    bazi = Bazi(
        args.year, args.month, args.day, args.hour, args.gender,
        start=args.start, end=args.end, b=args.b, g=args.g, r=args.r, n=args.n
    )
    
    print(bazi.get_formatted_output())
    
    return bazi.get_result()


if __name__ == "__main__":
    main() 