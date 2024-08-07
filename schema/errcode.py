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
    NO_ERROR = ErrInfo(code=0, message="Succeed")

    # 统一用户中心的错误代码
    WRONG_ACCOUNT_PASSWD = ErrInfo(
        code=1001,
        message="Wrong Account or Password"
    )

    ACCOUNT_STATUS_DISABLE = ErrInfo(
        code=1002,
        message="Account Disable"
    )

    WRONG_ORG_ACCOUNT = ErrInfo(
        code=1003,
        message="Organization disable or Organization User disable"
    )

    PHONE_ALREADY_EXISTS = ErrInfo(
        code=1004,
        message="Phone already exists"
    )

    ACCOUNT_ALREADY_EXISTS = ErrInfo(
        code=1005,
        message="Account already exists"
    )

    SUPERADMIN_DINIED = ErrInfo(
        code=1006,
        message="Superadmin can't edit or delete"
    )
