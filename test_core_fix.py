#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app/bazi_lib/bazi'))

def test_core_fix():
    print("=== 测试CoreBaseModule修复效果 ===\n")
    
    # 1. 测试CoreBaseModule直接计算
    try:
        from modules.core_base import CoreBaseModule
        
        print("1. CoreBaseModule直接测试:")
        core = CoreBaseModule(1990, 5, 15, 14, use_gregorian=True)
        result = core.get_result()
        bazi = result['bazi_info']
        
        gans_list = list(bazi['gans'].values())
        zhis_list = list(bazi['zhis'].values())
        
        print(f"   gans: {gans_list}")
        print(f"   zhis: {zhis_list}")
        print(f"   日主: {bazi['me']}")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 测试BaziAnalyzer整体计算
    try:
        from bazi_analyzer import BaziAnalyzer
        
        print("\n2. BaziAnalyzer整体测试:")
        analyzer = BaziAnalyzer(1990, 5, 15, 14, use_gregorian=True)
        
        if hasattr(analyzer, 'bazi_main_module'):
            module = analyzer.bazi_main_module
            print(f"   gans: {module.gans}")
            print(f"   zhis: {module.zhis}")
            print(f"   日主: {module.me}")
            print(f"   五行分数: {module.scores}")
            print(f"   天干非零分数: {dict([(k,v) for k,v in module.gan_scores.items() if v > 0])}")
            
            # 3. 获取完整的统计结果
            print("\n3. 完整统计结果:")
            result = analyzer.get_result()
            if 'analysis_results' in result and 'statistics' in result['analysis_results']:
                stats = result['analysis_results']['statistics']
                print(f"   五行统计: {stats.get('wuxing_statistics', {})}")
                print(f"   天干统计: {stats.get('gan_statistics', {})}")
            
        
    except Exception as e:
        print(f"   错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 手动验证计算
    print("\n4. 手动验证计算:")
    try:
        from ganzhi import gan5, zhi5, Gan
        
        # 使用正确的八字数据
        gans = ['庚', '辛', '庚', '癸']
        zhis = ['午', '巳', '辰', '未']
        
        scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        gan_scores = {gan: 0 for gan in Gan}
        
        # 天干计算
        for item in gans:
            if item in gan5:
                scores[gan5[item]] += 5
                gan_scores[item] += 5
        
        print(f"   天干计算后: {scores}")
        
        # 地支计算 - 按原版逻辑，月支(zhis[1])要重复计算
        zhis_to_process = list(zhis) + [zhis[1]]  # 添加月支'巳'
        print(f"   处理的地支: {zhis_to_process}")
        
        for item in zhis_to_process:
            if item in zhi5:
                print(f"   地支{item}藏干: {dict(zhi5[item])}")
                for gan in zhi5[item]:
                    if gan in gan5:
                        scores[gan5[gan]] += zhi5[item][gan]
                        gan_scores[gan] += zhi5[item][gan]
        
        print(f"   **最终五行**: {scores}")
        print(f"   **最终天干**: {dict([(k,v) for k,v in gan_scores.items() if v > 0])}")
        
    except Exception as e:
        print(f"   手动计算错误: {e}")
    
    # 5. 正确答案对比
    print("\n5. 期望的正确结果:")
    print("   你提供的正确答案: 金17 木3 水6 火17 土17")
    print("   八字: 庚午 辛巳 庚辰 癸未")

if __name__ == "__main__":
    test_core_fix() 