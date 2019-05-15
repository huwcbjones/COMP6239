package com.comp6239.Generic;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.Message;
import com.comp6239.Backend.Messaging.MessageRequest;
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
    private String threadId;
    private EditText mMessageBox;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_messaging);
        apiBackend = BackendRequestController.getInstance(this);

        if(getIntent().hasExtra("threadId")) {
            threadId = getIntent().getStringExtra("threadId");
            refreshMessageList();
        }

        mMessageBox = findViewById(R.id.edittext_chatbox);
        mMessageRecycler = findViewById(R.id.reyclerview_message_list);
        mMessageRecycler.setLayoutManager(new LinearLayoutManager(this));
        mMessageRecycler.setAdapter(mMessageAdapter);


        Button sendButton = findViewById(R.id.button_chatbox_send);
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendMessage();
            }
        });


    }

    public void sendMessage() {
        if(TextUtils.isEmpty(mMessageBox.getText().toString().trim())) {
            return; //Dont send an empty message
        }

        Call<Void> send = apiBackend.apiService.sendMessageToThread(threadId, new MessageRequest(mMessageBox.getText().toString()));

        send.enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                mMessageBox.setText("");
                refreshMessageList();
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Unable to send message! Please try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });

        //send the message followed by refresh messagelist
    }

    private void refreshMessageList() {
        Call<MessageThread> thread = apiBackend.apiService.getConversationThread(threadId);

        thread.enqueue(new Callback<MessageThread>() {
            @Override
            public void onResponse(Call<MessageThread> call, Response<MessageThread> response) {
                mMessageAdapter = new MessageListAdapter(getApplicationContext(), response.body());
            }

            @Override
            public void onFailure(Call<MessageThread> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Unable to get message list! Please try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }


}
