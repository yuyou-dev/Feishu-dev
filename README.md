# 飞书超级文档开发与应用
DeepSeek - 飞书超级文档开发

## 超级文档

- [分镜大师](https://test-cp80epxn7soj.feishu.cn/docx/OEgcdjv1DoSAS3xz08ccfb32nph)
- [珠宝设计800款](https://test-cp80epxn7soj.feishu.cn/share/base/view/shrcnUSDOeBx1jp9X62ipbm6Vnf)

- [字体大师2.0](https://test-cp80epxn7soj.feishu.cn/base/Ga1Vb55riaBvAqsi97ncunlFn9c?from=from_copylink)


### 预览
| ![Image 1](PiecesOfJewelry/jewerly_00094.jpg) | ![Image 2](PiecesOfJewelry/jewerly_00844.jpg) | ![Image 2](PiecesOfJewelry/jewerly_00613.jpg) |![Image 2](PiecesOfJewelry/jewerly_00670.jpg) |
|---------------------------------|---------------------------------|---------------------------------|---------------------------------|
| ![Image 3](PiecesOfJewelry/jewerly_00845.jpg) | ![Image 4](PiecesOfJewelry/jewerly_02510.jpg) | ![Image 2](PiecesOfJewelry/jewerly_00659.jpg) |![Image 2](PiecesOfJewelry/jewerly_00860.jpg) |


# Google Imagen-3 批量图像生成工具

这个Python脚本可以帮助你批量使用Google Imagen-3 API生成图像。它支持从文本文件读取提示词，使用多线程并行生成图像，并自动处理API调用的速率限制。

## 功能特点

- 从文本文件读取提示词，每行一个提示词
- 多线程并行生成图像，提高效率
- 自动处理API速率限制（默认每分钟20次调用）
- 自动重试失败的请求
- 自动创建输出文件夹
- 保存生成的图像及其对应的提示词文本
- 处理被API阻止的提示词
- 友好的进度和错误提示

## 安装依赖

1. 使用 venv（Python 内置模块）（可选）

   ```bash
   # Windows系统
   python -m venv myenv
   myenv\Scripts\activate

   # macOS/Linux系统
   python3 -m venv myenv
   source myenv/bin/activate
   ```

2. 安装 Python 3.9 及更高版本的依赖

   ```bash
   pip install -q -U google-genai
   pip install pillow
   ```

## 使用方法

### 1. 设置API密钥

首先需要设置你的Google API密钥：

```bash
export GOOGLE_API_KEY=你的API密钥
```

### 2. 准备提示词文件

创建一个名为`prompts.txt`的文本文件，每行包含一个图像生成提示词。例如：

```
a cat
a dog
an elephant
```

### 3. 运行脚本

```bash
python 你的脚本名.py
```

### 4. 查看结果

生成的图像和对应的提示词文本文件将保存在自动创建的`images`文件夹或其序号子文件夹中（如`images1`、`images2`等）。

## 配置选项

你可以通过修改代码中的以下参数来调整脚本行为：

- `num_parallel`: 并行处理的线程数
- `max_retries`: 每个请求的最大重试次数
- `RateLimiter`的参数: 调整API调用的速率限制
- `aspect_ratio`: 图像的宽高比

## 注意事项

- 请确保你的Google API密钥有访问Imagen-3 API的权限
- 脚本默认使用`imagen-3.0-generate-002`模型，请根据实际可用模型调整
- API调用会产生费用，请留意你的Google Cloud账户使用情况
- 生成的图像质量和内容由Imagen-3模型决定
- 被API阻止的提示词将被跳过并不再重试

## 错误处理

脚本会自动处理常见错误情况：

- API速率限制
- 请求超时或失败
- 被阻止的提示词
- 文件操作错误

遇到错误时，脚本会打印详细的错误信息，并根据情况进行重试或跳过。

如果你有任何问题或建议，请随时提出。
