# COMP6239
Mobile Applications Development


## API
* `POST /register`: register for account

* `GET /student/$ID/profile`: get profile for student `$ID`
* `POST /student/$ID/profile`: update profile for student `$ID`

* `GET /tutor/$ID/profile`: get profile for tutor `$ID`
* `POST /tutor/$ID/profile`: edit profile for tutor `$ID`

* `GET /search/tutors`: search tutors
* `GET /student/tutors`: get student's tutors
* `GET /student/requests`: get student's outgoing requests

* `GET /tutor/requests`: get tutor's tutee requests
* `GET /tutor/requests/$ID`: get a tutee request with `$ID`
* `POST /tutor/requests/$ID`: accept/reject a tutee request with `$ID`
* `GET /tutor/tutees`: get tutor's current tutees

* `GET /admin/tutors`: get a list of tutors awaiting approval
* `POST /admin/tutor/$ID`: approval tutor with `$ID`

* `GET /subject`: get a list of subjects
* `PUT /subject`: put a new subject
* `DELETE /subject/$ID`: delete subject with `$ID`



* `ws://*/message_gateway`