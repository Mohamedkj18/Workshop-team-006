from db.database import init_db
init_db()

from fastapi import FastAPI
from routers import buffer, profile, reply
from apscheduler.schedulers.background import BackgroundScheduler
from db.database import SessionLocal
from db.models import StyleEmailBuffer
from services.buffer_handler import check_and_learn

app = FastAPI()

app.include_router(buffer.router)
app.include_router(profile.router)
app.include_router(reply.router)

# Background job to check all user buffers every 10 minutes
def scheduled_style_learning():
    print("[ScheduledLearning]: Running")
    db = SessionLocal()
    user_ids = db.query(StyleEmailBuffer.user_id).distinct()
    for row in user_ids:
        try:
            check_and_learn(row.user_id)
        except Exception as e:
            print(f"[ScheduledLearning] Error processing {row.user_id}: {e}")
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_style_learning, 'interval', minutes=10)
scheduler.start()