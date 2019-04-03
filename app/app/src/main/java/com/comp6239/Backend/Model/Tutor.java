package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

public class Tutor extends User {
    @SerializedName("bio")
    private String bio;

    @SerializedName("price")
    private float price;

    @SerializedName("location")
    private String location;

    public String getBio() {
        return bio;
    }

    public void setBio(String bio) {
        this.bio = bio;
    }

    public float getPrice() {
        return price;
    }

    public void setPrice(float price) {
        this.price = price;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }
}
