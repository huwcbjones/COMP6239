package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

public class Tutor extends User {
    @SerializedName("bio")
    private String bio;

    @SerializedName("price")
    private float price;


    /**
     * Registration constructor for Tutor
     * @param email
     * @param firstName
     * @param lastName
     * @param gender
     * @param location
     * @param password
     * @param bio
     * @param price
     */
    public Tutor(String email, String firstName, String lastName, Gender gender, String location, String password, String bio, float price) {
        this.bio = bio;
        this.price = price;
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
    }

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

}
