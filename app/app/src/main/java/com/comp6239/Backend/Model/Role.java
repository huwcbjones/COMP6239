package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

public enum Role {
    @SerializedName("s")
    STUDENT,
    @SerializedName("t")
    TUTOR,
    @SerializedName("a")
    ADMIN
}
