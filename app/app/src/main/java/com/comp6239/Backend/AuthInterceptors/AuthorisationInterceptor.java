package com.comp6239.Backend.AuthInterceptors;

import android.util.Base64;

import com.comp6239.Backend.Authorisation;
import com.comp6239.Backend.AuthorisationRequest;
import com.comp6239.Backend.BackEndService;
import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Session;

import java.io.IOException;

import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

public class AuthorisationInterceptor implements Interceptor {
    private Session session;

    public AuthorisationInterceptor(Session session) {
        this.session = session;
    }

    @Override
    public Response intercept(Chain chain) throws IOException {

        Request request = chain.request();

        if(session.getToken() != null) {
            request = request.newBuilder()
                    .addHeader("Authorization", "Bearer " + session.getToken())
                    .build();
        }

        Response response = chain.proceed(request);
        return response;

    }

    /*
    Cyclic dependency
    @Override
    public Response intercept(Chain chain) throws IOException {
        //If auth token exists, then go ahead and attach it
        Response mainResponse; //TODO: try this without the clause first I guess, might not need it
        //if(session.getToken() != null) {
        //    mainResponse = chain.proceed(chain.request().newBuilder().addHeader("Authorization", "Bearer " + session.getToken()).build());
       // } else {
            mainResponse = chain.proceed(chain.request());
        //}

        Request mainRequest = chain.request();

        if (session.isLoggedIn()) {
            // if response code is 401 or 403, 'mainRequest' has encountered authentication error
            if (mainResponse.code() == 401 || mainResponse.code() == 403) {

                AuthorisationRequest authRequest = new AuthorisationRequest();
                authRequest.setUsername(session.getEmail());
                authRequest.setPassword(session.getPassword());
                authRequest.setGrant_type("password");


                // request to login API to get fresh token
                // synchronously calling login API
                retrofit2.Response<Authorisation> loginResponse = apiService.loginAccount(authRequest).execute();

                if (loginResponse.isSuccessful()) {
                    // login request succeed, new token generated
                    Authorisation authorization = loginResponse.body();
                    // save the new tokens
                    session.saveToken(authorization.getToken());
                    session.saveRefreshToken(authorization.getRefreshToken());
                    // retry the 'mainRequest' which encountered an authentication error
                    // add new token into 'mainRequest' header and request again
                    Request.Builder builder = mainRequest.newBuilder().header("Authorization", "Bearer " + session.getToken()).
                            method(mainRequest.method(), mainRequest.body());
                    mainResponse = chain.proceed(builder.build());
                }
            }
        }

        return mainResponse;
    }

    */
}