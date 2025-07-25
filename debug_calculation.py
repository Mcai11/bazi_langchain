#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app/bazi_lib/bazi'))

def debug_calculation_flow():
    """调试计算流程，确定问题出在哪里"""
    
    print("=== 调试八字计算流程 ===\n")
    
    # 1. 直接测试BaziScoreCalculator
    print("1. 直接测试BaziScoreCalculator:")
    try:
        from modules.bazi_score import BaziScoreCalculator
        from ganzhi import gan5, zhi5
        
        # 1990年5月15日14时的实际八字
        gans = ['庚', '辛', '丙', '戊']  # 根据lunar-python计算
        zhis = ['午', '巳', '戌', '未']  # 对应地支
        me = '丙'
        shens = []
        
        calculator = BaziScoreCalculator(gans, zhis, me, shens)
        result = calculator.get_complete_analysis()
        
        print(f"  gans: {gans}")
        print(f"  zhis: {zhis}")
        print(f"  结果: {result['wuxing_scores']}")
        print(f"  天干分数: {result['gan_scores']}")
        
    except Exception as e:
        print(f"  错误: {e}")
    
    # 2. 测试BaziMainModule
    print("\n2. 测试BaziMainModule:")
    try:
        from bazi_analyzer import BaziAnalyzer
        
        analyzer = BaziAnalyzer(1990, 5, 15, 14)
        if hasattr(analyzer, 'bazi_main_module'):
            module = analyzer.bazi_main_module
            print(f"  实际gans: {module.gans}")
            print(f"  实际zhis: {module.zhis}")
            print(f"  模块结果: {module.scores}")
            print(f"  模块天干分数: {module.gan_scores}")
        
    except Exception as e:
        print(f"  错误: {e}")
    
    # 3. 测试原版bazi.py的逻辑
    print("\n3. 手动按原版逻辑计算:")
    try:
        from ganzhi import gan5, zhi5, Gan
        
        # 使用实际的八字数据
        gans = ['庚', '辛', '丙', '戊']
        zhis = ['午', '巳', '戌', '未']
        
        scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        gan_scores = {gan: 0 for gan in Gan}
        
        # 天干计算
        for item in gans:
            if item in gan5:
                scores[gan5[item]] += 5
                gan_scores[item] += 5
        
        print(f"  天干计算后: {scores}")
        print(f"  天干分数: {gan_scores}")
        
        # 地支计算 - 按原版逻辑，月支(zhis[1])要重复计算
        zhis_to_process = list(zhis) + [zhis[1]]  # 添加月支
        print(f"  处理的地支: {zhis_to_process}")
        
        for item in zhis_to_process:
            if item in zhi5:
                print(f"  地支{item}藏干: {dict(zhi5[item])}")
                for gan in zhi5[item]:
                    if gan in gan5:
                        scores[gan5[gan]] += zhi5[item][gan]
                        gan_scores[gan] += zhi5[item][gan]
        
        print(f"  最终五行: {scores}")
        print(f"  最终天干: {gan_scores}")
        
    except Exception as e:
        print(f"  错误: {e}")
    
    # 4. 检查是否使用了fallback方法
    print("\n4. 检查BaziMainModule是否使用了fallback:")
    try:
        # 临时修改bazi_main.py来添加调试信息
        import importlib
        import modules.bazi_main
        importlib.reload(modules.bazi_main)
        
        print("  请检查控制台输出，看是否有'导入失败，使用备用方法'的信息")
        
    except Exception as e:
        print(f"  错误: {e}")

if __name__ == "__main__":
    debug_calculation_flow() 