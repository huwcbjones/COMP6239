# Messaging


## OpCodes
| Name | OpCode |
| ---- | ---- |
| DISPATCH | 0 |
| IDENTIFY | 2 |
| INVALID_SESSION | 9 |
| HELLO | 10 |
| UNKNOWN_ERROR | 4000 |
| UNKNOWN_OPCODE | 4001 |
| DECODE_ERROR | 4002 |
| NOT_AUTHENTICATED | 4003 |
| AUTHENTICATION_FAILED | 4004 |
| ALREADY_AUTHENTICATED | 4005 |
| RATE_LIMITED | 4008 |
| SESSION_TIMEOUT | 4009 |


## Payload Format
```json
{
  "o": "OpCode",
  "d": "dict/list of data",
  "e": "event (for OpCode 0)"
}
```

## How to Identify
Send a payload with OpCode 2 and data as follows
```json
{
  "properties": {
    "os": "your OS",
    "device": "device type"
  },
  "token": "oauth token"
}
```

## How to message
1. Open a websocket connection to: `ws(s)://$SERVER/ws`.
2. Wait for OpCode HELLO message.
3. Send IDENTIFY message.
4. Wait for READY DISPATCH event.
5. Communicate to your hearts content!


## How to send a message
Send a payload with OpCode 0 and event SEND_MESSAGE with data as follows:
```json
{
  "o": 0,
  "e": "SEND_MESSAGE",
  "d": {
    "to": "recipient's UUID",
    "message": "message content"
  }
}
```

You will then receive a `MESSAGE_SENT` with the `message_id` when the message has been sent!


## Receiving messages
Receive a payload with OpCode 0 and event `MESSAGE` with data as follows.
If the user is messaging for the first time, the event type will be `MESSAGE_REQUEST`.
The user then needs to approve or deny the request to be able to send/receive messages.
```json
{
  "o": 0,
  "e": "MESSAGE",
  "d": {
    "thread_id": "a2d40043-9282-45dd-9eab-b72588c3a6d6",
    "from": {
      "id": "sender's ID",
      "first_name": "First Name",
      "last_name": "Last Name"
    },
    "message": "Message content",
    "timestamp": "time of message"
  }
}
```

## To approve/deny a message request
POST to `/thread/$thread_id/$state`, where `$state` is either `approve` or `block`.
Only users with the `TUTOR` role can approve messages.


## To get a list of threads
GET `/thread`

## To get a messages from a thread with `$ID`
GET `/thread/$ID`