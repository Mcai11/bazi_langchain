#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from bazi_interpret import BaziInterpreter
import json

def test_statistics_debug():
    """测试统计计算的详细调试函数"""
    
    print("=== 八字统计计算诊断 ===\n")
    
    # 测试案例
    test_cases = [
        {"name": "测试案例1", "year": 1990, "month": 5, "day": 15, "hour": 14},
        {"name": "测试案例2", "year": 2000, "month": 1, "day": 1, "hour": 12},
        {"name": "测试案例3", "year": 1985, "month": 8, "day": 20, "hour": 8},
        {"name": "边界测试", "year": 1900, "month": 1, "day": 1, "hour": 0},
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"输入: {case['year']}年{case['month']}月{case['day']}日{case['hour']}时")
        
        try:
            # 使用BaziInterpreter进行测试
            interpreter = BaziInterpreter()
            
            # 构建查询
            query = f"请分析{case['year']}年{case['month']}月{case['day']}日{case['hour']}时的八字"
            
            # 进行分析
            result = interpreter.interpret_bazi_query(query)
            
            print(f"✓ 分析成功")
            
            # 查找统计信息
            if "statistics" in result:
                stats = result["statistics"]
                if "wuxing_statistics" in stats and "gan_statistics" in stats:
                    print(f"  五行统计: {stats['wuxing_statistics']}")
                    print(f"  天干统计: {stats['gan_statistics']}")
                    
                    # 检查是否全为0
                    wuxing_total = sum(stats['wuxing_statistics'].values())
                    gan_total = sum(stats['gan_statistics'].values())
                    
                    if wuxing_total == 0 and gan_total == 0:
                        print("  ❌ 发现问题：统计结果全为0！")
                        print("  完整结果：")
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                    else:
                        print(f"  ✓ 统计正常：五行总分={wuxing_total}, 天干总分={gan_total}")
                else:
                    print("  ⚠️  未找到完整的统计信息")
                    print(f"  可用字段: {list(stats.keys())}")
            else:
                print("  ⚠️  结果中没有统计信息")
                print(f"  可用字段: {list(result.keys())}")
                
        except Exception as e:
            print(f"  ❌ 分析异常: {str(e)}")
            import traceback
            traceback.print_exc()

def simple_test():
    """简单的直接测试"""
    print("\n=== 简单直接测试 ===")
    
    try:
        interpreter = BaziInterpreter()
        query = "请分析1990年5月15日14时的八字统计"
        result = interpreter.interpret_bazi_query(query)
        
        print("测试查询:", query)
        print("返回结果键值:", list(result.keys()))
        
        if "statistics" in result:
            print("统计信息:", result["statistics"])
        else:
            print("完整结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:1000] + "...")
            
    except Exception as e:
        print(f"简单测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_statistics_debug()
    simple_test() 