package com.comp6239.Student;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MenuItem;

import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.Generic.MessagingActivity;
import com.comp6239.R;
import com.comp6239.Tutor.TutorViewProfileActivity;

public class StudentHomeActivity extends AppCompatActivity implements StudentMyProfileFragment.OnFragmentInteractionListener, StudentMyTutorsFragment.OnMyTutorsFragmentInteractionListener, StudentSearchTutorsFragment.OnSearchTutorFragmentInteractionListener {


    //Keeps the Fragments persistent rather than loading and creating them fresh every time
    //they're selected
    final Fragment myProfile = new StudentMyProfileFragment();
    final Fragment searchTutors = new StudentSearchTutorsFragment();
    final Fragment myTutors = new StudentMyTutorsFragment();
    final FragmentManager fm = getSupportFragmentManager();
    Fragment activeFrag = searchTutors;


    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                case R.id.navigation_search_tutors:
                    Log.i("push button", "searchtutor");
                    fm.beginTransaction().hide(activeFrag).show(searchTutors).commit();
                    activeFrag = searchTutors;
                    return true;
                case R.id.navigation_my_tutors:
                    Log.i("push button", "mytutors");
                    fm.beginTransaction().hide(activeFrag).show(myTutors).commit();
                    activeFrag = myTutors;
                    return true;
                case R.id.navigation_my_profile:
                    Log.i("push button", "myprofile");
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


        setContentView(R.layout.activity_student_home);
        setTitle("Student Home");


        fm.beginTransaction().add(R.id.main_container, myProfile, "3").hide(myProfile).commit();
        fm.beginTransaction().add(R.id.main_container, myTutors, "2").hide(myTutors).commit();
        fm.beginTransaction().add(R.id.main_container,searchTutors, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }


    @Override
    public void onFragmentInteraction(Uri uri) {

    }

    @Override
    public void onMyTutorsFragmentInteraction(MessageThread item) {
        Intent i = new Intent(getApplicationContext(), MessagingActivity.class);
        i.putExtra("threadId", item.getId().toString());
        startActivity(i);
    }

    @Override
    public void onSearchTutorsFragmentInteraction(Tutor item) {
        Intent i = new Intent(getApplicationContext(), TutorViewProfileActivity.class);
        i.putExtra("tutorId", item.getId().toString());
        i.putExtra("isMyTutor", false);
        startActivity(i);
    }
}
