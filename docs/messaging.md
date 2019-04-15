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