from nextcord.types.base_flag import IntFlags, flag_value


class ExampleFlags(IntFlags):
    flags = ["ONE", "TWO"]

    @flag_value(0)
    def ONE(self):
        ...

    @flag_value(1)
    def TWO(self):
        ...


def test_flag_can_set():
    flags = ExampleFlags()
    flags.ONE = True
    assert flags.ONE is True, "Flag value was not set"
    assert flags.TWO is False, "Flag value impacted other flags"


def test_unknown_flag_should_error():
    try:
        ExampleFlags(three=True)
    except ValueError:
        ...
    else:
        assert False, "Providing with unknown flags should error"


def test_initial_values():
    flags = ExampleFlags(one=True, two=False)
    assert flags.ONE is True, "Flag value was not set"
    assert flags.TWO is False, "Flag value impacted other flags"


def test_flag_values():
    flags = ExampleFlags(one=True)
    assert flags.value == 1, "Flag value should be one"
