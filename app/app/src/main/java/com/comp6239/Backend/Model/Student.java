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
    public Student(String email, String firstName, String lastName, Gender gender, String location, String password) {
        this.setEmail(email);
        this.setFirstName(firstName);
        this.setLastName(lastName);
        this.setGender(gender);
        this.setLocation(location);
        this.setPassword(password);
    }

}
