package com.comp6239.Backend.Messaging;

import com.google.gson.annotations.SerializedName;

public enum ThreadState {
    @SerializedName("r")
    REQUESTED,
    @SerializedName("b")
    BLOCKED,
    @SerializedName("a")
    ALLOWED
}
