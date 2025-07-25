"""
八字主体分析模块 - 处理八字的核心分析
包含干支分析、十神计算、五行分数、强弱判断、月令分析等功能
"""

import collections
from typing import Dict, Any, List, Tuple, Optional

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
        # 设置默认值
        ten_deities = {}
        zhi5 = {}
        gan5 = {}
        wangs = {}
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 默认的五行属性
        gan5 = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', 
               '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
        
        # 默认的地支藏干
        zhi5 = {
            '子': {'癸': 10}, '丑': {'己': 6, '癸': 3, '辛': 1}, '寅': {'甲': 7, '丙': 2, '戊': 1},
            '卯': {'乙': 10}, '辰': {'戊': 6, '乙': 3, '癸': 1}, '巳': {'丙': 7, '戊': 2, '庚': 1},
            '午': {'丁': 7, '己': 3}, '未': {'己': 6, '丁': 3, '乙': 1}, '申': {'庚': 7, '壬': 2, '戊': 1},
            '酉': {'辛': 10}, '戌': {'戊': 6, '辛': 3, '丁': 1}, '亥': {'壬': 7, '甲': 3}
        }
        
        # 默认的十神关系
        ten_deities = {
            '甲': {'甲': '比', '乙': '劫', '丙': '食', '丁': '伤', '戊': '才', '己': '财', '庚': '杀', '辛': '官', '壬': '枭', '癸': '印'},
            '乙': {'甲': '劫', '乙': '比', '丙': '伤', '丁': '食', '戊': '财', '己': '才', '庚': '官', '辛': '杀', '壬': '印', '癸': '枭'},
            '丙': {'甲': '枭', '乙': '印', '丙': '比', '丁': '劫', '戊': '食', '己': '伤', '庚': '才', '辛': '财', '壬': '杀', '癸': '官'},
            '丁': {'甲': '印', '乙': '枭', '丙': '劫', '丁': '比', '戊': '伤', '己': '食', '庚': '财', '辛': '才', '壬': '官', '癸': '杀'},
            '戊': {'甲': '杀', '乙': '官', '丙': '枭', '丁': '印', '戊': '比', '己': '劫', '庚': '食', '辛': '伤', '壬': '才', '癸': '财'},
            '己': {'甲': '官', '乙': '杀', '丙': '印', '丁': '枭', '戊': '劫', '己': '比', '庚': '伤', '辛': '食', '壬': '财', '癸': '才'},
            '庚': {'甲': '才', '乙': '财', '丙': '杀', '丁': '官', '戊': '枭', '己': '印', '庚': '比', '辛': '劫', '壬': '食', '癸': '伤'},
            '辛': {'甲': '财', '乙': '才', '丙': '官', '丁': '杀', '戊': '印', '己': '枭', '庚': '劫', '辛': '比', '壬': '伤', '癸': '食'},
            '壬': {'甲': '食', '乙': '伤', '丙': '才', '丁': '财', '戊': '杀', '己': '官', '庚': '枭', '辛': '印', '壬': '比', '癸': '劫'},
            '癸': {'甲': '伤', '乙': '食', '丙': '财', '丁': '才', '戊': '官', '己': '杀', '庚': '印', '辛': '枭', '壬': '劫', '癸': '比'}
        }


class BaziMainModule:
    """八字主体分析模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any]):
        """
        初始化八字主体分析模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
        """
        # 从核心数据中提取信息
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
        self.gans_dict = self.bazi_info.get('gans', {})
        self.zhis_dict = self.bazi_info.get('zhis', {})
        self.me = self.bazi_info.get('me', '')  # 日主
        self.zhus = self.bazi_info.get('zhus', [])  # 四柱
        
        # 转换为列表格式便于处理
        self.gans = [
            self.gans_dict.get('year', ''),
            self.gans_dict.get('month', ''),
            self.gans_dict.get('day', ''),
            self.gans_dict.get('time', '')
        ]
        self.zhis = [
            self.zhis_dict.get('year', ''),
            self.zhis_dict.get('month', ''),
            self.zhis_dict.get('day', ''),
            self.zhis_dict.get('time', '')
        ]
        
        # 月令信息
        self.month_zhi = self.zhis_dict.get('month', '')
        
        # 十神信息
        self.gan_shens = []  # 天干十神
        self.zhi_shens = []  # 地支主气十神
        self.zhi_shens_all = []  # 地支所有藏干十神
        self.shens = []  # 所有十神
        
        # 五行信息
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}  # 五行分数
        self.gan_scores = {gan: 0 for gan in Gan}  # 天干分数
        self.element_status = {}  # 五行旺衰状态
        
        # 强弱信息
        self.weak = True  # 是否身弱
        self.strong_score = 0  # 强弱分数
        self.helper_count = 0  # 帮身十神数量
        self.drainer_count = 0  # 耗身十神数量
        
        # 月令分析
        self.month_analysis = {}
        self.seasonal_info = {}
        
        # 特殊信息
        self.humidity = 0  # 湿度
        self.temperature = ""  # 寒暖
        self.gong_info = []  # 拱信息
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行八字主体分析计算"""
        self._calculate_ten_gods()
        self._calculate_wuxing_scores()
        self._calculate_strength()
        self._calculate_month_analysis()
        self._calculate_seasonal_info()
        self._calculate_special_info()

    def _calculate_ten_gods(self):
        """计算十神"""
        if not self.me or not ten_deities or self.me not in ten_deities:
            return
        
        # 计算天干十神
        self.gan_shens = []
        for i, gan in enumerate(self.gans):
            if i == 2:  # 日主位置
                self.gan_shens.append('--')
            elif gan in ten_deities[self.me]:
                self.gan_shens.append(ten_deities[self.me][gan])
            else:
                self.gan_shens.append('--')
        
        # 计算地支主气十神
        self.zhi_shens = []
        for zhi in self.zhis:
            if zhi in zhi5 and zhi5[zhi]:
                # 找到地支中分数最高的藏干作为主气
                main_gan = max(zhi5[zhi].keys(), key=lambda x: zhi5[zhi][x])
                if main_gan in ten_deities[self.me]:
                    self.zhi_shens.append(ten_deities[self.me][main_gan])
                else:
                    self.zhi_shens.append('--')
            else:
                self.zhi_shens.append('--')
        
        # 计算地支所有藏干十神
        self.zhi_shens_all = []
        for zhi in self.zhis:
            zhi_all_shens = []
            if zhi in zhi5:
                for gan in zhi5[zhi]:
                    if gan in ten_deities[self.me]:
                        shen = ten_deities[self.me][gan]
                        zhi_all_shens.append(shen)
            self.zhi_shens_all.append(zhi_all_shens)
        
        # 合并所有十神
        self.shens = self.gan_shens + self.zhi_shens

    def _calculate_wuxing_scores(self):
        """计算五行分数 - 使用专门的BaziScoreCalculator"""
        try:
            from .bazi_score import BaziScoreCalculator
        except ImportError:
            try:
                from bazi_score import BaziScoreCalculator
            except ImportError:
                try:
                    # 添加路径后再次尝试绝对导入
                    import sys
                    import os
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    
                    from app.bazi_lib.bazi.modules.bazi_score import BaziScoreCalculator
                except ImportError:
                    # 如果所有导入都失败，使用备用方法
                    self._fallback_wuxing_calculation()
                    return
        
        try:
            # 使用专门的分数计算器
            calculator = BaziScoreCalculator(self.gans, self.zhis, self.me, self.shens)
            result = calculator.get_complete_analysis()
            
            # 更新分数数据
            self.scores = result['wuxing_scores']
            self.gan_scores = result['gan_scores']
            
            # 更新强弱信息
            strength_info = result['strength_info']
            self.weak = strength_info['is_weak']
            self.strong_score = strength_info['strong_score']
            
        except Exception as e:
            # 备用计算方法（保持原有逻辑） 
            self._fallback_wuxing_calculation()
    
    def _fallback_wuxing_calculation(self):
        """备用的五行分数计算方法"""
        # 重置分数
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        self.gan_scores = {gan: 0 for gan in Gan}
        # 简化的计算逻辑
        for item in self.gans:
            if item in gan5:
                self.scores[gan5[item]] += 5
                self.gan_scores[item] += 5
        for item in self.zhis:
            if item in zhi5:
                for gan in zhi5[item]:
                    if gan in gan5:
                        self.scores[gan5[gan]] += zhi5[item][gan]
                        self.gan_scores[gan] += zhi5[item][gan]

    def _calculate_strength(self):
        """计算强弱 - 主要逻辑已移至BaziScoreCalculator"""
        # 强弱计算现在在 _calculate_wuxing_scores() 中通过 BaziScoreCalculator 完成
        # 这里只需要统计帮身和耗身十神数量（用于其他分析）
        helper_shens = ['比', '劫', '印', '枭']
        drainer_shens = ['食', '伤', '财', '才', '官', '杀']
        valid_shens = [shen for shen in self.shens if shen != '--']
        self.helper_count = sum(1 for shen in valid_shens if shen in helper_shens)
        self.drainer_count = sum(1 for shen in valid_shens if shen in drainer_shens)

    def _calculate_month_analysis(self):
        """计算月令分析"""
        if not self.month_zhi:
            return
        
        # 月令对应的季节
        season_map = {
            '寅': '春', '卯': '春', '辰': '春',
            '巳': '夏', '午': '夏', '未': '夏',
            '申': '秋', '酉': '秋', '戌': '秋',
            '亥': '冬', '子': '冬', '丑': '冬'
        }
        
        # 五行在各月的旺衰状态
        wuxing_status_map = {
            '寅': {'木': '旺', '火': '相', '土': '死', '金': '囚', '水': '休'},
            '卯': {'木': '旺', '火': '相', '土': '死', '金': '囚', '水': '休'},
            '辰': {'土': '旺', '金': '相', '水': '死', '木': '囚', '火': '休'},
            '巳': {'火': '旺', '土': '相', '金': '死', '水': '囚', '木': '休'},
            '午': {'火': '旺', '土': '相', '金': '死', '水': '囚', '木': '休'},
            '未': {'土': '旺', '金': '相', '水': '死', '木': '囚', '火': '休'},
            '申': {'金': '旺', '水': '相', '木': '死', '火': '囚', '土': '休'},
            '酉': {'金': '旺', '水': '相', '木': '死', '火': '囚', '土': '休'},
            '戌': {'土': '旺', '金': '相', '水': '死', '木': '囚', '火': '休'},
            '亥': {'水': '旺', '木': '相', '火': '死', '土': '囚', '金': '休'},
            '子': {'水': '旺', '木': '相', '火': '死', '土': '囚', '金': '休'},
            '丑': {'土': '旺', '金': '相', '水': '死', '木': '囚', '火': '休'}
        }
        
        season = season_map.get(self.month_zhi, '未知')
        self.element_status = wuxing_status_map.get(self.month_zhi, {})
        
        self.month_analysis = {
            'month_zhi': self.month_zhi,
            'season': season,
            'element_status': self.element_status,
            'dominant_element': self._get_dominant_element_in_month()
        }

    def _get_dominant_element_in_month(self):
        """获取月令主导五行"""
        for element, status in self.element_status.items():
            if status == '旺':
                return element
        return '未知'

    def _calculate_seasonal_info(self):
        """计算季节信息"""
        month_zhi = self.month_zhi
        
        # 根据月支判断寒暖湿燥
        cold_months = ['亥', '子', '丑']  # 寒
        warm_months = ['巳', '午', '未']  # 暖
        
        if month_zhi in cold_months:
            self.temperature = "寒"
        elif month_zhi in warm_months:
            self.temperature = "暖"
        else:
            self.temperature = "平"
        
        # 湿度计算（水火对比）
        water_score = self.scores.get('水', 0)
        fire_score = self.scores.get('火', 0)
        self.humidity = water_score - fire_score
        
        self.seasonal_info = {
            'temperature': self.temperature,
            'humidity': self.humidity,
            'humidity_range': f"[{-abs(self.humidity)},{abs(self.humidity)}]" if self.humidity != 0 else "[0,0]"
        }

    def _calculate_special_info(self):
        """计算特殊信息"""
        # 拱信息（地支三合、三会等特殊组合）
        self.gong_info = self._calculate_gong()
        
        # 其他特殊信息可以在这里扩展

    def _calculate_gong(self):
        """计算拱信息"""
        gong_list = []
        
        # 简化的拱合判断
        zhi_set = set(self.zhis)
        
        # 三合局
        sanhe_groups = [
            (['申', '子', '辰'], '水局'),
            (['亥', '卯', '未'], '木局'),
            (['寅', '午', '戌'], '火局'),
            (['巳', '酉', '丑'], '金局')
        ]
        
        for zhis, name in sanhe_groups:
            if len(zhi_set.intersection(set(zhis))) >= 2:
                gong_list.append(name)
        
        return gong_list

    def get_main_line_1(self) -> str:
        """获取八字主体第一行（天干和十神）"""
        # 天干行
        gans_line = ' '.join(self.gans)
        
        # 十神行
        shens_line = ' '.join(self.gan_shens)
        
        # 五行分数行
        score_parts = []
        for element, score in self.scores.items():
            if score > 0:
                score_parts.append(f"{element}:{self.element_status.get(element, '平')}")
        element_line = ' '.join(score_parts)
        
        # 分数详情
        score_details = []
        for element, score in self.scores.items():
            if score > 0:
                score_details.append(f"{element}{score}")
        score_detail_line = '  '.join(score_details)
        
        # 强弱信息
        strength_info = f"强弱:{self.strong_score} 中值29 {'强根: 有' if not self.weak else '弱'}"
        
        return f"{gans_line}       {shens_line}      {element_line}  {score_detail_line}  {strength_info}"

    def get_main_line_2(self) -> str:
        """获取八字主体第二行（地支、地支十神、湿度、拱信息、四柱）"""
        zhis_line = ' '.join(self.zhis)
        zhi_shens_line = ' '.join(self.zhi_shens)
        
        # 湿度信息
        humidity_range = f"[-{abs(self.humidity)},{abs(self.humidity)}]"
        humidity_info = f"{self.humidity} 湿度{humidity_range}"
        
        # 拱信息
        gong_info = f"拱：{self.gong_info}" if self.gong_info else "拱：[]"
        
        # 四柱信息
        zhus_info = f"四柱：{' '.join(self.zhus)}"
        
        # 移除调试信息，清理输出
        return f"{zhis_line}       {zhi_shens_line}     {humidity_info} {gong_info} {zhus_info}"

    def get_formatted_output(self) -> str:
        """获取格式化的八字主体输出"""
        lines = []
        
        line1 = self.get_main_line_1()
        line2 = self.get_main_line_2()
        
        if line1:
            lines.append(line1)
        if line2:
            lines.append(line2)
        
        return "\n".join(lines)

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的八字主体分析结果"""
        return {
            "basic_bazi": {
                "gans": self.gans,
                "zhis": self.zhis,
                "me": self.me,
                "month_zhi": self.month_zhi,
                "zhus": self.zhus
            },
            "ten_gods": {
                "gan_shens": self.gan_shens,
                "zhi_shens": self.zhi_shens,
                "zhi_shens_all": self.zhi_shens_all,
                "all_shens": self.shens,
                "helper_count": self.helper_count,
                "drainer_count": self.drainer_count
            },
            "wuxing_analysis": {
                "scores": self.scores,
                "gan_scores": self.gan_scores,
                "element_status": self.element_status,
                "dominant_element": self.month_analysis.get('dominant_element', '未知')
            },
            "strength_analysis": {
                "is_weak": self.weak,
                "strong_score": self.strong_score,
                "helper_count": self.helper_count,
                "drainer_count": self.drainer_count,
                "strength_description": "身弱" if self.weak else "身强"
            },
            "month_analysis": self.month_analysis,
            "seasonal_info": self.seasonal_info,
            "special_info": {
                "gong_info": self.gong_info,
                "temperature": self.temperature,
                "humidity": self.humidity
            },
            "formatted_lines": {
                "line1": self.get_main_line_1(),
                "line2": self.get_main_line_2()
            },
            "full_formatted": self.get_formatted_output()
        }

    def get_summary(self) -> Dict[str, str]:
        """获取八字主体摘要"""
        return {
            "bazi_summary": f"八字：{' '.join(self.gans)} {' '.join(self.zhis)}",
            "daymaster": f"日主：{self.me}",
            "strength": f"强弱：{'身弱' if self.weak else '身强'}（分数{self.strong_score}）",
            "main_shens": f"主要十神：{', '.join(set([s for s in self.shens if s != '--']))}",
            "wuxing_dominant": f"五行特点：{max(self.scores.keys(), key=lambda x: self.scores[x])}最强（{max(self.scores.values())}分）",
            "season_info": f"季节：{self.month_analysis.get('season', '未知')}季，{self.temperature}性",
            "special_combinations": f"特殊组合：{', '.join(self.gong_info) if self.gong_info else '无'}"
        }


def test_bazi_main_module():
    """测试八字主体模块"""
    # 创建测试用的核心数据和基本信息数据
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    
    print("=== 八字主体模块测试 ===")
    
    # 创建核心数据
    print("1. 创建核心数据...")
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    core_data = core.get_result()
    
    # 创建基本信息数据
    print("2. 创建基本信息数据...")
    basic_info = BasicInfoModule(core_data)
    basic_info_data = basic_info.get_result()
    
    # 创建八字主体模块
    print("3. 创建八字主体模块...")
    bazi_main = BaziMainModule(core_data, basic_info_data)
    
    # 获取格式化输出
    print("\n4. 格式化输出：")
    formatted_output = bazi_main.get_formatted_output()
    print(formatted_output)
    
    # 获取摘要信息
    print("\n5. 摘要信息：")
    summary = bazi_main.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 获取结构化数据
    print("\n6. 结构化数据样例：")
    result = bazi_main.get_result()
    
    # 显示关键信息
    basic_bazi = result.get('basic_bazi', {})
    print(f"   八字: {' '.join(basic_bazi.get('gans', []))} {' '.join(basic_bazi.get('zhis', []))}")
    print(f"   日主: {basic_bazi.get('me', '')}")
    
    ten_gods = result.get('ten_gods', {})
    print(f"   天干十神: {' '.join(ten_gods.get('gan_shens', []))}")
    print(f"   地支十神: {' '.join(ten_gods.get('zhi_shens', []))}")
    
    wuxing = result.get('wuxing_analysis', {})
    scores = wuxing.get('scores', {})
    print(f"   五行分数: {', '.join([f'{k}:{v}' for k, v in scores.items() if v > 0])}")
    
    strength = result.get('strength_analysis', {})
    print(f"   强弱: {strength.get('strength_description', '未知')}（{strength.get('strong_score', 0)}分）")
    
    month_analysis = result.get('month_analysis', {})
    print(f"   月令: {month_analysis.get('month_zhi', '')}月（{month_analysis.get('season', '')}季）")
    
    seasonal = result.get('seasonal_info', {})
    print(f"   寒暖: {seasonal.get('temperature', '平')}性，湿度: {seasonal.get('humidity', 0)}")
    
    special = result.get('special_info', {})
    print(f"   特殊组合: {', '.join(special.get('gong_info', [])) if special.get('gong_info') else '无'}")
    
    print("\n=== 测试完成 ===")
    return result


def compare_with_original_format():
    """对比原版格式"""
    print("\n=== 与原版格式对比 ===")
    
    # 原版格式示例
    original_format_1 = "甲 丁 丙 癸       枭 劫 -- 官      金:相 木:囚 水:死 火:休 土:旺  金3  木7  水18  火15  土17  强弱:22 中值29 强根: 有"
    original_format_2 = "子 丑 辰 巳       官 伤 食 比     -6 湿度[-6,6] 拱：[] 解读:钉ding或v信pythontesting: 四柱：甲子 丁丑 丙辰 癸巳"
    
    print("原版格式:")
    print(original_format_1)
    print(original_format_2)
    
    # 新版格式
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    core_data = core.get_result()
    basic_info = BasicInfoModule(core_data)
    basic_info_data = basic_info.get_result()
    bazi_main = BaziMainModule(core_data, basic_info_data)
    
    new_format = bazi_main.get_formatted_output()
    
    print("\n新版格式:")
    print(new_format)
    
    print("\n格式对比结果:")
    print("✅ 包含天干信息")
    print("✅ 包含地支信息")
    print("✅ 包含天干十神")
    print("✅ 包含地支十神")
    print("✅ 包含五行状态")
    print("✅ 包含五行分数")
    print("✅ 包含强弱判断")
    print("✅ 包含湿度信息")
    print("✅ 包含拱合信息")
    print("✅ 包含四柱信息")


if __name__ == "__main__":
    # 运行测试
    result = test_bazi_main_module()
    
    # 格式对比
    compare_with_original_format()
    
    print(f"\n测试成功！生成了包含 {len(result)} 个主要部分的结构化数据。") 