package com.comp6239;

import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.widget.TextView;

public class TutorHomeActivity extends AppCompatActivity {

    final Fragment myTutees = new StudentSearchTutorsFragment();
    final Fragment myRequests = new StudentMyTutorsFragment();
    final FragmentManager fm = getSupportFragmentManager();
    Fragment activeFrag = myTutees;

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
            }
            return false;
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutor_home);

        fm.beginTransaction().add(R.id.main_container, myRequests, "2").hide(myRequests).commit();
        fm.beginTransaction().add(R.id.main_container, myTutees, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }

}
