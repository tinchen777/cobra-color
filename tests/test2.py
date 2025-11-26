

def split_by_offsets(s: str, A: int, B: int, direction: str = "left"):
    n = len(s)

    if direction == "left":
        # 第一个切点
        p1 = A
        # 第二个切点
        p2 = A + B
    elif direction == "right":
        # 从右计数
        p1 = n - A
        p2 = n - (A + B)
    else:
        raise ValueError("direction must be 'left' or 'right'")

    # 确保切点有序（从小到大）
    cut_points = sorted([p1, p2])

    # 去掉越界的切点
    cut_points = [p for p in cut_points if 0 < p < n]

    # 利用切点分割
    parts = []
    prev = 0
    for p in cut_points:
        parts.append(s[prev:p])
        prev = p
    parts.append(s[prev:])  # 最后一段

    return parts


a = "1234567890"

f = split_by_offsets(a, 1, 1, direction="right")

print(f)
