from typing import Optional

from ..exceptions import NextcordException


class IntFlags:
    def __init__(self, **kwargs: bool) -> None:
        self.value: int = 0

        flags: Optional[list[str]] = getattr(self, "flags", None)
        if flags is None:
            raise NextcordException("A flags attribute has to defined")  # TODO: Maybe make this a warning?

        for flag_name, flag_value in kwargs.items():
            flag_name = flag_name.upper()
            if flag_name not in flags:
                raise ValueError(f"Cannot set flag '{flag_name}' as it does not exist")
            setattr(self, flag_name, flag_value)


def flag_value(bit: int) -> bool:
    if bit < 0:
        raise ValueError("Bit cannot be less than 0")

    @property # type: ignore
    def flag(self: IntFlags) -> bool:
        return (self.value & bit) == bit

    @flag.setter
    def flag(self: IntFlags, value: bool) -> None:
        if value:
            self.value |= bit
        else:
            self.value &= ~bit

    return flag # type: ignore
