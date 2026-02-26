package api;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;

public class FlaskApiTest {

    @BeforeClass
    public void setup() {
        RestAssured.baseURI = "http://127.0.0.1:5000";
    }

    @Test
    public void testApiRegisterUser() {
        String username = "user" + System.currentTimeMillis();

        Map<String, String> body = new HashMap<>();
        body.put("username", username);
        body.put("password", "123456");

        Response res =
                given()
                        .contentType(ContentType.JSON)
                        .body(body)
                        .when()
                        .post("/api/register")
                        .then()
                        .statusCode(200)
                        .extract().response();

        Assert.assertEquals(res.jsonPath().getString("msg"), "register success");
    }

    @Test
    public void testApiLoginSuccess() {
        Map<String, String> body = new HashMap<>();
        body.put("username", "admin");
        body.put("password", "123456");

        Response res =
                given()
                        .contentType(ContentType.JSON)
                        .body(body)
                        .when()
                        .post("/api/login")
                        .then()
                        .statusCode(200)
                        .extract().response();

        Assert.assertEquals(res.jsonPath().getString("msg"), "login success");
    }

    @Test
    public void testApiLoginFail() {
        Map<String, String> body = new HashMap<>();
        body.put("username", "admin");
        body.put("password", "wrong");

        Response res =
                given()
                        .contentType(ContentType.JSON)
                        .body(body)
                        .when()
                        .post("/api/login")
                        .then()
                        .statusCode(401)
                        .extract().response();

        Assert.assertEquals(res.jsonPath().getString("msg"), "login failed");
    }

    @Test
    public void testApiGetUsers() {
        Response res =
                given()
                        .when()
                        .get("/api/users")
                        .then()
                        .statusCode(200)
                        .extract().response();

        Assert.assertTrue(res.jsonPath().getList("users").size() > 0);
    }

    @Test
    public void testApiDeleteUser() {
        // 1. 先注册用户
        String username = "del" + System.currentTimeMillis();
        Map<String, String> body = new HashMap<>();
        body.put("username", username);
        body.put("password", "123456");

        given()
                .contentType(ContentType.JSON)
                .body(body)
                .when()
                .post("/api/register")
                .then()
                .statusCode(200);

        // 2. 删除用户
        Response res =
                given()
                        .when()
                        .get("/api/delete/" + username)
                        .then()
                        .statusCode(200)
                        .extract().response();

        Assert.assertEquals(res.jsonPath().getString("msg"), "delete success");
    }
}