"""错误处理示例 - OOMOL Fusion SDK."""

from oomol_fusion_sdk import (
    OomolFusionSDK,
    OomolFusionError,
    TaskCancelledError,
    TaskFailedError,
    TaskSubmitError,
    TaskTimeoutError,
    NetworkError,
)

# 替换为你的 API token
API_TOKEN = "your-api-token-here"


def main() -> None:
    """演示如何处理各种错误."""
    sdk = OomolFusionSDK(
        token=API_TOKEN,
        timeout=60.0,  # 设置较短的超时时间用于演示
    )

    try:
        print("提交任务...")

        result = sdk.run(
            {
                "service": "fal-nano-banana-pro",
                "inputs": {"prompt": "A test image"},
            }
        )

        print(f"成功! 结果: {result.data}")

    except TaskSubmitError as e:
        print(f"❌ 任务提交失败:")
        print(f"   消息: {e.message}")
        print(f"   状态码: {e.status_code}")
        print(f"   响应: {e.response}")

    except TaskTimeoutError as e:
        print(f"⏱️  任务超时:")
        print(f"   消息: {e.message}")
        print(f"   Session ID: {e.session_id}")
        print(f"   服务: {e.service}")
        print(f"   超时时间: {e.timeout} 秒")

    except TaskCancelledError as e:
        print(f"🚫 任务被取消:")
        print(f"   消息: {e.message}")
        print(f"   Session ID: {e.session_id}")
        print(f"   服务: {e.service}")

    except TaskFailedError as e:
        print(f"💥 任务执行失败:")
        print(f"   消息: {e.message}")
        print(f"   Session ID: {e.session_id}")
        print(f"   服务: {e.service}")
        print(f"   状态: {e.state}")
        print(f"   错误详情: {e.error_details}")

    except NetworkError as e:
        print(f"🌐 网络错误:")
        print(f"   消息: {e.message}")
        print(f"   原始错误: {e.original_error}")

    except OomolFusionError as e:
        print(f"⚠️  SDK 错误:")
        print(f"   消息: {e.message}")

    except Exception as e:
        print(f"❓ 未知错误: {e}")

    finally:
        sdk.close()
        print("\n连接已关闭")


if __name__ == "__main__":
    main()
