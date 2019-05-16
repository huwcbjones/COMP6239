package com.comp6239.Student;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.MessageRequest;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;
import com.comp6239.Tutor.TutorHomeActivity;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class StudentViewProfileActivity extends AppCompatActivity {

    BackendRequestController backendApi;
    FloatingActionButton fab;
    private BackendRequestController apiBackend;
    private String tutorId;
    private String threadId;
    private FloatingActionButton blockFab;

    @SuppressLint("RestrictedApi")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutor_view_profile);
        apiBackend = BackendRequestController.getInstance(this);
        if(getIntent().hasExtra("studentId")) {
            tutorId = getIntent().getStringExtra("studentId");
            Call<Student> getTutor = backendApi.apiService.getStudent(getIntent().getStringExtra("studentId"));
            getTutor.enqueue(new Callback<Student>() {
                @Override
                public void onResponse(Call<Student> call, Response<Student> response) {
                    updateUIWithDetails(response.body());
                }

                @Override
                public void onFailure(Call<Student> call, Throwable t) {

                }
            });
        }

        if(getIntent().hasExtra("threadId")) {
            threadId = getIntent().getStringExtra("threadId");
        }

        blockFab = findViewById(R.id.block_fab);
        fab = findViewById(R.id.fab);

        fab.setVisibility(View.GONE);

        if(getIntent().hasExtra("isMyStudent")) {
            if(getIntent().getBooleanExtra("isMyStudent", false)) {
                blockFab.setVisibility(View.VISIBLE);
            } else {
                blockFab.setVisibility(View.GONE);
            }
        }

        blockFab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Call<Void> block = backendApi.apiService.blockConversationById(threadId);
                block.enqueue(new Callback<Void>() {
                    @Override
                    public void onResponse(Call<Void> call, Response<Void> response) {
                        Intent i = new Intent(getApplicationContext(), TutorHomeActivity.class);
                        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                        startActivity(i);
                        finish();
                    }

                    @Override
                    public void onFailure(Call<Void> call, Throwable t) {

                    }
                });
            }
        });



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

    private void sendMessageToTutor() {
        LayoutInflater layoutInflater = LayoutInflater.from(StudentViewProfileActivity.this);
        View promptView = layoutInflater.inflate(R.layout.dialog_add_subject, null);
        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(StudentViewProfileActivity.this);
        alertDialogBuilder.setView(promptView);
        ((TextView )promptView.findViewById(R.id.hint_message_dialog)).setText("Enter the message you wish to send to the tutor:");
        final EditText editText = promptView.findViewById(R.id.subject_name_edittext);
        // setup a dialog window
        alertDialogBuilder.setCancelable(false)
                .setPositiveButton("Send Message to Tutor:", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        Call<Void> createMessageRequest = apiBackend.apiService.startConversation(new MessageRequest(
                                tutorId,
                                editText.getText().toString()));
                        createMessageRequest.enqueue(new Callback<Void>() {
                            @SuppressLint("RestrictedApi")
                            @Override
                            public void onResponse(Call<Void> call, Response<Void> response) {
                                Toast toast = Toast.makeText(StudentViewProfileActivity.this, "Messaged the tutor!", Toast.LENGTH_LONG);
                                toast.show();
                                fab.setVisibility(View.GONE);
                            }

                            @Override
                            public void onFailure(Call<Void> call, Throwable t) {
                                Toast toast = Toast.makeText(StudentViewProfileActivity.this, "Failed to access the server!", Toast.LENGTH_LONG);
                                toast.show();
                            }
                        });

                    }
                })
                .setNegativeButton("Cancel",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                dialog.cancel();
                            }
                        });

        // create an alert dialog
        AlertDialog alert = alertDialogBuilder.create();
        alert.show();
    }

    private void updateUIWithDetails(Student student) {
        fillSubjects(Arrays.asList(student.getSubjects()));
        ((TextView) findViewById(R.id.tutorName)).setText(student.getFirstName() + " " + student.getLastName());
        ((TextView) findViewById(R.id.tutorPrice)).setVisibility(View.GONE);
        ((TextView) findViewById(R.id.tutorBio)).setVisibility(View.GONE);
        ((TextView) findViewById(R.id.tutorLocation)).setText(student.getLocation());
    }

}
