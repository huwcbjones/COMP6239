package com.comp6239.Backend;

import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Backend.Model.User;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface BackEndService {
    @POST("/register")
    Call<User> createUser(@Body User user);

    @GET("/student/{id}/profile")
    Call<Student> getUser(@Path("id") String ID);

    @POST("/student/{id}/profile")
    Call<Student> updateStudent(@Path("id") String id, @Body Student user);

    @GET("/tutor/{id}/profile")
    Call<Tutor> getTutor(@Path("id") String ID);

    @POST("/tutor/{id}/profile")
    Call<Tutor> updateTutor(@Path("id") String id, @Body Tutor tutor);

    @POST("/oauth/token")
    Call<Authorisation> loginAccount(@Body AuthorisationRequest request);

    @GET("/student/profile")
    Call<Student> getStudentProfile();

    @GET("/profile")
    Call<User> getProfile();

    @GET("/subject")
    Call<List<Subject>> getAllSubjects();

    @GET("/search/tutors")
    Call<List<Tutor>> getAvailableTutors();

    @GET("/student/tutors")
    Call<List<Tutor>> getLoggedStudentsTutors();

    @GET("/admin/tutors")
    Call<List<Tutor>> getAwaitingApprovalTutors();


    /* TODO: Implement these
    @GET("/student/tutors")

    @GET("/student/requests")

    @GET("/tutor/requests")
    */

}
