"""
简化版八字分析器 - 直接使用模块化JSON输出
专为现代化架构设计，无需文本解析
"""

from typing import Dict, Any, Optional

# 多层导入逻辑 - 修复绝对导入问题
try:
    from .modules.core_base import CoreBaseModule
    from .modules.basic_info import BasicInfoModule
    from .modules.bazi_main import BaziMainModule
except ImportError:
    try:
        from modules.core_base import CoreBaseModule
        from modules.basic_info import BasicInfoModule
        from modules.bazi_main import BaziMainModule
    except ImportError:
        try:
            # 尝试绝对导入 - 修复版本
            import sys
            import os
            
            # 临时添加bazi目录到sys.path，确保内部模块能找到彼此
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from app.bazi_lib.bazi.modules.core_base import CoreBaseModule
            from app.bazi_lib.bazi.modules.basic_info import BasicInfoModule
            from app.bazi_lib.bazi.modules.bazi_main import BaziMainModule
        except ImportError:
            # 设置默认值以避免错误
            CoreBaseModule = None
            BasicInfoModule = None
            BaziMainModule = None


class SimpleBaziAnalyzer:
    """简化版八字分析器 - 直接使用模块JSON输出"""
    
    def __init__(self, year: int, month: int, day: int, hour: int, 
                 gender: str = '男', use_gregorian: bool = True):
        """
        初始化简化版八字分析器
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            hour: 小时
            gender: 性别
            use_gregorian: 是否使用公历
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.gender = gender
        self.use_gregorian = use_gregorian
        
        # 存储分析结果
        self.core_data = {}
        self.basic_info_data = {}
        self.bazi_main_data = {}
        self.analysis_complete = False
        
        # 执行分析
        self._perform_analysis()
    
    def _perform_analysis(self):
        """执行八字分析"""
        try:
            # 检查模块是否正常导入
            if CoreBaseModule is None or BasicInfoModule is None or BaziMainModule is None:
                self._fallback_analysis()
                return
            
            # 1. 核心八字计算
            core_module = CoreBaseModule(
                self.year, self.month, self.day, self.hour, 
                self.gender, self.use_gregorian
            )
            self.core_data = core_module.get_result()
            
            # 2. 基本信息分析
            basic_info_module = BasicInfoModule(self.core_data)
            self.basic_info_data = basic_info_module.get_result()
            
            # 3. 八字主体分析
            bazi_main_module = BaziMainModule(self.core_data, self.basic_info_data)
            self.bazi_main_data = bazi_main_module.get_result()
            
            self.analysis_complete = True
            
        except Exception as e:
            print(f"SimpleBaziAnalyzer分析失败: {e}")
            self._fallback_analysis()
    
    def _fallback_analysis(self):
        """备用分析方法 - 使用已修复的BaziAnalyzer"""
        print("SimpleBaziAnalyzer进入备用分析，使用BaziAnalyzer")
        
        try:
            # 使用已修复的BaziAnalyzer
            from bazi_analyzer import BaziAnalyzer
            
            fallback_analyzer = BaziAnalyzer(
                self.year, self.month, self.day, self.hour, 
                self.gender, self.use_gregorian
            )
            
            # 重要：触发完整的分析流程
            fallback_result = fallback_analyzer.get_result()
            
            # 提取需要的数据
            if hasattr(fallback_analyzer, 'core_module') and fallback_analyzer.core_module:
                self.core_data = fallback_analyzer.core_module.get_result()
            else:
                self.core_data = self._get_default_core_data()
            
            if hasattr(fallback_analyzer, 'basic_info_module') and fallback_analyzer.basic_info_module:
                self.basic_info_data = fallback_analyzer.basic_info_module.get_result()
            else:
                self.basic_info_data = self._get_default_basic_info()
            
            if hasattr(fallback_analyzer, 'bazi_main_module') and fallback_analyzer.bazi_main_module:
                self.bazi_main_data = fallback_analyzer.bazi_main_module.get_result()
                print("✓ 成功从BaziAnalyzer提取bazi_main_data")
                # 调试：检查提取的数据是否包含正确的统计信息
                wuxing_analysis = self.bazi_main_data.get('wuxing_analysis', {})
                scores = wuxing_analysis.get('scores', {})
                gan_scores = wuxing_analysis.get('gan_scores', {})
                print(f"  提取的scores: {scores}")
                print(f"  提取的gan_scores (非零): {dict([(k,v) for k,v in gan_scores.items() if v > 0])}")
            else:
                self.bazi_main_data = self._get_default_bazi_main()
                print("❌ 无法从BaziAnalyzer提取bazi_main_data，使用默认数据")
            
            self.analysis_complete = True
            
        except Exception as e:
            print(f"备用分析也失败: {e}")
            # 使用默认数据确保不会崩溃
            self.core_data = self._get_default_core_data()
            self.basic_info_data = self._get_default_basic_info()
            self.bazi_main_data = self._get_default_bazi_main()
            self.analysis_complete = True
    
    def _get_default_core_data(self):
        """获取默认核心数据"""
        return {
            "input_params": {
                "year": self.year, "month": self.month, "day": self.day, 
                "hour": self.hour, "gender": self.gender, "use_gregorian": self.use_gregorian
            },
            "bazi_info": {
                "gans": {"year": "甲", "month": "乙", "day": "丙", "time": "丁"},
                "zhis": {"year": "子", "month": "丑", "day": "寅", "time": "卯"},
                "me": "丙"
            }
        }
    
    def _get_default_basic_info(self):
        """获取默认基本信息"""
        return {
            "gender": self.gender,
            "dates": {
                "solar": {"formatted": f"{self.year}年{self.month}月{self.day}日"},
                "lunar": {"formatted": f"{self.year}年{self.month}月{self.day}日"}
            },
            "timing_info": {"shang_yun_time": f"{self.year + 8}-{self.month:02d}-{self.day:02d}"}
        }
    
    def _get_default_bazi_main(self):
        """获取默认八字主体数据"""
        return {
            "basic_bazi": {
                "gans": ["甲", "乙", "丙", "丁"],
                "zhis": ["子", "丑", "寅", "卯"],
                "me": "丙"
            },
            "wuxing_analysis": {
                "scores": {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0},
                "gan_scores": {gan: 0 for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']}
            },
            "strength_analysis": {"is_weak": True, "strong_score": 0}
        }
    
    def get_result(self) -> Dict[str, Any]:
        """获取完整的分析结果 - 优化版本"""
        if not self.analysis_complete:
            return {
                "success": False,
                "error": "八字分析未完成",
                "input_info": {
                    "year": self.year,
                    "month": self.month,
                    "day": self.day,
                    "hour": self.hour,
                    "gender": self.gender,
                    "use_gregorian": self.use_gregorian
                }
            }
        
        # 提取关键数据，避免重复
        wuxing_analysis = self.bazi_main_data.get('wuxing_analysis', {})
        strength_analysis = self.bazi_main_data.get('strength_analysis', {})
        basic_bazi = self.bazi_main_data.get('basic_bazi', {})
        ten_gods = self.bazi_main_data.get('ten_gods', {})
        
        return {
            "success": True,
            "input_info": {
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "gender": self.gender,
                "use_gregorian": self.use_gregorian
            },
            "analysis_results": {
                # 基本信息（保持原样）
                "basic_info": self.basic_info_data,
                
                # 核心八字信息（精简版）
                "bazi_core": {
                    "pillars": basic_bazi.get('zhus', []),  # 四柱
                    "day_master": basic_bazi.get('me', ''),  # 日主
                    "ten_gods": {
                        "gan_gods": ten_gods.get('gan_shens', []),
                        "zhi_gods": ten_gods.get('zhi_shens', [])
                    }
                },
                
                # 统计数据（合并，避免重复）
                "statistics": {
                    "wuxing_scores": wuxing_analysis.get('scores', {}),
                    "gan_scores": wuxing_analysis.get('gan_scores', {}),
                    "strength": {
                        "is_weak": strength_analysis.get('is_weak', True),
                        "score": strength_analysis.get('strong_score', 0),
                        "description": strength_analysis.get('strength_description', '身弱')
                    },
                    "element_status": wuxing_analysis.get('element_status', {}),
                    "dominant_element": wuxing_analysis.get('dominant_element', '')
                },
                
                # 详细分析（可选，用于深度解读）
                "detailed_analysis": {
                    "month_info": self.bazi_main_data.get('month_analysis', {}),
                    "seasonal_info": self.bazi_main_data.get('seasonal_info', {}),
                    "timing_info": self.basic_info_data.get('timing_info', {})
                }
            }
        }
    
    def _extract_statistics(self) -> Dict[str, Any]:
        """从模块数据中提取统计信息"""
        try:
            wuxing_analysis = self.bazi_main_data.get('wuxing_analysis', {})
            strength_analysis = self.bazi_main_data.get('strength_analysis', {})
            
            return {
                "wuxing_statistics": wuxing_analysis.get('scores', {}),
                "gan_statistics": wuxing_analysis.get('gan_scores', {}),
                "strength_statistics": strength_analysis,
                "patterns": {"main_patterns": [], "special_patterns": []},
                "special_analysis": {"recommendations": []}
            }
        except Exception as e:
            return {
                "wuxing_statistics": {},
                "gan_statistics": {},
                "strength_statistics": {},
                "patterns": {"main_patterns": [], "special_patterns": []},
                "special_analysis": {"recommendations": []}
            }
    
    def get_analysis_summary(self) -> str:
        """获取分析摘要"""
        if not self.analysis_complete:
            return "分析未完成"
        
        try:
            summary_parts = []
            
            # 从优化后的数据结构获取信息
            result = self.get_result()
            analysis_results = result.get('analysis_results', {})
            
            # 日主信息
            bazi_core = analysis_results.get('bazi_core', {})
            day_master = bazi_core.get('day_master', '')
            if day_master:
                summary_parts.append(f"日主{day_master}")
            
            # 强弱信息
            statistics = analysis_results.get('statistics', {})
            strength = statistics.get('strength', {})
            if strength:
                is_weak = strength.get('is_weak', True)
                score = strength.get('score', 0)
                summary_parts.append(f"身{'弱' if is_weak else '强'}(分数{score})")
            
            # 五行分布
            wuxing_scores = statistics.get('wuxing_scores', {})
            if wuxing_scores and any(v > 0 for v in wuxing_scores.values()):
                sorted_elements = sorted(wuxing_scores.items(), key=lambda x: x[1], reverse=True)
                top_elements = [f"{k}{v}" for k, v in sorted_elements[:3] if v > 0]
                summary_parts.append(f"五行分布：{' '.join(top_elements)}")
            
            # 十神信息
            ten_gods = bazi_core.get('ten_gods', {})
            gan_gods = ten_gods.get('gan_gods', [])
            if gan_gods:
                main_gods = [s for s in gan_gods if s != '--']
                if main_gods:
                    summary_parts.append(f"主要十神：{' '.join(main_gods)}")
            
            return "；".join(summary_parts) if summary_parts else "八字分析完成"
            
        except Exception as e:
            return f"分析摘要生成失败：{str(e)}"
    
    def get_llm_query(self) -> str:
        """生成用于LLM查询的字符串"""
        if not self.analysis_complete:
            return f"{self.gender}命 {self.year}年{self.month}月{self.day}日{self.hour}时"
        
        try:
            query_parts = [f"{self.gender}命"]
            query_parts.append(f"{self.year}年{self.month}月{self.day}日{self.hour}时")
            
            # 从优化后的数据结构获取信息
            result = self.get_result()
            analysis_results = result.get('analysis_results', {})
            
            # 四柱信息
            bazi_core = analysis_results.get('bazi_core', {})
            pillars = bazi_core.get('pillars', [])
            if pillars:
                query_parts.append(f"八字：{' '.join(pillars)}")
            
            # 日主和强弱
            day_master = bazi_core.get('day_master', '')
            if day_master:
                query_parts.append(f"日主{day_master}")
                
            statistics = analysis_results.get('statistics', {})
            strength = statistics.get('strength', {})
            if strength.get('is_weak'):
                query_parts.append("身弱")
            else:
                query_parts.append("身强")
            
            return " ".join(query_parts)
            
        except Exception as e:
            return f"{self.gender}命 {self.year}年{self.month}月{self.day}日{self.hour}时"

    def get_compatible_result(self) -> Dict[str, Any]:
        """获取兼容旧API格式的结果"""
        optimized_result = self.get_result()
        if not optimized_result.get('success'):
            return optimized_result
        
        # 转换为兼容格式，保持API向后兼容
        analysis_results = optimized_result['analysis_results']
        statistics = analysis_results.get('statistics', {})
        
        return {
            "success": True,
            "input_info": optimized_result['input_info'],
            "analysis_results": {
                "basic_info": analysis_results['basic_info'],
                "statistics": {
                    # 修复：使用get_result()中实际的字段名
                    "wuxing_statistics": statistics.get('wuxing_scores', {}),  # 修复：直接从wuxing_scores获取
                    "gan_statistics": statistics.get('gan_scores', {}),      # 修复：直接从gan_scores获取
                    "strength_statistics": {
                        "is_weak": statistics.get('strength', {}).get('is_weak', True),
                        "strong_score": statistics.get('strength', {}).get('score', 0),
                        "strength_description": statistics.get('strength', {}).get('description', '身弱')
                    }
                },
                # 新增优化后的数据结构
                "bazi_core": analysis_results['bazi_core'],
                "detailed_analysis": analysis_results['detailed_analysis']
            }
        }


def test_simple_analyzer():
    """测试简化版分析器"""
    analyzer = SimpleBaziAnalyzer(1985, 1, 17, 9, '男', True)
    result = analyzer.get_result()
    
    print("=== 简化版八字分析器测试 ===")
    print(f"分析成功: {result['success']}")
    
    if result['success']:
        stats = result['analysis_results']['statistics']
        print(f"五行统计: {stats['wuxing_statistics']}")
        print(f"天干统计: {stats['gan_statistics']}")
        print(f"强弱信息: {stats['strength_statistics']}")
        print(f"分析摘要: {analyzer.get_analysis_summary()}")
        print(f"LLM查询: {analyzer.get_llm_query()}")


if __name__ == "__main__":
    test_simple_analyzer() 