from collections.abc import Callable
from typing import ClassVar, Protocol, runtime_checkable

PAYMENT_REGISTRY: dict[str, Callable[[], str]] = {}

def register(key):
    def decorator(func):
        PAYMENT_REGISTRY[key] = func
        return func
    return decorator

@register("stripe")
def process_stripe_payment() -> str:
 return "Processing Stripe payment"

@register("paypal")
def process_paypal_payment() -> str:
 return "Processing PayPal payment"

def dispatch_payment(method):
    handler = PAYMENT_REGISTRY.get(method)
    if handler:
        return handler()
    msg = f"Unknown payment method: {method}"
    raise ValueError(msg)

print(dispatch_payment("stripe"))
print(dispatch_payment("paypal"))




@runtime_checkable
class CanParse(Protocol):
    def parse(self, data: str) -> str: ...


class ParserRegistry:
    """A base class that automatically registers its subclasses."""
    _registry: ClassVar[dict[str, type[CanParse]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not isinstance(cls, CanParse):
            msg = f"{cls.__name__} must implement CanParse"
            raise TypeError(msg)
        cls._registry[cls.__class__.__name__.lower()] = type(cls)

    @classmethod
    def resolve(cls, parser_type: type[CanParse]) -> CanParse:
        """Retrieve a parser class by its format string."""
        parser_class: type[CanParse] | None = cls._registry.get(parser_type.__name__.lower())
        if not parser_class:
            msg = f"No parser registered for format: {parser_type.__name__.lower()}"
            raise ValueError(msg)
        return parser_class()

class Registry[I]:
    """A base class that automatically registers its subclasses."""
    _registry: ClassVar[dict[str, type]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not isinstance(cls, I):
            msg = f"{cls.__name__} must implement I"
            raise TypeError(msg)
        cls._registry[cls.__class__.__name__.lower()] = cls

    @classmethod
    def resolve(cls, parser_type: type[I]) -> I:
        """Retrieve a parser class by its format string."""
        parser_class: type[I] | None = cls._registry.get(parser_type.__name__.lower())
        if not parser_class:
            msg = f"No parser registered for format: {parser_type.__name__.lower()}"
            raise ValueError(msg)
        return parser_class()


# Subclasses automatically register themselves upon definition
class JSONParser(ParserRegistry, CanParse):
    def parse(self, data):
        return f"Parsing {data} as JSON"

class CSVParser(ParserRegistry, CanParse):
    def parse(self, data):
        return f"Parsing {data} as CSV"

# Usage
json_parser = ParserRegistry.resolve(JSONParser)
print(json_parser.parse("sample_data"))

csv_parser = ParserRegistry.resolve(CSVParser)
print(csv_parser.parse("sample_data"))
