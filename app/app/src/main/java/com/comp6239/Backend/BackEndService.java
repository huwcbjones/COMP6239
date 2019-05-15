package com.comp6239.Backend;

import com.comp6239.Backend.Messaging.MessageRequest;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Backend.Model.User;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.PUT;
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

    @POST("/thread/{id}")
    Call<MessageThread> sendMessageToThread(@Path("id") String id, @Body MessageRequest messageOnly);

    @GET("/search/tutors")
    Call<List<Tutor>> getAvailableTutors(@Query("name") String name,
                                         @Query("location") String location,
                                         @Query("price") String lowValueHighValue,
                                         @Query("q") String q);

    @GET("/student/tutors")
    Call<List<MessageThread>> getStudentsTutorConversations();

    @GET("/student/requests")
    Call<List<MessageThread>> getStudentTutorRequests();

    @GET("/tutor/tutees")
    Call<List<MessageThread>> getTutorsTuteesConversations();

    @GET("/tutor/requests")
    Call<List<MessageThread>> getTutorsStudentRequests();

    @GET("/admin/tutor")
    Call<List<Tutor>> getAwaitingApprovalTutors();

    @POST("/admin/tutor/{id}")
    Call<Void> approveTutor(@Path("id") String tutorId, @Body Tutor tutor);

    @GET("/thread/{id}")
    Call<MessageThread> getConversationThread(@Path("id") String threadId);

    @GET("/thread")
    Call<List<MessageThread>> getAllConversations();

    @POST("/thread")
    Call<Void> startConversation(@Body MessageRequest messageRequest);

    @DELETE("/subject/{id}")
    Call<Void> deleteSubject(@Path("id") String subjectId);

    @PUT("/subject")
    Call<Void> createNewSubject(@Body Subject subject);

    @POST("/thread/{id}/block")
    Call<Void> blockConversationById(@Path("id") String id);

    @POST("/thread/{id}/approve")
    Call<Void> approveConversationById(@Path("id") String id);

}
