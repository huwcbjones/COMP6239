package com.comp6239.Admin;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


public class AdminReviewTutor extends AppCompatActivity {

    BackendRequestController backendApi;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin_review_tutor);

        backendApi = BackendRequestController.getInstance(this);

        if(getIntent().hasExtra("tutorID")) {
            Call<Tutor> getTutor = backendApi.apiService.getTutor(getIntent().getStringExtra("tutorID"));
            getTutor.enqueue(new Callback<Tutor>() {
                @Override
                public void onResponse(Call<Tutor> call, Response<Tutor> response) {
                    updateUIWithDetails(response.body());
                }

                @Override
                public void onFailure(Call<Tutor> call, Throwable t) {

                }
            });
        }
    }

    private void updateUIWithDetails(Tutor tutor) {
        //TODO: fill in tutor details on page on update for admin review

    }
}
