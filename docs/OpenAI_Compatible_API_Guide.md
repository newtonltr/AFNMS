# OpenAI兼容API配置指南

本程序完全支持OpenAI兼容格式的API，可以轻松集成各种第三方AI服务。

## 支持的API类型

### 1. 官方OpenAI API
```json
{
  "id": "openai-gpt4",
  "type": "openai",
  "api_key": "sk-your-openai-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### 2. 本地部署的模型服务
```json
{
  "id": "local-llama",
  "type": "openai",
  "api_key": "local-key",
  "base_url": "http://localhost:8000/v1",
  "model": "llama-2-7b-chat"
}
```

### 3. 第三方OpenAI兼容服务

#### DeepSeek API
```json
{
  "id": "deepseek-chat",
  "type": "openai",
  "api_key": "your-deepseek-key",
  "base_url": "https://api.deepseek.com/v1",
  "model": "deepseek-chat"
}
```

#### 智谱AI GLM
```json
{
  "id": "zhipu-glm4",
  "type": "openai",
  "api_key": "your-zhipu-key",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "model": "glm-4"
}
```

#### 月之暗面 Kimi
```json
{
  "id": "kimi-chat",
  "type": "openai",
  "api_key": "your-kimi-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "moonshot-v1-8k"
}
```

#### 阿里云通义千问
```json
{
  "id": "qwen-chat",
  "type": "openai",
  "api_key": "your-qwen-key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-plus"
}
```

## 配置步骤

### 1. 修改配置文件
编辑 `config/ai_config.json`，添加您的API配置：

```json
{
  "models": [
    {
      "id": "your-custom-api",
      "type": "openai",
      "priority": 1,
      "api_key": "YOUR_API_KEY",
      "base_url": "YOUR_API_ENDPOINT",
      "model": "YOUR_MODEL_NAME",
      "max_tokens": 1000,
      "temperature": 0.3,
      "enabled": true,
      "description": "您的自定义API描述"
    }
  ]
}
```

### 2. 环境变量配置（推荐）
为了安全起见，建议使用环境变量：

```bash
# Windows
set AI_YOUR_CUSTOM_API_API_KEY=your-actual-api-key

# Linux/Mac
export AI_YOUR_CUSTOM_API_API_KEY=your-actual-api-key
```

### 3. 验证配置
程序启动时会自动验证所有配置的API：

```python
from src.model_router import get_model_router

router = get_model_router()
print("可用模型:", router.get_available_models())
print("健康模型:", router.get_healthy_models())
```

## 常见兼容服务配置

### Ollama本地服务
```json
{
  "id": "ollama-llama2",
  "type": "openai",
  "api_key": "ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "llama2:7b"
}
```

### LM Studio
```json
{
  "id": "lmstudio-model",
  "type": "openai",
  "api_key": "lm-studio",
  "base_url": "http://localhost:1234/v1",
  "model": "local-model"
}
```

### Text Generation WebUI
```json
{
  "id": "textgen-webui",
  "type": "openai",
  "api_key": "textgen",
  "base_url": "http://localhost:5000/v1",
  "model": "your-loaded-model"
}
```

### vLLM服务
```json
{
  "id": "vllm-service",
  "type": "openai",
  "api_key": "vllm-key",
  "base_url": "http://localhost:8000/v1",
  "model": "microsoft/DialoGPT-medium"
}
```

## 配置参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `id` | 唯一标识符 | ✅ |
| `type` | 必须为 "openai" | ✅ |
| `priority` | 优先级（数字越小优先级越高） | ✅ |
| `api_key` | API密钥 | ✅ |
| `base_url` | API基础URL | ✅ |
| `model` | 模型名称 | ✅ |
| `max_tokens` | 最大token数（null表示不限制） | ❌ |
| `temperature` | 温度参数 | ❌ |
| `enabled` | 是否启用 | ❌ |
| `description` | 描述信息 | ❌ |

### max_tokens参数详细说明

不限制最大tokens有以下几种方式：

#### 方法1：设置为null（推荐）
```json
{
  "max_tokens": null
}
```

#### 方法2：完全省略该参数
```json
{
  "id": "unlimited-model",
  "type": "openai",
  "api_key": "your-key",
  "base_url": "https://your-api.com/v1",
  "model": "your-model",
  "temperature": 0.3
  // 不包含max_tokens参数
}
```

#### 方法3：设置为非常大的数值
```json
{
  "max_tokens": 100000
}
```

**注意事项：**
- 不同API服务对max_tokens的处理可能略有不同
- 某些模型有内置的最大输出限制
- 不限制tokens可能导致更高的API费用
- 建议根据实际需求合理设置

## 故障排除

### 1. 连接失败
- 检查 `base_url` 是否正确
- 确认服务是否正常运行
- 验证网络连接

### 2. 认证失败
- 检查 `api_key` 是否正确
- 确认API密钥是否有效
- 检查环境变量设置

### 3. 模型不可用
- 确认 `model` 名称正确
- 检查服务是否支持该模型
- 查看服务日志

### 4. 响应格式错误
- 确认服务完全兼容OpenAI格式
- 检查返回的JSON结构
- 查看错误日志

## 自动故障转移

程序支持智能故障转移：
1. 按优先级依次尝试可用的API
2. 自动跳过不健康的服务
3. 定期进行健康检查
4. 详细的使用统计和错误报告

## 使用示例

```python
# 分析新闻
from src.model_router import get_model_router

router = get_model_router()
result = await router.analyze_news(
    "美联储宣布加息25个基点", 
    "Reuters"
)

print(f"影响评分: {result.impact_score}")
print(f"市场预测: {result.market_prediction}")
print(f"交易建议: {result.trading_suggestion}")
```

通过这种方式，您可以轻松集成任何OpenAI兼容的API服务到本程序中！ 