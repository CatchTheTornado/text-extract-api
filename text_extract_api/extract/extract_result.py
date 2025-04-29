from typing import Callable, Any

"""
IMPORTANT INFORMATION ABOUT THIS CLASS:

This is not the final version of the object, namespace, or intended use. 

For this reason, I am not creating an interface, etc. Add code here as soon as possible 
along with further integrations, and once we have gained sufficient experience, we will 
undertake a refactor.

Currently, the object's purpose is to replace the use of a primitive type, a string, for 
extract returns. The limitation of this approach became evident when returning only the 
resulting string caused us to lose valuable metadata about the document. Thanks to this 
class, we retain DoclingDocument and foresee that other converters/OCRs may have similar 
metadata.
"""


class ExtractResult:
    def __init__(self, value: Any, text_gatherer: Callable[[Any], str] = None):
        """
        Initializes a UnifiedText instance.

        Args:
            value (Any): The object containing or representing the text.
            text_gatherer (Callable[[Any], str], optional): A callable that extracts text
                from the `data`. Defaults to the `_default_text_gatherer`.

        Raises:
            ValueError: If `text_gatherer` is not callable or not provided when `value` is not a string.

        Examples:
            Using the default text gatherer

            >>> unified = ExtractResult("Example text")
            >>> print(unified.text())
            Example text

            Using a custom text gatherer

            >>> def custom_gatherer(value): return f"Custom: {value}"
            >>> unified = ExtractResult(123, custom_gatherer)
            >>> print(unified.text())
            Custom: 123
        """

        if text_gatherer is not None and not callable(text_gatherer):
            raise ValueError(
                "The `text_gatherer` provided to UnifiedText must be a callable."
            )

        if not isinstance(value, str) and not callable(text_gatherer):
            raise ValueError(
                "If `value` is not a string, `text_gatherer` must be provided."
            )

        self.value = value
        self.text_gatherer = text_gatherer or self._default_text_gatherer

    @staticmethod
    def from_text(value: str) -> "ExtractResult":
        return ExtractResult(value)

    @property
    def text(self) -> str:
        """
        Retrieves text using the text gatherer.

        Returns:
            str: The extracted text from `value`.
        """
        return self.text_gatherer(self.value)

    @staticmethod
    def _default_text_gatherer(value: Any) -> str:
        """
        Default method to extract str from str.
        So it just return value, obviously.

        Args:
            value (Any): The input value.

        Returns:
            str: The text representation of the input value.

        Raises:
            TypeError: If the `value` is not a string.
        """
        if isinstance(value, str):
            return value
        raise TypeError("Default text gatherer only supports strings.")
