package com.comp6239.Admin;

import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Generic.LoginActivity;
import com.comp6239.R;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


public class AdminReviewTutor extends AppCompatActivity {

    BackendRequestController backendApi;
    private AdminApproveTask mAuthTask = null;
    private String tutorId;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin_review_tutor);

        backendApi = BackendRequestController.getInstance(this);

        if(getIntent().hasExtra("tutorId")) {
            Call<Tutor> getTutor = backendApi.apiService.getTutor(getIntent().getStringExtra("tutorId"));
            getTutor.enqueue(new Callback<Tutor>() {
                @Override
                public void onResponse(Call<Tutor> call, Response<Tutor> response) {
                    updateUIWithDetails(response.body());
                    tutorId = response.body().getId().toString();
                }

                @Override
                public void onFailure(Call<Tutor> call, Throwable t) {

                }
            });
        }

        findViewById(R.id.accept_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptApproval(tutorId, true, null);
            }
        });

        findViewById(R.id.reject_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptApproval(tutorId, false, ((TextView) findViewById(R.id.reason_text)).getText().toString());
            }
        });




    }

    private void attemptApproval(String tutorId, Boolean isApproved, String reason) {
        if (mAuthTask != null) {
            return;
        }

        mAuthTask = new AdminApproveTask(tutorId, reason, isApproved);
        mAuthTask.execute((Void) null);

    }

    private void fillSubjects(List<Subject> subjects) {
        ArrayList<TextView> views = new ArrayList<TextView>();
        views.add((TextView) findViewById(R.id.tutorSubject));
        views.add((TextView) findViewById(R.id.tutorSubject2));
        views.add((TextView) findViewById(R.id.tutorSubject3));
        views.add((TextView) findViewById(R.id.tutorSubject4));
        views.add((TextView) findViewById(R.id.tutorSubject5));
        views.add((TextView) findViewById(R.id.tutorSubject6));
        views.add((TextView) findViewById(R.id.tutorSubject7));
        views.add((TextView) findViewById(R.id.tutorSubject8));
        views.add((TextView) findViewById(R.id.tutorSubject9));
        //Stick all of the subjects in
        for(int i = 0; i < subjects.size(); i++) {
            views.get(i).setText(subjects.get(i).getName());
            views.get(i).setVisibility(View.VISIBLE);
        }

    }

    private void updateUIWithDetails(Tutor tutor) {
        fillSubjects(Arrays.asList(tutor.getSubjects()));
        ((TextView) findViewById(R.id.tutorEmail)).setText(tutor.getEmail());
        ((TextView) findViewById(R.id.tutorName)).setText(tutor.getFirstName() + " " + tutor.getLastName());
        ((TextView) findViewById(R.id.tutorPrice)).setText("£" + tutor.getPrice() + " per hour");
        ((TextView) findViewById(R.id.tutorBio)).setText(tutor.getBio());
    }

    public class AdminApproveTask extends AsyncTask<Void, Void, Boolean> {
        private final String tutorId;
        private final String rejectReason;
        private final Boolean isApproved;

        AdminApproveTask(String tutorId, String rejectReason, Boolean isApproved) {
            this.tutorId = tutorId;
            this.rejectReason = rejectReason;
            this.isApproved = isApproved;
        }

        @Override
        protected Boolean doInBackground(Void... voids) {

            Response<Void> approvalResponse;

                try {
                    if(isApproved) {
                        approvalResponse = backendApi.apiService.approveTutor(tutorId, new Tutor(true, null)).execute();
                    } else {
                        approvalResponse = backendApi.apiService.approveTutor(tutorId, new Tutor(false, rejectReason)).execute();
                    }
                    if(approvalResponse.code() == 200) {
                        return true;
                    } else {
                        runOnUiThread(new Runnable() {
                            public void run() {
                                Toast.makeText(getApplicationContext(), "Unable to approve tutor, please try again later!", Toast.LENGTH_LONG).show();
                            }
                        });
                    }
                } catch (IOException e) {
                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(getApplicationContext(), "Unable to connect to the server, please try again later!", Toast.LENGTH_LONG).show();
                        }
                    });
                }

            return true;
        }

        @Override
        protected void onPostExecute(final Boolean success) {
            if(success) {
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Tutor has been moderated!", Toast.LENGTH_LONG).show();
                    }
                });
                finish();
            }
        }
    }
}
