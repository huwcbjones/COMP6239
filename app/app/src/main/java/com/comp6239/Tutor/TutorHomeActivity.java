package com.comp6239.Tutor;

import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

public class TutorHomeActivity extends AppCompatActivity implements TutorMyStudentsFragment.OnMyStudentFragmentInteractionListener, TutorStudentRequestsFragment.OnSearchStudentFragmentInteractionListener {

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
                    activeFrag = myRequests;
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
        if(loggedTutor.isApproved()) {
            myRequests = new TutorStudentRequestsFragment();
        } else {
            myRequests = new WaitForApprovalFragment();
        }



        fm.beginTransaction().add(R.id.main_container, myRequests, "2").hide(myRequests).commit();
        fm.beginTransaction().add(R.id.main_container, myProfile, "3").hide(myProfile).commit();
        fm.beginTransaction().add(R.id.main_container, myTutees, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }

    @Override
    public void onSearchStudentFragmentInteraction(Student item) {

    }

    @Override
    public void onMyStudentFragmentInteraction(Student item) {

    }
}
