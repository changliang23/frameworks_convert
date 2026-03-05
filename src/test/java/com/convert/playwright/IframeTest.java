package com.convert.playwright;

import com.microsoft.playwright.FrameLocator;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class IframeTest extends BaseTest {

    @Test
    void testIframeUsersPage() {

        page.navigate("http://127.0.0.1:5000/iframe");

        FrameLocator frame = page.frameLocator("#myframe");

        frame.getByText("用户列表").waitFor();

        Assertions.assertTrue(frame.getByText("用户列表").isVisible());
    }
}