from typing import Dict


# for state
firstQuestion: bool = True


# for getting the message body
call_messages: Dict[str, str] = {} # used to pass the response from rasp_db to the message sending method, in the message body

