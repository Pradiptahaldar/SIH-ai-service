def fuse_multimodal(
    text_result=None,
    image_result=None,
    audio_result=None
):
    """
    Combine information from text, image, and audio inputs
    into a single multimodal understanding.
    """

    sources = []
    combined_information = []

    # Text
    if text_result:
        sources.append("text")

        if isinstance(text_result, str):
            combined_information.append(text_result)

    # Image
    if image_result:
        sources.append("image")

        if isinstance(image_result, dict):
            analysis = image_result.get("analysis")

            if analysis and isinstance(analysis, dict):
                category = analysis.get("category")

                if category:
                    combined_information.append(
                        f"Image category: {category}"
                    )

    # Audio
    if audio_result:
        sources.append("audio")

        if isinstance(audio_result, dict):
            audio_text = audio_result.get("text")

            if audio_text:
                combined_information.append(
                    audio_text
                )

    return {
        "sources": sources,
        "combined_information": combined_information,
        "source_count": len(sources)
    }


def build_unified_text(
    text_result=None,
    image_result=None,
    audio_result=None
):
    """
    Build a single text representation from multimodal inputs.
    """

    parts = []

    # Original text
    if text_result:
        if isinstance(text_result, str):
            parts.append(text_result)

    if image_result:
        if isinstance(image_result, dict):
            image_result = [image_result]

        if isinstance(image_result, list):
            for image in image_result:
                if not isinstance(image, dict):
                    continue

                analysis = image.get("analysis")

                if analysis and isinstance(analysis, dict):
                    category = analysis.get("category")

                    if category:
                        parts.append(
                            f"Image context: {category}"
                        )

    # Audio transcription
    if audio_result and isinstance(audio_result, dict):
        audio_text = audio_result.get("text")

        if audio_text:
            parts.append(audio_text)

    return " ".join(parts)