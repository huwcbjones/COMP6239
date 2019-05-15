package com.comp6239.Generic;

import android.content.Context;
import android.os.Build;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import android.widget.Adapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.Message;
import com.comp6239.Backend.Messaging.MessageRequest;
import com.comp6239.Backend.Messaging.MessageState;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.R;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.List;
import java.util.TimeZone;
import java.util.UUID;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MessagingActivity extends AppCompatActivity {

    private RecyclerView mMessageRecycler;
    private MessageListAdapter mMessageAdapter;
    private BackendRequestController apiBackend;
    private String threadId;
    private EditText mMessageBox;

    private WebSocketListener mMessageListener;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_messaging);
        apiBackend = BackendRequestController.getInstance(this);

        mMessageBox = findViewById(R.id.edittext_chatbox);
        mMessageRecycler = findViewById(R.id.reyclerview_message_list);
        mMessageRecycler.setLayoutManager(new LinearLayoutManager(this));
        mMessageAdapter = new MessageListAdapter(this, null);
        mMessageRecycler.setAdapter(mMessageAdapter);

        if (getIntent().hasExtra("threadId")) {
            threadId = getIntent().getStringExtra("threadId");
            refreshMessageList();
        }

        Button sendButton = findViewById(R.id.button_chatbox_send);
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendMessage();
            }
        });
        Request request = new Request.Builder().url("wss://" + BackendRequestController.BASE_URL + "ws").build();
        mMessageListener = new MessagingSocketListener();
        WebSocket ws = new OkHttpClient().newWebSocket(request, mMessageListener);
    }


    public void sendMessage() {
        String messageContent = mMessageBox.getText().toString().trim();
        if (TextUtils.isEmpty(messageContent)) {
            return; //Dont send an empty message
        }

        Message m = new Message();
        m.setSentAt(DateTime.now(DateTimeZone.forTimeZone(TimeZone.getDefault())).toString());
        m.setMessage(messageContent);
        m.setSenderId(BackendRequestController.getInstance(getApplicationContext()).getSession().getUser().getId());
        m.setState(MessageState.SENDING);
        mMessageAdapter.newMessage(m);

        Call<MessageThread> send = apiBackend.apiService.sendMessageToThread(threadId, new MessageRequest(messageContent));

        send.enqueue(new Callback<MessageThread>() {
            @Override
            public void onResponse(Call<MessageThread> call, Response<MessageThread> response) {
                mMessageBox.setText("");
                mMessageAdapter.swapMessages(getApplicationContext(), response.body());
//                refreshMessageList();
            }

            @Override
            public void onFailure(Call<MessageThread> call, Throwable t) {
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
                mMessageAdapter.swapMessages(getApplicationContext(), response.body());
                Log.d("Messaging", "Setting the adapter after getting messages");
            }

            @Override
            public void onFailure(Call<MessageThread> call, Throwable t) {
                Toast toast = Toast.makeText(getApplicationContext(), "Unable to get message list! Please try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }

    public class MessagingSocketListener extends WebSocketListener {

        private static final int NORMAL_CLOSURE_STATUS = 1000;

        public String identify() {
            JsonObject payload = new JsonObject();
            payload.addProperty("o", 2);
            JsonObject data = new JsonObject();
            JsonObject properties = new JsonObject();
            properties.addProperty("device", Build.MANUFACTURER + " " + Build.MODEL);
            properties.addProperty("os", "Android " + Build.VERSION.RELEASE + "(" + Build.VERSION.SDK_INT + ")");

            data.add("properties", properties);
            data.addProperty("token", BackendRequestController.getInstance(getApplicationContext()).getSession().getToken());
            payload.add("d", data);

            return payload.toString();
        }


        @Override
        public void onOpen(WebSocket socket, okhttp3.Response response) {
            socket.send(identify());
        }

        @Override
        public void onMessage(WebSocket webSocket, String text) {
            JsonObject payload = new JsonParser().parse(text).getAsJsonObject();
            if (payload.getAsJsonPrimitive("o").getAsInt() != 0) {
                Log.d("WebSocket", "Ignoring OpCode of " + payload.getAsJsonPrimitive("o"));
                return;
            }
            String event = payload.get("e").getAsString();
            JsonObject data = payload.getAsJsonObject("d");

            switch (event){
                case "MESSAGE":
                    handle_new_message(data);
                    break;
                case "MESSAGE_SENT":
                    break;
            }

            Log.d("WebSocket", "Received: " + text);
        }

        private void handle_new_message(JsonObject data){
            String thread_id = data.get("thread_id").getAsString();
            if (!thread_id.equals(threadId)) return;

            Message m = new Message();
            m.setId(UUID.fromString(data.get("id").getAsString()));
            m.setSenderId(UUID.fromString(data.getAsJsonObject("from").get("id").getAsString()));
            m.setMessage(data.get("message").getAsString());
            m.setSentAt(data.get("timestamp").getAsString());
            MessageState state = null;
            switch(data.get("state").getAsString()){
                case "s":
                    state = MessageState.SENT;
                    break;
                case "d":
                    state = MessageState.DELIVERED;
                    break;
                case "r":
                    state = MessageState.READ;
                    break;
            }
            m.setState(state);
            mMessageAdapter.newMessage(m);
        }

        @Override
        public void onClosing(WebSocket webSocket, int code, String reason) {
            webSocket.close(NORMAL_CLOSURE_STATUS, null);
            Log.d("WebSocket", "Closing : " + code + " / " + reason);
        }

        @Override
        public void onFailure(WebSocket webSocket, Throwable t, okhttp3.Response response) {
            Log.d("WebSocket", "Error : " + t.getMessage());
        }

    }


}
