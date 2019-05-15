package com.comp6239.Generic;


import android.content.Context;
import android.os.Build;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.Message;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.Backend.Model.User;
import com.comp6239.R;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

public class MessageListAdapter extends RecyclerView.Adapter {
    private static final int MESSAGE_SENT = 1;
    private static final int MESSAGE_RECEIVED = 2;

    private BackendRequestController backend;
    private MessageThread mThread;
    private Context mContext;
    private List<Message> mMessageList;

    public MessageListAdapter(Context context, MessageThread thread) {
        swapMessages(context, thread);
    }

    public void swapMessages(Context context, MessageThread thread){
        mContext = context;

        if (thread == null) return;
        mThread = thread;
        mMessageList = Arrays.asList(thread.getMessages());
        backend = BackendRequestController.getInstance(context);
        notifyDataSetChanged();
    }

    @Override
    public int getItemCount() {
        if(mMessageList == null) {
            return 0;
        }
        return mMessageList.size();
    }

    @Override
    public int getItemViewType(int position) {
        Message message = (Message) mMessageList.get(position);

        //If the sender ID is the person logged in, then put it on the right side
        if (message.getSenderId().equals(backend.getSession().getUser().getId())) {
            return MESSAGE_SENT;
        } else {
            return MESSAGE_RECEIVED;
        }
    }

    // Place the message depending on either sent or received
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view;

        if (viewType == MESSAGE_SENT) {
            view = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.message_sent, parent, false);
            return new SentMessageHolder(view);
        } else if (viewType == MESSAGE_RECEIVED) {
            view = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.message_received, parent, false);
            return new ReceivedMessageHolder(view);
        }

        return null;
    }

    // Passes the message object to a ViewHolder so that the contents can be bound to UI.
    @Override
    public void onBindViewHolder(RecyclerView.ViewHolder holder, int position) {
        Message message = (Message) mMessageList.get(position);

        switch (holder.getItemViewType()) {
            case MESSAGE_SENT:
                ((SentMessageHolder) holder).bind(message);
                break;
            case MESSAGE_RECEIVED:
                ((ReceivedMessageHolder) holder).bind(message);
        }
    }

    private class SentMessageHolder extends RecyclerView.ViewHolder {
        TextView messageText, timeText;

        SentMessageHolder(View itemView) {
            super(itemView);

            messageText = itemView.findViewById(R.id.text_message_body);
            timeText = itemView.findViewById(R.id.text_message_time);
        }

        void bind(Message message) {
            messageText.setText(message.getMessage());

            // Format the stored timestamp into a readable String using method.
            //timeText.setText(Utils.formatDateTime(message.getCreatedAt()));
        }
    }

    private class ReceivedMessageHolder extends RecyclerView.ViewHolder {
        TextView messageText, timeText, nameText;
        ImageView profileImage;

        ReceivedMessageHolder(View itemView) {
            super(itemView);

            messageText = itemView.findViewById(R.id.text_message_body);
            timeText = itemView.findViewById(R.id.text_message_time);
            nameText = itemView.findViewById(R.id.recipient_name);
            //profileImage = (ImageView) itemView.findViewById(R.id.image_message_profile);
        }

        void bind(Message message) {
            messageText.setText(message.getMessage());
            

            nameText.setText(mThread.getRecipient().getFirstName());
            // Insert the profile image from the URL into the ImageView.
            //Utils.displayRoundImageFromUrl(mContext, message.getSender().getProfileUrl(), profileImage);
        }
    }
}