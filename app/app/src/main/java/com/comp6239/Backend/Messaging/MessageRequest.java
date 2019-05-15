package com.comp6239.Backend.Messaging;

import com.google.gson.annotations.SerializedName;

import java.util.UUID;

public class MessageRequest {
    @SerializedName("to")
    String recipientId;

    @SerializedName("message")
    String message;

    public MessageRequest(String recipientId, String message) {
        this.recipientId = recipientId;
        this.message = message;
    }

    public MessageRequest(String message) {
        this.message = message;
    }

    public String getRecipientId() {
        return recipientId;
    }

    public void setRecipientId(String recipientId) {
        this.recipientId = recipientId;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
