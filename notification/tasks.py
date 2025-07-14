from .worker import celery_worker
from .email_service import emailservice
from .sms_service import send_sms_service
from sqlmodel import select
from .database import sync_session  
from .models import EmailNotificationLog,SmsNotificationLog


@celery_worker.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_notification(self, event_id, sender, receiver, title, content):
    session = sync_session()

    try:
        cur_event = session.execute(select(EmailNotificationLog).where(EmailNotificationLog.event_id == event_id))
        event = cur_event.scalar_one_or_none()

        if not event:
            return {"error": "Notification log not found"}

        status_code = emailservice(sender, receiver, title, content)

        if status_code == 202:
            event.state = "sent"
            session.add(event)
            session.commit()
            return {"message": "Notification sent successfully"}

        if self.request.retries >= self.max_retries:
            event.state = "failed"
            session.add(event)
            session.commit()
            return {"error": "Max retries exceeded. Notification marked as failed."}

        raise self.retry(exc=Exception(f"Email failed with status {status_code}"))

    except Exception as e:
        session.rollback()

        if self.request.retries >= self.max_retries:
            event = session.execute(select(EmailNotificationLog).where(EmailNotificationLog.event_id == event_id)).scalar_one_or_none()
            if event:
                event.state = "failed"
                session.add(event)
                session.commit()
            return {"error": f"Retry limit reached. Final failure. Reason: {str(e)}"}

        raise self.retry(exc=e)

    finally:
        session.close()


@celery_worker.task(bind=True,max_retries=3,default_retry_delay=10)
def send_sms_task(self,event_id,receiver,message):
    session = sync_session()

    try:
        query = session.execute(select(SmsNotificationLog).where(SmsNotificationLog.event_id == event_id))
        event = query.scalar_one_or_none()

        if not event:
            return {"error":"An error occured"}
        
        result = send_sms_service(receiver,message)

        status = result.get("status") if result else None

        if result and  status == "success":
            event.state = "sent"
            session.add(event)
            session.commit()

            return {"message":"message delivered successfully"}
        
        if self.request.retries  >= self.max_retries:
            event.state = "failed"
            session.add(event)
            session.commit()

            return {"error": "Max retries exceeded. Notification marked as failed."}
        
        raise self.retry(exc=Exception(f"sms still in {status}"))
    
    except Exception as e:
        session.rollback()

        if self.request.retries >= self.max_retries:
            query = session.execute(select(SmsNotificationLog).where(SmsNotificationLog.event_id == event_id))
            event = query.scalar_one_or_none()

            event.state = "failed"
            session.add(event)
            session.commit()
            return {"error": "Max retries exceeded. Notification marked as failed."}


        raise self.retry(exc=e)
    
    finally:
        session.close()

        



    


    


