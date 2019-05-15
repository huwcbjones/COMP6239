package com.comp6239.Backend.Messaging;

import com.google.gson.annotations.SerializedName;

import org.joda.time.DateTime;

import java.util.UUID;

public class Message {


    @SerializedName("id")
    private UUID id;

    @SerializedName("sender_id")
    private UUID senderId;

    @SerializedName("timestamp")
    private String sentAt;

    private DateTime timestamp;

    @SerializedName("message")
    private String message;

    @SerializedName("state")
    private MessageState state;

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getSenderId() {
        return senderId;
    }

    public void setSenderId(UUID senderId) {
        this.senderId = senderId;
    }

    public String getSentAt() {
        return sentAt;
    }

    public void setSentAt(String sentAt) {
        this.timestamp = new DateTime(sentAt);
        this.sentAt = sentAt;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public MessageState getState() {
        return state;
    }

    public void setState(MessageState state) {
        this.state = state;
    }

    public DateTime getTimestamp() {
        if (timestamp == null){
            setSentAt(sentAt);
        }
        return timestamp;
    }
}

