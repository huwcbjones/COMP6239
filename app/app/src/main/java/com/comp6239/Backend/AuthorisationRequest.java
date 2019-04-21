package com.comp6239.Backend;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class AuthorisationRequest {
    @SerializedName("username")
    @Expose //Constant for Client ID
    private String username;

    @SerializedName("password")
    @Expose //Constant for Client ID
    private String password;

    @SerializedName("client_id")
    @Expose
    private final String client_id = "7834452b12ab480d9fc99f23b3546524";

    @SerializedName("grant_type")
    @Expose
    private String grant_type;

    @SerializedName("refresh_token")
    @Expose
    private String refresh_token;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getGrant_type() {
        return grant_type;
    }

    public void setGrant_type(String grant_type) {
        this.grant_type = grant_type;
    }

    public String getClient_id() {
        return client_id;
    }
}
