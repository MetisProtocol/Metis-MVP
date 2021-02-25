# _*_ coding: utf-8 _*_

"""
@author: Liu
@file: email.py
@time: 2020/12/7 上午11:56
@desc:
"""
import os
from flask_mail import Message
from metis.extensions import mail
from flask import current_app
from threading import Thread
from metis.config.Const import MAIL_SENDER


def send_async_email(app, msg):
    with app.app_context():     # 使用上下文语境，否则会报错
        mail.send(msg)


class SendMail:
    # 通知质押邮件模板
    PLEDGE = '''
            <p>您发布的项目已被接收，请及时发送token（ps：本邮件由程序自动发送，请勿回复）</p>
            <p>&nbsp;</p>
            <table>
            <tbody>
            <tr>
            <td>msc合约地址：</td>
            <td><a href="{0}">{0}</a></td>
            </tr>
            <tr>
            <td>任务WIKI：</td>
            <td><a href="{1}">{1}</a></td>
            </tr>
             <tr>
            <td>任务地址：</td>
            <td><a href="{2}">{2}</a></td>
            </tr>
            </tbody>
            </table>
    '''

    # <tr>
    #             <td>任务价格：</td>
    #             <td><a href="{3}">{3}</a></td>
    #             </tr>

    PLEDGE_SERVICE = """
        <p>您好！(ps: 本邮件由程序自动发送，请勿回复)</p>
        <p>您的工作申请成功。请按照提案中的具体要求，按时提交交付物。</p><br />
        <p>工作说明WIKI地址：{0}</p>
        <p>工作提交时间：{1}</p>
        <p>工作提交地址：{2}</p><br />
        Metis Lab

    """
    # 通知审核邮件模板
    REVIEW_TASK = '''
            <p>您发布的项目已被提交，请及时审核（ps：本邮件由程序自动发送，请勿回复）</p>
            <p>&nbsp;</p>
            <table>
            <tbody>
            <tr>
            <td>项目说明WIKI：</td>
            <td><a href="{0}">{0}</a></td>
            </tr>
            <tr>
            <td>成果WIKI：</td>
            <td><a href="{1}">{1}</a></td>
            </tr>
            </tbody>
            </table>
    '''
    INVITE = '''
    <p>您好！</p>
    <p>谢谢您选择加入到Metis DAC。请点击下面的链接，完成注册。</p>
    <p>请注意，Metis DAC生成了您专属的以太坊钱包地址，这个地址仅供注册角色使用，不会牵扯到转账，请在下面的注册链接中填写。</p>
    <table>
            <tbody>
            <tr>
            <td>以太坊钱包地址：</td>
            <td><p>{0}</p></td>
            </tr>
            <tr>
            <td>角色：DAC成员</td>
            </tr>
            <tr>
            <td>注册链接：</td>
            <td><a href="http://mvp.metis.apple-store-signature.com/account/registerV2">http://mvp.metis.apple-store-signature.com/account/registerV2</a></td>
            </tr>
            <tr>
            <td>被邀请人邮箱：</td>
            <td><a href="{1}">{1}</a></td>
            </tbody>
            </table>
    <p>祝玩得愉快！</p>
    <p>Metis Lab</p>（ps：本邮件由程序自动发送，请勿回复）
    '''
    REGISTER = '''
        <p>Hi Gang,</p><br />
        <p>Congratulations and thank you for your registration! </p>
        <p>You are about to start the journey in a new decentralized world and create your first decentralized company. </p>
        <p>This is your private key <span>{0}</span>, please keep the private key in a safe place for account restoration,</p><br />

        <p>Thank you and Happy Collaborations!</p><br />
        <p>Metis Lab</p>


    '''
    ARBITRATION = """
        <p>您好！（ps：本邮件由程序自动发送，请勿回复）</p>
        <p>用户{}申请仲裁，需要仲裁的提案wiki地址是：{}</p>
    """
    TEMP_DCT = {
        "pledge": PLEDGE,
        "pledge_service": PLEDGE_SERVICE,
        "review": REVIEW_TASK,
        "register": REGISTER,
        'invite': INVITE,
        "arbitration": ARBITRATION
    }

    def __init__(self, recipients: list, template_type: str):
        """
        :param recipients:
        :param template_type:  pledge（质押） | review（审核）
        """
        self.recipients = recipients
        self.template_type = template_type
        self.frm = MAIL_SENDER      # 需要固定，config配置固定的

    def send(self, *args):
        template = self.__class__.TEMP_DCT.get(self.template_type)
        msg = Message('Metis通知邮件', sender=self.frm, recipients=self.recipients)
        # if self.template_type == 'register':  # 如果是注册邮件，需要发送一个附件
        #     with current_app.open_resource(os.path.dirname(os.path.abspath(__file__)) + "/manual.pdf") as f:
        #         msg.attach('用户手册(首次安装引导).pdf', current_app.config['MIME_TYPE']['.pdf'], f.read())
        msg.html = template.format(*args)
        thread = Thread(target=send_async_email, args=(current_app._get_current_object(), msg))
        thread.start()