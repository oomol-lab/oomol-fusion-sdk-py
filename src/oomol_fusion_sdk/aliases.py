from __future__ import annotations

from typing import List, Union

try:
    from typing import Literal, TypeAlias
except ImportError:  # pragma: no cover
    from typing_extensions import Literal, TypeAlias

from .generated.openapi_types import (
    ActionResponse,
    CphoneNanoBananaSubmit,
    DoubaoSTTSubmit,
    DoubaoTextToImageSeedreamActionGeneratePostRequest,
    DoubaoTTSSubmit,
    FalAuraSrSubmit,
    FalFluxProKontextSubmit,
    FalNanoBanana2Submit,
    FalNanoBananaProSubmit,
    FalNanoBananaSubmit,
    FalRemoveBackgroundResult,
    FalRemoveBackgroundSubmit,
    FalSora2ImageToVideoSubmit,
    FalSora2TextToVideoSubmit,
    FileUploadAbortMultipartRequest,
    FileUploadBaseRequest,
    FileUploadCompleteMultipartRequest,
    FileUploadCompleteMultipartRequestPartsItem,
    FileUploadCreateMultipartRequest,
    FileUploadPresignedUrlsRequest,
    ImageTranslateSubmitConfigTranslator,
    ImageTranslateResultSessionID200Response,
    ImageTranslateSubmit,
    JinaReaderReadURLRequest,
    JinaReaderSearchContentRequest,
    MangaZipTranslateResultSessionID200Response,
    MangaZipTranslateSubmit,
    PDFTransformEpubSubmit,
    PDFTransformMarkdownSubmit,
    QwenDocTurboRequest,
    QwenImageEditPlusRequest,
    QwenMtImageSubmit,
    TextToAudioSubmit,
    TextToEpubIllustrateActionGeneratePostRequest,
    TinifyPNGShrinkRequest,
    WanxImageSubmitPostRequest,
    WanxKf2vVideoSubmit,
)
from .types import QueryParams

TranslatorLanguageCode: TypeAlias = Literal[
    "CHS",
    "CHT",
    "CSY",
    "NLD",
    "ENG",
    "FRA",
    "DEU",
    "HUN",
    "ITA",
    "JPN",
    "KOR",
    "POL",
    "PTB",
    "ROM",
    "RUS",
    "ESP",
    "TRK",
    "UKR",
    "VIN",
    "ARA",
    "CNR",
    "SRP",
    "HRV",
    "THA",
    "IND",
    "FIL",
]

ImageTranslateInput: TypeAlias = Union[str, List[int]]
ImageTranslateTranslatorConfig = ImageTranslateSubmitConfigTranslator

ImageTranslateResultData = ImageTranslateResultSessionID200Response
ImageTranslateCompletedResponse = ImageTranslateResultSessionID200Response
MangaZipTranslateResultData = MangaZipTranslateResultSessionID200Response
MangaZipTranslateCompletedResponse = MangaZipTranslateResultSessionID200Response
FalRemoveBackgroundImage = FalRemoveBackgroundResult
FalRemoveBackgroundCompletedResponse = FalRemoveBackgroundResult
FileUploadPart = FileUploadCompleteMultipartRequestPartsItem
DoubaoTextToImageSeedreamGenerateRequest = (
    DoubaoTextToImageSeedreamActionGeneratePostRequest
)
TextToEpubIllustrateGenerateRequest = TextToEpubIllustrateActionGeneratePostRequest
WanxImageSubmit = WanxImageSubmitPostRequest
GenericActionRequest = QueryParams

__all__ = [
    "ActionResponse",
    "CphoneNanoBananaSubmit",
    "DoubaoSTTSubmit",
    "DoubaoTTSSubmit",
    "TextToAudioSubmit",
    "FalRemoveBackgroundSubmit",
    "FalRemoveBackgroundImage",
    "FalRemoveBackgroundCompletedResponse",
    "FalFluxProKontextSubmit",
    "FalAuraSrSubmit",
    "FalSora2ImageToVideoSubmit",
    "FalSora2TextToVideoSubmit",
    "FalNanoBanana2Submit",
    "FalNanoBananaSubmit",
    "ImageTranslateInput",
    "ImageTranslateTranslatorConfig",
    "ImageTranslateSubmit",
    "ImageTranslateResultData",
    "ImageTranslateCompletedResponse",
    "MangaZipTranslateSubmit",
    "MangaZipTranslateResultData",
    "MangaZipTranslateCompletedResponse",
    "JinaReaderReadURLRequest",
    "JinaReaderSearchContentRequest",
    "TinifyPNGShrinkRequest",
    "QwenMtImageSubmit",
    "FileUploadBaseRequest",
    "FileUploadCreateMultipartRequest",
    "FileUploadPresignedUrlsRequest",
    "FileUploadCompleteMultipartRequest",
    "FileUploadPart",
    "FileUploadAbortMultipartRequest",
    "PDFTransformEpubSubmit",
    "PDFTransformMarkdownSubmit",
    "FalNanoBananaProSubmit",
    "QwenImageEditPlusRequest",
    "QwenDocTurboRequest",
    "WanxKf2vVideoSubmit",
    "TranslatorLanguageCode",
    "DoubaoTextToImageSeedreamGenerateRequest",
    "TextToEpubIllustrateGenerateRequest",
    "WanxImageSubmit",
    "GenericActionRequest",
]
