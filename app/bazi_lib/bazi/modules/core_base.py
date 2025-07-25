"""
核心基础模块 - 参数解析、时间转换、八字计算
"""

import collections
import datetime
from typing import Dict, Any, Optional, Tuple

try:
    from lunar_python import Lunar, Solar
except ImportError:
    Solar = None
    Lunar = None

try:
    from ..datas import *
    from ..bazi_core import *
except ImportError:
    try:
        from datas import *
        from bazi_core import *
    except ImportError:
        # 设置默认值
        Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# Named tuples
Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")


class CoreBaseModule:
    """核心基础模块"""
    
    def __init__(self, year: int, month: int, day: int, hour: int, 
                 gender: str = '男', use_gregorian: bool = False, 
                 is_leap: bool = False, use_bazi_input: bool = False):
        """
        初始化核心基础模块
        
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
        
        # 时间对象
        self.solar = None
        self.lunar = None
        self.ba = None
        
        # 八字信息
        self.gans = None
        self.zhis = None
        self.me = None  # 日主
        self.month_zhi = None
        self.zhus = None  # 四柱
        self.alls = None  # 所有干支
        
        # 执行计算
        self._calculate()

    def _calculate(self):
        """执行核心计算"""
        self._convert_time()
        self._get_bazi_info()

    def _convert_time(self):
        """时间转换"""
        try:
            if self.use_bazi_input:
                # 直接输入八字的情况
                self._handle_bazi_input()
            else:
                if Solar and Lunar:
                    try:
                        if self.use_gregorian:
                            self.solar = Solar.fromYmdHms(self.year, self.month, self.day, self.hour, 0, 0)
                            self.lunar = self.solar.getLunar()
                        else:
                            month_ = self.month * -1 if self.is_leap else self.month
                            self.lunar = Lunar.fromYmdHms(self.year, month_, self.day, self.hour, 0, 0)
                            self.solar = self.lunar.getSolar()
                        
                        # 确保lunar对象创建成功
                        if self.lunar is None:
                            raise Exception("lunar对象创建失败")
                            
                    except Exception as e:
                        print(f"lunar-python计算失败: {e}")
                        self._simple_time_conversion()
                else:
                    # lunar-python库不可用，使用简化处理
                    print("lunar-python库不可用，使用简化计算")
                    self._simple_time_conversion()
        except Exception as e:
            print(f"时间转换错误: {e}")
            self._simple_time_conversion()

    def _handle_bazi_input(self):
        """处理直接输入八字的情况"""
        # 这里需要特殊处理，目前简化为普通计算
        self._simple_time_conversion()

    def _simple_time_conversion(self):
        """简化的时间转换"""
        # 创建简化的时间对象
        class SimpleTime:
            def __init__(self, year, month, day):
                self.year = year
                self.month = month
                self.day = day
            
            def getYear(self): return self.year
            def getMonth(self): return self.month
            def getDay(self): return self.day

        if self.use_gregorian:
            self.solar = SimpleTime(self.year, self.month, self.day)
            # 简化的农历计算
            lunar_year = self.year - 1 if self.month <= 2 else self.year
            lunar_month = (self.month + 10) % 12 + 1
            lunar_day = self.day - 15 if self.day > 15 else self.day + 15
            self.lunar = SimpleTime(lunar_year, lunar_month, lunar_day)
        else:
            self.lunar = SimpleTime(self.year, self.month, self.day)
            # 简化的公历计算
            solar_year = self.year + 1 if self.month >= 11 else self.year
            solar_month = (self.month + 1) % 12 + 1
            solar_day = self.day + 20
            self.solar = SimpleTime(solar_year, solar_month, solar_day)

    def _get_bazi_info(self):
        """获取八字信息"""
        try:
            # 优先使用lunar_python的精确计算
            if (Solar and Lunar and self.lunar and 
                hasattr(self.lunar, 'getEightChar')):
                
                try:
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
                except Exception as e:
                    self._simple_bazi_calculation()
            else:
                self._simple_bazi_calculation()
            
            if self.gans and self.zhis:
                self.me = self.gans.day
                self.month_zhi = self.zhis.month
                self.alls = list(self.gans) + list(self.zhis)
                self.zhus = [f"{gan}{zhi}" for gan, zhi in zip(self.gans, self.zhis)]
                
        except Exception as e:
            self._simple_bazi_calculation()

    def _simple_bazi_calculation(self):
        """简化的八字计算"""
        # 年干支
        year_gan_idx = (self.year - 4) % 10
        year_zhi_idx = (self.year - 4) % 12
        
        # 月干支
        month_gan_idx = (year_gan_idx * 2 + self.month) % 10
        month_zhi_idx = (self.month - 1) % 12
        
        # 日干支（简化计算）
        days_since_epoch = (self.year - 1900) * 365 + self.month * 30 + self.day
        day_gan_idx = days_since_epoch % 10
        day_zhi_idx = days_since_epoch % 12
        
        # 时干支
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

    def get_result(self) -> Dict[str, Any]:
        """获取核心基础数据"""
        return {
            "input_params": {
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "gender": self.gender,
                "use_gregorian": self.use_gregorian,
                "is_leap": self.is_leap,
                "is_female": self.is_female
            },
            "time_info": {
                "solar": {
                    "year": self.solar.getYear() if self.solar else self.year,
                    "month": self.solar.getMonth() if self.solar else self.month,
                    "day": self.solar.getDay() if self.solar else self.day
                },
                "lunar": {
                    "year": self.lunar.getYear() if self.lunar else self.year,
                    "month": self.lunar.getMonth() if self.lunar else self.month,
                    "day": self.lunar.getDay() if self.lunar else self.day
                }
            },
            "bazi_info": {
                "gans": {
                    "year": self.gans.year if self.gans else "",
                    "month": self.gans.month if self.gans else "",
                    "day": self.gans.day if self.gans else "",
                    "time": self.gans.time if self.gans else ""
                },
                "zhis": {
                    "year": self.zhis.year if self.zhis else "",
                    "month": self.zhis.month if self.zhis else "",
                    "day": self.zhis.day if self.zhis else "",
                    "time": self.zhis.time if self.zhis else ""
                },
                "me": self.me,
                "month_zhi": self.month_zhi,
                "zhus": [f"{gan}{zhi}" for gan, zhi in self.zhus] if self.zhus else [],
                "alls": self.alls
            }
        }


def test_core_base():
    """测试核心基础模块"""
    core = CoreBaseModule(1985, 1, 17, 14, '男', use_gregorian=True)
    result = core.get_result()
    
    import json
    print("=== 核心基础模块测试 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_core_base() 