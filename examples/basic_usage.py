"""基础使用示例 - OOMOL Fusion SDK."""

from oomol_fusion_sdk import OomolFusionSDK

# 替换为你的 API token
API_TOKEN = "your-api-token-here"


def main() -> None:
    """基础使用示例."""
    # 初始化 SDK
    sdk = OomolFusionSDK(token=API_TOKEN)

    try:
        # 提交任务并等待结果
        result = sdk.run(
            {
                "service": "fal-nano-banana-pro",
                "inputs": {
                    "prompt": "A beautiful sunset over the mountains",
                    "image_size": "landscape_4_3",
                },
            }
        )

        # 打印结果
        print("任务完成!")
        print(f"Session ID: {result.session_id}")
        print(f"Service: {result.service}")
        print(f"Result data: {result.data}")

    except Exception as e:
        print(f"错误: {e}")

    finally:
        # 关闭连接
        sdk.close()


if __name__ == "__main__":
    main()
