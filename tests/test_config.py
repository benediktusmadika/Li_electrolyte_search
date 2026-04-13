from __future__ import annotations

from pathlib import Path

from extractor.config import DEFAULT_MODEL, load_api_config


def test_load_api_config_plain_key(tmp_path: Path) -> None:
    path = tmp_path / "gpt_api.txt"
    path.write_text("sk-test-key", encoding="utf-8")
    config = load_api_config(path)
    assert config.api_key == "sk-test-key"
    assert config.model == DEFAULT_MODEL


def test_load_api_config_env_style(tmp_path: Path) -> None:
    path = tmp_path / "gpt_api.txt"
    path.write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=sk-test-key",
                "MODEL=gpt-5.4",
                "REASONING_EFFORT=medium",
                "DELETE_REMOTE_FILE_AFTER_RUN=true",
            ]
        ),
        encoding="utf-8",
    )
    config = load_api_config(path)
    assert config.api_key == "sk-test-key"
    assert config.model == "gpt-5.4"
    assert config.reasoning_effort == "medium"
    assert config.delete_remote_file_after_run is True