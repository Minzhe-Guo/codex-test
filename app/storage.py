from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from .models import (
    Employee,
    EmployeeCreate,
    LeaveDecision,
    LeaveRequest,
    LeaveRequestCreate,
    LeaveRequestWithDecision,
    LeaveStatus,
)


class StorageError(RuntimeError):
    """Represents a generic persistence error."""


class Storage:
    """A tiny JSON-file based persistence layer for the leave system."""

    def __init__(self, data_path: Path | None = None) -> None:
        self._path = data_path or Path("data.json")
        self._data = {
            "employees": [],
            "leave_requests": [],
            "next_employee_id": 1,
            "next_leave_request_id": 1,
        }
        self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            content = json.loads(self._path.read_text())
            self._data.update(content)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Invalid data file {self._path}: {exc}") from exc

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))

    # ------------------------------------------------------------------
    # Employee operations
    def create_employee(self, payload: EmployeeCreate) -> Employee:
        employee = Employee(id=self._data["next_employee_id"], **payload.dict())
        self._data["employees"].append(employee.dict())
        self._data["next_employee_id"] += 1
        self._save()
        return employee

    def list_employees(self) -> List[Employee]:
        return [Employee(**item) for item in self._data["employees"]]

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        for item in self._data["employees"]:
            if item["id"] == employee_id:
                return Employee(**item)
        return None

    # ------------------------------------------------------------------
    # Leave requests operations
    def create_leave_request(self, payload: LeaveRequestCreate) -> LeaveRequest:
        if not self.get_employee(payload.employee_id):
            raise StorageError(f"Employee {payload.employee_id} does not exist")

        leave_request = LeaveRequest(
            id=self._data["next_leave_request_id"],
            status=LeaveStatus.PENDING,
            **payload.dict(),
        )
        request_data = leave_request.dict()
        request_data.update({"reviewer": None, "comment": None})
        self._data["leave_requests"].append(request_data)
        self._data["next_leave_request_id"] += 1
        self._save()
        return leave_request

    def list_leave_requests(self, *, employee_id: Optional[int] = None, status: Optional[LeaveStatus] = None) -> List[LeaveRequestWithDecision]:
        requests: List[LeaveRequestWithDecision] = []
        for item in self._data["leave_requests"]:
            if employee_id is not None and item["employee_id"] != employee_id:
                continue
            if status is not None and item["status"] != status:
                continue
            requests.append(LeaveRequestWithDecision(**item))
        return requests

    def get_leave_request(self, request_id: int) -> Optional[LeaveRequestWithDecision]:
        for item in self._data["leave_requests"]:
            if item["id"] == request_id:
                return LeaveRequestWithDecision(**item)
        return None

    def apply_decision(self, request_id: int, decision: LeaveDecision) -> LeaveRequestWithDecision:
        for item in self._data["leave_requests"]:
            if item["id"] == request_id:
                item.update(
                    {
                        "status": decision.status,
                        "reviewer": decision.reviewer,
                        "comment": decision.comment,
                    }
                )
                self._save()
                return LeaveRequestWithDecision(**item)
        raise StorageError(f"Leave request {request_id} does not exist")


__all__ = ["Storage", "StorageError"]

