package com.comp6239.Backend;

import android.content.Context;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class BackendRequestController {
    /**
     * Static controller object that accesses the backend
     */

    private final static String BASE_URL = "url";
    private static BackendRequestController instance;
    private static BackEndService apiServiceAsync;
    private Context context;

    private BackendRequestController(Context context) {

        this.context = context;

        //RxJava2CallAdapterFactory rxAdapter = RxJava2CallAdapterFactory.createWithScheduler(Schedulers.io());

        Retrofit retrofitAsync = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                //.addCallAdapterFactory(rxAdapter)
                .build();

        apiServiceAsync = retrofitAsync.create(BackEndService.class);
    }


    public static BackendRequestController getInstance(Context context) {
        if (instance == null) {
            instance = new BackendRequestController(context);
        }
        return instance;
    }


}
