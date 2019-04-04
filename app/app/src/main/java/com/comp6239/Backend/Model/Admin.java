package com.comp6239.Backend.Model;

import com.google.gson.annotations.SerializedName;

import java.util.UUID;

public class Admin extends User {

    public Admin() {
        this.setRole(Role.ADMIN);
    }

}
