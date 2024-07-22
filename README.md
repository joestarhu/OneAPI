# OneAPI
> OneAPI是基于Python的Web框架:FastAPI开发的一个统一用户中心的服务。OneAPI作为平台方，旨在提供一套全局统一且通用的用户体系，帮助业务系统或应用减少开发相关的底层用户体系，并在业务形态上支持toB,toC,toBtoB,toBtoC的平台化服务。

# 账号
> 账号是OneAPI的基础数据，用户在多系统(※接入OneAPI的)之间，可通过账号信息来打通相关的业务数据
- 账户ID，手机号是唯一标识；其中，三方登录的时候，可通过手机号来关联到一个账号上

```mermaid
erDiagram
a["账号信息"]{
	id bigint pk "账号ID"
	account str(128) uk "用户账号,全局唯一"
	phone str(256) uk "用户手机号,全局唯一"
	nick_name str(128) "用户昵称"
	status smallint "状态 0:停用,1:启用"
	deleted smallint "逻辑删除标志 0:未删除 1:已删除"
}

b["账号认证信息"]{
	id bigint pk "ID"
	account_id bigint fk "账号ID"
	auth_type int "认证类型"
	auth_identify str(256) "认证类型标识"
	auth_value str(256) "认证类型值"
}

a || -- |{b : "一个账号可拥有多种认证方式"
```

