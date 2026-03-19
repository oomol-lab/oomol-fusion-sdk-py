from oomol_fusion_sdk import FusionClient, OomolFusionSdkError


def main() -> None:
    client = FusionClient(api_key="your-api-key")

    try:
        search_result = client.jina_reader.search(
            {
                "content": "Fusion API SDK",
                "jsonResponse": True,
            }
        )
        print("Search result:", search_result["data"])

        report_result = client.custom_financial_fundamental_report.report_list(
            {
                "symbol": "AAPL",
            }
        )
        print("Report list:", report_result["data"])
    except Exception as error:
        normalized = OomolFusionSdkError.from_unknown(error)
        print("Code:", normalized.code)
        print("Status:", normalized.status)
        print("Retryable:", normalized.retryable)
        print("Details:", normalized.details)


if __name__ == "__main__":
    main()
