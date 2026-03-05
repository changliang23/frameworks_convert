package com.convert.playwright;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class RegisterTest extends BaseTest {

    @Test
    void testRegisterUser() {

        String user = "user" + System.currentTimeMillis();

        page.navigate("http://127.0.0.1:5000/register");

        page.fill("#username", user);
        page.fill("#password", "123456");

        page.click("#registerBtn");

        page.waitForURL("**/login");

        Assertions.assertTrue(page.url().contains("/login"));
    }
}