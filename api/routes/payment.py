from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from uuid import UUID
import razorpay
import os
import time
import json
from dotenv import load_dotenv

from DB.deps import get_db
from DB.db_models import Plan, UserSubscription, User
from auth.deps import get_current_user

load_dotenv()

router = APIRouter(prefix="/payment", tags=["Payment"])

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ============================= #
# 💰 ONE-TIME PAYMENT SYSTEM   #
# ============================= #

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
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Skip payment for free plan
    if plan.price == 0:
        result, _ = await upgrade_plan_direct(user, plan, request.subscription_type, db)
        return result
    
    # Calculate amount based on subscription type
    amount = int(plan.price * 100)
    currency = "INR"
    
    # Create Razorpay order
    order_data = {
        "amount": amount,
        "currency": currency,
        "receipt": f"plan_{request.plan_id}_{int(time.time())}",
        "notes": {
            "user_id": str(user.id),
            "plan_id": str(request.plan_id),
            "subscription_type": str(request.subscription_type)
        }
    }
    
    try:
        order = await run_in_threadpool(lambda: client.order.create(data=order_data))
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
        
        # Extract plan info from order notes
        plan_id = int(order["notes"]["plan_id"])
        subscription_type = order["notes"]["subscription_type"]
        
        # Get plan
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Upgrade user plan (this handles subscription creation/update)
        result, subscription = await upgrade_plan_direct(user, plan, subscription_type, db)
        
        # Update subscription with payment details
        subscription.razorpay_order_id = request.razorpay_order_id
        subscription.razorpay_payment_id = request.razorpay_payment_id
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

# ============================ #
# 🔁 RECURRING SUBSCRIPTIONS  #
# ============================ #

class CreateSubscriptionRequest(BaseModel):
    plan_id: int
    subscription_type: str  # monthly, yearly

@router.post("/create-subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a recurring subscription for a user"""
    # 1️⃣ Validate plan
    plan = db.query(Plan).filter(Plan.id == request.plan_id, Plan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 2️⃣ Handle free plan instantly (no Razorpay)
    if plan.price == 0:
        result, _ = await upgrade_plan_direct(user, plan, request.subscription_type, db)
        return result

    # 3️⃣ Validate subscription type
    if request.subscription_type not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="subscription_type must be 'monthly' or 'yearly'")

    # 4️⃣ Check if user already has an active subscription
    existing_sub = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user.id, UserSubscription.is_active == True)
        .first()
    )

    # If yes → cancel it both in Razorpay and locally
    if existing_sub:
        try:
            if existing_sub.razorpay_subscription_id:
                await run_in_threadpool(
                    lambda: client.subscription.cancel(existing_sub.razorpay_subscription_id)
                )
                print(f"🛑 Cancelled old Razorpay subscription {existing_sub.razorpay_subscription_id}")
        except Exception as e:
            print(f"⚠️ Razorpay cancellation failed (might already be cancelled): {str(e)}")

        # Deactivate locally
        existing_sub.is_active = False
        existing_sub.payment_status = "cancelled"
        existing_sub.end_date = datetime.now(timezone.utc)
        db.commit()

    # 5️⃣ Create a new Razorpay plan
    plan_payload = {
        "period": "monthly" if request.subscription_type == "monthly" else "yearly",
        "interval": 1,
        "item": {
            "name": f"{plan.name} Plan ({request.subscription_type})",
            "amount": int(plan.price * 100),
            "currency": "INR",
        },
    }

    razorpay_plan = await run_in_threadpool(lambda: client.plan.create(data=plan_payload))

    # Total billing cycles: 12 for monthly (1 year), 1 for yearly
    total_count = 12 if request.subscription_type == "monthly" else 1

    # 6️⃣ Create new subscription on Razorpay
    sub_payload = {
        "plan_id": razorpay_plan["id"],
        "total_count": total_count,
        "customer_notify": 1,
        "notes": {
            "user_id": str(user.id),
            "plan_id": str(plan.id),
            "subscription_type": request.subscription_type,
        },
    }

    subscription = await run_in_threadpool(lambda: client.subscription.create(data=sub_payload))

    # 7️⃣ Save new subscription in DB
    new_sub = UserSubscription(
        user_id=user.id,
        plan_id=plan.id,
        razorpay_plan_id=razorpay_plan["id"],
        razorpay_subscription_id=subscription["id"],
        subscription_type=request.subscription_type,
        is_active=False,  # will be activated via webhook
        payment_status="created",
    )
    db.add(new_sub)
    db.commit()

    print(f"✅ Created new subscription {subscription['id']} for user {user.email}")

    return {
        "subscription_id": subscription["id"],
        "plan_id": razorpay_plan["id"],
        "amount": plan.price,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID,
    }


# ============================ #
# 💬 WEBHOOK EVENTS HANDLER    #
# ============================ #

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhook events (Live + Test compatible)"""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        # ✅ Verify webhook authenticity
        client.utility.verify_webhook_signature(
            body.decode("utf-8"), signature, RAZORPAY_WEBHOOK_SECRET
        )

        data = json.loads(body.decode("utf-8"))
        event = data.get("event")
        print(f"📩 Webhook event received: {event}")

        # --- Subscription success/renewal ---
        if event in ["subscription.activated", "subscription.charged", "invoice.paid"]:
            sub_entity = data["payload"]["subscription"]["entity"]
            sub_id = sub_entity["id"]
            next_due = sub_entity.get("current_end")

            notes = sub_entity.get("notes", {})
            user_id = notes.get("user_id")
            plan_id = notes.get("plan_id")

            if not user_id:
                print("⚠️ Missing user_id in notes — skipping update.")
                return {"status": "ignored"}

            # UUID-safe conversion
            try:
                user_uuid = UUID(user_id)
            except Exception:
                print("⚠️ Invalid user_id format in notes.")
                return {"status": "invalid_user_id"}

            subscription = db.query(UserSubscription).filter(
                UserSubscription.razorpay_subscription_id == sub_id
            ).first()

            if not subscription:
                print(f"⚠️ Subscription {sub_id} not found.")
                return {"status": "not_found"}

            if subscription.payment_status == "active":
                return {"status": "already_active"}

            subscription.is_active = True
            subscription.payment_status = "active"
            subscription.start_date = subscription.start_date or datetime.now(timezone.utc)
            subscription.next_billing_date = (
                datetime.fromtimestamp(next_due, tz=timezone.utc) if next_due else None
            )

            user = db.query(User).filter(User.id == user_uuid).first()
            if user:
                plan = db.query(Plan).filter(Plan.id == plan_id).first()
                if plan:
                    user.plan = plan.name
                    print(f"✅ Updated {user.email} to plan {plan.name}")

            db.commit()
            return {"status": "updated"}

        # --- Subscription cancellation or end ---
        elif event in ["subscription.cancelled", "subscription.completed", "subscription.halted", "subscription.paused"]:
            sub_entity = data["payload"]["subscription"]["entity"]
            sub_id = sub_entity["id"]

            subscription = db.query(UserSubscription).filter(
                UserSubscription.razorpay_subscription_id == sub_id
            ).first()
            if subscription:
                subscription.is_active = False
                subscription.payment_status = "cancelled"
                db.commit()
            return {"status": "cancelled"}

        # --- Payment failed ---
        elif event == "payment.failed":
            payment_entity = data["payload"]["payment"]["entity"]
            order_id = payment_entity.get("order_id")

            subscription = db.query(UserSubscription).filter(
                UserSubscription.razorpay_order_id == order_id
            ).first()
            if subscription:
                subscription.payment_status = "failed"
                db.commit()
            return {"status": "failed"}

        return {"status": "ignored", "event": event}

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

# ============================ #
# 💳 CREDIT TOP-UP SYSTEM      #
# ============================ #

class CreateCreditOrderRequest(BaseModel):
    credits: int  # between 10 and 50

@router.post("/create-credit-order")
async def create_credit_order(
    request: CreateCreditOrderRequest,
    user=Depends(get_current_user)
):
    """Create Razorpay order for manual credit purchase"""
    if request.credits < 10 or request.credits > 50:
        raise HTTPException(status_code=400, detail="Credits must be between 10 and 50")

    amount = request.credits * 2 * 100  # ₹2 per credit → in paisa

    # Razorpay requires receipt length <= 40
    short_user = str(user.id).split("-")[0]  # first 8 chars of UUID
    receipt = f"cr_{short_user}_{int(time.time())}"
    if len(receipt) > 40:
        receipt = receipt[:40]

    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": receipt,
        "notes": {"user_id": str(user.id), "credits": str(request.credits)},
    }

    order = await run_in_threadpool(lambda: client.order.create(data=order_data))
    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": RAZORPAY_KEY_ID,
    }

class VerifyCreditPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/verify-credit-payment")
async def verify_credit_payment(
    request: VerifyCreditPaymentRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify credit purchase payment and add credits to user account"""
    try:
        # Verify payment signature
        await run_in_threadpool(lambda: client.utility.verify_payment_signature({
            "razorpay_order_id": request.razorpay_order_id,
            "razorpay_payment_id": request.razorpay_payment_id,
            "razorpay_signature": request.razorpay_signature
        }))

        # Get order details from Razorpay
        order = await run_in_threadpool(lambda: client.order.fetch(request.razorpay_order_id))
        
        # Extract credit info from order notes
        credits = int(order["notes"]["credits"])
        
        # Add credits to user account
        user.credits = user.credits + credits
        db.commit()
        
        return {
            "message": f"Payment verified and {credits} credits added to your account!",
            "total_credits": user.credits
        }
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

# Helper function for plan upgrades
async def upgrade_plan_direct(user, plan, subscription_type: str, db: Session):
    """Direct plan upgrade without payment (for free plans or after payment verification)
    Returns: (result_dict, subscription_object)
    """
    
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
    
    # Query for existing subscription (not using relationship to avoid ambiguity)
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.is_active == True
    ).first()
    
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
        subscription = new_sub  # Set subscription to the newly created one
        user.plan = plan.name
    
    db.commit()
    
    result = {
        "message": f"Upgraded to {plan.name} ({subscription_type}) plan successfully!",
        "start_date": start_date,
        "end_date": end_date
    }
    
    return result, subscription
