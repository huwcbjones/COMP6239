package com.comp6239.Backend.AuthInterceptors;

import com.comp6239.Backend.Session;

import java.io.IOException;

import okhttp3.Interceptor;
import okhttp3.Response;

public class RenewTokenInterceptor implements Interceptor {
    private Session session;

    public RenewTokenInterceptor(Session session) {
        this.session = session;
    }

    @Override
    public Response intercept(Chain chain) throws IOException {
        Response response = chain.proceed(chain.request());

        /* if 'x-auth-token' is available into the response header
        * save the new token into session.The header key can be
        * different upon implementation of backend.*/
        String newToken = response.header("x-auth-token");
        if (newToken != null) {
            session.saveToken(newToken);
        }

        return response;
    }
}