"""
详细信息模块 - 处理八字的详细分析表格
包含年月日时详细信息、天干地支属性、藏干分析、关系分析等功能
既提供结构化JSON数据，也提供格式化表格输出
"""

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
        temps = {}
        nayins = {}
        relations = {}
        yinyang = lambda x: '+' if x in ['甲', '丙', '戊', '庚', '壬', '子', '寅', '辰', '午', '申', '戌'] else '-'
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 默认的温度数据
        temps = {
            '甲': 3, '乙': -4, '丙': 6, '丁': -4, '戊': 0, '己': 0,
            '庚': -6, '辛': -4, '壬': 0, '癸': -6,
            '子': 5, '丑': -4, '寅': 0, '卯': 0, '辰': -4, '巳': 0,
            '午': 0, '未': 0, '申': 0, '酉': 0, '戌': 0, '亥': 0
        }
        
        # 默认的纳音数据
        nayins = {}
        for gan in Gan:
            for zhi in Zhi:
                nayins[(gan, zhi)] = f"{gan}{zhi}纳音"
        
        # 默认的关系数据
        relations = {
            ('木', '土'): '↑', ('火', '金'): '↓', ('土', '水'): '→', 
            ('金', '木'): '←', ('水', '火'): '↕'
        }


class DetailInfoModule:
    """详细信息模块"""
    
    def __init__(self, core_data: Dict[str, Any], basic_info_data: Dict[str, Any], 
                 bazi_main_data: Dict[str, Any]):
        """
        初始化详细信息模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
            basic_info_data: 来自BasicInfoModule的基本信息数据
            bazi_main_data: 来自BaziMainModule的八字主体数据
        """
        # 从各模块数据中提取信息
        self.input_params = core_data.get('input_params', {})
        self.bazi_info = core_data.get('bazi_info', {})
        
        # 基本参数
        self.gender = self.input_params.get('gender', '男')
        self.is_female = self.input_params.get('is_female', False)
        
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
        
        # 十神信息
        if 'ten_gods' in bazi_main_data:
            ten_gods = bazi_main_data['ten_gods']
            self.gan_shens = ten_gods.get('gan_shens', [])
            self.zhi_shens = ten_gods.get('zhi_shens', [])
        else:
            self.gan_shens = bazi_main_data.get('gan_shens', [])
            self.zhi_shens = bazi_main_data.get('zhi_shens', [])
        
        # 详细分析结果
        self.pillar_details = []  # 年月日时柱详细信息
        self.gan_details = []     # 天干详细信息
        self.zhi_details = []     # 地支详细信息
        self.canggan_details = [] # 藏干详细信息
        self.relations_info = {}  # 关系信息
        self.nayin_info = []      # 纳音信息
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行详细信息计算"""
        self._analyze_pillar_details()
        self._analyze_gan_details()
        self._analyze_zhi_details()
        self._analyze_canggan_details()
        self._analyze_relations()
        self._analyze_nayin()

    def _analyze_pillar_details(self):
        """分析年月日时柱详细信息"""
        labels = ['年', '月', '日', '时']
        
        for i, (gan, zhi) in enumerate(zip(self.gans, self.zhis)):
            if not gan or not zhi:
                continue
                
            # 获取温度信息
            gan_temp = temps.get(gan, 0)
            zhi_temp = temps.get(zhi, 0)
            
            # 获取建禄信息
            jian_info = ""
            if i != 2 and self.me in ten_deities and gan in ten_deities[self.me]:
                # 非日柱且能查到十神关系时
                jian_info = "建" if ten_deities[self.me][gan] == '比' else ""
            
            # 获取合冲关系
            he_info = self._get_gan_zhi_he(gan, zhi)
            
            # 空亡信息
            empty_info = self._get_empty_info(i, zhi)
            
            pillar_detail = {
                'position': labels[i],
                'gan': gan,
                'zhi': zhi,
                'gan_temp': gan_temp,
                'zhi_temp': zhi_temp,
                'jian_info': jian_info,
                'he_info': he_info,
                'empty_info': empty_info,
                'formatted': f"【{labels[i]}】{gan_temp}:{zhi_temp}{jian_info}{he_info}{empty_info}"
            }
            
            self.pillar_details.append(pillar_detail)

    def _analyze_gan_details(self):
        """分析天干详细信息"""
        for i, gan in enumerate(self.gans):
            if not gan:
                continue
                
            # 阴阳性
            yin_yang = yinyang(gan)
            
            # 五行属性
            element = gan5.get(gan, '未知')
            
            # 十神
            shen = self.gan_shens[i] if i < len(self.gan_shens) else '--'
            
            # 特殊检查
            special_check = self._check_gan_special(gan, i)
            
            gan_detail = {
                'position': i,
                'gan': gan,
                'yin_yang': yin_yang,
                'element': element,
                'shen': shen,
                'special_check': special_check,
                'formatted': f"{gan}{yin_yang}{element}【{shen}】{special_check}"
            }
            
            self.gan_details.append(gan_detail)

    def _analyze_zhi_details(self):
        """分析地支详细信息"""
        for i, zhi in enumerate(self.zhis):
            if not zhi:
                continue
                
            # 阴阳性
            yin_yang = yinyang(zhi)
            
            # 主要十神（对各天干的关系）
            zhi_shens_to_gans = []
            if self.me in ten_deities:
                for gan in self.gans:
                    if gan and gan in ten_deities and zhi in ten_deities[gan]:
                        zhi_shens_to_gans.append(ten_deities[gan][zhi])
                    else:
                        zhi_shens_to_gans.append('--')
            
            # 对日主的十神
            main_shen = self.zhi_shens[i] if i < len(self.zhi_shens) else '--'
            
            # 空亡信息
            empty_info = self._get_empty_info(i, zhi)
            
            zhi_detail = {
                'position': i,
                'zhi': zhi,
                'yin_yang': yin_yang,
                'main_shen': main_shen,
                'shens_to_gans': zhi_shens_to_gans,
                'empty_info': empty_info,
                'formatted': f"{zhi}{yin_yang}{''.join(zhi_shens_to_gans)}【{main_shen}】{empty_info}"
            }
            
            self.zhi_details.append(zhi_detail)

    def _analyze_canggan_details(self):
        """分析地支藏干详细信息"""
        for i, zhi in enumerate(self.zhis):
            if not zhi or zhi not in zhi5:
                continue
            
            canggan_list = []
            for gan, score in zhi5[zhi].items():
                # 五行属性
                element = gan5.get(gan, '未知')
                
                # 十神
                shen = ten_deities[self.me][gan] if self.me in ten_deities and gan in ten_deities[self.me] else '--'
                
                canggan_item = {
                    'gan': gan,
                    'score': score,
                    'element': element,
                    'shen': shen,
                    'formatted': f"{gan}{element}{shen}"
                }
                canggan_list.append(canggan_item)
            
            canggan_detail = {
                'position': i,
                'zhi': zhi,
                'canggan_list': canggan_list,
                'formatted': '　'.join([item['formatted'] for item in canggan_list])
            }
            
            self.canggan_details.append(canggan_detail)

    def _analyze_relations(self):
        """分析各种关系"""
        # 合冲关系
        he_relations = []
        chong_relations = []
        
        # 刑害关系
        xing_relations = []
        hai_relations = []
        
        # 简化的关系分析
        for i, zhi1 in enumerate(self.zhis):
            for j, zhi2 in enumerate(self.zhis):
                if i >= j or not zhi1 or not zhi2:
                    continue
                
                # 六合关系
                if self._is_liu_he(zhi1, zhi2):
                    he_relations.append((i, j, zhi1, zhi2, '六合'))
                
                # 六冲关系
                if self._is_liu_chong(zhi1, zhi2):
                    chong_relations.append((i, j, zhi1, zhi2, '六冲'))
        
        self.relations_info = {
            'he_relations': he_relations,
            'chong_relations': chong_relations,
            'xing_relations': xing_relations,
            'hai_relations': hai_relations
        }

    def _analyze_nayin(self):
        """分析纳音信息"""
        for i, (gan, zhi) in enumerate(zip(self.gans, self.zhis)):
            if not gan or not zhi:
                continue
            
            # 纳音
            nayin = nayins.get((gan, zhi), f"{gan}{zhi}纳音")
            
            # 天干地支关系
            gan_element = gan5.get(gan, '未知')
            zhi_element = self._get_zhi_main_element(zhi)
            relation_symbol = relations.get((gan_element, zhi_element), '○')
            
            # 特殊标记
            special_marks = []
            
            # 劫杀标记（简化）
            if i == 3:  # 时柱
                special_marks.append('劫杀')
            
            # 元辰标记（简化）
            # 这里可以添加更复杂的元辰判断逻辑
            
            nayin_info = {
                'position': i,
                'gan': gan,
                'zhi': zhi,
                'nayin': nayin,
                'relation_symbol': relation_symbol,
                'special_marks': special_marks,
                'formatted': f"{relation_symbol}{nayin}" + ('－' + '－'.join(special_marks) if special_marks else '')
            }
            
            self.nayin_info.append(nayin_info)

    def _get_gan_zhi_he(self, gan: str, zhi: str) -> str:
        """获取干支合冲关系"""
        # 简化的合冲关系判断
        he_pairs = {
            ('甲', '己'): '合', ('乙', '庚'): '合', ('丙', '辛'): '合',
            ('丁', '壬'): '合', ('戊', '癸'): '合'
        }
        
        chong_pairs = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        
        result = ""
        
        # 检查天干合
        if (gan, zhi) in he_pairs.values() or (zhi, gan) in he_pairs.values():
            result += "合"
        
        # 检查地支冲
        if zhi in chong_pairs and chong_pairs[zhi] in self.zhis:
            result += "冲"
        
        return result

    def _get_empty_info(self, position: int, zhi: str) -> str:
        """获取空亡信息"""
        # 简化的空亡判断
        if position == 0:  # 年柱
            return "建空"
        elif position == 1:  # 月柱
            return "冠空"
        else:
            return ""

    def _check_gan_special(self, gan: str, position: int) -> str:
        """检查天干特殊情况"""
        # 简化的特殊检查
        if position == 2:  # 日主
            return ""
        elif gan == self.me:
            return "同"
        else:
            return ""

    def _get_zhi_main_element(self, zhi: str) -> str:
        """获取地支主要五行"""
        if zhi in zhi5:
            # 找到地支中分数最高的藏干
            main_gan = max(zhi5[zhi].keys(), key=lambda x: zhi5[zhi][x])
            return gan5.get(main_gan, '未知')
        return '未知'

    def _is_liu_he(self, zhi1: str, zhi2: str) -> bool:
        """判断是否为六合关系"""
        he_pairs = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]
        return (zhi1, zhi2) in he_pairs or (zhi2, zhi1) in he_pairs

    def _is_liu_chong(self, zhi1: str, zhi2: str) -> bool:
        """判断是否为六冲关系"""
        chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        return (zhi1, zhi2) in chong_pairs or (zhi2, zhi1) in chong_pairs

    def get_pillar_table_line(self) -> str:
        """获取年月日时表格行"""
        if len(self.pillar_details) < 4:
            return ""
        
        # 使用中文全角空格对齐
        formatted_parts = [detail['formatted'] for detail in self.pillar_details]
        return "{1:{0}^15s}{2:{0}^15s}{3:{0}^15s}{4:{0}^15s}".format(
            chr(12288), *formatted_parts
        )

    def get_gan_table_line(self) -> str:
        """获取天干详细表格行"""
        if len(self.gan_details) < 4:
            return ""
        
        formatted_parts = [detail['formatted'] for detail in self.gan_details]
        return "{1:{0}<15s}{2:{0}<15s}{3:{0}<15s}{4:{0}<15s}".format(
            chr(12288), *formatted_parts
        )

    def get_zhi_table_line(self) -> str:
        """获取地支详细表格行"""
        if len(self.zhi_details) < 4:
            return ""
        
        formatted_parts = [detail['formatted'] for detail in self.zhi_details]
        return "{1:{0}<15s}{2:{0}<15s}{3:{0}<15s}{4:{0}<15s}".format(
            chr(12288), *formatted_parts
        )

    def get_canggan_lines(self) -> List[str]:
        """获取藏干详细行"""
        lines = []
        for detail in self.canggan_details:
            if detail['formatted']:
                line = "{1:{0}<15s}".format(chr(12288), detail['formatted'])
                lines.append(line)
        return lines

    def get_nayin_line(self) -> str:
        """获取纳音行"""
        if len(self.nayin_info) < 4:
            return ""
        
        formatted_parts = [info['formatted'] for info in self.nayin_info]
        return "{1:{0}<15s}{2:{0}<15s}{3:{0}<15s}{4:{0}<15s}".format(
            chr(12288), *formatted_parts
        )

    def get_formatted_table(self) -> str:
        """获取完整的格式化表格"""
        lines = []
        
        # 分隔线
        lines.append("-" * 120)
        
        # 年月日时基本信息行
        pillar_line = self.get_pillar_table_line()
        if pillar_line:
            lines.append(pillar_line)
        
        # 分隔线
        lines.append("-" * 120)
        
        # 天干详细行
        gan_line = self.get_gan_table_line()
        if gan_line:
            lines.append(gan_line)
        
        # 地支详细行
        zhi_line = self.get_zhi_table_line()
        if zhi_line:
            lines.append(zhi_line)
        
        # 藏干详细行
        canggan_lines = self.get_canggan_lines()
        for line in canggan_lines:
            lines.append(line)
        
        # 纳音行
        nayin_line = self.get_nayin_line()
        if nayin_line:
            lines.append(nayin_line)
        
        return "\n".join(lines)

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的详细信息结果"""
        return {
            "pillar_details": self.pillar_details,
            "gan_details": self.gan_details,
            "zhi_details": self.zhi_details,
            "canggan_details": self.canggan_details,
            "relations_info": self.relations_info,
            "nayin_info": self.nayin_info,
            "formatted_table": self.get_formatted_table(),
            "table_lines": {
                "pillar_line": self.get_pillar_table_line(),
                "gan_line": self.get_gan_table_line(),
                "zhi_line": self.get_zhi_table_line(),
                "nayin_line": self.get_nayin_line()
            }
        }

    def get_summary(self) -> Dict[str, str]:
        """获取详细信息摘要"""
        return {
            "pillar_summary": f"年月日时柱：{len(self.pillar_details)}个柱位详细分析",
            "gan_summary": f"天干分析：{len(self.gan_details)}个天干的阴阳五行十神",
            "zhi_summary": f"地支分析：{len(self.zhi_details)}个地支的详细关系",
            "canggan_summary": f"藏干分析：{len(self.canggan_details)}个地支的藏干详情",
            "relations_summary": f"关系分析：合{len(self.relations_info.get('he_relations', []))}个，冲{len(self.relations_info.get('chong_relations', []))}个",
            "nayin_summary": f"纳音分析：{len(self.nayin_info)}个柱位的纳音五行"
        }

    def get_llm_friendly_data(self) -> Dict[str, Any]:
        """获取适合LLM处理的数据格式"""
        return {
            "structured_analysis": {
                "pillars": [
                    {
                        "position": detail['position'],
                        "ganzhi": f"{detail['gan']}{detail['zhi']}",
                        "temperatures": f"天干{detail['gan_temp']}，地支{detail['zhi_temp']}",
                        "relationships": detail['he_info'],
                        "special_notes": detail['jian_info'] + detail['empty_info']
                    }
                    for detail in self.pillar_details
                ],
                "heavenly_stems": [
                    {
                        "stem": detail['gan'],
                        "properties": f"{detail['yin_yang']}性{detail['element']}",
                        "deity": detail['shen'],
                        "special": detail['special_check']
                    }
                    for detail in self.gan_details
                ],
                "earthly_branches": [
                    {
                        "branch": detail['zhi'],
                        "properties": f"{detail['yin_yang']}性",
                        "main_deity": detail['main_shen'],
                        "relationships": detail['shens_to_gans'],
                        "empty_status": detail['empty_info']
                    }
                    for detail in self.zhi_details
                ],
                "hidden_stems": [
                    {
                        "branch": detail['zhi'],
                        "hidden_stems": [
                            f"{item['gan']}({item['element']}{item['shen']},{item['score']}分)"
                            for item in detail['canggan_list']
                        ]
                    }
                    for detail in self.canggan_details
                ]
            },
            "visual_table": self.get_formatted_table(),
            "key_relationships": {
                "harmonies": [f"{rel[2]}-{rel[3]}({rel[4]})" for rel in self.relations_info.get('he_relations', [])],
                "conflicts": [f"{rel[2]}-{rel[3]}({rel[4]})" for rel in self.relations_info.get('chong_relations', [])],
                "nayin_elements": [f"{info['gan']}{info['zhi']}:{info['nayin']}" for info in self.nayin_info]
            }
        }


def test_detail_info_module():
    """测试详细信息模块"""
    from .core_base import CoreBaseModule
    from .basic_info import BasicInfoModule
    from .bazi_main import BaziMainModule
    
    print("=== 详细信息模块测试 ===")
    
    # 创建依赖数据
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    core_data = core.get_result()
    
    basic_info = BasicInfoModule(core_data)
    basic_info_data = basic_info.get_result()
    
    bazi_main = BaziMainModule(core_data, basic_info_data)
    bazi_main_data = bazi_main.get_result()
    
    # 创建详细信息模块
    detail_info = DetailInfoModule(core_data, basic_info_data, bazi_main_data)
    
    # 获取结果
    result = detail_info.get_result()
    
    print("格式化表格：")
    print(result['formatted_table'])
    
    print("\n摘要信息：")
    summary = detail_info.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\nLLM友好数据样例：")
    llm_data = detail_info.get_llm_friendly_data()
    structured = llm_data['structured_analysis']
    print(f"  年月日时柱: {len(structured['pillars'])}个")
    print(f"  天干分析: {len(structured['heavenly_stems'])}个")
    print(f"  地支分析: {len(structured['earthly_branches'])}个")
    print(f"  藏干分析: {len(structured['hidden_stems'])}个")
    
    key_relations = llm_data['key_relationships']
    print(f"  关键关系: 合{len(key_relations['harmonies'])}个，冲{len(key_relations['conflicts'])}个")
    
    return result


if __name__ == "__main__":
    test_detail_info_module() 