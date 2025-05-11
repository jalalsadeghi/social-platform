# crud.py
from sqlalchemy.orm import Session
from modules.post.models import Post, Comment
from modules.product_queue.models import ProductQueue
from modules.payment.models import Payment
from modules.plan.models import Plan
from modules.user.models import User

def get_dashboard_report(db: Session, user_id):
    posts = db.query(Post).filter(Post.user_id == user_id).count()
    comments = db.query(Comment).join(Post).filter(Post.user_id == user_id).count()
    queue_products = db.query(ProductQueue).filter(ProductQueue.user_id == user_id).count()
    return {"posts_count": posts, "comments_count": comments, "queue_products_count": queue_products}

def update_user_profile(db: Session, user_id, data):
    user = db.query(User).filter(User.id == user_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user