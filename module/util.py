# 比较2个时间数组的大小
# 数组格式为：[小时，分钟，秒]
# 如果第一个数组大于等于第二个数组，返回True，否则返回False
def compare_time(time1, time2):
    if time1[0] > time2[0]:
        return True
    if time1[0] == time2[0]:
        if time1[1] > time2[1]:
            return True
        if time1[1] == time2[1] and time1[2] >= time2[2]:
            return True
    return False
