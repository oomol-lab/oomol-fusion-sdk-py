from __future__ import annotations

from typing import Dict, List, Tuple

from .types import ActionEndpointConfig

BUILTIN_TASK_SERVICES: Tuple[str, ...] = (
    "cphone-nano-banana",
    "doubao-stt",
    "doubao-tts",
    "fal-aura-sr",
    "fal-flux-pro-kontext",
    "fal-nano-banana",
    "fal-nano-banana-2",
    "fal-nano-banana-pro",
    "fal-remove-background",
    "fal-sora2-image-to-video",
    "fal-sora2-text-to-video",
    "image-translate",
    "manga-zip-translate",
    "oomol-tts",
    "pdf-transform-epub",
    "pdf-transform-markdown",
    "qwen-mt-image",
    "wanx-image",
    "wanx-kf2v-video",
)

BUILTIN_ACTION_ENDPOINTS: Tuple[ActionEndpointConfig, ...] = (
    {"key": "custom-financial-fundamental-report/predefined-questions", "method": "GET"},
    {"key": "custom-financial-fundamental-report/report", "method": "GET"},
    {"key": "custom-financial-fundamental-report/report-list", "method": "GET"},
    {"key": "doubao-text-to-image-seedream/generate", "method": "POST"},
    {"key": "file-upload/abort-multipart-upload", "method": "POST"},
    {"key": "file-upload/complete-multipart-upload", "method": "POST"},
    {"key": "file-upload/create-multipart-upload", "method": "POST"},
    {"key": "file-upload/generate-presigned-url", "method": "POST"},
    {"key": "file-upload/generate-presigned-urls", "method": "POST"},
    {"key": "jina-reader/read", "method": "POST"},
    {"key": "jina-reader/search", "method": "POST"},
    {"key": "qwen-doc-turbo/analyze", "method": "POST"},
    {"key": "qwen-image-edit-plus/edit", "method": "POST"},
    {"key": "text-to-epub-illustrate/generate", "method": "POST"},
    {"key": "tinify-png-shrink/compress", "method": "POST"},
)

TASK_SHORTCUTS: Tuple[Tuple[str, str, str], ...] = (
    ("cphone_nano_banana", "cphoneNanoBanana", "cphone-nano-banana"),
    ("doubao_stt", "doubaoStt", "doubao-stt"),
    ("doubao_tts", "doubaoTts", "doubao-tts"),
    ("fal_aura_sr", "falAuraSr", "fal-aura-sr"),
    ("fal_flux_pro_kontext", "falFluxProKontext", "fal-flux-pro-kontext"),
    ("fal_nano_banana", "falNanoBanana", "fal-nano-banana"),
    ("fal_nano_banana_2", "falNanoBanana2", "fal-nano-banana-2"),
    ("fal_nano_banana_pro", "falNanoBananaPro", "fal-nano-banana-pro"),
    ("fal_remove_background", "falRemoveBackground", "fal-remove-background"),
    ("fal_sora2_image_to_video", "falSora2ImageToVideo", "fal-sora2-image-to-video"),
    ("fal_sora2_text_to_video", "falSora2TextToVideo", "fal-sora2-text-to-video"),
    ("image_translate", "imageTranslate", "image-translate"),
    ("manga_zip_translate", "mangaZipTranslate", "manga-zip-translate"),
    ("oomol_tts", "oomolTts", "oomol-tts"),
    ("pdf_transform_epub", "pdfTransformEpub", "pdf-transform-epub"),
    ("pdf_transform_markdown", "pdfTransformMarkdown", "pdf-transform-markdown"),
    ("qwen_mt_image", "qwenMtImage", "qwen-mt-image"),
    ("wanx_image", "wanxImage", "wanx-image"),
    ("wanx_kf2v_video", "wanxKf2vVideo", "wanx-kf2v-video"),
)

ACTION_SHORTCUTS: Tuple[Tuple[str, str, Tuple[Tuple[str, str, str], ...]], ...] = (
    (
        "custom_financial_fundamental_report",
        "customFinancialFundamentalReport",
        (
            ("predefined_questions", "predefinedQuestions", "custom-financial-fundamental-report/predefined-questions"),
            ("report", "report", "custom-financial-fundamental-report/report"),
            ("report_list", "reportList", "custom-financial-fundamental-report/report-list"),
        ),
    ),
    (
        "doubao_text_to_image_seedream",
        "doubaoTextToImageSeedream",
        (
            ("generate", "generate", "doubao-text-to-image-seedream/generate"),
        ),
    ),
    (
        "file_upload",
        "fileUpload",
        (
            ("abort_multipart_upload", "abortMultipartUpload", "file-upload/abort-multipart-upload"),
            ("complete_multipart_upload", "completeMultipartUpload", "file-upload/complete-multipart-upload"),
            ("create_multipart_upload", "createMultipartUpload", "file-upload/create-multipart-upload"),
            ("generate_presigned_url", "generatePresignedUrl", "file-upload/generate-presigned-url"),
            ("generate_presigned_urls", "generatePresignedUrls", "file-upload/generate-presigned-urls"),
        ),
    ),
    (
        "jina_reader",
        "jinaReader",
        (
            ("read", "read", "jina-reader/read"),
            ("search", "search", "jina-reader/search"),
        ),
    ),
    (
        "qwen_doc_turbo",
        "qwenDocTurbo",
        (
            ("analyze", "analyze", "qwen-doc-turbo/analyze"),
        ),
    ),
    (
        "qwen_image_edit_plus",
        "qwenImageEditPlus",
        (
            ("edit", "edit", "qwen-image-edit-plus/edit"),
        ),
    ),
    (
        "text_to_epub_illustrate",
        "textToEpubIllustrate",
        (
            ("generate", "generate", "text-to-epub-illustrate/generate"),
        ),
    ),
    (
        "tinify_png_shrink",
        "tinifyPngShrink",
        (
            ("compress", "compress", "tinify-png-shrink/compress"),
        ),
    ),
)

