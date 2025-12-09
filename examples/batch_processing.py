"""批量处理示例 - OOMOL Fusion SDK."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from oomol_fusion_sdk import OomolFusionSDK

# 替换为你的 API token
API_TOKEN = "your-api-token-here"


def process_prompt(sdk: OomolFusionSDK, prompt: str, index: int) -> tuple[int, dict]:
    """处理单个提示词.

    Args:
        sdk: SDK 实例
        prompt: 提示词
        index: 索引

    Returns:
        索引和结果的元组
    """
    print(f"[{index}] 开始处理: {prompt}")

    result = sdk.run(
        {
            "service": "fal-nano-banana-pro",
            "inputs": {"prompt": prompt, "image_size": "square"},
        }
    )

    print(f"[{index}] 完成!")
    return index, result.data


def main() -> None:
    """演示如何批量处理多个任务."""
    # 要处理的提示词列表
    prompts = [
        "A sunset over the ocean",
        "A mountain landscape with snow",
        "A city skyline at night",
        "A tropical beach with palm trees",
        "A forest in autumn colors",
    ]

    sdk = OomolFusionSDK(token=API_TOKEN)

    try:
        print(f"开始批量处理 {len(prompts)} 个任务...\n")

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有任务
            futures = {
                executor.submit(process_prompt, sdk, prompt, i): i
                for i, prompt in enumerate(prompts, 1)
            }

            # 收集结果
            results = {}
            for future in as_completed(futures):
                index = futures[future]
                try:
                    idx, data = future.result()
                    results[idx] = data
                except Exception as e:
                    print(f"[{index}] 错误: {e}")

        print(f"\n所有任务完成! 成功: {len(results)}/{len(prompts)}")

        # 打印结果
        for i in sorted(results.keys()):
            print(f"\n结果 {i}:")
            print(f"  提示词: {prompts[i-1]}")
            print(f"  数据: {results[i]}")

    finally:
        sdk.close()


if __name__ == "__main__":
    main()
