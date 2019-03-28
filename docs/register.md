# /register Endpoints #

## Contents
* [API](api.md)
* Endpoints
    * [/register](register.md)
    * [/student](student.md)
* Objects
    * [Enumerations](#enumerations)
        * [Gender](#gender)
        * [Role](#role)
    * [User](#user)
        * [Student](#student)
    * [Subject](#subject)
  
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