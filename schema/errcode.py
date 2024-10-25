from dataclasses import dataclass


@dataclass
class ErrInfo:
    code: int
    message: str

    @property
    def value(self) -> dict:
        return dict(code=self.code, message=self.message)


@dataclass
class APIErrors:
    NO_ERROR = ErrInfo(code=0, message="成功")

    # 登录业务
    LOGIN_WRONG_ACCOUNT_PASSWD = ErrInfo(
        code=1001,
        message="抱歉,您输入的账号或密码不正确"
    )
    LOGIN_ACCOUNT_STATUS_DISABLE = ErrInfo(
        code=1002,
        message="抱歉,您的账号处于停用状态"
    )
    LOGIN_ORG_DINED = ErrInfo(
        code=1003,
        message="抱歉,您无权进入该组织"
    )

    # 账号业务
    USER_ACCOUNT_ALREADY_EXISTS = ErrInfo(
        code=2001,
        message="账号已存在"
    )
    USER_PHONE_ALREADY_EXISTS = ErrInfo(
        code=2002,
        message="手机号已存在"
    )
    USER_ADMIN_CTRL_DINED = ErrInfo(
        code=2003,
        message="超级管理员账号不允许修改或删除"
    )
    USER_ORG_OWN_DELETE_DINED = ErrInfo(
        code=2004,
        message="组织的所有者不允许删除"
    )

    # 组织业务
    ORG_NAME_ALREADY_EXISTS = ErrInfo(
        code=3001,
        message="组织名称已存在"
    )
    ORG_ADMIN_CTRL_DINED = ErrInfo(
        code=3002,
        message="平台组织不允许修改或删除"
    )
    ORG_OWNER_NOT_AVAIABLE = ErrInfo(
        code=3003,
        message="无效组织所有者,账号不存在或状态异常"
    )
