package com.convert.playwright;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class LoginTest extends BaseTest {

    @Test
    void testLoginSuccess() {

        page.navigate("http://127.0.0.1:5000/login");

        page.fill("#username", "admin");
        page.fill("#password", "123456");

        page.click("#loginBtn");

        page.waitForURL("**/dashboard");

        Assertions.assertTrue(page.url().contains("/dashboard"));
    }
}