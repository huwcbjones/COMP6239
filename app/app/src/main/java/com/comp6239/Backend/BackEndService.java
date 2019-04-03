package com.comp6239.Backend;

import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Backend.Model.User;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface BackEndService {
    @POST("/register")
    Call<User> createUser(@Body User user);

    @GET("/student/{ID}/profile")
    Call<Student> getUser(@Path("ID") String ID);

    @POST("/student/{ID}/profile")
    Call<Student> updateStudent(@Path("ID") @Body Student user);

    @GET("/tutor/{ID}/profile")
    Call<Tutor> getTutor(@Path("ID") String ID);

    @POST("/tutor/{ID}/profile")
    Call<Tutor> updateTutor(@Path("ID") @Body Tutor tutor);

    /* TODO: Implement these
    @GET("/search/tutors")
    Call<List<User>> groupList(@Path("id") int groupId, @Query("sort") String sort);

    @GET("/student/tutors")

    @GET("/student/requests")

    @GET("/tutor/requests")
    */

}
