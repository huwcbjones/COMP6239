package com.comp6239.Backend;

import android.content.Context;

import com.comp6239.Backend.Model.Admin;
import com.comp6239.Backend.Model.RuntimeTypeAdapterFactory;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Tutor;

import com.comp6239.Backend.Model.User;
import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.text.DateFormat;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;

import okhttp3.Cache;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class BackendRequestController {
    /**
     * Static controller object that accesses the backend
     */

    private final static String BASE_URL = "https://comp6239.biggy.hcbj.io";
    private static BackendRequestController instance;
    public static BackEndService apiServiceAsync;
    private Context context;

    private BackendRequestController(Context context) {

        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);
        OkHttpClient client = new OkHttpClient.Builder()
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
                .serializeNulls()
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

        apiServiceAsync = retrofitAsync.create(BackEndService.class);
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


}
