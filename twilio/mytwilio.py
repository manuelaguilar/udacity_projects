#!/usr/bin/python
#number: +15142075592
#twilio number: +1 (438) 795-2199
#twilio test number: +15005550006
#account sid: ACca22dda0ce14fa204d924ce2d7acf60b

from twilio.rest import TwilioRestClient

account_sid="ACca22dda0ce14fa204d924ce2d7acf60b"
auth_token="c44968b5e6841675bda174758efd24c6"

client = TwilioRestClient(account_sid, auth_token)

message = client.sms.messages.create(
  body = "This is a test message from client.",
  to = "+15142075592",
  from_ = "+14387952199")

print message.sid

  
