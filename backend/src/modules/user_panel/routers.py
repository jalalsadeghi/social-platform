# routers.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.user_panel import schemas, crud, services
from modules.auth.jwt import verify_token

router = APIRouter(prefix="/user", tags=["user_panel"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload['sub']

# Dashboard Reports
@router.get("/dashboard", response_model=schemas.DashboardReport)
def dashboard(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_dashboard_report(db, user_id)

# Profile Management
@router.put("/profile")
def update_profile(data: schemas.UserProfileUpdate, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.update_user_profile(db, user_id, data)

# Scraping API
@router.post("/scrape", response_model=schemas.ScrapedData)
def scrape_product(url: schemas.HttpUrl):
    return services.scrape_data_from_url(url)

# AI Content Generation
@router.post("/generate-content", response_model=schemas.AIGeneratedContent)
def generate_ai_content(product_id: UUID4, db: Session = Depends(get_db)):
    return services.generate_ai_content(db, product_id)

# Product Queue
@router.get("/queue", response_model=List[schemas.ProductQueueOut])
def list_queue_products(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_user_queue(db, user_id)

# Post Archive
@router.get("/posts/archive", response_model=List[schemas.PostArchiveOut])
def post_archive(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_posts(db, user_id)

# Comments Management
@router.get("/comments", response_model=List[schemas.CommentOut])
def user_comments(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_comments(db, user_id)

@router.post("/comments/{comment_id}/reply", response_model=schemas.CommentOut)
def reply_comment(comment_id: UUID4, reply: schemas.CommentReply, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.reply_to_comment(db, user_id, comment_id, reply.content)

# Payments
@router.post("/payment", response_model=schemas.PaymentResponse)
def initiate_payment(request: schemas.PaymentRequest, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return services.create_payment(db, user_id, request.plan_id, request.payment_method)