package com.convert.playwright;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class DeleteUserTest extends BaseTest {

    @Test
    void testDeleteUser() {

        page.navigate("http://127.0.0.1:5000/login");

        page.fill("#username", "admin");
        page.fill("#password", "123456");

        page.click("#loginBtn");

        page.waitForURL("**/dashboard");

        page.navigate("http://127.0.0.1:5000/users");

        page.locator("a[href^='/delete/']").first().click();

        Assertions.assertTrue(page.content().contains("删除成功"));
    }
}