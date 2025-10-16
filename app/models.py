from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmployeeBase(BaseModel):
    name: str = Field(..., description="Employee name")
    department: Optional[str] = Field(None, description="Department name")

    @validator("name")
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Employee name cannot be empty")
        return cleaned


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int = Field(..., description="Employee identifier")


class LeaveRequestBase(BaseModel):
    employee_id: int = Field(..., description="Identifier of the employee requesting leave", ge=1)
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    reason: Optional[str] = Field(None, description="Optional leave reason", max_length=500)

    @validator("end_date")
    def validate_end_date(cls, end_date: date, values: dict[str, date]) -> date:
        start_date = values.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date cannot be before start_date")
        return end_date


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequest(LeaveRequestBase):
    id: int = Field(..., description="Leave request identifier")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING, description="Status of the leave request")


class LeaveDecision(BaseModel):
    status: LeaveStatus = Field(..., description="Decision for the leave request")
    reviewer: str = Field(..., description="Name of the reviewer handling the decision")
    comment: Optional[str] = Field(None, description="Optional comment about the decision", max_length=500)

    @validator("status")
    def validate_status(cls, status: LeaveStatus) -> LeaveStatus:
        if status == LeaveStatus.PENDING:
            raise ValueError("Decision status must be either approved or rejected")
        return status


class LeaveRequestWithDecision(LeaveRequest):
    reviewer: Optional[str] = Field(None, description="Reviewer that processed the request")
    comment: Optional[str] = Field(None, description="Decision comment")

