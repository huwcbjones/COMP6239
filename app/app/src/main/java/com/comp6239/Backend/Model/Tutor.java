package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

import java.time.LocalDateTime;

public class Tutor extends User {
    @SerializedName("bio")
    private String bio;

    @SerializedName("status")
    private Boolean isApproved;

    @SerializedName("price")
    private Double price;

    @SerializedName("subjects")
    Subject[] subjects;

    @SerializedName("reason")
    String reasonForRejection;

    @SerializedName("revision")
    LocalDateTime dateOfLastRevision;

    @SerializedName("reviewed_at")
    LocalDateTime lastTimeReviewed;

    public Subject[] getSubjects() {
        return subjects;
    }

    public void setSubjects(Subject[] subjects) {
        this.subjects = subjects;
    }

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
    public Tutor(String email, String firstName, String lastName, Gender gender, String location, String password, String bio, Double price) {
        this.bio = bio;
        this.price = price;
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
    }

    public Tutor(String email, String firstName, String lastName, Gender gender, String location, String password) {
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
    }

    public Tutor() {
        //Empty constructor
    }

    public Boolean isApproved() {
        return isApproved;
    }

    public void setApproved(Boolean approved) {
        isApproved = approved;
    }

    public String getBio() {
        return bio;
    }

    public void setBio(String bio) {
        this.bio = bio;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public String getReasonForRejection() {
        return reasonForRejection;
    }

    public void setReasonForRejection(String reasonForRejection) {
        this.reasonForRejection = reasonForRejection;
    }

    public LocalDateTime getDateOfLastRevision() {
        return dateOfLastRevision;
    }

    public void setDateOfLastRevision(LocalDateTime dateOfLastRevision) {
        this.dateOfLastRevision = dateOfLastRevision;
    }

    public LocalDateTime getLastTimeReviewed() {
        return lastTimeReviewed;
    }

    public void setLastTimeReviewed(LocalDateTime lastTimeReviewed) {
        this.lastTimeReviewed = lastTimeReviewed;
    }
}
