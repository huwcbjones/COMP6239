package com.comp6239.Tutor;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;

import com.comp6239.Backend.BackEndService;
import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class TutorViewProfileActivity extends AppCompatActivity {

    BackendRequestController backendApi;
    FloatingActionButton fab;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutor_view_profile);

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

        fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });
    }

    private void updateUIWithDetails(Tutor tutor) {
        //TODO: fill in tutor details on page on update

    }

}
