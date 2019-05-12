package com.comp6239.Generic;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.Message;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.R;

import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MessagingActivity extends AppCompatActivity {

    private RecyclerView mMessageRecycler;
    private MessageListAdapter mMessageAdapter;
    private BackendRequestController apiBackend;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_messaging);
        apiBackend = BackendRequestController.getInstance(this);

        final MessageThread threadObj;
        if(getIntent().hasExtra("threadId")) {

            Call<MessageThread> thread = apiBackend.apiService
                    .getConversationThread(getIntent().getStringExtra("threadId"));

            thread.enqueue(new Callback<MessageThread>() {
                @Override
                public void onResponse(Call<MessageThread> call, Response<MessageThread> response) {
                    mMessageAdapter = new MessageListAdapter(getApplicationContext(), response.body());
                }

                @Override
                public void onFailure(Call<MessageThread> call, Throwable t) {

                }
            });
        }


        mMessageRecycler = findViewById(R.id.reyclerview_message_list);
        mMessageRecycler.setLayoutManager(new LinearLayoutManager(this));
        mMessageRecycler.setAdapter(mMessageAdapter);
    }


}
