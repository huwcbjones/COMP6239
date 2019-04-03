package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

public class Student extends User {

    @SerializedName("location")
    private String location;
}
