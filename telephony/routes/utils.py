import os
import re
from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import PlainTextResponse
import httpx
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse,  Gather
from twilio.rest import Client
from . import options
from . import state
from .state import call_messages

load_dotenv()
router = APIRouter()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone = os.environ["TWILIO_PHONE_NUMBER"]

BASE_URL = 'https://7e7d77ce2da0.ngrok-free.app'


"""
Twilio will call this when the call ends (statusCallback).
You must configure the Twilio number with:
    Status Callback URL = https://<your-domain>/call-status
"""


@router.post("/message")
async def message(request: Request):
    resp = VoiceResponse()

    # fetch callSid provided in the redirect
    call_sid = request.query_params.get('CallSid')

    default_body = 'Check our platform for your specific form on your request: '

    sms_body = call_messages.pop(call_sid, default_body) if call_sid else default_body

    resp.say('You will receive a SMS regarding your request shortly. ')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        # TODO pui linku de la frontend
        body=sms_body,
        to="+40774596204",
        from_=str(twilio_phone)
    )
    state.firstQuestion = False
    resp.redirect(url="/voice", method="POST")
    return PlainTextResponse(str(resp), status_code=200, media_type="text/xml")


@router.post("/call-status")
async def call_status(request: Request) -> PlainTextResponse:
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    duration = form.get("CallDuration")
    call_number = form.get("From", "")


    print(f"Call {call_sid} ended with status={call_status}, duration={duration}, call_number={call_number}")

    if call_status == "completed":
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{BASE_URL}/stop_call",
                    json={
                        'text': call_number
                    },
                    timeout=10
                )
            except Exception as e:
                print("Failed to forward end-of-call event:", e)

    state.firstQuestion = True
    options.message_case = 0

    return PlainTextResponse("", status_code=204)


  