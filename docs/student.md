# /student Endpoints #

## Contents
* [API](api.md)
* Endpoints
  * /student
* [Objects](objects.md)
  
## /student

### /student/profile
__GET__ current student's profile
See [Objects/Student](objects.md#student)

### /student/profile
__POST__ update current student's profile
See [Objects/Student](objects.md#student)

Permissible fields:
* email
* first_name
* last_name
* gender
* location

### /student/`$ID`/profile
__GET__ profile for student with `$ID`
See [Objects/Student](objects.md#student)