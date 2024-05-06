from jhu.security import AESAPI, HashAPI, JWTAPI  # noqa
from jhu.auth import ThridAuth, AuthType  # noqa
from api.config.settings import settings  # noqa

# 用于服务端的加密
aes_api = AESAPI(settings.encrypt_key)
# 用于客户端和服务端的加密
client_aes_api = AESAPI(settings.hash_key)
# hash加密
hash_api = HashAPI()
# jwt加密
jwt_api = JWTAPI(settings.jwt_key, settings.jwt_expire_min)


class FieldSecurity:
    @staticmethod
    def phone_encrypt(plain_text: str) -> str:
        """加密手机号;手机号按照每3位组成一段密文,然后拼接而成;
        如:18012345678,分为 180,801,012,123,......678;  
        使用AES ECB模式加密,保障同样的明文输出同样的密文,用于手机号的模糊匹配

        Args:
            plain_text:手机号明文,例如:18012345678

        Return:
            str:加密后的手机号
        """

        phone_len = len(plain_text)
        if phone_len > 11:
            raise ValueError("手机号长度必须小于11位")
        end_pos = max(0, phone_len - 3)

        return ",".join([aes_api.encrypt(plain_text[i:i+3]) for i in range(end_pos+1)])

    @staticmethod
    def phone_decrypt(encrypted_text: str, mask: bool = True) -> str:
        """解密手机号

        Args:
            encrypted_text:加密的手机号
            mask: 是否脱敏显示,比如180****5678

        Return:
            str:手机号明文
        """
        phone_array = [aes_api.decrypt(v) for v in encrypted_text.split(",")]

        try:
            phone = "".join([phone_array[i][0]
                            for i in range(8)]) + phone_array[-1]
        except Exception as e:
            raise e

        if mask:
            return f"{phone[:3]}****{phone[7:]}"
        else:
            return phone
