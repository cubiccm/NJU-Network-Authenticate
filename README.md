# NJU-Network-Authenticate

登录南京大学校园网的脚本，支持验证码识别。

注：现时仍可使用原本的入口登录，只需

```shell
curl -d 'username=学号&password=统一身份认证密码' p.nju.edu.cn/portal_io/login
```

即可。

登录部分参考：https://github.com/forewing/nju-health-checkin

验证码部分（muggle-ocr）使用：https://github.com/kerlomz/captcha_trainer

## 用法

首先 clone 代码，安装 python3 环境，并安装必要依赖：

```shell
pip install -r requirements.txt
```

如果不需要验证码识别功能，则不需要保存 `muggle_ocr` 目录，也不需要安装多余的依赖，只需 `pip install -r requirements-no-captcha.txt`。

安装完成之后，执行

```shell
python3 login.py [username] [password]
```

并将 `username` 和 `password` 替换为统一认证的用户名和密码即可。

也可设置环境变量 `NJU_USERNAME` 和 `NJU_PASSWORD` 后直接执行 `python3 login.py`。

## 登出

```shell
curl "http://p.nju.edu.cn/api/portal/v1/logout" --data '{"domain":"default"}'
```

