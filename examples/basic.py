from oomol_fusion_sdk import FusionClient


def main() -> None:
    client = FusionClient(api_key="your-api-key")

    tts_result = client.doubao_tts.run_data(
        {
            "text": "你好，欢迎使用 Fusion API SDK。",
            "voice": "zh_female_vv_uranus_bigtts",
        }
    )
    print("TTS result:", tts_result)

    page = client.jina_reader.read(
        {
            "URL": "https://example.com/article",
            "format": "markdown",
        }
    )
    print("Reader result:", page["data"])


if __name__ == "__main__":
    main()

