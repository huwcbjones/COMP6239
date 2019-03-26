# API Objects #

## Contents
* [API](api.md)
* Endpoints
  * [/student](student.md)
* Objects
  * [Enumerations](#enumerations)
    * [Gender](#gender)
    * [Role](#role)
  * [User](#user)
    * [Student](#student)
  * [Subject](#subject)

## Enumerations

### Gender
| Name | Value | Description |
| --- | --- | --- |
| MALE | `m` | |
| FEMALE | `f` | |
| NOT_SAY | `n` | |

### Role
| Name | Value | Description |
| --- | --- | --- |
| ADMIN | `a` | |
| STUDENT | `s` | |
| TUTOR | `t` | |

## User
| Field | Type | Description |
| --- | --- | --- |
| `id` | UUID | ID of user |
| `first_name` | String | User's first name |
| `last_name` | String | User's last name |
| `email` | String | User's email address (visible only to user) |
| `role` | [Role](#role) | Role |
| `gender` | [Gender](#gender) | Gender |
| `location` | String | Location of student |


### Student
Extends [User](#user)

| Field | Type | Description |
| --- | --- | --- |
| `subjects` | List[[Subject](#subject)] | List of subjects |

## Subject

| Field | Type | Description |
| --- | --- | --- |
| `id` | UUID | Subject ID |
| `name` | String | Subject name |