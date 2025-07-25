import re

def parse_bazi_output(text):
    # 只用连续10个及以上的 = 或 - 作为分块分隔符
    blocks = re.split(r'(?:=|-){10,}', text)
    blocks = [b.strip() for b in blocks if b.strip()]
    # section 列表
    sections = blocks[:]
    # 依次赋值到固定key
    keys = [
        "base_info", "bazi_main", "detail", "dayun_table", "analysis", "tiangan", "personality", "liunian_table"
    ]
    result = {k: blocks[i] if i < len(blocks) else "" for i, k in enumerate(keys)}
    result["sections"] = sections
    return result 