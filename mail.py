from libs.log import i


def send_mail(recipients: list, title, content_txt: str = None, content_html=None):
    from config import app
    if app.config['SEND_MAIL']:
        print('DEBUG状态，邮件被禁止发送了 \r\n \t%s \r\n \t%s \r\n \t%s' % (
            recipients, title, content_txt if content_html is None else content_html))
        return
    from flask_mail import Message
    from config import mail

    msg = Message(title, sender=('oneself - service', app.config['MAIL_USERNAME']), recipients=recipients)
    msg.body = content_txt
    msg.html = content_html
    try:
        mail.send(msg)
    except Exception:
        try:
            with app.app_context():
                mail.send(msg)
        except Exception as e:
            import traceback
            i('邮件发送失败%s' % traceback.format_exc())
