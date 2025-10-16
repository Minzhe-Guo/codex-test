from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query

from .models import (
    Employee,
    EmployeeCreate,
    LeaveDecision,
    LeaveRequest,
    LeaveRequestCreate,
    LeaveRequestWithDecision,
    LeaveStatus,
)
from .storage import Storage, StorageError

app = FastAPI(title="Leave Management System", version="1.0.0")


def get_storage() -> Storage:
    return Storage()


@app.post("/employees", response_model=Employee, status_code=201)
def create_employee(payload: EmployeeCreate, storage: Storage = Depends(get_storage)) -> Employee:
    """Register a new employee."""
    return storage.create_employee(payload)


@app.get("/employees", response_model=List[Employee])
def list_employees(storage: Storage = Depends(get_storage)) -> List[Employee]:
    """Return all registered employees."""
    return storage.list_employees()


@app.post("/leave-requests", response_model=LeaveRequest, status_code=201)
def submit_leave_request(
    payload: LeaveRequestCreate, storage: Storage = Depends(get_storage)
) -> LeaveRequest:
    """Submit a leave request for an employee."""
    try:
        return storage.create_leave_request(payload)
    except StorageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/leave-requests", response_model=List[LeaveRequestWithDecision])
def list_leave_requests(
    employee_id: Optional[int] = Query(None, description="Filter by employee identifier"),
    status: Optional[LeaveStatus] = Query(None, description="Filter by leave status"),
    storage: Storage = Depends(get_storage),
) -> List[LeaveRequestWithDecision]:
    """List leave requests optionally filtered by employee or status."""
    return storage.list_leave_requests(employee_id=employee_id, status=status)


@app.get("/leave-requests/{request_id}", response_model=LeaveRequestWithDecision)
def get_leave_request(request_id: int, storage: Storage = Depends(get_storage)) -> LeaveRequestWithDecision:
    """Retrieve a single leave request."""
    leave_request = storage.get_leave_request(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_request


@app.post("/leave-requests/{request_id}/decision", response_model=LeaveRequestWithDecision)
def decide_leave_request(
    request_id: int,
    decision: LeaveDecision,
    storage: Storage = Depends(get_storage),
) -> LeaveRequestWithDecision:
    """Approve or reject a leave request."""
    try:
        return storage.apply_decision(request_id, decision)
    except StorageError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app"]

