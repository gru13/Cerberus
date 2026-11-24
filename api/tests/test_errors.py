"""Intent: Test the CerberusError base class, including its payload."""

from typing import ClassVar

from cerberus.errors import CerberusError, ErrorPayload


class SampleError(CerberusError):
    code: ClassVar[str] = "test.sample"
    message: ClassVar[str] = "The sample step fails."
    http_status: ClassVar[int] = 409


def test_payload_has_fixed_code_and_message() -> None:
    error = SampleError(details={"run_id": "r1"})

    assert error.to_payload() == ErrorPayload(
        code="test.sample", message="The sample step fails.", details={"run_id": "r1"}
    )
    assert str(error) == "The sample step fails."
    assert error.http_status == 409


def test_details_are_copied() -> None:
    details: dict[str, str | int | float | bool | None] = {"run_id": "r1"}
    error = SampleError(details=details)
    details["run_id"] = "changed"

    assert error.details == {"run_id": "r1"}
