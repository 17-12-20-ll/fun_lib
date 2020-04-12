from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


def send_mail(to, msg='', sequence=''):
    try:
        host_server = 'smtp.126.com'
        # sender_qq为发件人的邮126箱
        sender_qq = 'chongyan_ll@126.com'
        # pwd为126邮箱的授权码
        pwd = 'll11075215'
        # 发件人的邮箱
        sender_qq_mail = 'chongyan_ll@126.com'
        # 收件人邮箱
        receiver = to
        # 邮件的正文内容
        if sequence:
            mail_content = f"""
            <html>
                <body>
                    <h1>开心图书馆</h1>
                    <h3><font color="red">密码30分钟找回有效，请尽快点击下面链接</font></h3>
                    <a href="http://localhost:8080/resetpwd?s={sequence}">http://localhost:8080/resetpwd?s={sequence}</a>
                </body>
            </html>
            """
        else:
            mail_content = f"""
                        <html>
                            <body>
                                <h1>开心图书馆</h1>
                                <h3><font color="red">{msg}</font></h3>
                            </body>
                        </html>
             """
        # 邮件标题
        mail_title = '开心图书馆'
        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(0)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)
        msg = MIMEText(mail_content, _subtype="html", _charset='utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = receiver
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    if send_mail('1096195574@qq.com', 'aaaaaaaaaaaaa'):
        print("发送成功")
    else:
        print("发送失败")
