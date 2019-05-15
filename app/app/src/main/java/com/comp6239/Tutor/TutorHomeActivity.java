package com.comp6239.Tutor;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Generic.MessagingActivity;
import com.comp6239.R;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class TutorHomeActivity extends AppCompatActivity implements
        TutorMyStudentsFragment.OnMyStudentFragmentInteractionListener, TutorStudentRequestsFragment.OnSearchStudentFragmentInteractionListener, WaitForApprovalFragment.OnFragmentInteractionListener, TutorMyProfileFragment.OnFragmentInteractionListener{

    final Fragment myTutees = new TutorMyStudentsFragment();
    Fragment myRequests;
    final Fragment myProfile = new TutorMyProfileFragment();
    final FragmentManager fm = getSupportFragmentManager();
    Fragment activeFrag = myTutees;
    private BackendRequestController backendApi;

    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                case R.id.navigation_my_tutees:
                    fm.beginTransaction().hide(activeFrag).show(myTutees).commit();
                    activeFrag = myTutees;
                    return true;
                case R.id.navigation_my_requests:
                    fm.beginTransaction().hide(activeFrag).show(myRequests).commit();
                    activeFrag = myRequests;
                    return true;

                case R.id.navigation_my_profile:
                    fm.beginTransaction().hide(activeFrag).show(myProfile).commit();
                    activeFrag = myProfile;
                    return true;
            }
            return false;
        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutor_home);
        backendApi = BackendRequestController.getInstance(this);

        Tutor loggedTutor = (Tutor) backendApi.getSession().getUser();
        Log.d("Tutor Login", "IsApproved?:" + loggedTutor.isApproved());
        if(loggedTutor.isApproved() == null || !loggedTutor.isApproved()) {
            myRequests = new WaitForApprovalFragment();
        } else {
            myRequests = new TutorStudentRequestsFragment();
        }



        fm.beginTransaction().add(R.id.main_container, myRequests, "2").hide(myRequests).commit();
        fm.beginTransaction().add(R.id.main_container, myProfile, "3").hide(myProfile).commit();
        fm.beginTransaction().add(R.id.main_container, myTutees, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }

    @Override
    public void onSearchStudentFragmentInteraction(final MessageThread item) {

        LayoutInflater layoutInflater = LayoutInflater.from(TutorHomeActivity.this);
        View promptView = layoutInflater.inflate(R.layout.dialog_student_request, null);
        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(TutorHomeActivity.this);
        alertDialogBuilder.setView(promptView);
        //TextView fromStudentMessage = promptView.findViewById(R.id.view_from_student);
        //TextView actualMessage = promptView.findViewById(R.id.view_student_message);
        //fromStudentMessage.setText("A student has sent you a request!");
        //actualMessage.setText(item.getMessages()[0].getMessage());
        ((TextView) promptView.findViewById(R.id.view_from_student)).setText(item.getRecipient().getFirstName() + " " + item.getRecipient().getLastName() + " has sent you a request!");
        ((TextView) promptView.findViewById(R.id.view_student_message)).setText(item.getMessages()[0].getMessage());
        // setup a dialog window
        alertDialogBuilder.setCancelable(false)
                .setPositiveButton("Accept", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        Call<Void> response = backendApi.apiService.approveConversationById(item.getId().toString());
                        response.enqueue(new Callback<Void>() {
                            @Override
                            public void onResponse(Call<Void> call, Response<Void> response) {
                                Toast toast = Toast.makeText(TutorHomeActivity.this, "Accepted new student!", Toast.LENGTH_LONG);
                                toast.show();
                                ((TutorMyStudentsFragment) myTutees).refreshStudentList();
                            }

                            @Override
                            public void onFailure(Call<Void> call, Throwable t) {
                                Toast toast = Toast.makeText(TutorHomeActivity.this, "Failed to access the server!", Toast.LENGTH_LONG);
                                toast.show();
                            }
                        });

                    }
                })
                .setNegativeButton("Reject",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                Call<Void> response = backendApi.apiService.blockConversationById(item.getId().toString());
                                response.enqueue(new Callback<Void>() {
                                    @Override
                                    public void onResponse(Call<Void> call, Response<Void> response) {
                                        Toast toast = Toast.makeText(TutorHomeActivity.this, "Rejected student!", Toast.LENGTH_LONG);
                                        toast.show();
                                        ((TutorStudentRequestsFragment) myRequests).refreshStudentList();
                                    }

                                    @Override
                                    public void onFailure(Call<Void> call, Throwable t) {
                                        Toast toast = Toast.makeText(TutorHomeActivity.this, "Failed to access the server!", Toast.LENGTH_LONG);
                                        toast.show();
                                    }
                                });
                            }
                        });

        // create an alert dialog
        AlertDialog alert = alertDialogBuilder.create();
        alert.show();

    }

    @Override
    public void onMyStudentFragmentInteraction(MessageThread item) {
        Intent i = new Intent(getApplicationContext(), MessagingActivity.class);
        i.putExtra("threadId", item.getId().toString());
        startActivity(i);
    }

    @Override
    public void onWaitingApprovalFragmentInteraction(Uri uri) {

    }

    @Override
    public void onFragmentInteraction(Uri uri) {

    }
}
