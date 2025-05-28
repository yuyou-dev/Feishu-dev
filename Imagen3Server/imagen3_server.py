import concurrent.futures
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import time
import threading
from collections import deque


class RateLimiter:
    def __init__(self, max_calls, period_seconds):
        self.max_calls = max_calls
        self.period = period_seconds
        self.lock = threading.Lock()
        self.calls = deque()

    def acquire(self):
        while True:
            with self.lock:
                now = time.time()
                # 移除超过周期的旧调用记录
                while self.calls and self.calls[0] <= now - self.period:
                    self.calls.popleft()

                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return  # 允许执行

                # 否则等待
                # 计算下一次调用最早可能的时间
                next_possible_call_time = self.calls[0] + self.period
                sleep_time = next_possible_call_time - now
                # 确保由于潜在的竞态条件或时钟偏移，sleep_time 不为负
                sleep_time = max(0, sleep_time)

            if sleep_time > 0:  # 仅在必要时休眠
                time.sleep(sleep_time)


# 新增参数 rate_limiter
def generate_image(index, prompt, client, rate_limiter, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            rate_limiter.acquire()  # 限速：每分钟最多20张
            print(f"正在为提示词生成第{index}张图片: '{prompt[:50]}...'")  # 为清晰起见添加打印
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',  # 确保此模型名称正确
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1"
                )
            )
            # 确保 response.generated_images 不为空且包含图像数据
            if response.generated_images and response.generated_images[0].image and response.generated_images[0].image.image_bytes:
                image_bytes = response.generated_images[0].image.image_bytes
                image = Image.open(BytesIO(image_bytes))
                return image
            else:
                print(f"未收到第{index}张图片的数据。响应: {response}")
                # 进入重试逻辑
        except types.generation_types.BlockedPromptException as bpe:  # 特定的提示词被阻止异常
            print(f"第{index}张图片的提示词被阻止: {bpe}。跳过此提示词。")
            return None  # 跳过此提示词并不再重试
        except Exception as e:
            print(f"生成第{index}张图片的第{retries + 1}次尝试失败: {e}")
            retries += 1
            if retries < max_retries:
                time.sleep(5)  # 重试前稍等片刻
    print(f"在{max_retries}次重试后放弃生成第{index}张图片。")
    return None


def get_image_folder(base_name="images", max_index=100):
    if not os.path.exists(base_name):
        os.makedirs(base_name, exist_ok=True)  # 如果 base_name 不存在则创建
        return base_name
    for i in range(1, max_index + 1):
        folder = f"{base_name}{i}"
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)  # 如果文件夹不存在则创建
            return folder
    raise ValueError(f"超过最大文件夹限制 ({max_index})")


# 从TXT文件读取提示词的新函数
def load_prompts_from_file(filepath="prompts.txt"):
    """从文本文件读取提示词，每行一个提示词。"""
    prompts_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line:  # 确保行不为空
                    prompts_list.append(stripped_line)
        if not prompts_list:
            print(f"警告: 在{filepath}中未找到提示词。")
        return prompts_list
    except FileNotFoundError:
        print(f"错误: 未找到文件{filepath}。")
        return []  # 如果文件未找到则返回空列表
    except Exception as e:
        print(f"从{filepath}读取提示词时出错: {e}")
        return []


def main():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("错误: 未设置 GOOGLE_API_KEY 环境变量。")
        return
    print(f"使用API密钥: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else '未设置'}")  # 打印时屏蔽API密钥

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"初始化 genai.Client 失败: {e}")
        return

    num_parallel = 5
    folder_path = get_image_folder()
    # os.makedirs(folder_path, exist_ok=True)  # get_image_folder 现在处理创建
    folder_basename = os.path.basename(folder_path)

    # 从文本文件加载提示词
    prompts = load_prompts_from_file("prompts.txt")  # 假设 prompts.txt 在同一目录中
    if not prompts:
        print("没有要处理的提示词。退出。")
        return

    # 初始化速率限制器: 每分钟20次调用
    rate_limiter = RateLimiter(max_calls=20, period_seconds=60)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_parallel) as executor:
        futures = []
        for index, prompt in enumerate(prompts, start=1):
            future = executor.submit(generate_image, index, prompt, client, rate_limiter)
            futures.append((index, prompt, future))

        for index, prompt, future in futures:
            try:
                image = future.result()  # 这可能会重新抛出 generate_image 中的异常
                if image:
                    image_path = os.path.join(folder_path, f"{folder_basename}_{index:05d}.png")
                    text_path = os.path.join(folder_path, f"{folder_basename}_{index:05d}.txt")
                    image.save(image_path)
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(prompt)
                    print(f'已保存 {image_path} 和 {text_path}')
            except Exception as e:
                print(f"处理提示词 '{prompt[:50]}...' 的结果时出错: {e}")


if __name__ == "__main__":
    main()