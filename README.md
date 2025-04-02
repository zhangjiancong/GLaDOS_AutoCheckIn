# GLaDOS_AutoCheckIn
GLaDOS自动签到脚本 本地运行

## 更新历史
V1.3 正式发布  
V2.0 新增Github Action支持
V2.1 优化钉钉消息发送逻辑,仅在签到成功和异常时发送消息;取消了多账户支持

## 配置设置
**为了确保程序正常运行，建议您填写配置字段后进行json格式检查**  
示例:  
`
{
    "gladosHost": "https://glados.rocks",
    "dingWebhook": "钉钉webhook地址",
    "users": "GlaDOS cookie"
}
`  

解释:  
**gladosHost**:GLaDOS有效域名,可保持此值不变  
**dingWebhook**:钉钉群机器人地址，安全方式选择关键词，填写英文句号`.`和横线`-`  
**users**:GlaDOS账户cookie

## 使用指引
### 本地部署
- 准备Python3环境
- 执行 `pip install requests` 安装依赖
- 将配置写入 `config.json` 文件中
- 执行 `run.py`
### Github Action
- Fork本仓库至自己的账号中
- 在`Settings`-`Secrets and variables`-`Actions`页面中调整至`Variables`选项卡,点击`New repository variable`
- `Name`为`config`,`Value`为配置字段(见 配置设置 )
- 点击`Add variable`确认添加
- 您可在`Actions`进行手动运行,也可等待程序自动运行(10点，15点，19点)
