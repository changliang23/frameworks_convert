//package com.convert.cucumber.runner;
//
//import io.cucumber.testng.AbstractTestNGCucumberTests;
//import io.cucumber.testng.CucumberOptions;
//
//@CucumberOptions(
//        features = "src/test/resources/features",
//        glue = "steps",
//        plugin = {"pretty"}
//)
//public class CucumberTest extends AbstractTestNGCucumberTests {
//}

package com.convert.cucumber.runner;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
        features = "src/test/resources/features",
        glue = "steps",
        plugin = {"pretty", "html:target/cucumber-report.html"}
)
public class CucumberTest extends AbstractTestNGCucumberTests {
}