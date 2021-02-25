# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: claim_excitation.py
@time: 2020/6/4 10:37 上午
@desc:
"""
import datetime
import attr
from flask_login import current_user
from itertools import chain
from metis.config.Const import ACCOUNT_LAST
from metis.CommonService import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, PersistenceError, StopValidation, EthError
from metis.SmartContract.contracts import MSC, MToken, TaskList
from metis.Proposal.model import Operation


@attr.s(repr=True, cmp=False, hash=True, frozen=True)
class ClaimExcitationInfo:
    dac_id = attr.ib()
    work_id = attr.ib()
    current_user = attr.ib()    # uid
    excitation = attr.ib()  # view中需要重新查一次数据库再填入
    balance = attr.ib()
    user_eth = attr.ib()
    work_describe = attr.ib()


class WorkEffectiveValidator(ValidatorsMeta):

    def __init__(self, work):
        self.db = work

    def validate(self, info):
        print(info.work_id)
        print("=======================")
        print("=======================")
        print("=======================")
        if not self.db.is_effective(info.work_id):
            raise ValidationError("claim", "该工作无效")


class AdminRoleValidator(ValidatorsMeta):
    """
    验证提交数据的用户是否是dac管理员，只有管理员有权限质押激励
    """
    def __init__(self, dac):
        self.db = dac

    def validate(self, info):
        if not self.db.is_admin(info.dac_id, info.current_user):
            raise ValidationError("claim", "权限不足")


class BalanceValidator(ValidatorsMeta):
    """
    验证该用户余额是否足够激活该工作
    """

    def validate(self, info):
        if int(info.balance) - int(info.excitation) < 0:
            raise ValidationError("claim", '余额不足')


class ClaimExcitationService:

    def __init__(self, plugins, work_orm, msc_orm, db):
        self.plugins = plugins
        self.work_orm = work_orm
        self.msc_orm = msc_orm
        self.db = db

    def claim(self, info):
        try:
            # 验证信息
            self._validate_info(info)
            # 质押操作
            self._publish_work_to_block_chain(info)
            msc_addr = self._deploy_tmp_msc(info)
            # 数据库修改状态为已激活
            work = self._fresh_work_data(info)
            # 将数据写入MSCTable中
            msc = self._store_msc(info, msc_addr)
            # 将数据库数据保存
            self._persistence([work, msc])
            # self._persistence([work])
        except Exception:
            raise
        return

    def _validate_info(self, info):
        validators = self.plugins.hook.metis_proposal_gather_claim_excitation_validators()
        failures = list()

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _fresh_work_data(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        Operation.create_operation(current_user.uid, '工作激活', '激活%s' % work.work_name, 'Activate %s' % work.work_name)
        work.is_active = True
        work.utime = datetime.datetime.now()
        return work

    def _deploy_tmp_msc(self, info):
        # M Token合约 关于货币合约
        token = MToken()
        # 质押合约
        msc = MSC()
        # deploy msc
        msc_addr = msc.deploy_msc([info.user_eth, ACCOUNT_LAST], 0)
        # msc_addr 部署合约的地址
        # transfer excitation to this msc 将质押金从账户中扣出
        token.transfer(msc_addr, info.excitation, info.user_eth)
        # sys account active this contract 质押第三方
        token.transfer(msc_addr, 0, ACCOUNT_LAST, value=1)
        return msc_addr

    def _publish_work_to_block_chain(self, work_info):
        task = TaskList()
        task.web3.eth.defaultAccount = work_info.user_eth
        task.add_task(
            work_info.work_describe,
            50,
            work_info.excitation,
            "0x0000000000000000000000000000000000000000",
            work_info.user_eth,
        )
        print("添加到TASTLIST中")


    def _store_msc(self, info, msc_addr):
        # msc_type, party_a, party_b, work_id
        msc = self.msc_orm(
            msc_type="TEMPORARY",
            party_a=info.current_user,
            work_id=info.work_id,
            msc_addr=msc_addr,
            party_b="SYS",
        )
        return msc

    def _persistence(self, iterable):
        for item in iterable:
            try:
                self.db.session.add(item)
            except Exception:
                self.db.session.rollback()
                raise PersistenceError
        self.db.session.commit()



