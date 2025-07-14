from fastapi import APIRouter,HTTPException,status,Depends
from .models import UserCreate,User,UserResponse,EmailCreate,EmailNotificationLog,NotificationSettings,SmsCreate,NotificationResponse,SmsNotificationLog
from .database import get_session
from sqlmodel import select, or_
from .tasks import send_email_notification,send_sms_task


register = APIRouter(prefix="/api/notifications/register", tags = ["Registration endpoints"])
notifications = APIRouter(prefix= "/api/notifications/send", tags = ["Notification endpoints"])


@register.post('/',response_model=UserResponse)
async def register_user(user:UserCreate,session = Depends(get_session)):
    # build query based on provided params
    # query = select(User)
    if user.email:
        # query = query.where(User.email ==)

        check_email = select(User).where(User.email == user.email)   
        result_email = await session.exec(check_email)

        
        if result_email.first():
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail="Email already exist")

    if user.phone_number:
        check_phone = select(User).where(User.phone_number == user.phone_number)
        result_phone = await session.exec(check_phone)

        if result_phone.first():
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail="Phone number already exist")


    cur_user = User(**user.model_dump(exclude_none=True,exclude_unset=True))
    session.add(cur_user)
    await session.commit()
    await session.refresh(cur_user)


    return cur_user



@notifications.post('/email',response_model=NotificationResponse)
async def send_email(data: EmailCreate, session=Depends(get_session)):
    
    result = await session.exec(select(User.id).where(User.email == data.receiver))
    user_id = result.one_or_none()

    if not user_id:
        raise HTTPException(status_code=404, detail="Receiver not found")

    opt_result = await session.exec(
        select(NotificationSettings.opt_in).where(NotificationSettings.user_id == user_id)
    )
    opt_in = opt_result.one_or_none()

    if opt_in is False:
        return {"message": "User has opted out of email notifications"}

    cur_log = EmailNotificationLog(**data.model_dump(exclude_none=True))
    session.add(cur_log)
    await session.commit()
    await session.refresh(cur_log)

    send_email_notification.delay(
        event_id=cur_log.event_id,
        sender=data.sender,
        receiver=data.receiver,
        title=data.title,
        content=data.content
    )

    return  NotificationResponse(
        message = "Email is being processed",
        event_id= cur_log.event_id
    )

@notifications.post("/sms")
async def send_sms(data:SmsCreate,session = Depends(get_session)):

    query = await session.exec(select(User.id).where(User.phone_number == data.receiver))
    result = query.one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail="Receiver not found")
    

    cur_log = SmsNotificationLog(**data.model_dump(exclude_none=True,exclude_unset=True))
    session.add(cur_log)
    await session.commit()
    await session.refresh(cur_log)

    send_sms_task.delay(
        event_id = cur_log.event_id,
        receiver = data.receiver,
        message = data.message
    )

    return  NotificationResponse(
        message = "sms is being processed",
        event_id= cur_log.event_id
    )







