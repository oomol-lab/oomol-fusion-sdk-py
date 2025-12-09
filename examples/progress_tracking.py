"""进度跟踪示例 - OOMOL Fusion SDK."""

from oomol_fusion_sdk import OomolFusionSDK, RunOptions

# 替换为你的 API token
API_TOKEN = "your-api-token-here"


def main() -> None:
    """演示如何使用进度回调."""
    # 使用上下文管理器
    with OomolFusionSDK(token=API_TOKEN) as sdk:

        def on_progress(progress: float) -> None:
            """进度回调函数."""
            print(f"进度: {progress:.1f}%")

        print("开始执行任务...")

        result = sdk.run(
            {
                "service": "fal-nano-banana-pro",
                "inputs": {
                    "prompt": "A cat wearing sunglasses on the beach",
                    "image_size": "square",
                },
            },
            options=RunOptions(on_progress=on_progress),
        )

        print("\n任务完成!")
        print(f"结果: {result.data}")


if __name__ == "__main__":
    main()
