# /register Endpoints #

## Contents
* [API](api.md)
* Endpoints
  * /register
  * [/student](student.md)
* [Objects](objects.md)
  
## /register

__POST__ register an account
See [Objects/User](objects.md#user)

Required fields:
* email
* first_name
* last_name
* gender
* location
* role
* password

Please note `role` cannot be `ADMIN` (see [Role](objects.md#role)).