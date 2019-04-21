package com.comp6239.Backend;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class Authorisation {


    @SerializedName("token_type")
    @Expose //Constant for Client ID
    private String tokenType;

    @SerializedName("scope")
    @Expose //Constant for Client ID
    private String scope;

    @SerializedName("refresh_token")
    @Expose
    private String refreshToken;

    @SerializedName("access_token")
    @Expose
    private String token;

    @SerializedName("expires_in")
    @Expose
    private double expiresIn;

    public String getTokenType() {
        return tokenType;
    }

    public void setTokenType(String tokenType) {
        this.tokenType = tokenType;
    }

    public String getScope() {
        return scope;
    }

    public void setScope(String scope) {
        this.scope = scope;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public double getExpiresIn() {
        return expiresIn;
    }

    public void setExpiresIn(double expiresIn) {
        this.expiresIn = expiresIn;
    }
}
