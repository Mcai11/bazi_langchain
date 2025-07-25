import sys
import io
import re
import subprocess
import json
print("bazi_json.py loaded")

# 用 subprocess 调用 bazi.py，捕获 print 输出

def run_bazi_py(args):
    import locale
    cmd = [sys.executable, 'bazi.py'] + [str(a) for a in args]
    # 不指定 encoding，先拿 bytes
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 尝试 utf-8 解码，失败则用 gbk
    try:
        out = result.stdout.decode('utf-8')
    except UnicodeDecodeError:
        try:
            out = result.stdout.decode('gbk')
        except Exception:
            # 最后尝试本地默认编码
            out = result.stdout.decode(locale.getpreferredencoding(), errors='replace')
    return out

# 分块结构化

def parse_bazi_output(text):
    import re
    # 只用连续10个及以上的 = 或 - 作为分块分隔符
    blocks = re.split(r'(?:=|-){10,}', text)
    blocks = [b.strip() for b in blocks if b.strip()]
    filtered_blocks = []
    for block in blocks:
        if block.startswith('你属:') and '建议参见' in block:
            continue
        filtered_blocks.append(block)
    blocks = filtered_blocks
    skip = False
    final_blocks = []
    for block in blocks:
        if False:  # 古籍引用已移除
            skip = True
        if skip and ('大运' in block or re.match(r'^\d+\s+[甲乙丙丁戊己庚辛壬癸]', block)):
            skip = False
        if not skip:
            final_blocks.append(block)
    blocks = final_blocks
    keys = [
        "base_info", "bazi_main", "detail", "detailed_info", "dayun_table", "analysis", "tiangan", "personality", "liunian_table"
    ]
    result = {}
    bazi_main_raw = ""
    for idx, block in enumerate(blocks):
        if idx < len(keys) - 1:
            if keys[idx] == "bazi_main":
                bazi_main_raw = block.strip()
            else:
                result[keys[idx]] = block.strip()
        else:
            if keys[-1] == "bazi_main":
                bazi_main_raw = block.strip()
            else:
                if keys[-1] not in result:
                    result[keys[-1]] = block.strip()
                else:
                    result[keys[-1]] += "\n" + block.strip()
    # 进一步结构化 bazi_main
    bazi_main_lines = [line for line in bazi_main_raw.splitlines() if line.strip()]
    # 清理无效内容
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    bazi_main_lines = [ansi_escape.sub('', line) for line in bazi_main_lines]
    # 只去除“解读:钉ding或v信pythontesting:”及其后内容，保留前面内容
    bazi_main_lines = [re.sub(r'解读:钉ding或v信pythontesting:', '', line) for line in bazi_main_lines]
    bazi_main = {}
    if len(bazi_main_lines) >= 2:
        # 第一行为天干主行，第二行为地支主行
        gans_line = bazi_main_lines[0]
        zhis_line = bazi_main_lines[1]
        # 按2个及以上空格或tab分割
        gans_cols = re.split(r'\s{2,}|\t', gans_line.strip())
        zhis_cols = re.split(r'\s{2,}|\t', zhis_line.strip())
        bazi_main['gans'] = gans_cols[0].split() if gans_cols else []
        bazi_main['gans_extra'] = gans_cols[1:] if len(gans_cols) > 1 else []
        bazi_main['zhis'] = zhis_cols[0].split() if zhis_cols else []
        bazi_main['zhis_extra'] = zhis_cols[1:] if len(zhis_cols) > 1 else []
        # 其余行可按需扩展
    else:
        bazi_main['raw'] = '\n'.join(bazi_main_lines)
    result["bazi_main"] = bazi_main
    # 结构化 dayun_table
    def parse_dayun_table(table_raw):
        table = {}
        for line in table_raw.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r'^(\d+)\s+(.+)$', line)
            if m:
                age = m.group(1)
                detail = m.group(2).strip()
                table[age] = detail
        return table
    # dayun_table内容进一步分割
    def split_dayun_detail_by_index(detail):
        idx1 = 9
        idx2 = 19
        idx3 = 37
        part1 = detail[:idx1+1]
        part2 = detail[idx1+1:idx2+1]
        part3 = detail[idx2+1:idx3+1]
        part4 = detail[idx3+1:]
        return [part1.strip(), part2.strip(), part3.strip(), part4.strip()]
    if "dayun_table" in result:
        dayun_table = parse_dayun_table(result["dayun_table"])
        # 进一步分割每个大运内容
        for k, v in dayun_table.items():
            if isinstance(v, str):
                parts = split_dayun_detail_by_index(v)
                while len(parts) < 4:
                    parts.append("")
                dayun_table[k] = parts[:4]
        result["dayun_table"] = dayun_table
    def parse_liunian_table(table_raw):
        table = {}
        for line in table_raw.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r'^(\d+)\s+(\d{4}|[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+(.*)$', line)
            if m:
                age = int(m.group(1))
                year = m.group(2)
                detail = m.group(3).strip()
                table[year] = [age, detail]
            else:
                m2 = re.match(r'^(\d+)\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+(.*)$', line)
                if m2:
                    age = int(m2.group(1))
                    year = m2.group(2)
                    detail = m2.group(3).strip()
                    table[year] = [age, detail]
                else:
                    m3 = re.match(r'^\s*(\d+)\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+(.*)$', line)
                    if m3:
                        age = int(m3.group(1))
                        year = m3.group(2)
                        detail = m3.group(3).strip()
                        table[year] = [age, detail]
        return table
    if "liunian_table" in result:
        # 先结构化
        liunian_table = parse_liunian_table(result["liunian_table"])
        # 只保留key为纯数字的项
        liunian_table = {k: v for k, v in liunian_table.items() if str(k).isdigit()}
        # 进一步细分每个年份的内容（定长index分割）
        def split_liunian_detail_by_index(detail):
            # 固定分割点
            idx1 = 9   # 第一段0-9（共10个字符）
            idx2 = 19  # 第二段9-19（共10个字符）
            idx3 = 37  # 第三段19-37（共18个字符）
            part1 = detail[:idx1+1]
            part2 = detail[idx1+1:idx2+1]
            part3 = detail[idx2+1:idx3+1]
            part4 = detail[idx3+1:]
            return [part1.strip(), part2.strip(), part3.strip(), part4.strip()]
        for year, value in liunian_table.items():
            if isinstance(value, list) and len(value) == 2:
                age, detail = value
                parts = split_liunian_detail_by_index(detail)
                while len(parts) < 4:
                    parts.append("")
                liunian_table[year] = [str(age)] + parts[:4]
        result["liunian_table"] = liunian_table
    # personality: 古籍引用已移除，使用其他分块
    personality = ""
    for i, block in enumerate(blocks):
        if False and i > 0:  # 古籍引用已移除
            personality = blocks[i-1]
            break
    if personality:
        result["personality"] = personality
    # 确保所有主板块都存在
    for k in keys:
        if k not in result:
            result[k] = {} if k == "bazi_main" else ""
    
    # 新增：提取 detail_columns
    # 1. 解析表头
    detail = result.get("detail", "")
    detailed_info = result.get("detailed_info", "")
    headers = re.findall(r'【[^】]+】[^\s]+', detail)
    # 2. 去除ANSI颜色码
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    clean = ansi_escape.sub('', detailed_info)
    # 3. 按行分割
    lines = clean.splitlines()
    # 4. 每行分4列（用2个及以上全角空格分割）
    columns = [[] for _ in range(4)]
    for line in lines:
        parts = re.split(r'　{2,}', line)
        while len(parts) < 4:
            parts.append('')
        for i in range(4):
            columns[i].append(parts[i].strip())
    # 5. 组装为dict
    detail_columns = {}
    for i, header in enumerate(headers):
        detail_columns[header] = [item for item in columns[i] if item]
    result["detail_columns"] = detail_columns
    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='结构化八字输出')
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    parser.add_argument('day', type=int)
    parser.add_argument('hour', type=int)
    parser.add_argument('-n', '--female', action='store_true', help='女命')
    parser.add_argument('-g', '--gregorian', action='store_true', help='公历')
    parser.add_argument('-r', '--leap', action='store_true', help='闰月')
    args = parser.parse_args()
    # 构造参数
    bazi_args = [args.year, args.month, args.day, args.hour]
    if args.female:
        bazi_args.append('-n')
    if args.gregorian:
        bazi_args.append('-g')
    if args.leap:
        bazi_args.append('-r')
    text = run_bazi_py(bazi_args)
    result = parse_bazi_output(text)
    # 只保留指定key
    keys_to_keep = [
        "base_info", "bazi_main", "detail_columns", "dayun_table", "tiangan", "personality", "liunian_table"
    ]
    filtered_result = {k: result[k] for k in keys_to_keep if k in result}

    # 对 tiangan 和 personality 字段进行分割和清洗
    for key in ["tiangan", "personality"]:
        if key in filtered_result and isinstance(filtered_result[key], str):
            # 按换行符分割
            items = re.split(r'[\r\n]+', filtered_result[key])
            # 去除空项和仅为分隔符的项和“大运”
            items = [item.strip() for item in items if item.strip() and item.strip() != "大运"]
            filtered_result[key] = items

    print(json.dumps(filtered_result, ensure_ascii=False, indent=2))
    # 新增：写入文件
    with open('bazi_result.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_result, f, ensure_ascii=False, indent=2) 