package com.comp6239.Backend.Messaging;

import com.comp6239.Backend.Model.User;
import com.google.gson.annotations.SerializedName;

import java.util.UUID;

public class MessageThread {
    @SerializedName("id")
    private UUID id;

    @SerializedName("recipient")
    private User recipient;

    @SerializedName("state")
    private ThreadState state;

    @SerializedName("messages")
    private Message[] messages;

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public User getRecipient() {
        return recipient;
    }

    public void setRecipient(User recipient) {
        this.recipient = recipient;
    }

    public ThreadState getState() {
        return state;
    }

    public void setState(ThreadState state) {
        this.state = state;
    }

    public Message[] getMessages() {
        return messages;
    }

    public void setMessages(Message[] messages) {
        this.messages = messages;
    }
}
