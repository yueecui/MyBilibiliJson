def calc_side_height(heights):
    max_height = heights[-1]
    left = 0
    start = False
    result = []

    for i in range(len(heights) - 1):
        h = heights[i]
        if h == 0 and not start:
            result.append(0)
            continue
        else:
            start = True
        if h > left:
            result.append(0)
            left = h
            continue
        if h <= left:
            result.append(min(left, max_height) - h)
            continue

    return result


def calc_mid_height(heights):
    if len(heights) <= 2:
        assert len(heights) == 1 or heights[0] == heights[1]
        return [0] * len(heights)

    max_height = heights[0]
    result = [0]
    for i in range(1, len(heights) - 1):
        h = heights[i]
        result.append(max_height - h)
    result.append(0)
    return result


def execute():
    questions = [
        [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
        [4, 2, 0, 3, 2, 5],
        [4, 2, 6, 2, 4, 6, 3, 8, 2, 3, 5, 8, 2, 5],
    ]

    for q in questions:
        max_height = max(q)
        left_max_index = q.index(max_height)
        right_max_index = len(q) - q[::-1].index(max_height) - 1

        total_result = []
        total_result.extend(calc_side_height(q[:left_max_index + 1]))
        total_result.extend(calc_mid_height(q[left_max_index:right_max_index + 1]))
        total_result.extend(calc_side_height(q[right_max_index:][::-1])[::-1])

        print('Q:', q)
        print('A:', total_result, 'Total:', sum(total_result))
        print('')


if __name__ == '__main__':
    execute()
