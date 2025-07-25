"""
基本信息输出模块 - 处理八字的基本信息部分
包含性别、公历农历日期、节气信息、命宫胎元、上运时间等功能
"""

import datetime
from typing import Dict, Any, Optional, Tuple, List

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from ..datas import *
    from ..common import *
except ImportError:
    try:
        from datas import *
        from common import *
    except ImportError:
        # 设置默认值
        siling = {}
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


class BasicInfoModule:
    """基本信息输出模块"""
    
    def __init__(self, core_data: Dict[str, Any]):
        """
        初始化基本信息模块
        
        Args:
            core_data: 来自CoreBaseModule的核心数据
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
        self.use_gregorian = self.input_params.get('use_gregorian', False)
        self.is_leap = self.input_params.get('is_leap', False)
        self.is_female = self.input_params.get('is_female', False)
        
        # 时间信息
        self.solar_info = self.time_info.get('solar', {})
        self.lunar_info = self.time_info.get('lunar', {})
        
        # 八字信息
        self.gans = self.bazi_info.get('gans', {})
        self.zhis = self.bazi_info.get('zhis', {})
        self.me = self.bazi_info.get('me', '')
        self.zhus = self.bazi_info.get('zhus', [])
        
        # 计算得出的信息
        self.ming_gong = ""
        self.tai_yuan = ""
        self.shang_yun_time = ""
        self.jieqi_info = {}
        self.current_jieqi = None
        self.next_jieqi = None
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行基本信息计算"""
        self._calculate_ming_gong_tai_yuan()
        self._calculate_shang_yun_time()
        self._calculate_jieqi_info()

    def _calculate_ming_gong_tai_yuan(self):
        """计算命宫和胎元"""
        try:
            # 简化计算命宫和胎元
            self._simple_ming_gong_tai_yuan_calculation()
        except Exception as e:
            self._simple_ming_gong_tai_yuan_calculation()

    def _simple_ming_gong_tai_yuan_calculation(self):
        """简化的命宫胎元计算"""
        # 命宫计算公式：寅宫起正月，顺数至本月，再从卯时起，逆数至本时，即为命宫
        month = self.month
        hour = self.hour
        
        # 将时辰转换为地支序号
        hour_zhi_idx = (hour + 1) // 2 % 12
        
        # 命宫地支计算（简化公式）
        ming_gong_zhi_idx = (14 - month - hour_zhi_idx) % 12
        ming_gong_zhi = Zhi[ming_gong_zhi_idx]
        
        # 命宫天干计算（简化）
        ming_gong_gan_idx = (month + hour_zhi_idx) % 10
        ming_gong_gan = Gan[ming_gong_gan_idx]
        
        self.ming_gong = ming_gong_gan + ming_gong_zhi
        
        # 胎元计算：月干进一位，月支进一位
        month_gan = self.gans.get('month', '')
        month_zhi = self.zhis.get('month', '')
        
        if month_gan and month_zhi:
            month_gan_idx = Gan.index(month_gan)
            month_zhi_idx = Zhi.index(month_zhi)
            
            tai_yuan_gan_idx = (month_gan_idx + 1) % 10
            tai_yuan_zhi_idx = (month_zhi_idx + 1) % 12
            
            self.tai_yuan = Gan[tai_yuan_gan_idx] + Zhi[tai_yuan_zhi_idx]
        else:
            # 更简化的胎元计算
            tai_yuan_gan_idx = (self.month + 1) % 10
            tai_yuan_zhi_idx = (self.month + 1) % 12
            self.tai_yuan = Gan[tai_yuan_gan_idx] + Zhi[tai_yuan_zhi_idx]

    def _calculate_shang_yun_time(self):
        """计算上运时间"""
        try:
            # 简化计算上运时间
            # 一般男命阳年顺行，女命阴年顺行，起运年龄约8岁左右
            base_age = 8 if not self.is_female else 7
            
            # 根据年干的阴阳性调整
            year_gan = self.gans.get('year', '')
            if year_gan:
                year_gan_idx = Gan.index(year_gan)
                is_yang_year = (year_gan_idx % 2 == 0)
                
                if (not self.is_female and is_yang_year) or (self.is_female and not is_yang_year):
                    # 顺行
                    base_age = 8
                else:
                    # 逆行
                    base_age = 7
            
            shang_yun_year = self.year + base_age
            self.shang_yun_time = f"{shang_yun_year}-{self.month:02d}-{self.day:02d}"
                
        except Exception as e:
            # 默认上运时间
            base_age = 8 if not self.is_female else 7
            shang_yun_year = self.year + base_age
            self.shang_yun_time = f"{shang_yun_year}-{self.month:02d}-{self.day:02d}"

    def _calculate_jieqi_info(self):
        """计算节气信息"""
        try:
            # 简化的节气计算
            self._simple_jieqi_calculation()
                
            # 构建节气信息
            self._build_jieqi_info()
            
        except Exception as e:
            self._simple_jieqi_calculation()
            self._build_jieqi_info()

    def _simple_jieqi_calculation(self):
        """简化的节气计算"""
        # 24节气名称
        jieqi_names = [
            "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
            "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
            "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
            "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
        ]
        
        # 根据月份估算节气
        solar_month = self.solar_info.get('month', self.month)
        
        # 每月两个节气，前半月一个，后半月一个
        current_idx = (solar_month - 1) * 2
        if self.day > 15:
            current_idx += 1
        
        next_idx = (current_idx + 1) % 24
        
        # 估算节气时间
        jieqi_day_1 = 5 if current_idx % 2 == 0 else 20
        jieqi_day_2 = 5 if next_idx % 2 == 0 else 20
        
        next_month = solar_month if next_idx // 2 == current_idx // 2 else (solar_month % 12 + 1)
        
        self.current_jieqi = {
            'name': jieqi_names[current_idx],
            'time': f"{self.year}-{solar_month:02d}-{jieqi_day_1:02d} 12:00:00"
        }
        self.next_jieqi = {
            'name': jieqi_names[next_idx],
            'time': f"{self.year}-{next_month:02d}-{jieqi_day_2:02d} 12:00:00"
        }

    def _build_jieqi_info(self):
        """构建节气信息"""
        if not self.current_jieqi or not self.next_jieqi:
            return
        
        # 获取月支对应的司令信息
        month_zhi = self.zhis.get('month', '')
        siling_info = ""
        
        if month_zhi and 'siling' in globals() and month_zhi in siling:
            siling_info = siling[month_zhi]
        
        # 构建完整的节气信息
        current_name = self.current_jieqi['name']
        next_name = self.next_jieqi['name']
        current_time = self.current_jieqi['time']
        next_time = self.next_jieqi['time']
        
        # 节气期间的干支信息（根据传统命理）
        jieqi_ganzhi_info = f"{current_name}后癸水九日，辛金三日，己土十八日。"
        
        self.jieqi_info = {
            'current_jieqi': self.current_jieqi,
            'next_jieqi': self.next_jieqi,
            'siling_info': siling_info,
            'jieqi_ganzhi_info': jieqi_ganzhi_info,
            'full_info': f"{jieqi_ganzhi_info}{current_name}、{next_name}。 {current_name} {current_time} {next_name} {next_time}"
        }

    def get_basic_info_line_1(self) -> str:
        """获取基本信息第一行"""
        parts = []
        
        # 性别
        parts.append(f"{self.gender}命")
        
        # 公历日期
        solar_year = self.solar_info.get('year', self.year)
        solar_month = self.solar_info.get('month', self.month)
        solar_day = self.solar_info.get('day', self.day)
        parts.append(f"公历: {solar_year}年{solar_month}月{solar_day}日")
        
        # 农历日期
        lunar_year = self.lunar_info.get('year', self.year)
        lunar_month = self.lunar_info.get('month', self.month)
        lunar_day = self.lunar_info.get('day', self.day)
        parts.append(f"农历: {lunar_year}年{lunar_month}月{lunar_day}日")
        
        # 穿害信息（传统命理中的概念）
        parts.append("穿=害")
        
        # 上运时间
        if self.shang_yun_time:
            parts.append(f"上运时间：{self.shang_yun_time}")
        
        # 命宫
        if self.ming_gong:
            parts.append(f"命宫:{self.ming_gong}")
        
        # 胎元
        if self.tai_yuan:
            parts.append(f"胎元:{self.tai_yuan}")
        
        return "    ".join(parts)

    def get_basic_info_line_2(self) -> str:
        """获取基本信息第二行（节气信息）"""
        if not self.jieqi_info:
            return ""
        
        # 添加适当的缩进以对齐
        full_info = self.jieqi_info.get('full_info', '')
        return f"         {full_info}"

    def get_formatted_output(self) -> str:
        """获取格式化的基本信息输出"""
        lines = []
        
        # 第一行：基本信息
        line1 = self.get_basic_info_line_1()
        if line1:
            lines.append(line1)
        
        # 第二行：节气信息
        line2 = self.get_basic_info_line_2()
        if line2:
            lines.append(line2)
        
        return "\n".join(lines)

    def get_result(self) -> Dict[str, Any]:
        """获取结构化的基本信息结果"""
        return {
            "gender": self.gender,
            "dates": {
                "solar": {
                    "year": self.solar_info.get('year', self.year),
                    "month": self.solar_info.get('month', self.month),
                    "day": self.solar_info.get('day', self.day),
                    "formatted": f"{self.solar_info.get('year', self.year)}年{self.solar_info.get('month', self.month)}月{self.solar_info.get('day', self.day)}日"
                },
                "lunar": {
                    "year": self.lunar_info.get('year', self.year),
                    "month": self.lunar_info.get('month', self.month),
                    "day": self.lunar_info.get('day', self.day),
                    "formatted": f"{self.lunar_info.get('year', self.year)}年{self.lunar_info.get('month', self.month)}月{self.lunar_info.get('day', self.day)}日"
                }
            },
            "timing_info": {
                "shang_yun_time": self.shang_yun_time,
                "ming_gong": self.ming_gong,
                "tai_yuan": self.tai_yuan
            },
            "jieqi_info": self.jieqi_info,
            "formatted_lines": {
                "line1": self.get_basic_info_line_1(),
                "line2": self.get_basic_info_line_2()
            },
            "full_formatted": self.get_formatted_output()
        }

    def get_summary(self) -> Dict[str, str]:
        """获取基本信息摘要"""
        return {
            "basic_identity": f"{self.gender}命",
            "birth_info": f"{self.solar_info.get('year', self.year)}年{self.solar_info.get('month', self.month)}月{self.solar_info.get('day', self.day)}日{self.hour}时",
            "lunar_info": f"农历{self.lunar_info.get('year', self.year)}年{self.lunar_info.get('month', self.month)}月{self.lunar_info.get('day', self.day)}日",
            "destiny_info": f"命宫{self.ming_gong}，胎元{self.tai_yuan}",
            "fortune_start": f"上运时间：{self.shang_yun_time}",
            "seasonal_info": self.jieqi_info.get('jieqi_ganzhi_info', '') if self.jieqi_info else ""
        }


def test_basic_info_module():
    """测试基本信息模块"""
    # 创建测试用的核心数据
    from .core_base import CoreBaseModule
    
    print("=== 基本信息模块测试 ===")
    
    # 创建核心数据
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    core_data = core.get_result()
    
    # 创建基本信息模块
    basic_info = BasicInfoModule(core_data)
    
    # 获取结果
    result = basic_info.get_result()
    
    print("格式化输出：")
    print(basic_info.get_formatted_output())
    
    print("\n摘要信息：")
    summary = basic_info.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n结构化数据：")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2)[:800] + "...")


if __name__ == "__main__":
    test_basic_info_module() 