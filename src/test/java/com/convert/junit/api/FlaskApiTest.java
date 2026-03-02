package com.convert.junit.api;

import com.convert.junit.common.BaseTest;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.*;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class FlaskApiTest extends BaseTest {

    static String tempUser;

    @Test
    @Order(1)
    void test_register_user() {
        tempUser = "user" + System.currentTimeMillis();

        Map<String, String> body = new HashMap<>();
        body.put("username", tempUser);
        body.put("password", "123456");

        Response response = given()
                .contentType(ContentType.JSON)
                .body(body)
                .post("/api/register");

        assertEquals(200, response.statusCode());
        assertEquals("register success", response.jsonPath().getString("msg"));
    }

    @Test
    @Order(2)
    void test_login_success() {
        Map<String, String> body = new HashMap<>();
        body.put("username", tempUser);
        body.put("password", "123456");

        Response response = given()
                .contentType(ContentType.JSON)
                .body(body)
                .post("/api/login");

        assertEquals(200, response.statusCode());
        assertEquals("login success", response.jsonPath().getString("msg"));
    }

    @Test
    @Order(3)
    void test_login_fail() {
        Map<String, String> body = new HashMap<>();
        body.put("username", tempUser);
        body.put("password", "wrong");

        Response response = given()
                .contentType(ContentType.JSON)
                .body(body)
                .post("/api/login");

        assertEquals(401, response.statusCode());
        assertEquals("login failed", response.jsonPath().getString("msg"));
    }

    @Test
    @Order(4)
    void test_get_users() {
        Response response = given().get("/api/users");

        assertEquals(200, response.statusCode());
        assertTrue(response.jsonPath().getList("users").size() > 0);
    }

    @Test
    @Order(5)
    void test_delete_user() {
        Response response = given().get("/api/delete/" + tempUser);

        assertEquals(200, response.statusCode());
        assertEquals("delete success", response.jsonPath().getString("msg"));
    }
}
