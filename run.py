import sys
import requests
import json
import time
import traceback
import os
# 程序版本
VERSION = '2.0'
config = {}
tasks = []
runtime=''
success=0


def api_check_in(host, cookie):
    global success
    check_in_url = f"{host}/api/user/checkin"
    referer_url = f"{host}/console/checkin"
    payload = {"token": "glados.network"}
    with requests.post(
            check_in_url,
            headers={'authority': 'glados.rocks',
                     'accept': 'application/json, text/plain, */*',
                     'dnt': '1',
                     'cookie': cookie,
                     'referer': referer_url,
                     'sec-fetch-mode': 'cors',
                     'sec-fetch-dest': 'empty',
                     'origin': host,
                     'user-agent': 'Not A;Brand;v=99, Chromium;v=102, Google Chrome;v=102',
                     'content-type': 'application/json;charset=UTF-8',
                     'accept-language': 'zh-CN,zh;q=0.9', },
            data=json.dumps(payload)
    ) as r:
        if(r.status_code == 200):
            res = r.json()
            try:
                if res["message"] == '没有权限':
                    tasks.append({'uid':'未知','state':f'✘ cookie填写有误','days':'-'})
                    return
                if res["message"] == 'oops, token error':
                    tasks.append({'uid':'未知','state':f'✘ token异常,请更新cookie','days':'-'})
                    return
                if res["message"] == 'Checkin! Get 1 Day':
                    success+=1
                    tasks.append({'uid':res['list'][0]['user_id'],'state':'√ 成功','days':int(float(res['list'][0]['balance']))})
                    return
                if res["message"] == 'Please Try Tomorrow':
                    success+=1
                    tasks.append({'uid':res['list'][0]['user_id'],'state':'√ 今日已经成功签到','days':int(float(res['list'][0]['balance']))})
                    return
                tasks.append({'uid':'未知','state':f'？ Glados响应正常,但响应内容无法解析。\n 响应内容：{res["message"]}','days':0})
            except BaseException as e:
                print(traceback.format_exc())
                tasks.append({'uid':'未知','state':f'✘ 程序异常{e}','days':'-'})
        else:
            tasks.append({'uid':'未知','state':f'网络响应异常{r.status_code},可能是网络连接失败.','days':'-'})


def ding_send():
    global tasks
    dingMsg = f"--- GLaDOS_AutoCheckIn ---\n开始时间:{runtime}\n成功率:{round(success/len(config['users'])*100)}%\n\n"
    for t in tasks:
        try:
            dingMsg=dingMsg+f'「{t["uid"]}」\n状态:{t["state"]}\n天数:{t["days"]}\n'
        except:
            dingMsg=dingMsg+'**ERROR**\n'
    version_remote=get_new_version()
    if not VERSION==version_remote:
        dingMsg = dingMsg+f'\n当前版本:{VERSION}\n⚠最新版本:{version_remote}'
    else:
        dingMsg = dingMsg+f'\n当前版本:{VERSION}\n最新版本:{version_remote}'

    res = requests.post(url=config["dingWebhook"],
                        data=json.dumps({"msgtype": "text", "text": {"content": dingMsg}}), headers={'Content-Type': 'application/json'})
    res = json.loads(res.text)
    print(f'\nDingDing系统返回:\n{res}')


def ding_send_errors(e):
    res = requests.post(url=config["dingWebhook"],
                        data=json.dumps({"msgtype": "text", "text": {"content": e}}), headers={'Content-Type': 'application/json'})
    print(f'\nDingDing系统返回:{res.text}')
    sys.exit()

def get_new_version():
    try:
        v=requests.get('https://api.github.com/repos/zhangjiancong/GLaDOS_AutoCheckIn/releases/latest')
        return (v.json())["tag_name"]
    except:
        return '?'
    

# 将签到成功日期写入sign.lock
def record_signed():
    signed_date = time.strftime("%Y-%m-%d", time.localtime())
    lock = open('sign.lock', 'w')
    lock.write(signed_date)
    lock.close()

# 检查今日是否已签
def check_signed() -> bool:
    now_date = time.strftime("%Y-%m-%d", time.localtime())
    try:
        lock = open('sign.lock', 'r')
        if(lock.readline() == now_date):
            print('\n读取本地签到数据,今日已成功签到\n')
            return True
        else:
            return False
    except:
        return False


def main():
    global config
    getConfig=False
    # 加载配置信息
    try:
        with open('config.json', 'r') as f:
            config = f.read()
            config = json.loads(config)
        print('成功从配置文件中拉取配置')
        getConfig = True
    except:
        try:
            config=json.loads(os.environ.get('CONFIG'))
            getConfig = True
        except:
            print('[ X ] 在读取环境变量中的配置时失败')
    finally:
        if(not getConfig):
            print('从本地文件和环境变量中拉取配置失败!')
            ding_send_errors('从本地文件和环境变量中拉取配置失败.\n请建立配置文件或将配置填入环境变量!')

    # 检查今日是否已签到
    if(check_signed()):
        sys.exit('local:is signed')
    else:
        print('未发现签到lock文件或今日未签到')
    
    # 开始签到
    try:
        doing=1
        print('\n=== 开始签到 ===')
        for t in config['users']:
            print(f'正在进行第{doing}个 共{len(config["users"])}个')
            api_check_in(config['gladosHost'],t)
            doing+=1
        ding_send()
        if(success==len(config['users'])):
            record_signed()
    except BaseException:
        print(traceback.format_exc())
        ding_send_errors(traceback.format_exc())
    


if __name__ == '__main__':
    runtime=time.strftime("%m月%d日 %H:%M:%S", time.localtime())
    main()
