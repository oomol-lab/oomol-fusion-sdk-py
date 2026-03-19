from oomol_fusion_sdk import FusionClient


def main() -> None:
    client = FusionClient(api_key="your-api-key")

    submit_response = client.pdf_transform_markdown.submit(
        {
            "pdfURL": "https://example.com/book.pdf",
            "includesFootnotes": True,
        }
    )
    session_id = submit_response["sessionID"]
    print("Session:", session_id)

    def on_progress(progress: float, payload: dict) -> None:
        print("Progress:", progress, "State:", payload.get("state"))

    result = client.pdf_transform_markdown.wait_data(
        session_id,
        {
            "poll_interval_ms": 1000,
            "timeout_ms": 300000,
            "on_progress": on_progress,
        },
    )

    print("Result:", result)


if __name__ == "__main__":
    main()

