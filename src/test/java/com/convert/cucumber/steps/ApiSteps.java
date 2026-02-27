package steps;

import io.cucumber.java.en.*;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.testng.Assert.*;

public class ApiSteps {

    Response response;
    String tempUser;

    @Given("API server is running")
    public void api_server_is_running() {
        RestAssured.baseURI = "http://127.0.0.1:5000";
    }

    @When("I register via api")
    public void i_register_via_api() {
        tempUser = "user" + System.currentTimeMillis();
        Map<String, String> body = new HashMap<>();
        body.put("username", tempUser);
        body.put("password", "123456");

        response = given()
                .contentType(ContentType.JSON)
                .body(body)
                .post("/api/register");
    }

    @Then("api register response should be success")
    public void api_register_response_should_be_success() {
        assertEquals(response.statusCode(), 200);
        assertEquals(response.jsonPath().getString("msg"), "register success");
    }

    @When("I login via api with username {string} and password {string}")
    public void i_login_via_api(String u, String p) {
        Map<String, String> body = new HashMap<>();
        body.put("username", u);
        body.put("password", p);

        response = given()
                .contentType(ContentType.JSON)
                .body(body)
                .post("/api/login");
    }

    @Then("api login response should be {string}")
    public void api_login_response_should_be(String msg) {
        assertEquals(response.jsonPath().getString("msg"), msg);
    }

    @When("I get user list via api")
    public void i_get_user_list_via_api() {
        response = given().get("/api/users");
    }

    @Then("api user list should not be empty")
    public void api_user_list_should_not_be_empty() {
        assertTrue(response.jsonPath().getList("users").size() > 0);
    }

    @When("I create and delete user via api")
    public void i_create_and_delete_user_via_api() {
        tempUser = "del" + System.currentTimeMillis();
        Map<String, String> body = new HashMap<>();
        body.put("username", tempUser);
        body.put("password", "123456");

        given().contentType(ContentType.JSON).body(body).post("/api/register");
        response = given().get("/api/delete/" + tempUser);
    }

    @Then("api delete response should be success")
    public void api_delete_response_should_be_success() {
        assertEquals(response.jsonPath().getString("msg"), "delete success");
    }
}