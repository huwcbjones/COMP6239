package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;


public enum Gender {
    @SerializedName("m")
    MALE,
    @SerializedName("f")
    FEMALE,
    @SerializedName("n")
    NOT_SAY
}
