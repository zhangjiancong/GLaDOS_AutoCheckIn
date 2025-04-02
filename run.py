import sys
import requests
import json
import time
import traceback
import os

# 程序版本
VERSION = "2.1"
config = {}
runtime = ""


def api_check_in(host, cookie):
    check_in_url = f"{host}/api/user/checkin"
    referer_url = f"{host}/console/checkin"
    payload = {"token": "glados.one"}
    with requests.post(
        check_in_url,
        headers={
            "authority": "glados.rocks",
            "accept": "application/json, text/plain, */*",
            "dnt": "1",
            "cookie": cookie,
            "referer": referer_url,
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "origin": host,
            "user-agent": "Not A;Brand;v=99, Chromium;v=102, Google Chrome;v=102",
            "content-type": "application/json;charset=UTF-8",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        data=json.dumps(payload),
    ) as r:
        if r.status_code == 200:
            res = r.json()
            try:
                if res["message"] == "没有权限":
                    ding_send(
                        {"uid": "未知", "state": f"✘ cookie填写有误", "days": "-"}
                    )
                    return False
                if res["message"] == "oops, token error":
                    ding_send(
                        {
                            "uid": "未知",
                            "state": f"✘ token异常,请联系程序作者更新token",
                            "days": "-",
                        }
                    )
                    return False
                if res["message"].startswith("Checkin!"):
                    ding_send(
                        {
                            "uid": res["list"][0]["user_id"],
                            "state": f"√ 成功 获得{res['points']}点",
                            "days": int(float(res["list"][0]["balance"])),
                        }
                    )
                    return True
                if res["message"] == "Checkin Repeats! Please Try Tomorrow":
                    print("[INFO] GLADOS返回 今日已成功签到")
                    return True
                ding_send(
                    {
                        "uid": "未知",
                        "state": f'？ Glados响应正常,但响应内容无法解析。\n 响应内容：{res["message"]}',
                        "days": 0,
                    }
                )
            except BaseException as e:
                print(traceback.format_exc())
                ding_send({"uid": "未知", "state": f"✘ 程序异常{e}", "days": "-"})
        else:
            ding_send(
                {
                    "uid": "未知",
                    "state": f"网络响应异常{r.status_code},可能是网络连接失败.",
                    "days": "-",
                }
            )


def ding_send(msg):
    print(f"[INFO] 签到结果:{msg}")
    dingMsg = f"--- GLaDOS_AutoCheckIn ---\n开始时间:{runtime}\n\n"
    dingMsg = dingMsg + f'「{msg["uid"]}」\n状态:{msg["state"]}\n天数:{msg["days"]}\n'
    version_remote = get_new_version()
    if not VERSION == version_remote:
        dingMsg = dingMsg + f"\n当前版本:{VERSION}\n⚠最新版本:{version_remote}"
    else:
        dingMsg = dingMsg + f"\n当前版本:{VERSION}\n最新版本:{version_remote}"

    res = requests.post(
        url=config["dingWebhook"],  # type: ignore
        data=json.dumps({"msgtype": "text", "text": {"content": dingMsg}}),
        headers={"Content-Type": "application/json"},
    )
    if res.status_code != 200:
        print("[ X ] 请求钉钉服务器异常")
    if res.json()["errcode"] == 0:
        print("[INFO] 发送钉钉消息成功")
    else:
        print(
            f"[ X ] 发送钉钉异常.code:{res.json()['errcode']} msg:{res.json()['errmsg']}"
        )


def ding_send_errors(e):
    res = requests.post(
        url=config["dingWebhook"],  # type: ignore
        data=json.dumps({"msgtype": "text", "text": {"content": e}}),
        headers={"Content-Type": "application/json"},
    )
    print(f"\nDingDing系统返回:{res.text}")
    sys.exit()


def get_new_version():
    try:
        v = requests.get(
            "https://api.github.com/repos/zhangjiancong/GLaDOS_AutoCheckIn/releases/latest",
            timeout=10,
        )
        return (v.json())["tag_name"]
    except:
        return "?"


# 将签到成功日期写入sign.lock
def record_signed():
    signed_date = time.strftime("%Y-%m-%d", time.localtime())
    lock = open("sign.lock", "w")
    lock.write(signed_date)
    lock.close()


# 检查今日是否已签
def check_signed() -> bool:
    now_date = time.strftime("%Y-%m-%d", time.localtime())
    try:
        lock = open("sign.lock", "r")
        if lock.readline() == now_date:
            print("\n读取本地签到数据,今日已成功签到\n")
            return True
        else:
            return False
    except:
        return False


def main():
    global config
    getConfig = False
    # 加载配置信息
    try:
        with open("config.json", "r") as f:
            config = f.read()
            config = json.loads(config)
        print("[INFO] 成功从配置文件中拉取配置")
        getConfig = True
    except ValueError:
        print("[ X ] 在读取配置文件时,json不合法")
    except:
        try:
            config = json.loads(os.environ.get("CONFIG"))  # type: ignore
            getConfig = True
        except ValueError:
            print("[ X ] 在读取环境变量中的配置时,json不合法")
        except Exception as e:
            print(f"[ X ] 在读取环境变量中的配置时失败:{e}")
    finally:
        if not getConfig:
            print("[ X ] 从本地文件和环境变量中拉取配置失败!")
            ding_send_errors(
                "从本地文件和环境变量中拉取配置失败.\n请建立配置文件或将配置填入环境变量!"
            )

    # 检查今日是否已签到
    if check_signed():
        print("[WARN] 发现签到lock文件,今日已签")
        sys.exit("local:is signed")
    else:
        print("[INFO] 未发现签到lock文件或今日未签到")

    # 开始签到
    try:
        print("\n=== 开始签到 ===")
        checkin_issuccess = api_check_in(config["gladosHost"], config["users"])  # type: ignore
        if checkin_issuccess:
            record_signed()
    except BaseException:
        print(traceback.format_exc())
        ding_send_errors(traceback.format_exc())


if __name__ == "__main__":
    runtime = time.strftime("%m月%d日 %H:%M:%S", time.localtime())
    main()
