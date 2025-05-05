from __future__ import annotations
import os
import yaml
import importlib
import pkgutil
from typing import Type, Dict


from extract.extract_result import ExtractResult
from text_extract_api.files.file_formats.file_format import FileFormat


class Strategy:
    _strategies: Dict[str, Strategy] = {}
    _strategy_config: Dict[str, Dict] = {}

    def __init__(self):
        self.update_state_callback = None
        self._strategy_config = None

    def set_strategy_config(self, config: Dict):
        self._strategy_config = config

    def set_update_state_callback(self, callback):
        self.update_state_callback = callback

    def update_state(self, state, meta):
        if self.update_state_callback:
            self.update_state_callback(state, meta)

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError("Strategy subclasses must implement name")

    @classmethod
    def extract_text(
        cls, file_format: Type["FileFormat"], language: str = "en"
    ) -> ExtractResult:
        raise NotImplementedError(
            "Strategy subclasses must implement extract_text method"
        )

    @classmethod
    def get_strategy(cls, name: str) -> Type["Strategy"]:
        """
        Fetches and returns a registered strategy class based on the given name.

        Args:
            name: The name of the strategy to fetch.

        Returns:
            The strategy class corresponding to the provided name.

        Raises:
            ValueError: If the specified strategy name does not exist among the registered strategies.
        """

        if name not in cls._strategies:
            cls.load_strategies_from_config()

        if name not in cls._strategies:
            cls.autodiscover_strategies()

        if name not in cls._strategies:
            available = ", ".join(cls._strategies.keys())
            raise ValueError(f"Unknown strategy '{name}'. Available: {available}")

        return cls._strategies[name]

    @classmethod
    def register_strategy(
        cls, strategy: Type["Strategy"], name: str = None, override: bool = False
    ):
        name = name or strategy.name()
        if override or name not in cls._strategies:
            cls._strategies[name] = strategy

    @classmethod
    def load_strategies_from_config(
        cls, path: str = os.getenv("OCR_CONFIG_PATH", "config/strategies.yaml")
    ):
        strategies = cls._strategies
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
        config_file_path = os.path.join(project_root, path)

        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(
                f"Config file not found at path: {config_file_path}"
            )

        with open(config_file_path, "r") as f:
            config = yaml.safe_load(f)

        if "strategies" not in config or not isinstance(config["strategies"], dict):
            raise ValueError(
                f"Missing or invalid 'strategies' section in the {config_file_path} file"
            )

        for strategy_name, strategy_config in config["strategies"].items():
            if "class" not in strategy_config:
                raise ValueError(
                    f"Missing 'class' attribute for OCR strategy: {strategy_name}"
                )

            strategy_class_path = strategy_config["class"]
            module_path, class_name = strategy_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)

            strategy = getattr(module, class_name)
            strategy_instance = strategy()
            strategy_instance.set_strategy_config(strategy_config)

            cls.register_strategy(strategy_instance, strategy_name)
            print(
                f"Loaded strategy from {config_file_path} {strategy_name} [{strategy_class_path}]"
            )

        return strategies

    @classmethod
    def autodiscover_strategies(cls) -> Dict[str, Type]:
        strategies = cls._strategies
        for module_info in pkgutil.iter_modules():
            if not module_info.name.startswith("text_extract_api"):
                continue

            try:
                module = importlib.import_module(module_info.name)
            except ImportError:
                continue

            if not hasattr(module, "__path__"):
                continue

            for submodule_info in pkgutil.walk_packages(
                module.__path__, module_info.name + "."
            ):
                if ".strategies." not in submodule_info.name:
                    continue

                try:
                    ocr_module = importlib.import_module(submodule_info.name)
                except ImportError as e:
                    print(
                        "Error loading strategy " + submodule_info.name + ": " + str(e)
                    )
                    continue
                for attr_name in dir(ocr_module):
                    attr = getattr(ocr_module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, Strategy)
                        and attr is not Strategy
                        and attr.name() not in strategies
                    ):
                        strategies[attr.name()] = attr()
                        print(
                            f"Discovered strategy {attr.name()} from {submodule_info.name} [{module_info.name}]"
                        )

        cls._strategies = strategies
