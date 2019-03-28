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
* subjects (list of subject IDs)

### /student/`$ID`/profile
__GET__ profile for student with `$ID`
See [Objects/Student](objects.md#student)

### /student/profile/subjects
### /student/`$ID`/profile/subjects
__GET__ current student's or subjects for student with `$ID`
See [Objects/Student](objects.md#student)

### /student/profile/subject
__POST__ add subject(s) to student. Send a list of IDs
E.g.:
```json
[
  "id",
  "id"
]
```

### /student/profile/subject
__DELETE__ remove subject(s) from student. Send a list of IDs
E.g.:
```json
[
  "id",
  "id"
]
```