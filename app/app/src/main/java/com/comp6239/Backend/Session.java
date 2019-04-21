package com.comp6239.Backend;

import com.comp6239.Backend.Model.User;

public interface Session {
    boolean isLoggedIn();

    void saveToken(String token);

    void saveRefreshToken(String token);

    String getToken();

    String getRefreshToken();

    void saveEmail(String email);

    String getEmail();

    void savePassword(String password);

    String getPassword();

    void invalidate();

    User getUser();

    void setUser(User user);
}