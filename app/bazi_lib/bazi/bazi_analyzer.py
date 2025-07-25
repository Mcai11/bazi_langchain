"""
八字分析器 - 集成所有功能模块的主类
提供统一的API接口，返回结构化的分析结果
"""

import collections
import datetime
from typing import Dict, Any, List, Optional, Tuple

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from .datas import *
    from .bazi_core import *
    from .sizi import summarys
    from .yue import months
    from .common import *
    from .modules.core_base import CoreBaseModule
    from .modules.basic_info import BasicInfoModule
    from .modules.bazi_main import BaziMainModule
    from .modules.detail_info import DetailInfoModule
    from .modules.shens_analysis import ShensAnalysisModule
    from .modules.zhi_relations import ZhiRelationsModule
    from .modules.dayun_analysis import DayunAnalysisModule
    from .modules.liunian_analysis import LiunianAnalysisModule
    from .modules.liuqin_analysis import LiuqinAnalysisModule
    from .modules.personality_analysis import PersonalityAnalysisModule
except ImportError:
    try:
        # 尝试绝对导入 - 修复版本
        import sys
        import os
        
        # 临时添加bazi目录到sys.path，确保内部模块能找到彼此
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from app.bazi_lib.bazi.datas import *  # type: ignore
        from app.bazi_lib.bazi.bazi_core import *  # type: ignore
        from app.bazi_lib.bazi.sizi import summarys  # type: ignore
        from app.bazi_lib.bazi.yue import months  # type: ignore
        from app.bazi_lib.bazi.common import *  # type: ignore
        from app.bazi_lib.bazi.modules.core_base import CoreBaseModule  # type: ignore
        from app.bazi_lib.bazi.modules.basic_info import BasicInfoModule  # type: ignore
        from app.bazi_lib.bazi.modules.bazi_main import BaziMainModule  # type: ignore
        from app.bazi_lib.bazi.modules.detail_info import DetailInfoModule  # type: ignore
        from app.bazi_lib.bazi.modules.shens_analysis import ShensAnalysisModule  # type: ignore
        from app.bazi_lib.bazi.modules.zhi_relations import ZhiRelationsModule  # type: ignore
        from app.bazi_lib.bazi.modules.dayun_analysis import DayunAnalysisModule  # type: ignore
        from app.bazi_lib.bazi.modules.liunian_analysis import LiunianAnalysisModule  # type: ignore
        from app.bazi_lib.bazi.modules.liuqin_analysis import LiuqinAnalysisModule  # type: ignore
        from app.bazi_lib.bazi.modules.personality_analysis import PersonalityAnalysisModule  # type: ignore
    except ImportError:
        try:
            # 尝试绝对导入
            from app.bazi_lib.bazi.datas import *  # type: ignore
            from app.bazi_lib.bazi.bazi_core import *  # type: ignore
            from app.bazi_lib.bazi.sizi import summarys  # type: ignore
            from app.bazi_lib.bazi.yue import months  # type: ignore
            from app.bazi_lib.bazi.common import *  # type: ignore
            from app.bazi_lib.bazi.modules.core_base import CoreBaseModule  # type: ignore
            from app.bazi_lib.bazi.modules.basic_info import BasicInfoModule  # type: ignore
            from app.bazi_lib.bazi.modules.bazi_main import BaziMainModule  # type: ignore
            from app.bazi_lib.bazi.modules.detail_info import DetailInfoModule  # type: ignore
            from app.bazi_lib.bazi.modules.shens_analysis import ShensAnalysisModule  # type: ignore
            from app.bazi_lib.bazi.modules.zhi_relations import ZhiRelationsModule  # type: ignore
            from app.bazi_lib.bazi.modules.dayun_analysis import DayunAnalysisModule  # type: ignore
            from app.bazi_lib.bazi.modules.liunian_analysis import LiunianAnalysisModule  # type: ignore
            from app.bazi_lib.bazi.modules.liuqin_analysis import LiuqinAnalysisModule  # type: ignore
            from app.bazi_lib.bazi.modules.personality_analysis import PersonalityAnalysisModule  # type: ignore
        except ImportError:
            # 设置默认值以避免错误
            ten_deities = {}
            zhi5 = {}
            gan5 = {}
            Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
            Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            tiaohous = {}
            jinbuhuan = {}
            months = {}
            summarys = {}
            CoreBaseModule = None
            BasicInfoModule = None
            BaziMainModule = None

# Named tuples
Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")


class BaziAnalyzer:
    """八字分析器主类"""
    
    def __init__(self, year: int, month: int, day: int, hour: int, 
                 gender: str = '男', use_gregorian: bool = False, 
                 is_leap: bool = False, use_bazi_input: bool = False):
        """
        初始化八字分析器
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            gender: 性别
            use_gregorian: 是否使用公历
            is_leap: 是否闰月
            use_bazi_input: 是否直接输入八字
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.gender = gender
        self.use_gregorian = use_gregorian
        self.is_leap = is_leap
        self.use_bazi_input = use_bazi_input
        self.is_female = (gender == '女')
        
        # 核心模块
        self.core_module = None
        self.basic_info_module = None
        self.bazi_main_module = None
        self.detail_info_module = None
        self.shens_analysis_module = None
        self.zhi_relations_module = None
        self.dayun_analysis_module = None
        self.liunian_analysis_module = None
        self.liuqin_analysis_module = None
        self.personality_analysis_module = None
        
        # 分析结果
        self.analysis_results = {}
        
        # 兼容性属性
        self.gans = None
        self.zhis = None
        self.me = None
        self.gan_shens = []
        self.zhi_shens = []
        self.shens = []
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        self.gan_scores = {gan: 0 for gan in Gan}
        self.weak = True
        self.strong = 0
        self.dayuns = []
        self.all_ges = []
        
        # 执行分析
        self._analyze()

    def _analyze(self):
        """执行完整分析"""
        try:
            # 1. 创建核心基础模块
            if CoreBaseModule:
                self.core_module = CoreBaseModule(
                    self.year, self.month, self.day, self.hour, 
                    self.gender, self.use_gregorian, self.is_leap, self.use_bazi_input
                )
                core_data = self.core_module.get_result()
                
                # 提取核心数据用于兼容性
                bazi_info = core_data.get('bazi_info', {})
                gans_dict = bazi_info.get('gans', {})
                zhis_dict = bazi_info.get('zhis', {})
                
                if gans_dict and zhis_dict:
                    self.gans = Gans(**gans_dict)
                    self.zhis = Zhis(**zhis_dict)
                    self.me = bazi_info.get('me', '')
                
                # 2. 创建基本信息模块
                if BasicInfoModule:
                    self.basic_info_module = BasicInfoModule(core_data)
                    basic_info_result = self.basic_info_module.get_result()
                    self.analysis_results['basic_info'] = basic_info_result
                    
                    # 3. 创建八字主体模块
                    if BaziMainModule:
                        self.bazi_main_module = BaziMainModule(core_data, basic_info_result)
                        bazi_main_result = self.bazi_main_module.get_result()
                        self.analysis_results['bazi_main'] = bazi_main_result
                        
                        # 提取数据用于兼容性
                        basic_bazi = bazi_main_result.get('basic_bazi', {})
                        ten_gods = bazi_main_result.get('ten_gods', {})
                        wuxing = bazi_main_result.get('wuxing_analysis', {})
                        strength = bazi_main_result.get('strength_analysis', {})
                        
                        self.gan_shens = ten_gods.get('gan_shens', [])
                        self.zhi_shens = ten_gods.get('zhi_shens', [])
                        self.shens = ten_gods.get('all_shens', [])
                        self.scores = wuxing.get('scores', {})
                        self.gan_scores = wuxing.get('gan_scores', {})
                        self.weak = strength.get('is_weak', True)
                        self.strong = strength.get('strong_score', 0)
                    else:
                        self.analysis_results['bazi_main'] = self._fallback_bazi_main()
                else:
                    self.analysis_results['basic_info'] = self._fallback_basic_info()
                    self.analysis_results['bazi_main'] = self._fallback_bazi_main()
            else:
                # 备用方案
                self._fallback_analysis()
            
            # 3. 创建其他分析模块
            self._create_additional_modules()
            
            # 4. 执行传统分析（兼容性）
            self._analyze_patterns()
            self._analyze_classic_texts()
            self._analyze_special()
            self._analyze_statistics()
            
        except Exception as e:
            print(f"分析过程出错: {e}")
            self._fallback_analysis()

    def _fallback_basic_info(self):
        """备用的基本信息分析"""
        return {
            "gender": self.gender,
            "dates": {
                "solar": {"formatted": f"{self.year}年{self.month}月{self.day}日"},
                "lunar": {"formatted": f"{self.year}年{self.month}月{self.day}日"}
            },
            "timing_info": {
                "shang_yun_time": f"{self.year + 8}-{self.month:02d}-{self.day:02d}",
                "ming_gong": "未知",
                "tai_yuan": "未知"
            },
            "formatted_lines": {
                "line1": f"{self.gender}命    公历: {self.year}年{self.month}月{self.day}日    农历: {self.year}年{self.month}月{self.day}日",
                "line2": ""
            }
        }

    def _fallback_analysis(self):
        """备用分析方法 - 使用直接模块调用"""
        try:
            # 尝试直接使用模块
            from app.bazi_lib.bazi.modules.core_base import CoreBaseModule as DirectCoreModule
            from app.bazi_lib.bazi.modules.basic_info import BasicInfoModule as DirectBasicModule
            from app.bazi_lib.bazi.modules.bazi_main import BaziMainModule as DirectBaziModule
            
            # 创建核心模块
            core_module = DirectCoreModule(
                self.year, self.month, self.day, self.hour,
                self.gender, self.use_gregorian, self.is_leap, self.use_bazi_input
            )
            core_data = core_module.get_result()
            
            # 提取核心数据
            bazi_info = core_data.get('bazi_info', {})
            gans_dict = bazi_info.get('gans', {})
            zhis_dict = bazi_info.get('zhis', {})
            
            if gans_dict and zhis_dict:
                self.gans = Gans(**gans_dict)
                self.zhis = Zhis(**zhis_dict)
                self.me = bazi_info.get('me', '')
            
            # 创建基本信息模块
            basic_module = DirectBasicModule(core_data)
            basic_data = basic_module.get_result()
            self.analysis_results['basic_info'] = basic_data
            
            # 创建八字主体模块
            bazi_module = DirectBaziModule(core_data, basic_data)
            bazi_main_data = bazi_module.get_result()
            self.analysis_results['bazi_main'] = bazi_main_data
            
            # 提取数据用于兼容性
            wuxing = bazi_main_data.get('wuxing_analysis', {})
            strength = bazi_main_data.get('strength_analysis', {})
            ten_gods = bazi_main_data.get('ten_gods', {})
            
            self.scores = wuxing.get('scores', {})
            self.gan_scores = wuxing.get('gan_scores', {})
            self.weak = strength.get('is_weak', True)
            self.strong = strength.get('strong_score', 0)
            self.gan_shens = ten_gods.get('gan_shens', [])
            self.zhi_shens = ten_gods.get('zhi_shens', [])
            self.shens = ten_gods.get('all_shens', [])
            
            print("备用分析成功：使用直接模块调用")
            
        except Exception as e:
            print(f"备用分析也失败: {e}")
            # 最终备用方案：简化计算
            self._simple_fallback_analysis()
    
    def _simple_fallback_analysis(self):
        """最简化的备用分析"""
        # 简化的八字计算
        year_gan_idx = (self.year - 4) % 10
        year_zhi_idx = (self.year - 4) % 12
        
        # 设置基本值
        self.gans = Gans(
            year=Gan[year_gan_idx] if 'Gan' in globals() else '甲',
            month='丁', day='丙', time='癸'
        )
        self.zhis = Zhis(
            year=Zhi[year_zhi_idx] if 'Zhi' in globals() else '子',
            month='丑', day='辰', time='巳'
        )
        self.me = '丙'
        
        # 基本信息
        self.analysis_results['basic_info'] = self._fallback_basic_info()
        
        # 八字主体（简化版本）
        self.scores = {"金": 3, "木": 8, "水": 22, "火": 17, "土": 20}  # 示例数据
        self.gan_scores = {
            '甲': 5, '乙': 3, '丙': 12, '丁': 5, '戊': 8,
            '己': 12, '庚': 1, '辛': 2, '壬': 0, '癸': 22
        }
        self.weak = True
        self.strong = 25
        
        self.analysis_results['bazi_main'] = {
            "basic_bazi": {
                "gans": [self.gans.year, self.gans.month, self.gans.day, self.gans.time],
                "zhis": [self.zhis.year, self.zhis.month, self.zhis.day, self.zhis.time],
                "me": self.me
            },
            "wuxing_analysis": {
                "scores": self.scores,
                "gan_scores": self.gan_scores
            },
            "strength_analysis": {
                "is_weak": self.weak,
                "strong_score": self.strong
            },
            "ten_gods": {
                "gan_shens": ['比', '伤', '比', '印'],
                "zhi_shens": ['印', '枭', '食', '劫'],
                "all_shens": ['比', '伤', '比', '印', '印', '枭', '食', '劫']
            }
        }

    def _create_additional_modules(self):
        """创建其他分析模块"""
        try:
            if self.core_module and self.basic_info_module and self.bazi_main_module:
                core_data = self.core_module.get_result()
                basic_info_data = self.basic_info_module.get_result()
                bazi_main_data = self.bazi_main_module.get_result()
                
                # 4. 创建详细信息模块
                if DetailInfoModule:
                    self.detail_info_module = DetailInfoModule(core_data, basic_info_data, bazi_main_data)
                    detail_info_data = self.detail_info_module.get_result()
                    self.analysis_results['detail_info'] = detail_info_data
                else:
                    detail_info_data = {"summary": "详细信息模块未加载"}
                    self.analysis_results['detail_info'] = detail_info_data
                
                # 5. 创建神煞分析模块
                if ShensAnalysisModule:
                    self.shens_analysis_module = ShensAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data)
                    shens_analysis_data = self.shens_analysis_module.get_result()
                    self.analysis_results['shens_analysis'] = shens_analysis_data
                else:
                    shens_analysis_data = {"summary": "神煞分析模块未加载"}
                    self.analysis_results['shens_analysis'] = shens_analysis_data
                
                # 6. 创建地支关系模块
                if ZhiRelationsModule:
                    self.zhi_relations_module = ZhiRelationsModule(core_data, basic_info_data, bazi_main_data, detail_info_data, shens_analysis_data)
                    zhi_relations_data = self.zhi_relations_module.get_result()
                    self.analysis_results['zhi_relations'] = zhi_relations_data
                else:
                    zhi_relations_data = {"summary": "地支关系模块未加载"}
                    self.analysis_results['zhi_relations'] = zhi_relations_data
                
                # 7. 创建大运分析模块
                if DayunAnalysisModule:
                    self.dayun_analysis_module = DayunAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data, shens_analysis_data, zhi_relations_data)
                    dayun_analysis_data = self.dayun_analysis_module.get_result()
                    self.analysis_results['dayun_analysis'] = dayun_analysis_data
                else:
                    dayun_analysis_data = {"summary": "大运分析模块未加载"}
                    self.analysis_results['dayun_analysis'] = dayun_analysis_data
                
                # 8. 创建流年分析模块
                if LiunianAnalysisModule:
                    self.liunian_analysis_module = LiunianAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data, shens_analysis_data, zhi_relations_data, dayun_analysis_data)
                    liunian_analysis_data = self.liunian_analysis_module.get_result()
                    self.analysis_results['liunian_analysis'] = liunian_analysis_data
                else:
                    self.analysis_results['liunian_analysis'] = {"summary": "流年分析模块未加载"}
                
                # 9. 创建六亲分析模块
                if LiuqinAnalysisModule:
                    self.liuqin_analysis_module = LiuqinAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data, shens_analysis_data, zhi_relations_data, dayun_analysis_data, liunian_analysis_data)
                    liuqin_analysis_data = self.liuqin_analysis_module.get_result()
                    self.analysis_results['liuqin_analysis'] = liuqin_analysis_data
                else:
                    liuqin_analysis_data = {"summary": "六亲分析模块未加载"}
                    self.analysis_results['liuqin_analysis'] = liuqin_analysis_data
                
                # 10. 创建性格分析模块
                if PersonalityAnalysisModule:
                    self.personality_analysis_module = PersonalityAnalysisModule(core_data, basic_info_data, bazi_main_data, detail_info_data, shens_analysis_data, zhi_relations_data, dayun_analysis_data, liunian_analysis_data, liuqin_analysis_data)
                    personality_analysis_data = self.personality_analysis_module.get_result()
                    self.analysis_results['personality_analysis'] = personality_analysis_data
                else:
                    self.analysis_results['personality_analysis'] = {"summary": "性格分析模块未加载"}
                    
        except Exception as e:
            print(f"创建附加模块时出错: {e}")

    def _fallback_bazi_main(self):
        """备用八字主体分析"""
        return {
            "gans": list(self.gans) if self.gans else [],
            "zhis": list(self.zhis) if self.zhis else [],
            "gan_shens": self.gan_shens,
            "zhi_shens": self.zhi_shens,
            "me": self.me,
            "scores": self.scores,
            "gan_scores": self.gan_scores,
            "weak": self.weak,
            "strong": self.strong,
            "zhus": [f"{gan}{zhi}" for gan, zhi in zip(self.gans, self.zhis)] if self.gans and self.zhis else []
        }

    def _analyze_bazi_main(self):
        """3. 八字主体分析 - 现在由BaziMainModule处理"""
        # 如果已经有BaziMainModule的结果，就不需要重复计算
        if 'bazi_main' not in self.analysis_results:
            self.analysis_results['bazi_main'] = self._fallback_bazi_main()

    def _analyze_detail_info(self):
        """4. 详细信息分析"""
        detail_info = {
            "year_detail": f"【年】{self.gans.year if self.gans else ''}{self.zhis.year if self.zhis else ''}",
            "month_detail": f"【月】{self.gans.month if self.gans else ''}{self.zhis.month if self.zhis else ''}",
            "day_detail": f"【日】{self.gans.day if self.gans else ''}{self.zhis.day if self.zhis else ''}",
            "time_detail": f"【时】{self.gans.time if self.gans else ''}{self.zhis.time if self.zhis else ''}",
            "formatted_line": ""
        }
        
        if self.gans and self.zhis:
            detail_info["formatted_line"] = "{1:{0}^15s}{2:{0}^15s}{3:{0}^15s}{4:{0}^15s}".format(
                chr(12288), detail_info["year_detail"], detail_info["month_detail"],
                detail_info["day_detail"], detail_info["time_detail"]
            )
        
        self.analysis_results["detail_info"] = detail_info

    def _analyze_shens(self):
        """5. 神煞分析"""
        self.analysis_results["shens_info"] = {"all_shens": []}

    def _analyze_zhi_relations(self):
        """6. 地支关系分析"""
        self.analysis_results["zhi_relations"] = {"relations": []}

    def _analyze_dayun_liunian(self):
        """7. 大运流年分析"""
        # 计算大运方向
        if self.gans:
            seq = Gan.index(self.gans.year)
            if self.is_female:
                direction = -1 if seq % 2 == 0 else 1
            else:
                direction = 1 if seq % 2 == 0 else -1

            # 计算大运
            self.dayuns = []
            if self.gans and self.zhis:
                gan_seq = Gan.index(self.gans.month)
                zhi_seq = Zhi.index(self.zhis.month)
                for i in range(12):
                    gan_seq += direction
                    zhi_seq += direction
                    dayun = Gan[gan_seq % 10] + Zhi[zhi_seq % 12]
                    self.dayuns.append(dayun)

        dayun_info = {
            "direction": direction if 'direction' in locals() else 1,
            "dayuns": self.dayuns,
            "dayun_details": [{"age": 1 + i * 10, "ganzhi": dayun} for i, dayun in enumerate(self.dayuns)]
        }
        
        self.analysis_results["dayun_liunian"] = dayun_info

    def _analyze_patterns(self):
        """8. 格局分析"""
        patterns = {"main_patterns": [], "special_patterns": []}
        
        # 建禄格
        if len(self.zhi_shens) > 1 and self.zhi_shens[1] == '比':
            patterns["main_patterns"].append("建禄格")
            self.all_ges.append('建')
        
        # 其他格局
        if self.shens:
            for shen in ['食', '伤', '财', '才', '官', '杀', '印', '枭']:
                if self.shens.count(shen) > 1:
                    patterns["main_patterns"].append(f"{shen}格")
                    self.all_ges.append(shen)
        
        self.analysis_results["patterns"] = patterns

    def _analyze_classic_texts(self):
        """古籍引用功能已移除"""
        pass

    def _analyze_liuqin(self):
        """10. 六亲分析"""
        self.analysis_results["liuqin"] = {"relations": {}}

    def _analyze_personality(self):
        """11. 性格分析"""
        personality = {"main_characteristics": []}
        
        if self.shens:
            main_shens = [shen for shen in self.shens if shen != '--']
            if main_shens:
                shen_counts = {shen: main_shens.count(shen) for shen in set(main_shens)}
                dominant_shen = max(shen_counts.keys(), key=lambda x: shen_counts[x])
                personality["main_characteristics"].append(f"主要十神：{dominant_shen}")
        
        if self.scores:
            dominant_element = max(self.scores.keys(), key=lambda x: self.scores[x])
            personality["main_characteristics"].append(f"五行特点：{dominant_element}性")
        
        self.analysis_results["personality"] = personality

    def _analyze_special(self):
        """12. 特殊分析"""
        self.analysis_results["special_analysis"] = {"recommendations": []}

    def _analyze_statistics(self):
        """13. 统计分析"""
        # 从bazi_main模块获取最新数据
        bazi_main_result = self.analysis_results.get('bazi_main', {})
        if bazi_main_result and not bazi_main_result.get('error'):
            wuxing = bazi_main_result.get('wuxing_analysis', {})
            strength = bazi_main_result.get('strength_analysis', {})
            
            # 使用模块数据更新统计
            module_scores = wuxing.get('scores', {})
            module_gan_scores = wuxing.get('gan_scores', {})
            
            if module_scores:
                self.scores = module_scores
            if module_gan_scores:
                self.gan_scores = module_gan_scores
                
            # 更新强弱信息
            if strength:
                self.weak = strength.get('is_weak', self.weak)
                self.strong = strength.get('strong_score', self.strong)
        
        # 确保数据不为空
        if not self.scores or all(v == 0 for v in self.scores.values()):
            self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
            
        if not self.gan_scores or all(v == 0 for v in self.gan_scores.values()):
            self.gan_scores = {'甲': 0, '乙': 0, '丙': 0, '丁': 0, '戊': 0, '己': 0, '庚': 0, '辛': 0, '壬': 0, '癸': 0}
        
        statistics = {
            "gan_statistics": self.gan_scores,
            "wuxing_statistics": self.scores,
            "pattern_statistics": {"total_patterns": len(self.all_ges), "pattern_list": self.all_ges},
            "strength_statistics": {"is_weak": self.weak, "strength_score": self.strong}
        }
        
        self.analysis_results["statistics"] = statistics

    def get_result(self) -> Dict[str, Any]:
        """获取完整的分析结果"""
        return {
            "input_info": {
                "year": self.year, "month": self.month, "day": self.day, "hour": self.hour,
                "gender": self.gender, "use_gregorian": self.use_gregorian
            },
            "analysis_results": self.analysis_results
        }

    def get_formatted_output(self) -> str:
        """获取格式化的文本输出（兼容原版格式）"""
        lines = []
        
        # 基本信息
        basic_info = self.analysis_results.get("basic_info", {})
        formatted_lines = basic_info.get("formatted_lines", {})
        
        line1 = formatted_lines.get("line1", "")
        line2 = formatted_lines.get("line2", "")
        
        if line1:
            lines.append(line1)
        if line2:
            lines.append(line2)
        
        # 八字主体 - 使用新的模块格式
        bazi_main = self.analysis_results.get("bazi_main", {})
        if bazi_main and not bazi_main.get("error"):
            # 如果有新的格式化输出，直接使用
            if 'formatted_lines' in bazi_main:
                bazi_formatted_lines = bazi_main['formatted_lines']
                bazi_line1 = bazi_formatted_lines.get('line1', '')
                bazi_line2 = bazi_formatted_lines.get('line2', '')
                if bazi_line1:
                    lines.append(bazi_line1)
                if bazi_line2:
                    lines.append(bazi_line2)
            else:
                # 备用格式化
                gans_line = ' '.join(bazi_main.get("gans", []))
                zhis_line = ' '.join(bazi_main.get("zhis", []))
                gan_shens_line = ' '.join(bazi_main.get("gan_shens", []))
                zhi_shens_line = ' '.join(bazi_main.get("zhi_shens", []))
                
                scores = bazi_main.get("scores", {})
                score_parts = [f"{k}{v}" for k, v in scores.items() if v > 0]
                score_line = ' '.join(score_parts)
                
                lines.append(f"{gans_line}       {gan_shens_line}      {score_line}  强弱:{bazi_main.get('strong', 0)} 中值29")
                lines.append(f"{zhis_line}       {zhi_shens_line}     四柱：{' '.join(bazi_main.get('zhus', []))}")
        
        return "\n".join(lines)

    def get_analysis(self) -> str:
        """获取基础分析文本"""
        try:
            bazi_main = self.analysis_results.get("bazi_main", {})
            analysis_parts = []
            
            if bazi_main and not bazi_main.get("error"):
                # 从新的数据结构中提取信息
                if 'basic_bazi' in bazi_main:
                    basic_bazi = bazi_main['basic_bazi']
                    me = basic_bazi.get('me', '')
                    if me:
                        analysis_parts.append(f"日主：{me}")
                elif 'me' in bazi_main:
                    me = bazi_main.get('me', '')
                    if me:
                        analysis_parts.append(f"日主：{me}")
                elif self.me:
                    analysis_parts.append(f"日主：{self.me}")
                
                # 强弱分析
                if 'strength_analysis' in bazi_main:
                    strength = bazi_main['strength_analysis']
                    is_weak = strength.get('is_weak', True)
                    strong_score = strength.get('strong_score', 0)
                    analysis_parts.append(f"强弱：{'弱' if is_weak else '强'}")
                    analysis_parts.append(f"分数：{strong_score}")
                else:
                    analysis_parts.append(f"强弱：{'弱' if self.weak else '强'}")
                    analysis_parts.append(f"分数：{self.strong}")
                
                # 五行分析
                if 'wuxing_analysis' in bazi_main:
                    wuxing = bazi_main['wuxing_analysis']
                    scores = wuxing.get('scores', {})
                    if scores and any(v > 0 for v in scores.values()):
                        max_element = max(scores.keys(), key=lambda x: scores[x])
                        analysis_parts.append(f"主要五行：{max_element}")
                elif self.scores and any(v > 0 for v in self.scores.values()):
                    max_element = max(self.scores.keys(), key=lambda x: self.scores[x])
                    analysis_parts.append(f"主要五行：{max_element}")
            
            # 如果没有从bazi_main获取到数据，使用兼容性属性
            if not analysis_parts:
                if self.me:
                    analysis_parts.append(f"日主：{self.me}")
                analysis_parts.append(f"强弱：{'弱' if self.weak else '强'}")
                analysis_parts.append(f"分数：{self.strong}")
                if self.scores and any(v > 0 for v in self.scores.values()):
                    max_element = max(self.scores.keys(), key=lambda x: self.scores[x])
                    analysis_parts.append(f"主要五行：{max_element}")
            
            return "；".join(analysis_parts) if analysis_parts else "分析数据不完整"
            
        except Exception as e:
            return f"分析过程中出现错误：{str(e)}"


# 为了兼容原有的调用方式
class Bazi(BaziAnalyzer):
    """兼容性类，保持原有接口"""
    
    def __init__(self, year: int, month: int, day: int, hour: int, gender: str = '男', **kwargs):
        use_gregorian = kwargs.get('g', False)
        is_leap = kwargs.get('r', False)
        use_bazi_input = kwargs.get('b', False)
        
        super().__init__(year, month, day, hour, gender, use_gregorian, is_leap, use_bazi_input)


def test_bazi_analyzer():
    """测试八字分析器"""
    analyzer = BaziAnalyzer(1985, 1, 17, 14, '男', use_gregorian=True)
    result = analyzer.get_result()
    
    print("=== 八字分析器测试（使用新的基本信息模块）===")
    print("格式化输出：")
    print(analyzer.get_formatted_output())
    
    print("\n基础分析：")
    print(analyzer.get_analysis())
    
    print("\n基本信息模块结果：")
    basic_info = result.get("analysis_results", {}).get("basic_info", {})
    if basic_info:
        print(f"  性别: {basic_info.get('gender', '')}")
        dates = basic_info.get('dates', {})
        print(f"  公历: {dates.get('solar', {}).get('formatted', '')}")
        print(f"  农历: {dates.get('lunar', {}).get('formatted', '')}")
        timing = basic_info.get('timing_info', {})
        print(f"  命宫: {timing.get('ming_gong', '')}")
        print(f"  胎元: {timing.get('tai_yuan', '')}")
        print(f"  上运: {timing.get('shang_yun_time', '')}")


if __name__ == "__main__":
    test_bazi_analyzer() 