package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

import java.util.UUID;

public class Subject {
    @SerializedName("name")
    String name;
    @SerializedName("id")
    UUID id;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }
}
