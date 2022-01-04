from typing import Any
from spade.message import Message
from spade.template import Template
from enum import Enum

class Performative(Enum):
	AcceptProposal = 'accept-proposal'
	Agree = 'agree'
	Cancel = 'cancel'
	CFP = 'cfp'
	Confirm = 'confirm'
	Failure = 'failure'
	Inform = 'inform'
	Propose = 'propose'
	QueryIf = 'query-if'
	Refuse = 'refuse'
	RefuseProposal= 'refuse-proposal'
	Request = 'request'
	Query = 'query'

def setPerformative(msg: Any, performative: Performative) -> None:
	msg.set_metadata('performative', performative)

def getPerformative(msg: Any) -> Performative:
	return Performative(msg.metadata['performative'])
