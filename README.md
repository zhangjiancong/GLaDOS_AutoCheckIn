# GLaDOS_AutoCheckIn
GLaDOS自动签到脚本 本地运行

## 使用指引
- 准备Python3环境
- 执行 `pip install requests` 安装依赖
- 填写 `config.json` 进行配置
- 执行 `run.py`
  
## 配置设置
示例:  
`
{
    "gladosHost": "https://glados.rocks",
    "dingWebhook": "钉钉webhook地址",
    "users": [
        "GlaDOS cookie"
    ]
}
`  

解释:  
**gladosHost**:GLaDOS有效域名  
**dingWebhook**:钉钉群机器人地址，安全方式选择关键词，填写英文句号`.`和横线`-`  
**users**:GlaDOS账户cookie，此值接收一个数组允许使用多账号

## 预期规划
当前主线版本为V1，V2版本加入Action功能