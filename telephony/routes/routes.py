import os
import re
from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import PlainTextResponse
import httpx
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse,  Gather
from twilio.rest import Client
from .options import router as option_router
from .utils import router as utils_router
from . import options
from . import state


"""

route that gets triggered when the user calls -> listed under "When a call comes in" on the Twilio phone number

"""

router = APIRouter()
router.include_router(option_router)
router.include_router(utils_router)

@router.post("/", response_class=PlainTextResponse)
async def root_fallback():
    return PlainTextResponse("<Response><Say>Missing /voice path.</Say></Response>",
                             media_type="text/xml")



@router.post("/voice", response_class=PlainTextResponse)
async def voice(Digits:int = Form(None)) -> PlainTextResponse:
    options.message_case = 0
    resp = VoiceResponse()
    
    if Digits:
            if Digits == 1:
                resp.redirect('/handle-intent-general')
            elif Digits == 2:
                resp.redirect('/handle-intent-specific')
            elif Digits == 3:
                resp.redirect('/human-escalation-message')
    
    gather = Gather(input="dtmf", partialResultCallback="/partial", timeout="5", speechTimeout="auto")

    if state.firstQuestion:
        gather.say('Hi! Tell me what you need. For general purpose information, press one. For more specific informations, press 2. For speaking with an agent press 3.')
        state.firstQuestion = False
    else:
        gather.say('Can I help you with something else? Press one for general purpose and two for more specific.')
    
    resp.append(gather)
    resp.say("Sorry, I didn't catch that.")

    return PlainTextResponse(str(resp), media_type="text/xml")


@router.post("/partial")
async def partial(request: Request) -> PlainTextResponse:
    form = await request.form()
    print("Partial:", dict(form))
    return PlainTextResponse("", status_code=204)


