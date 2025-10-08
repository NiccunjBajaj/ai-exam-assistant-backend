from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
import razorpay
import os
import time
from dotenv import load_dotenv

from DB.deps import db_dependency, get_db
from DB.db_models import Plan, UserSubscription
from auth.deps import get_current_user

load_dotenv()

router = APIRouter(prefix="/payment", tags=["Payment"])

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class CreateOrderRequest(BaseModel):
    plan_id: int
    subscription_type: str  # monthly, yearly

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Razorpay order for plan upgrade"""

    # Validate plan
    plan = db.query(Plan).filter(Plan.id == request.plan_id, Plan.is_active == True).first()
    print("Plan fetched:", plan)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Skip payment for free plan
    if plan.price == 0:
        return await upgrade_plan_direct(user, plan, request.subscription_type, db)
    
    # Calculate amount based on subscription type
    amount = int(plan.price * 100)
    currency = "INR"
    
    # Create Razorpay order
    order_data = {
        "amount": amount,
        "currency": currency,
        "receipt": f"plan_{request.plan_id}_{int(time.time())}",  # max ~13 chars
        "notes": {
            "user_id": str(user.id),
            "plan_id": str(request.plan_id),
            "subscription_type": str(request.subscription_type)
        }
    }
    
    try:
        order = await run_in_threadpool(lambda: client.order.create(data=order_data))
        print("Created order:", order)
        print("Order notes:", order.get("notes"))
        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.post("/verify-payment")
async def verify_payment(
    request: VerifyPaymentRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment and upgrade user plan"""
    
    try:
        # Verify payment signature
        await run_in_threadpool(lambda: client.utility.verify_payment_signature({
            "razorpay_order_id": request.razorpay_order_id,
            "razorpay_payment_id": request.razorpay_payment_id,
            "razorpay_signature": request.razorpay_signature
        }))

        
        # Get order details from Razorpay
        order = await run_in_threadpool(lambda: client.order.fetch(request.razorpay_order_id))
        
        print("Fetched order:", order)
        print("Order notes:", order.get("notes"))


        # Extract plan info from order notes
        plan_id = int(order["notes"]["plan_id"])
        subscription_type = order["notes"]["subscription_type"]
        
        # Get plan
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Upgrade user plan
        result = await upgrade_plan_direct(user, plan, subscription_type, db)
        
        # Update subscription with payment details
        subscription = user.subscription
        if subscription:
            subscription.razorpay_order_id = request.razorpay_order_id
            subscription.razorpay_payment_id = request.razorpay_payment_id
        else:
            from DB.db_models import UserSubscription
            subscription = UserSubscription(
                user_id=user.id,
                plan_id=plan.id,
                razorpay_order_id=request.razorpay_order_id,
                razorpay_payment_id=request.razorpay_payment_id,
                start_date=datetime.now(timezone.utc),
                is_active=True,
                subscription_type=subscription_type
            )
            db.add(subscription)
        db.commit()
        
        return {
            "message": "Payment verified and plan upgraded successfully!",
            "plan": plan.name,
            "subscription_type": subscription_type
        }
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhook events"""
    
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    try:
        # Verify webhook signature
        client.utility.verify_webhook_signature(
            body.decode('utf-8'),
            signature,
            RAZORPAY_WEBHOOK_SECRET
        )
        
        # Parse webhook data
        import json
        webhook_data = json.loads(body.decode('utf-8'))
        event = webhook_data.get("event")
        
        if event == "payment.captured":
            # Handle successful payment
            payment_data = webhook_data.get("payload", {}).get("payment", {})
            order_id = payment_data.get("order_id")
            
            # Find subscription by order_id
            subscription = db.query(UserSubscription).filter(
                UserSubscription.razorpay_order_id == order_id
            ).first()
            
            if subscription:
                subscription.is_active = True
                db.commit()
        
        elif event == "payment.failed":
            # Handle failed payment
            payment_data = webhook_data.get("payload", {}).get("payment", {})
            order_id = payment_data.get("order_id")
            
            # Find subscription by order_id
            subscription = db.query(UserSubscription).filter(
                UserSubscription.razorpay_order_id == order_id
            ).first()
            
            if subscription:
                subscription.is_active = False
                db.commit()
        
        return {"status": "success"}
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def upgrade_plan_direct(user, plan, subscription_type: str, db: Session):
    """Direct plan upgrade without payment (for free plans or after payment verification)"""
    
    # Determine end_date based on subscription_type
    start_date = datetime.now(timezone.utc)
    if subscription_type == "monthly":
        end_date = start_date + timedelta(days=30)
    elif subscription_type == "yearly":
        end_date = start_date + timedelta(days=365)
    elif subscription_type == "lifetime":
        end_date = None  # No expiry for lifetime
    else:
        raise HTTPException(status_code=400, detail="Invalid subscription_type")
    
    # Check if user already has a subscription
    subscription = user.subscription
    if subscription:
        subscription.plan_id = plan.id
        subscription.start_date = start_date
        subscription.end_date = end_date
        subscription.subscription_type = subscription_type
        subscription.is_active = True
        user.plan = plan.name
    else:
        new_sub = UserSubscription(
            user_id=user.id,
            plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            subscription_type=subscription_type,
            is_active=True
        )
        db.add(new_sub)
        user.plan = plan.name
    
    db.commit()
    
    return {
        "message": f"Upgraded to {plan.name} ({subscription_type}) plan successfully!",
        "start_date": start_date,
        "end_date": end_date
    }

