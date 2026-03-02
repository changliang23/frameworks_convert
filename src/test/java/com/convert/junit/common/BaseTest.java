package com.convert.junit.common;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeAll;

public class BaseTest {

    @BeforeAll
    public static void init() {
        RestAssured.baseURI = "http://127.0.0.1:5000";
    }
}