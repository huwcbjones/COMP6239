package com.comp6239.Backend.Messaging;

import com.google.gson.annotations.SerializedName;

public enum MessageState {
    SENDING,
    @SerializedName("s")
    SENT,
    @SerializedName("d")
    DELIVERED,
    @SerializedName("d")
    READ
}
