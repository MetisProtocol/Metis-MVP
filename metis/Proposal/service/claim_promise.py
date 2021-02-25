# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: claim_promise.py
@time: 2020/6/4 6:01 下午
@desc:
"""
import attr
import datetime
import logging
from flask_login import current_user
from itertools import chain
from metis.MetisExecption.MetisError import ValidationError, StopValidation, FirstClaimPromiseError, PersistenceError
from metis.CommonService.common_validators import ValidatorsMeta
from metis.SmartContract.contracts import MToken, MSC, TaskList
from metis.Proposal.model import Operation
from metis.config.Const import ACCOUNT_START

logger = logging.getLogger('metis')


@attr.s(repr=True, cmp=False, hash=True, frozen=True)
class ClaimPromiseInfo:
    work_id = attr.ib()
    current_user_uid = attr.ib()
    current_user_eth = attr.ib()
    publisher_uid = attr.ib()
    publisher_eth = attr.ib()
    balance = attr.ib()
    excitation = attr.ib()


class FirstClaimPromiseValidator(ValidatorsMeta):
    """
    验证是否是首次与对方合作，即便以前有合作关系，合作关系解除也看作是首次合作
    抛出一个FirstClaimPromise Error前端显示，双方首次建立合作关系，进行保证金的质押，一般都是从接受者开始质押
    等待发布方质押保证金之后，任务开始进行
    """
    def __init__(self, msc_orm):
        self.msc_orm = msc_orm

    def validate(self, info):
        """
        查找msc表，看看双方是否建立了PROMISE类型的合约，并且合约没有退出，正在进行中
        如果合约已经退出，抛出FirstPromiseError 表示双方是首次进行合作，提示用户进行质押 ，然后开启该任务
        :param info:
        :return:
        """
        if self.msc_orm.is_first_claim_promise(info.current_user_uid):
            raise FirstClaimPromiseError("首次建立合作关系，质押保证金之后进行后续操作")


class ClaimPromiseBalanceValidator(ValidatorsMeta):
    """
    质押保证金时验证该用户的余额是否充足
    """

    def validate(self, info):
        if info.balance - 10 < 0:
            raise ValidationError('promise claim', '余额不足')


class ClaimPromiseService:
    """
    到这里，说明双方已经建立了合作关系，直接申领任务即可
    需要将之前发布方建立的激励质押合约从第三方变成双方的合约，或者申领方同这个第三方建立合作关系
    变成双方合约：
        1. 发布方和第三方退出合约，将质押的激励返还到各自账户
        2. 然后申领方同发布方直接建立关系，将刚才返还的token质押到新
    """

    def __init__(self, plugins, msc_orm, work_orm, db):
        self.plugins = plugins
        self.msc_orm = msc_orm
        self.work_orm = work_orm
        self.db = db

    def claim(self, info):
        try:
            # 验证信息是否通过（余额、工作、是否第一次合作）
            print("验证不知道什么鬼东西")
            self._validate_promise_claim(info)
            # 发布方和第三方退出合约并将质押激励返还
            print("验证信息是否通过（余额、工作、是否第一次合作）")
            self._discard_temporary_contract(info)
            print("--------------------------")
            # 发布方与申领方建立新的合约
            print("发布方与申领方建立新的合约")
            # msc表中增加新合约数据
            msc_addr = self._deploy_formal_msc(info)
            print("msc表中增加新合约数据")
            msc = self._store_formal_contract(info, msc_addr)
            # 更新work表状态 增加申领方
            print("更新work表状态 增加申领方")
            work = self._fresh_work_state(info)
            self._take_task(info)
            self._store([msc, work])
        except Exception:
            raise
        return msc

    def _validate_promise_claim(self, info):
        validators = self.plugins.hook.metis_proposal_gather_claim_promise_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _deploy_formal_msc(self, info):
        token = MToken()
        msc = MSC()
        msc_addr = msc.deploy_msc([info.current_user_eth, info.publisher_eth], 0)   # 建立双方的新合约
        token.transfer(msc_addr, info.excitation, info.publisher_eth)   # 发布方质押激励token激活新的双方合约
        token.transfer(msc_addr, 0, info.current_user_eth)  # 申领方质押0以激活该合约
        return msc_addr

    def _discard_temporary_contract(self, info):
        msc_record = self.msc_orm.get_temporary_by_work_id(info.work_id)
        msc = MSC()
        # publisher out 发布方退出合约
        print("111")
        msc.i_want_out(info.publisher_eth, msc_record.msc_addr)
        # temporary out 第三方退出合约
        print("222")
        msc.i_want_out(ACCOUNT_START, msc_record.msc_addr)
        # publisher withdraw 发布方撤出合约
        print("333")
        msc.withdraw(info.publisher_eth, msc_record.msc_addr, 1)
        # temporary withdraw 第三方撤出合约
        print("444")
        msc.withdraw(ACCOUNT_START, msc_record.msc_addr, 1)
        # 标记此记录无效
        msc_record.is_effective = 0
        msc_record.utime = datetime.datetime.now()
        msc_record.save()

    def _store_formal_contract(self, info, msc_addr):
        msc = self.msc_orm(
            msc_type="FORMAL",
            party_a=info.current_user_uid,
            work_id=info.work_id,  # uid
            msc_addr=msc_addr,
            party_b=info.publisher_uid  # uid
        )
        print("增加FORMAL=============")
        msc.msc_status = 1
        return msc

    def _take_task(self, info):
        print("第二次查询TASKLIST")
        task = TaskList()
        work = self.work_orm.get_work_by_work_id(info.work_id)
        Operation.create_operation(current_user.uid, '任务申领', '成功申领%s' % work.work_name, 'Successful claimed %s' % work.work_name)
        task_index = task.get_task_index(info.publisher_eth, work.work_describe)
        print(task_index, info.publisher_eth, info.current_user_eth)
        print("=============================")
        task.take_task(info.publisher_eth, task_index, info.current_user_eth, value=1)

    def _fresh_work_state(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        work.utime = datetime.datetime.now()
        work.work_status = 1
        work.participants = info.current_user_uid
        return work

    def _store(self, iterable):
        for item in iterable:
            try:
                self.db.session.add(item)
            except Exception:
                self.db.session.rollback()
                logger.error("Persistence error")
                raise PersistenceError
        self.db.session.commit()

    def post_process(self):
        pass





