from uuid import uuid4
from jhu.security import AESAPI, HashAPI, JWTAPI
from .settings import settings


jwt_api = JWTAPI(key=settings.jwt_key, expire_min=settings.jwt_expire_min)

hash_api = HashAPI()

# 用于处理客户端加密:比如加解密登录密码
client_aes_api = AESAPI(settings.aes_key_32)

# 用于处理服务内部加密:比如手机号的加解密
server_aes_api = AESAPI(settings.aes_key_16)


def phone_encrypt(plain_text: str) -> str:
    """加密手机号;手机号按照每3位组成一段密文,然后拼接而成;
    如:18012345678,分为 180,801,012,123,......678;  
    使用AES ECB模式加密,保障同样的明文输出同样的密文,用于手机号的模糊匹配

    Args:
        plain_text:手机号明文,例如:18012345678

    Return:
        str:加密后的手机号
    """
    length = len(plain_text)
    end_pos = max(length-3, 0)
    return ",".join([server_aes_api.encrypt(plain_text[i:i+3]) for i in range(end_pos+1)])


def phone_decrypy(encrypted_text: str, mask: bool = True) -> str:
    """解密手机号

    Args:
        encrypted_text:加密的手机号
        mask: 是否脱敏显示,比如180****5678

    Return:
        str:手机号明文
    """
    phone_array = [server_aes_api.decrypt(v)
                   for v in encrypted_text.split(",")]

    phone = "".join([phone_array[i][0] for i in range(8)]) + phone_array[-1]

    if mask:
        phone = f"{phone[:3]}****{phone[7:]}"
    return phone


def generate_uuid_str() -> str:
    return "".join(str(uuid4()).split("-"))
