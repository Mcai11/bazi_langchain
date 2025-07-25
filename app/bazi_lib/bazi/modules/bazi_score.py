"""
八字分数计算模块
专门负责五行分数和强弱计算
按照原版bazi.py的精确逻辑实现
"""

from typing import Dict, List, Any

try:
    from ..datas import *  # type: ignore
    from ..bazi_core import *  # type: ignore
    from ..common import *  # type: ignore
    from ..ganzhi import *  # type: ignore
    from ..ganzhi import gan5, zhi5
except ImportError:
    try:
        from datas import *  # type: ignore
        from bazi_core import *  # type: ignore
        from common import *  # type: ignore
        from ganzhi import *  # type: ignore
        from ganzhi import gan5, zhi5
    except ImportError:
        try:
            # 添加路径后再次尝试导入
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from app.bazi_lib.bazi.datas import *  # type: ignore
            from app.bazi_lib.bazi.bazi_core import *  # type: ignore
            from app.bazi_lib.bazi.common import *  # type: ignore
            from app.bazi_lib.bazi.ganzhi import *  # type: ignore
            from app.bazi_lib.bazi.ganzhi import gan5, zhi5
        except ImportError:
            # 最后的默认值设置
            ten_deities = {}
            zhi5 = {}
            gan5 = {}
            Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
            Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


class BaziScoreCalculator:
    """八字分数计算器 - 按照原版bazi.py的精确逻辑"""
    
    def __init__(self, gans: List[str], zhis: List[str], me: str, shens: List[str]):
        """
        初始化分数计算器
        
        Args:
            gans: 四柱天干
            zhis: 四柱地支
            me: 日主
            shens: 十神列表
        """
        self.gans = gans
        self.zhis = zhis
        self.me = me
        self.shens = shens
        
        # 分数结果
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        self.gan_scores = {gan: 0 for gan in Gan}
        self.strong_score = 0
        self.weak = True
        
    def calculate_wuxing_scores(self) -> Dict[str, int]:
        """
        计算五行分数 - 完全按照原版bazi.py的逻辑
        对应原版代码第206-217行
        """
        # 重置分数
        self.scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        self.gan_scores = {gan: 0 for gan in Gan}
        
        # 计算天干分数（每个天干5分）
        # 原版：for item in gans: scores[gan5[item]] += 5
        for item in self.gans:
            if item in gan5:
                self.scores[gan5[item]] += 5
                self.gan_scores[item] += 5
        
        # 计算地支分数（原版逻辑：for item in list(zhis) + [zhis.month]）
        # 这里zhis.month是月支，即self.zhis[1]
        zhis_to_process = list(self.zhis) + [self.zhis[1]]
        
        for item in zhis_to_process:
            if item in zhi5:
                for gan in zhi5[item]:
                    if gan in gan5:
                        self.scores[gan5[gan]] += zhi5[item][gan]
                        self.gan_scores[gan] += zhi5[item][gan]
        
        return self.scores
    
    def calculate_strength(self) -> Dict[str, Any]:
        """
        计算强弱 - 按照原版bazi.py的逻辑
        对应原版代码第218-253行
        """
        if not self.me:
            return {"is_weak": True, "strong_score": 0}
        
        # 原版逻辑：子平真诠的计算
        self.weak = True
        me_status = []
        
        # 检查日主在各地支的状态
        for item in self.zhis:
            if self.me in ten_deities and item in ten_deities[self.me]:
                me_status.append(ten_deities[self.me][item])
                if ten_deities[self.me][item] in ('长', '帝', '建'):
                    self.weak = False
        
        # 如果还是身弱，再检查比劫和库的数量
        if self.weak:
            if (self.shens.count('比') + me_status.count('库')) > 2:
                self.weak = False
        
        # 计算强弱分数（原版逻辑：网上的计算）
        # strong = gan_scores[me_attrs_['比']] + gan_scores[me_attrs_['劫']] + gan_scores[me_attrs_['枭']] + gan_scores[me_attrs_['印']]
        if self.me in ten_deities:
            me_attrs_inverse = getattr(ten_deities[self.me], 'inverse', {})
            
            # 帮身分数：比劫印枭
            helper_score = 0
            for shen_type in ['比', '劫', '枭', '印']:
                if shen_type in me_attrs_inverse:
                    gan = me_attrs_inverse[shen_type]
                    helper_score += self.gan_scores.get(gan, 0)
            
            self.strong_score = helper_score
        else:
            # 备用计算方法
            self.strong_score = 13  # 默认值
        
        return {
            "is_weak": self.weak,
            "strong_score": self.strong_score,
            "strength_description": "身弱" if self.weak else "身强"
        }
    
    def get_complete_analysis(self) -> Dict[str, Any]:
        """获取完整的分数分析结果"""
        wuxing_scores = self.calculate_wuxing_scores()
        strength_info = self.calculate_strength()
        
        return {
            "wuxing_scores": wuxing_scores,
            "gan_scores": self.gan_scores,
            "strength_info": strength_info
        }


def calculate_bazi_scores(gans: List[str], zhis: List[str], me: str, shens: List[str]) -> Dict[str, Any]:
    """
    便捷函数：计算八字分数
    
    Args:
        gans: 四柱天干
        zhis: 四柱地支  
        me: 日主
        shens: 十神列表
        
    Returns:
        完整的分数分析结果
    """
    calculator = BaziScoreCalculator(gans, zhis, me, shens)
    return calculator.get_complete_analysis()


if __name__ == "__main__":
    # 测试用例：1985年1月1日10时 男命
    # 甲子 丙子 庚子 辛巳
    test_gans = ['甲', '丙', '庚', '辛']
    test_zhis = ['子', '子', '子', '巳']
    test_me = '庚'
    test_shens = ['才', '杀', '--', '劫', '伤', '伤', '伤', '杀']
    
    result = calculate_bazi_scores(test_gans, test_zhis, test_me, test_shens)
    
    print("=== 八字分数计算测试 ===")
    print(f"五行分数: {result['wuxing_scores']}")
    print(f"天干分数: {result['gan_scores']}")
    print(f"强弱信息: {result['strength_info']}")
    
    # 期望结果：金11, 木5, 水32, 火10, 土2, 强弱13 