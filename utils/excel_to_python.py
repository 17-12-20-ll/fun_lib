from xlrd import open_workbook  # xlrd用于读取xld
import datetime as dt

__s_date = dt.date(1899, 12, 31).toordinal() - 1


def getdate(date):
    if isinstance(date, float):
        date = int(date)
    d = dt.date.fromordinal(__s_date + date)
    return d


def format_data(i):
    ret = {}
    ret['id'] = int(i[0])
    # ret['add_time'] = getdate(i[1]).isoformat()
    ret['add_time'] = i[1].split('.')[0]
    ret['name'] = i[2]
    ret['desc'] = i[3]
    ret['pos'] = i[4]
    ret['url'] = i[5]
    ret['username'] = i[6]
    ret['pwd'] = i[7]
    ret['username_field'] = i[8]
    ret['pwd_field'] = i[9]
    ret['two_src_id'] = int(i[10])
    return ret


workbook = open_workbook(r'./13.xls')  # 打开xls文件
sheet_name = workbook.sheet_names()  # 打印所有sheet名称，是个列表
sheet1 = workbook.sheet_by_name('Sheet1')  # 根据sheet名称读取sheet中的所有内容
# print(sheet1._cell_values)
# print(getdate(sheet1._cell_values[5][1]))  # sheet的名称、行数、列数
L = [format_data(j) for i, j in enumerate(sheet1._cell_values) if i > 0]
print(L)
# for i in List:
#     res.setdefault(i['one_src_id'], []).append(i)
