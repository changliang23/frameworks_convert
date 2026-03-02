package com.convert.junit.ui;

import org.junit.jupiter.api.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import java.time.Duration;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.testng.Assert;

import static org.junit.jupiter.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class GeneratedUITest {

    private static WebDriver driver;

    @BeforeAll
    public static void setUp() {
        // 如果不用 WebDriverManager，就手动指定
        // System.setProperty("webdriver.chrome.driver", "/path/to/chromedriver");
        System.setProperty("webdriver.chrome.driver", "/Users/liangchang/code/frameworks_convert/chromedriver/chromedriver");
        driver = new ChromeDriver();
        driver.manage().window().maximize();
    }

    @AfterAll
    public static void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    @Order(1)
    public void test_login_success() {
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.cssSelector("#username")).sendKeys("admin");
        driver.findElement(By.cssSelector("#password")).sendKeys("123456");
        driver.findElement(By.cssSelector("#loginBtn")).click();

        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
        wait.until(ExpectedConditions.urlContains("/dashboard"));

        assertTrue(driver.getCurrentUrl().contains("/dashboard"));
    }

    @Test
    @Order(2)
    public void test_login_fail() {
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.cssSelector("#username")).sendKeys("admin");
        driver.findElement(By.cssSelector("#password")).sendKeys("wrong");
        driver.findElement(By.cssSelector("#loginBtn")).click();
        assertTrue(driver.getPageSource().contains("登录失败"));
    }

    @Test
    @Order(3)
    public void test_register_user() {
        driver.get("http://127.0.0.1:5000/register");
        driver.findElement(By.cssSelector("#username")).sendKeys("testuser");
        driver.findElement(By.cssSelector("#password")).sendKeys("111111");
        driver.findElement(By.cssSelector("#registerBtn")).click();
        assertTrue(driver.getCurrentUrl().contains("/login"));
    }

    @Test
    @Order(4)
    public void test_delete_user() {
        // 1. 注册一个新用户
        driver.get("http://127.0.0.1:5000/register");
        String username = "user" + System.currentTimeMillis();
        driver.findElement(By.cssSelector("#username")).sendKeys(username);
        driver.findElement(By.cssSelector("#password")).sendKeys("111111");
        driver.findElement(By.cssSelector("#registerBtn")).click();

        // 2. 登录 admin
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.cssSelector("#username")).sendKeys("admin");
        driver.findElement(By.cssSelector("#password")).sendKeys("123456");
        driver.findElement(By.cssSelector("#loginBtn")).click();

        // 3. 打开用户列表
        driver.get("http://127.0.0.1:5000/users");

        // 4. 删除刚刚创建的用户
        driver.findElement(By.cssSelector("a[href='/delete/" + username + "']")).click();

        Assert.assertTrue(driver.getPageSource().contains("删除成功"));
    }

    @Test
    @Order(5)
    public void test_iframe_users_page() {
        driver.get("http://127.0.0.1:5000/iframe");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(0));

        assertTrue(driver.findElement(By.tagName("body"))
                .getText().contains("用户列表"));

        driver.switchTo().defaultContent();
    }

    @Test
    @Order(6)
    public void test_upload_file() {
        driver.get("http://127.0.0.1:5000/upload");
        driver.findElement(By.cssSelector("#fileInput"))
                .sendKeys("/Users/liangchang/code/frameworks_convert/test.txt");
        driver.findElement(By.cssSelector("#uploadBtn")).click();
        assertTrue(driver.getPageSource().contains("上传成功"));
    }
}