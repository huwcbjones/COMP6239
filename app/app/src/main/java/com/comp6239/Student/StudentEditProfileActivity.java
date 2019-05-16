package com.comp6239.Student;

import android.Manifest;
import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.annotation.TargetApi;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Address;
import android.location.Criteria;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Looper;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.R;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import static com.comp6239.Backend.BackendRequestController.apiService;

public class StudentEditProfileActivity extends AppCompatActivity {

    private StudentProfileUpdateTask mAuthTask;
    private View mStudentUpdateForm;
    private View mProgressView;
    private EditText mEmailView;
    private EditText mFirstNameView;
    private BackendRequestController apiBackend;
    private EditText mLastNameView;
    private LocationListener locationListener;
    private Location mLocation;
    private Subject[] allSubjects;
    private HashSet<Subject> chosenSubjects;
    private Spinner spinner;
    private HashMap<Integer, TextView> subjectViews;
    private EditText mPasswordView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("Edit My Profile");
        setContentView(R.layout.activity_student_edit_profile);
        apiBackend = BackendRequestController.getInstance(this);

        chosenSubjects = new HashSet<Subject>();
        setupSpinner();

        mStudentUpdateForm = findViewById(R.id.student_update_form);
        mProgressView = findViewById(R.id.login_progress);
        mEmailView = findViewById(R.id.email_update_student);
        mFirstNameView = findViewById(R.id.firstname_update_student);
        mLastNameView = findViewById(R.id.lastname_update_student);
        mPasswordView = findViewById(R.id.password_update_student);

        findViewById(R.id.update_details_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptUpdate();
            }
        });

        locationListener  = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                mLocation = location;
                Log.d("Location Changes", location.toString());
            }

            @Override
            public void onStatusChanged(String provider, int status, Bundle extras) {
                Log.d("Status Changed", String.valueOf(status));
            }

            @Override
            public void onProviderEnabled(String provider) {
                Log.d("Provider Enabled", provider);
            }

            @Override
            public void onProviderDisabled(String provider) {
                Log.d("Provider Disabled", provider);
            }
        };

        Criteria criteria = new Criteria();
        criteria.setAccuracy(Criteria.ACCURACY_COARSE);
        criteria.setPowerRequirement(Criteria.POWER_LOW);
        criteria.setAltitudeRequired(false);
        criteria.setBearingRequired(false);
        criteria.setSpeedRequired(false);
        criteria.setCostAllowed(true);
        criteria.setHorizontalAccuracy(Criteria.ACCURACY_HIGH);
        criteria.setVerticalAccuracy(Criteria.ACCURACY_HIGH);

        if(ContextCompat.checkSelfPermission(getApplicationContext(),
                Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {

            final LocationManager locationManager = (LocationManager)getSystemService(Context.LOCATION_SERVICE);
            final Looper looper = null;
            locationManager.requestSingleUpdate(criteria, locationListener, looper);
        }
    }

    int currentViewIndex; //Literally exists to keep track of which view to activate / deactivate
    private void putSubject(String subjectName) {
        //Set the text and make it visible
        TextView curView = subjectViews.get(currentViewIndex);
        curView.setText(subjectName);
        curView.setVisibility(View.VISIBLE);

        //Add it to the chosen list of subjects
        for(Subject s : allSubjects) {
            if(subjectName.equals(s.getName())) {
                chosenSubjects.add(s);
                break;
            }
        }

        //Look for the next empty spot
        for(int i = 0; i < subjectViews.size(); i++) {
            TextView view = subjectViews.get(i);
            //Log.d("SubjectChoose", "What is it to string?: " + view.getText().toString());
            if(view.getText().toString().equals("")) {
                currentViewIndex = i;

                //Log.d("SubjectChoose", "Next index: " + currentViewIndex);
                break;
            }
        }
    }

    private void removeSubject(String subjectName) {
        for(TextView tv : subjectViews.values()) {
            if(tv.toString().equals(subjectName)) {
                tv.setText("");
                tv.setVisibility(View.GONE);
                break;
            }
        }

        for(Subject s : allSubjects) {
            if(subjectName.equals(s.getName())) {
                chosenSubjects.remove(s);
                break;
            }
        }

        //Look for the next empty spot
        for(int i = 0; i < subjectViews.size(); i++) {
            TextView view = (TextView) subjectViews.get(i);
            if(view.getText().toString().equals("")) {
                currentViewIndex = i;
                //Log.d("SubjectChoose", "What is it to string?: " + subjectViews.get(i).getText().toString());
                //Log.d("SubjectChoose", "Next index: " + currentViewIndex);
                break;
            }
        }
    }

    private void setupSpinner() {
        spinner = (Spinner) findViewById(R.id.subject_spinner);
        subjectViews = new HashMap<>();
        subjectViews.put(0, (TextView) findViewById(R.id.recipient_name));
        subjectViews.put(1, (TextView) findViewById(R.id.subject_name2));
        subjectViews.put(2, (TextView) findViewById(R.id.subject_name3));
        subjectViews.put(3, (TextView) findViewById(R.id.subject_name4));
        subjectViews.put(4, (TextView) findViewById(R.id.subject_name5));
        subjectViews.put(5, (TextView) findViewById(R.id.subject_name6));
        subjectViews.put(6, (TextView) findViewById(R.id.subject_name7));
        subjectViews.put(7, (TextView) findViewById(R.id.subject_name8));
        subjectViews.put(8, (TextView) findViewById(R.id.subject_name9));
        currentViewIndex = 0;

        for(TextView tv : subjectViews.values()) {
            tv.setVisibility(View.GONE);
            tv.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    removeSubject(v.toString());
                }
            });
        }

        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                String subjectName = spinner.getSelectedItem().toString();
                Log.d("SubjectChoose", "Putting subject: " + subjectName);
                putSubject(subjectName);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });

        //grab the big list of allSubjects
        Call<List<Subject>> subjectList = apiBackend.apiService.getAllSubjects();
        subjectList.enqueue(new Callback<List<Subject>>() {

            @Override
            public void onResponse(Call<List<Subject>> call, Response<List<Subject>> response) {
                allSubjects = new Subject[response.body().size()];
                for(int i = 0; i < response.body().size(); i++) {
                    allSubjects[i] = response.body().get(i);
                }

                addItemsOnSpinner(spinner);
            }

            @Override
            public void onFailure(Call<List<Subject>> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Could not retrieve user data!", Toast.LENGTH_LONG);
                toast.show(); //If you cant grab the subject list, then just go back since you cant fill out allSubjects
                finish();
            }
        });
    }

    private void addItemsOnSpinner(Spinner spinner) {

        List<String> list = new ArrayList<String>();
        for(Subject s : allSubjects) {
            list.add(s.getName());
        }
        ArrayAdapter<String> dataAdapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_item, list);
        dataAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(dataAdapter);
    }

    private void attemptUpdate() {
        if (mAuthTask != null) {
            return;
        }

        showProgress(true);
        mAuthTask = new StudentEditProfileActivity.StudentProfileUpdateTask(
                mEmailView.getText().toString(), 
                mFirstNameView.getText().toString(),  
                mLastNameView.getText().toString(),
                mPasswordView.getText().toString());
        mAuthTask.execute((Void) null);

    }

    @TargetApi(Build.VERSION_CODES.HONEYCOMB_MR2)
    private void showProgress(final boolean show) {
        // On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
        // for very easy animations. If available, use these APIs to fade-in
        // the progress spinner.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2) {
            int shortAnimTime = getResources().getInteger(android.R.integer.config_shortAnimTime);

            mStudentUpdateForm.setVisibility(show ? View.GONE : View.VISIBLE);
            mStudentUpdateForm.animate().setDuration(shortAnimTime).alpha(
                    show ? 0 : 1).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mStudentUpdateForm.setVisibility(show ? View.GONE : View.VISIBLE);
                }
            });

            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mProgressView.animate().setDuration(shortAnimTime).alpha(
                    show ? 1 : 0).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
                }
            });
        } else {
            // The ViewPropertyAnimator APIs are not available, so simply show
            // and hide the relevant UI components.
            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mStudentUpdateForm.setVisibility(show ? View.GONE : View.VISIBLE);
        }
    }

    public class StudentProfileUpdateTask extends AsyncTask<Void, Void, Boolean> {

        private String mEmail;
        private String mFirstName;
        private String mLastName;
        private String mPassword;

        StudentProfileUpdateTask(String email, String firstName, String lastName, String password) {
            mEmail = email;
            mFirstName = firstName;
            mLastName = lastName;
            mPassword = password;
        }

        @Override
        protected Boolean doInBackground(Void... params) {
            Student oldUser = (Student) apiBackend.getSession().getUser();
            Response<Student>  studentUpdate;

            final String[] loc = {""};
            Geocoder geocoder = new Geocoder(getApplicationContext(), Locale.getDefault());
            try {
                if(mLocation != null) {
                    List<Address> addresses = geocoder.getFromLocation(
                            mLocation.getLatitude(),
                            mLocation.getLongitude(),
                            // In this sample, get just a single address.
                            1);
                    loc[0] = addresses.get(0).getSubAdminArea();
                }
            } catch (IOException e) {
                // Catch network or other I/O problems.
                Log.e("Registration-GEOCODER", "Network unavailable, location will not be updated.", e);
                loc[0] = oldUser.getLocation();
            } catch (IllegalArgumentException e) {
                // Catch invalid latitude or longitude values.
                Log.e("Registration-GEOCODER", "Invalid location passed, location will not be updated..", e);
                loc[0] = oldUser.getLocation();
            }

            try {
                // Simulate network access, since Geocode wont to synchronous
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                return false;
            }

            Student updatedUser = new Student();
            updatedUser.setId(oldUser.getId());
            if(!TextUtils.isEmpty(mFirstName)) updatedUser.setFirstName(mFirstName);
            if(!TextUtils.isEmpty(mLastName)) updatedUser.setLastName(mLastName);
            if(!TextUtils.isEmpty(mEmail)) updatedUser.setLastName(mEmail);
            if(!TextUtils.isEmpty(mPassword)) updatedUser.setPassword(mPassword);
            if(!chosenSubjects.isEmpty()) {
                Subject[] finalSub = new Subject[chosenSubjects.size()];
                int i = 0;
                for(Object s : chosenSubjects.toArray()) {
                    if(s instanceof Subject) {
                        finalSub[i] = (Subject) s;
                        i++;
                    }
                }
                updatedUser.setSubjects(finalSub);

            }
            if(loc[0] != null) updatedUser.setLocation(loc[0]);

            try {
                studentUpdate = apiService.updateStudent(oldUser.getId().toString(), updatedUser).execute();

                if(studentUpdate.isSuccessful()) {
                    apiBackend.getSession().setUser(studentUpdate.body());
                    return true;
                }


            } catch(IOException e) {
                Toast toast = Toast.makeText(getApplicationContext(), "Failed to access the server!", Toast.LENGTH_LONG);
                toast.show();
            }

            return false;
        }

        @Override
        protected void onPostExecute(final Boolean success) {
            mAuthTask = null;
            showProgress(false);

            if (success) {
                Toast toast = Toast.makeText(getApplicationContext(), "Profile has been updated!", Toast.LENGTH_LONG);
                toast.show();
                finish();
            } else {
                Toast toast = Toast.makeText(getApplicationContext(), "There was a network error updating your profile!", Toast.LENGTH_LONG);
                toast.show();
                //mFirstNameView.requestFocus();
            }
        }

        @Override
        protected void onCancelled() {
            mAuthTask = null;
            showProgress(false);
        }
    }

}
