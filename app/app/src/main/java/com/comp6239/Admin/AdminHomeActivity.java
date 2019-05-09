package com.comp6239.Admin;

import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;

import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

//Home Activity, containing two tabs
public class AdminHomeActivity extends AppCompatActivity implements AdminSubjectListFragment.OnListFragmentInteractionListener, AdminApprovalFragment.OnApproveTutorFragmentInteractionListener {

    //sfinal Fragment tutorApproval = new AdminApprovalFragment();
    final Fragment subjects = new AdminSubjectListFragment();
    final FragmentManager fm = getSupportFragmentManager();
    Fragment activeFrag = subjects;

    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                /*case R.id.navigation_tutor_approval:
                    fm.beginTransaction().hide(activeFrag).show(tutorApproval).commit();
                    activeFrag = tutorApproval;
                    return true;*/
                case R.id.navigation_subjects:
                    fm.beginTransaction().hide(activeFrag).show(subjects).commit();
                    activeFrag = subjects;
                    return true;

            }
            return false;
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin_home);

        fm.beginTransaction().add(R.id.main_container, subjects, "2").hide(subjects).commit();
        //fm.beginTransaction().add(R.id.main_container, tutorApproval, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }


    @Override
    public void onApproveTutorFragmentInteraction(Tutor item) {

    }

    @Override
    public void onSubjectListFragmentInteraction(Subject item) {

    }
}
