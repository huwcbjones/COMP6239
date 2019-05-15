package com.comp6239.Backend;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import com.comp6239.Backend.AuthInterceptors.AuthorisationInterceptor;
import com.comp6239.Backend.Model.Admin;
import com.comp6239.Backend.Model.RuntimeTypeAdapterFactory;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Tutor;

import com.comp6239.Backend.Model.User;
import com.comp6239.Generic.LoginActivity;
import com.comp6239.R;
import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.text.DateFormat;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class BackendRequestController {
    /**
     * Static controller object that accesses the backend
     */

    private final static String BASE_URL = "https://comp6239.biggy.hcbj.io";
    private static BackendRequestController instance;
    public static BackEndService apiService;
    private Context context;
    private Session session;
    private AuthenticationListener authenticationListener;
    SharedPreferences sharedPreferences;
    SharedPreferences.Editor editor;

    private BackendRequestController(Context context) {

        //Logging for debugging
        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);
        //Interceptor for OAuth and Logging
        OkHttpClient client = new OkHttpClient.Builder()
                //.addInterceptor(new RenewTokenInterceptor(getSession()))
                .addInterceptor(new AuthorisationInterceptor(getSession()))
                .addInterceptor(logging)
                .build();


        this.context = context;
        //Basically this is meant to make GSON support the polymorphism of our model
        final RuntimeTypeAdapterFactory<User> typeFactory = RuntimeTypeAdapterFactory
                .of(User.class, "role", false)
                .registerSubtype(Student.class, "s")
                .registerSubtype(Tutor.class, "t")
                .registerSubtype(Admin.class, "a");

        //The GSON converter itself, with the polymorphism factory added in
        Gson gson = new GsonBuilder()
                .registerTypeAdapterFactory(typeFactory)
                .enableComplexMapKeySerialization()
                .setDateFormat(DateFormat.LONG)
                .setFieldNamingPolicy(FieldNamingPolicy.UPPER_CAMEL_CASE)
                .setPrettyPrinting()
                .setVersion(1.0)
                .create();


        //The retrofit itself
        Retrofit retrofitAsync = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build();

        apiService = retrofitAsync.create(BackEndService.class);

        sharedPreferences = context.getSharedPreferences(context.getResources().getString(R.string.preference_file_key) , Context.MODE_PRIVATE);
        editor = sharedPreferences.edit();
    }

    /**
     * Returns the static instance of the backend controller
     * @param context The instance of 'this' for most Activities
     * @return The Backend Request Controller
     */
    public static BackendRequestController getInstance(Context context) {
        if (instance == null) {
            instance = new BackendRequestController(context);
        }
        return instance;
    }

    public interface AuthenticationListener {
        void onUserLoggedOut();
    }

    public void setAuthenticationListener(AuthenticationListener listener) {
        this.authenticationListener = listener;
    }

    public Session getSession() {
        if (session == null) {
            session = new Session() {
                String refreshToken;
                String password;
                User user;

                @Override
                public boolean isLoggedIn() {
                    return true;
                }

                @Override
                public void saveToken(String token) {
                    editor.putString(context.getResources().getString(R.string.tokenSharePref), token);
                    editor.commit();

                }

                @Override
                public void saveRefreshToken(String token) {
                    refreshToken = token;
                }

                @Override
                public String getToken() {
                    // return the token that was saved earlier
                    return sharedPreferences.getString(context.getResources().getString(R.string.tokenSharePref), null);
                }

                @Override
                public String getRefreshToken() {
                    return refreshToken;
                }

                @Override
                public void saveEmail(String email) {
                    editor.putString(context.getResources().getString(R.string.emailSharePref), email);
                    editor.commit();
                }


                @Override
                public String getEmail() {
                    return sharedPreferences.getString(context.getResources().getString(R.string.emailSharePref), null);
                }

                @Override
                public void savePassword(String password) {
                    this.password = password;
                }

                @Override
                public String getPassword() {
                    // should return null 99% of the time aside from on login
                    return password;
                }

                @Override
                public void invalidate() {
                    // get called when user become logged out
                    // delete token and other user info
                    // (i.e: email, password)
                    // from the storage
                    editor.remove(context.getResources().getString(R.string.emailSharePref));
                    editor.remove(context.getResources().getString(R.string.tokenSharePref));

                    // sending logged out event to it's listener
                    // i.e: Activity, Fragment, Service
                    if (authenticationListener != null) {
                        authenticationListener.onUserLoggedOut();
                    }
                }

                @Override
                public User getUser() {
                    return user;
                }

                @Override
                public void setUser(User user) {
                    this.user = user;
                }
            };
        }

        return session;
    }


}
