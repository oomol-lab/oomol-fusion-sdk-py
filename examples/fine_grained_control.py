"""细粒度控制示例 - OOMOL Fusion SDK."""

import time
from oomol_fusion_sdk import OomolFusionSDK, TaskState

# 替换为你的 API token
API_TOKEN = "your-api-token-here"


def main() -> None:
    """演示如何细粒度控制任务执行."""
    sdk = OomolFusionSDK(token=API_TOKEN)

    try:
        # 第一步: 提交任务
        print("步骤 1: 提交任务...")
        response = sdk.submit(
            {
                "service": "fal-nano-banana-pro",
                "inputs": {"prompt": "A robot writing code"},
            }
        )

        session_id = response["sessionID"]
        print(f"✓ 任务已提交")
        print(f"  Session ID: {session_id}")
        print(f"  Success: {response['success']}")

        # 第二步: 做其他事情
        print("\n步骤 2: 做其他工作...")
        print("  (模拟其他操作...)")
        time.sleep(2)

        # 第三步: 手动检查状态
        print("\n步骤 3: 检查任务状态...")
        status = sdk.get_task_status("fal-nano-banana-pro", session_id)

        print(f"  状态: {status['state']}")
        print(f"  进度: {status.get('progress', 0):.1f}%")

        if status["state"] == TaskState.COMPLETED:
            print(f"  结果: {status['data']}")
            return

        # 第四步: 等待任务完成
        print("\n步骤 4: 等待任务完成...")

        def on_progress(progress: float) -> None:
            print(f"  进度更新: {progress:.1f}%")

        from oomol_fusion_sdk import RunOptions

        result = sdk.wait_for(
            service="fal-nano-banana-pro",
            session_id=session_id,
            options=RunOptions(on_progress=on_progress),
        )

        print("\n✓ 任务完成!")
        print(f"  Session ID: {result.session_id}")
        print(f"  Service: {result.service}")
        print(f"  Result: {result.data}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")

    finally:
        sdk.close()


if __name__ == "__main__":
    main()
