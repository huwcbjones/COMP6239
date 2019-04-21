package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

public class Student extends User {

    /**
     * Registration constructor for Student
     * @param email
     * @param firstName
     * @param lastName
     * @param gender
     * @param location
     * @param password
     */

    @SerializedName("subjects")
    Subject[] subjects;

    public Student(String email, String firstName, String lastName, Gender gender, String location, String password) {
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
        subjects = new Subject[0];
    }

    public Student(String email, String firstName, String lastName, Gender gender, String location, String password, Subject[] subjects) {
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
        this.subjects = subjects;
    }

    public Subject[] getSubjects() {
        return subjects;
    }

    public void setSubjects(Subject[] subjects) {
        this.subjects = subjects;
    }
}
