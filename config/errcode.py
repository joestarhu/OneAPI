from dataclasses import dataclass


@dataclass
class ErrInfo:
    code: int = 0
    message: str = "Succeed"

    @property
    def value(self) -> dict:
        return dict(code=self.code, message=self.message)


class ErrCode:
    # 无错误,正常
    NO_ERROR = ErrInfo()

    # 账号已存在
    ACCOUNT_ALREADY_EXISTS = ErrInfo(1001, "Account already exists")
    # 手机号已存在
    PHONE_ALREADY_EXISTS = ErrInfo(1002, "Phone already exists")
    # 用户账号或密码错误
    WRONG_ACCOUNT_PASSWD = ErrInfo(1003, "Wrong account or password")
    # 用户状态被停用
    STATUS_DISBALE = ErrInfo(1004, "User status is disable")
