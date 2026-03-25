# routers/requests.py
# All API routes for help requests

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/requests", tags=["Requests"])


# ─────────────────────────────────────────────
# POST /api/requests/
# Create a new help request (elder only)
# ─────────────────────────────────────────────
@router.post("/", response_model=schemas.RequestOut, status_code=201)
def create_request(
    req_data: schemas.RequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Only elders can create requests
    if current_user.role != "elder":
        raise HTTPException(status_code=403, detail="Only elders can create help requests")

    new_request = models.HelpRequest(
        title=req_data.title,
        description=req_data.description,
        category=req_data.category,
        location=req_data.location,
        elder_id=current_user.id,
        status="pending",
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


# ─────────────────────────────────────────────
# GET /api/requests/
# List all requests — supports filtering by status and category
# ─────────────────────────────────────────────
@router.get("/", response_model=List[schemas.RequestOut])
def list_requests(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.HelpRequest)

    if status:
        query = query.filter(models.HelpRequest.status == status)
    if category:
        query = query.filter(models.HelpRequest.category == category)

    return query.order_by(models.HelpRequest.created_at.desc()).all()


# ─────────────────────────────────────────────
# GET /api/requests/my
# Get requests created by the logged-in elder
# ─────────────────────────────────────────────
@router.get("/my", response_model=List[schemas.RequestOut])
def my_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == "elder":
        return db.query(models.HelpRequest)\
            .filter(models.HelpRequest.elder_id == current_user.id)\
            .order_by(models.HelpRequest.created_at.desc()).all()
    else:
        # Volunteers see the requests they've accepted
        return db.query(models.HelpRequest)\
            .filter(models.HelpRequest.volunteer_id == current_user.id)\
            .order_by(models.HelpRequest.created_at.desc()).all()


# ─────────────────────────────────────────────
# GET /api/requests/{id}
# Get a single request by ID
# ─────────────────────────────────────────────
@router.get("/{request_id}", response_model=schemas.RequestOut)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    req = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


# ─────────────────────────────────────────────
# PATCH /api/requests/{id}/accept
# Volunteer accepts a pending request
# ─────────────────────────────────────────────
@router.patch("/{request_id}/accept", response_model=schemas.RequestOut)
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "volunteer":
        raise HTTPException(status_code=403, detail="Only volunteers can accept requests")

    req = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request is not pending")

    req.status = "accepted"
    req.volunteer_id = current_user.id
    db.commit()
    db.refresh(req)
    return req


# ─────────────────────────────────────────────
# PATCH /api/requests/{id}/complete
# Mark a request as completed (volunteer or elder)
# ─────────────────────────────────────────────
@router.patch("/{request_id}/complete", response_model=schemas.RequestOut)
def complete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    req = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "accepted":
        raise HTTPException(status_code=400, detail="Request must be accepted first")
    # Only assigned volunteer or elder who owns it can complete
    if current_user.id not in [req.volunteer_id, req.elder_id]:
        raise HTTPException(status_code=403, detail="Not authorized")

    req.status = "completed"
    db.commit()
    db.refresh(req)
    return req


# ─────────────────────────────────────────────
# DELETE /api/requests/{id}
# Elder deletes their own pending request
# ─────────────────────────────────────────────
@router.delete("/{request_id}", status_code=204)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    req = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.elder_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your request")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot delete an accepted or completed request")

    db.delete(req)
    db.commit()


# ─────────────────────────────────────────────
# POST /api/requests/{id}/messages
# Send a message related to a request (basic chat)
# ─────────────────────────────────────────────
@router.post("/{request_id}/messages", response_model=schemas.MessageOut, status_code=201)
def send_message(
    request_id: int,
    msg: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    req = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    new_msg = models.Message(
        request_id=request_id,
        sender_id=current_user.id,
        content=msg.content,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


# ─────────────────────────────────────────────
# GET /api/requests/{id}/messages
# Get all messages for a request
# ─────────────────────────────────────────────
@router.get("/{request_id}/messages", response_model=List[schemas.MessageOut])
def get_messages(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Message)\
        .filter(models.Message.request_id == request_id)\
        .order_by(models.Message.created_at.asc()).all()
