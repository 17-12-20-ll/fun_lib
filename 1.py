import re

a = '★VIP4高级大客户专用包年 3000元【专享端口，高权限，高速，稳定】'
b = 'VIP3会员包月 100元【Reaxys、药典、中英文等，无发票】'

print(re.findall(r'(VIAA.*?\d)', b))
print(None.strip())
