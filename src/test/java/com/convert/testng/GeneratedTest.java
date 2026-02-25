package com.convert.testng;

import org.testng.annotations.Test;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.AfterClass;
import org.testng.Assert;
import org.openqa.selenium.*;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class GeneratedTest {
    private WebDriver driver;

    @BeforeClass
    public void setUp() {
        // 方式1：直接设置系统属性
        System.setProperty("webdriver.chrome.driver", "/Users/liangchang/code/frameworks_convert/chromedriver/chromedriver");
        driver = new ChromeDriver();

        // 方式2：使用WebDriverManager（推荐，需要添加依赖）
        // WebDriverManager.chromedriver().setup();
        // driver = new ChromeDriver();

        // 最大化窗口
        driver.manage().window().maximize();
    }
    @Test
    public void test_login_success() {
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.cssSelector("#username")).sendKeys("admin");
        driver.findElement(By.cssSelector("#password")).sendKeys("123456");
        driver.findElement(By.cssSelector("#loginBtn")).click();
        Assert.assertTrue(driver.getCurrentUrl().contains("/dashboard"));
    }
    @Test
    public void test_login_fail() {
        driver.get("http://127.0.0.1:5000/login");
        driver.findElement(By.cssSelector("#username")).sendKeys("admin");
        driver.findElement(By.cssSelector("#password")).sendKeys("wrong");
        driver.findElement(By.cssSelector("#loginBtn")).click();
        Assert.assertTrue(driver.getPageSource().contains("登录失败"));
    }
    @Test
    public void test_register_user() {
        driver.get("http://127.0.0.1:5000/register");
        String username = "user" + System.currentTimeMillis();
        driver.findElement(By.cssSelector("#username")).sendKeys(username);
        driver.findElement(By.cssSelector("#password")).sendKeys("111111");
        driver.findElement(By.cssSelector("#registerBtn")).click();
        Assert.assertTrue(driver.getPageSource().contains("登录"));
    }
    @Test
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
    public void test_iframe_users_page() {
        driver.get("http://127.0.0.1:5000/iframe");
        WebElement frame = driver.findElement(By.cssSelector("#myframe"));
        driver.switchTo().frame(frame);
        Assert.assertTrue(driver.getPageSource().contains("用户列表"));
        driver.switchTo().defaultContent();
    }
    @Test
    public void test_upload_file() {
        driver.get("http://127.0.0.1:5000/upload");
        driver.findElement(By.cssSelector("#fileInput")).sendKeys("/Users/liangchang/code/frameworks_convert/test.txt");
        driver.findElement(By.cssSelector("#uploadBtn")).click();
        Assert.assertTrue(driver.getPageSource().contains("上传成功"));
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}