package com.comp6239.Admin;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

//Home Activity, containing two tabs
public class AdminHomeActivity extends AppCompatActivity implements AdminSubjectListFragment.OnListFragmentInteractionListener, AdminApprovalFragment.OnApproveTutorFragmentInteractionListener {

    //final Fragment tutorApproval = new AdminApprovalFragment();
    final Fragment subjects = new AdminSubjectListFragment();
    final FragmentManager fm = getSupportFragmentManager();
    Fragment activeFrag = subjects;
    BackendRequestController apiBackend;

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

        apiBackend = BackendRequestController.getInstance(this);

        fm.beginTransaction().add(R.id.main_container, subjects, "2").hide(subjects).commit();
        //fm.beginTransaction().add(R.id.main_container, tutorApproval, "1").commit();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
    }


    @Override
    public void onApproveTutorFragmentInteraction(Tutor item) {

    }

    @Override
    public void onSubjectListFragmentInteraction(final Subject item) {


        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Are you sure?");
        builder.setMessage("You are about to delete the subject " + item.getName() +  ". Do you want to proceed?");

        builder.setCancelable(false);
        builder.setPositiveButton("Yes", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                deleteSubject(item);

            }
        });

        builder.setNegativeButton("No", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.cancel();
            }
        });

        builder.show();
    }

    public void deleteSubject(Subject item) {
        Call<Void> delete = apiBackend.apiService.deleteSubject(item.getId().toString());
        delete.enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                Toast toast = Toast.makeText(getApplicationContext(), "Successfully deleted subject!", Toast.LENGTH_LONG);
                toast.show();
                ((AdminSubjectListFragment) subjects).createSubjectList();

            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Failed to access the server! Try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }
}
