package com.comp6239.Tutor;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

import com.comp6239.R;

public class WaitForApprovalActivity extends AppCompatActivity {
    //Activity could also be used as the Application Rejection page?
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_wait_for_approval);
    }
}
