# 设置验证码的位数
import io
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from utils.tools import img_code_overdue_create

# 设置验证码距离
number = 4
# 生成验证码图片的高度和宽度，可以依据实际情况选择
size = (60, 28)
# 背景颜色，默认为白色
bgcolor = (250, 250, 250)
# 是否要加入干扰线
draw_line = True
# 加入干扰线条数的上下限
line_number = (5, 5)


# 获取使用加减乘除的方式的验证码
def gen_text():
    one_num = str(random.randint(1, 9))
    two_num = str(random.randint(1, 9))
    operation = random.choice(['+', '*'])
    # number是生成验证码的位数
    return one_num + operation + two_num


# 用来绘制干扰线
def gene_line(draw, width, height):
    linecolor = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
    begin = (random.randint(0, width), random.randint(0, height))
    end = (random.randint(0, width), random.randint(0, height))
    draw.line([begin, end], fill=linecolor)


def create_img(_time):
    fontcolor = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
    width, height = size
    text = gen_text()
    token = img_code_overdue_create(_time=_time, val=eval(text), ex=5 * 60)
    image = Image.new('RGBA', (width, height), bgcolor)
    font = ImageFont.truetype('static/fonts/sylfaen.ttf', size=30)
    draw = ImageDraw.Draw(image)
    font_width, font_height = font.getsize(text)
    draw.text(
        ((width - font_width) / number + random.randint(0, 15),
         (height - font_height) / number - random.randint(-3, 3)),
        text, font=font, fill=fontcolor)
    if draw_line:
        for _ in line_number:
            gene_line(draw, width, height)
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    del draw
    buf = io.BytesIO()
    image.save(buf, 'png')
    return buf.getvalue(), token
