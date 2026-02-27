package steps;

import io.cucumber.java.en.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;

public class UiSteps {

    WebDriver driver;
    String tempUser;

    @Given("browser is open")
    public void browser_is_open() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
    }

    @When("I open login page")
    public void i_open_login_page() {
        driver.get("http://127.0.0.1:5000/login");
    }

    @When("I login via ui with username {string} and password {string}")
    public void i_login_via_ui(String u, String p) {
        driver.findElement(By.id("username")).sendKeys(u);
        driver.findElement(By.id("password")).sendKeys(p);
        driver.findElement(By.id("loginBtn")).click();
    }

    @Then("I should see dashboard")
    public void i_should_see_dashboard() {
        Assert.assertTrue(driver.getCurrentUrl().contains("/dashboard"));
        driver.quit();
    }

    @When("I open register page")
    public void i_open_register_page() {
        driver.get("http://127.0.0.1:5000/register");
    }

    @When("I register random user via ui")
    public void i_register_random_user_via_ui() {
        tempUser = "user" + System.currentTimeMillis();
        driver.findElement(By.id("username")).sendKeys(tempUser);
        driver.findElement(By.id("password")).sendKeys("123456");
        driver.findElement(By.id("registerBtn")).click();
    }

    @Then("I should go to login page")
    public void i_should_go_to_login_page() {
        Assert.assertTrue(driver.getCurrentUrl().contains("/login"));
        driver.quit();
    }

    @When("I login as admin via ui")
    public void i_login_as_admin_via_ui() {
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.id("username")).sendKeys("admin");
        driver.findElement(By.id("password")).sendKeys("123456");
        driver.findElement(By.id("loginBtn")).click();
    }

    @When("I delete user via ui")
    public void i_delete_user_via_ui() {
        driver.get("http://127.0.0.1:5000/users");
        driver.findElement(By.cssSelector("a[href^='/delete/']")).click();
    }

    @Then("I should see delete success")
    public void i_should_see_delete_success() {
        Assert.assertTrue(driver.getPageSource().contains("删除成功"));
        driver.quit();
    }
}