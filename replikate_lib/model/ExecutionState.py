from enum import Enum


class Status(Enum):
    VALID = 0
    MISSING_FIELD_ERROR = 1
    FILE_SYSTEM_ERROR = 2
    INTERNAL_ERROR = 3
    INVALID_SCRIPT_EXECUTION = 4


class ExecutionState:
    def __init__(self, status: Status, message: str):
        self.status = status
        self.message = message

    def __str__(self):
        return "ExecutionState(status={}, message={})".format(self.status, self.message)

    def __bool__(self):
        return self.status == Status.VALID

    def __or__(self, other):
        if self.status != Status.VALID:
            return other
        else:
            return self

    def __and__(self, other):
        if self.status == Status.VALID:
            return other
        else:
            return self


Ok = ExecutionState(Status.VALID, "Ok")
Cancelled = ExecutionState(Status.VALID, "Cancelled")
