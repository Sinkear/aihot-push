# AI HOT 定时推送

每天自动从 [aihot.virxact.com](https://aihot.virxact.com) 拉取精选 AI 资讯，推送到企业微信群。

## 功能特性

- **每天 3 次定时推送**：北京时间 9:00、12:00、18:00
- **精选内容**：从 24 小时内精选 AI 动态中筛选
- **分类展示**：模型发布 / 产品更新 / 行业动态 / 论文研究 / 技巧观点
- **手动触发测试**：支持随时触发一次推送
- **零服务器成本**：基于 GitHub Actions 免费额度运行

## 推送效果预览

```
🤖 AI HOT · 早间精选（10 条精选）

1. **OpenRouter月活突破1亿** — X
   > 来源：X (@s_Jaeson) · 3小时前
   > OpenRouter日活增速超同类平台...

2. **Mistral推出小型多模态模型Le Chat** — X
   > 来源：X (@MistralAI) · 21小时前
   > Mistral发布Le Chat，轻量级多模态模型...
...
```

## 快速部署

### 1. 创建企业微信群机器人

1. 在企业微信中创建一个内部群
2. 群设置 → 群机器人 → 添加机器人
3. 复制 Webhook URL

### 2. 配置 GitHub Secrets

1. 打开仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. **Name**: `WECOM_WEBHOOK_URL`
4. **Value**: 填入你的企业微信 Webhook URL
5. 点击 **Add secret**

### 3. 完成

- 定时推送会自动开始（北京时间 9:00、12:00、18:00）
- 也可以手动触发：仓库 → **Actions** → **AI HOT 定时推送** → **Run workflow**

## 本地运行

```bash
# 安装依赖
pip install requests

# 设置环境变量
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的KEY"

# 运行
python aihot_push.py
```

## 数据来源

- [aihot.virxact.com](https://aihot.virxact.com) — AI 行业资讯精选平台
- 无需 API Key，直接调用公开接口
