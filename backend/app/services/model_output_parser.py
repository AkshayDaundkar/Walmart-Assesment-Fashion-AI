from app.schemas.library import AiAttributes


def parse_model_output(raw_output: dict[str, object]) -> AiAttributes:
    return AiAttributes.model_validate(raw_output)
