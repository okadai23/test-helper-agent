"""File handler utility module (test_helper)."""

import json
from pathlib import Path
from typing import Any, Literal

import yaml

from test_helper.utils.logger import get_logger

logger = get_logger(__name__)

EncodingType = Literal["utf-8", "cp932", "shift_jis"]


class FileHandler:
    """Generic file handler with support for multiple encodings and formats."""

    def __init__(self, encoding: EncodingType = "utf-8") -> None:
        """Initialize handler with default text encoding.

        Args:
            encoding: Default encoding used for file operations.

        """
        self.encoding = encoding
        logger.debug("FileHandler initialized", encoding=encoding)

    def read_text(
        self,
        path: str | Path,
        encoding: EncodingType | None = None,
    ) -> str:
        """Read text content from a file.

        Args:
            path: Target file path.
            encoding: Override encoding. Defaults to handler encoding.

        Returns:
            The file content as a string.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug("Reading text file", path=str(path), encoding=use_encoding)
        try:
            with path.open("r", encoding=use_encoding) as f:
                content = f.read()
            logger.info(
                "Text file read successfully",
                path=str(path),
                size=len(content),
                encoding=use_encoding,
            )
            return content
        except FileNotFoundError:
            logger.error("File not found", path=str(path))
            raise
        except UnicodeDecodeError as e:
            logger.error(
                "Failed to decode file",
                path=str(path),
                encoding=use_encoding,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error("Error reading file", path=str(path), error=str(e))
            raise
        else:
            return content

    def write_text(
        self,
        path: str | Path,
        content: str,
        encoding: EncodingType | None = None,
        create_parents: bool = True,
    ) -> None:
        """Write text content to a file.

        Args:
            path: Target file path.
            content: Text content to write.
            encoding: Override encoding. Defaults to handler encoding.
            create_parents: Create parent directories when missing.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug(
            "Writing text file",
            path=str(path),
            encoding=use_encoding,
            content_length=len(content),
        )
        try:
            if create_parents and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Created parent directories", path=str(path.parent))
            with path.open("w", encoding=use_encoding) as f:
                f.write(content)
            logger.info(
                "Text file written successfully",
                path=str(path),
                size=len(content),
                encoding=use_encoding,
            )
        except UnicodeEncodeError as e:
            logger.error(
                "Failed to encode content",
                path=str(path),
                encoding=use_encoding,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error("Error writing file", path=str(path), error=str(e))
            raise

    def read_json(
        self,
        path: str | Path,
        encoding: EncodingType | None = None,
    ) -> Any:
        """Read and parse JSON file.

        Args:
            path: JSON file path.
            encoding: Override encoding. Defaults to handler encoding.

        Returns:
            Parsed Python object.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug("Reading JSON file", path=str(path), encoding=use_encoding)
        try:
            content = self.read_text(path, encoding=use_encoding)  # type: ignore[arg-type]
            data = json.loads(content)
            logger.info(
                "JSON file parsed successfully",
                path=str(path),
                data_type=type(data).__name__,
            )
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON format",
                path=str(path),
                error=str(e),
                line=e.lineno,
                column=e.colno,
            )
            raise
        else:
            return data

    def write_json(
        self,
        path: str | Path,
        data: Any,
        encoding: EncodingType | None = None,
        indent: int = 2,
        ensure_ascii: bool = False,
        sort_keys: bool = False,
        create_parents: bool = True,
    ) -> None:
        """Serialize data and write as JSON.

        Args:
            path: Output file path.
            data: Serializable data.
            encoding: Override encoding. Defaults to handler encoding.
            indent: JSON indent size.
            ensure_ascii: Escape non-ASCII when True.
            sort_keys: Sort keys in output.
            create_parents: Create directories as needed.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug(
            "Writing JSON file",
            path=str(path),
            encoding=use_encoding,
            data_type=type(data).__name__,
        )
        try:
            json_content = json.dumps(
                data,
                indent=indent,
                ensure_ascii=ensure_ascii,
                sort_keys=sort_keys,
            )
            self.write_text(
                path,
                json_content,
                encoding=(
                    use_encoding
                    if use_encoding in ["utf-8", "cp932", "shift_jis"]
                    else "utf-8"
                ),  # type: ignore[arg-type]
                create_parents=create_parents,
            )
            logger.info("JSON file written successfully", path=str(path))
        except TypeError as e:
            logger.error(
                "Failed to serialize data to JSON",
                path=str(path),
                data_type=type(data).__name__,
                error=str(e),
            )
            raise

    def read_yaml(
        self,
        path: str | Path,
        encoding: EncodingType | None = None,
    ) -> Any:
        """Read and parse YAML file.

        Args:
            path: YAML file path.
            encoding: Override encoding. Defaults to handler encoding.

        Returns:
            Parsed Python object.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug("Reading YAML file", path=str(path), encoding=use_encoding)
        try:
            content = self.read_text(path, encoding=use_encoding)  # type: ignore[arg-type]
            data = yaml.safe_load(content)
            logger.info(
                "YAML file parsed successfully",
                path=str(path),
                data_type=type(data).__name__,
            )
        except yaml.YAMLError as e:
            logger.error("Invalid YAML format", path=str(path), error=str(e))
            raise
        else:
            return data

    def write_yaml(
        self,
        path: str | Path,
        data: Any,
        encoding: EncodingType | None = None,
        default_flow_style: bool = False,
        sort_keys: bool = False,
        create_parents: bool = True,
    ) -> None:
        """Serialize data and write as YAML.

        Args:
            path: Output file path.
            data: Serializable data.
            encoding: Override encoding. Defaults to handler encoding.
            default_flow_style: Use flow style when True.
            sort_keys: Sort keys in output.
            create_parents: Create directories as needed.

        """
        path = Path(path)
        use_encoding = encoding or self.encoding
        logger.debug(
            "Writing YAML file",
            path=str(path),
            encoding=use_encoding,
            data_type=type(data).__name__,
        )
        try:
            yaml_content = yaml.dump(
                data,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=True,
            )
            self.write_text(
                path,
                yaml_content,
                encoding=(
                    use_encoding
                    if use_encoding in ["utf-8", "cp932", "shift_jis"]
                    else "utf-8"
                ),  # type: ignore[arg-type]
                create_parents=create_parents,
            )
            logger.info("YAML file written successfully", path=str(path))
        except yaml.YAMLError as e:
            logger.error(
                "Failed to serialize data to YAML",
                path=str(path),
                data_type=type(data).__name__,
                error=str(e),
            )
            raise


_default_handler = FileHandler(encoding="utf-8")


def read_text(path: str | Path, encoding: EncodingType = "utf-8") -> str:
    """Read a text file."""
    return _default_handler.read_text(path, encoding)


def write_text(
    path: str | Path,
    content: str,
    encoding: EncodingType = "utf-8",
    create_parents: bool = True,
) -> None:
    """Write a text file."""
    _default_handler.write_text(path, content, encoding, create_parents)


def read_json(path: str | Path, encoding: EncodingType = "utf-8") -> Any:
    """Read a JSON file."""
    return _default_handler.read_json(path, encoding)


def write_json(
    path: str | Path,
    data: Any,
    encoding: EncodingType = "utf-8",
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    create_parents: bool = True,
) -> None:
    """Write a JSON file."""
    _default_handler.write_json(
        path,
        data,
        encoding,
        indent,
        ensure_ascii,
        sort_keys,
        create_parents,
    )


def read_yaml(path: str | Path, encoding: EncodingType = "utf-8") -> Any:
    """Read a YAML file."""
    return _default_handler.read_yaml(path, encoding)


def write_yaml(
    path: str | Path,
    data: Any,
    encoding: EncodingType = "utf-8",
    default_flow_style: bool = False,
    sort_keys: bool = False,
    create_parents: bool = True,
) -> None:
    """Write a YAML file."""
    _default_handler.write_yaml(
        path,
        data,
        encoding,
        default_flow_style,
        sort_keys,
        create_parents,
    )
