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
import android.widget.EditText;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Student;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.R;

import java.io.IOException;
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
    private Subject[] subjects;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_student_edit_profile);
        apiBackend = BackendRequestController.getInstance(this);

        //grab the big list of subjects
        Call<List<Subject>> subjectList = apiBackend.apiService.getAllSubjects();
        subjectList.enqueue(new Callback<List<Subject>>() {

            @Override
            public void onResponse(Call<List<Subject>> call, Response<List<Subject>> response) {
                subjects = (Subject[])response.body().toArray();
            }

            @Override
            public void onFailure(Call<List<Subject>> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Could not retrieve user data!", Toast.LENGTH_LONG);
                toast.show(); //If you cant grab the subject list, then just go back since you cant fill out subjects
                finish();
            }
        });


        mStudentUpdateForm = findViewById(R.id.student_update_form);
        mProgressView = findViewById(R.id.login_progress);
        mEmailView = findViewById(R.id.email_update_student);
        mFirstNameView = findViewById(R.id.firstname_update_student);
        mLastNameView = findViewById(R.id.lastname_update_student);

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



    private void attemptUpdate() {
        if (mAuthTask != null) {
            return;
        }

        showProgress(true);
        mAuthTask = new StudentEditProfileActivity.StudentProfileUpdateTask(mEmailView.getText().toString(), mFirstNameView.getText().toString(),  mLastNameView.getText().toString());
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



        StudentProfileUpdateTask(String email, String firstName, String lastName) {
            mEmail = email;
            mFirstName = firstName;
            mLastName = lastName;
        }

        @Override
        protected Boolean doInBackground(Void... params) {
            Student oldUser = (Student) apiBackend.getSession().getUser();
            Response<Student>  studentUpdate;

            if(TextUtils.isEmpty(mEmail))
                mEmail = oldUser.getEmail();

            if(TextUtils.isEmpty(mFirstName))
                mFirstName = oldUser.getFirstName();

            if(TextUtils.isEmpty(mLastName))
                mLastName = oldUser.getLastName();


            final String[] loc = {""};
            Geocoder geocoder = new Geocoder(getApplicationContext(), Locale.getDefault());

            try {
                List<Address> addresses = geocoder.getFromLocation(
                        mLocation.getLatitude(),
                        mLocation.getLongitude(),
                        // In this sample, get just a single address.
                        1);
                loc[0] = addresses.get(0).getSubAdminArea();
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
                // Simulate network access.
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                return false;
            }

            Student updatedUser = new Student(mEmail, mFirstName, mLastName, oldUser.getGender(), loc[0], "password");
            updatedUser.setId(oldUser.getId());

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
                mFirstNameView.setError(getString(R.string.error_incorrect_password));
                mFirstNameView.requestFocus();
            }
        }

        @Override
        protected void onCancelled() {
            mAuthTask = null;
            showProgress(false);
        }
    }

}
