import json

ir = json.load(open("ir.json", encoding="utf-8"))

def gen_testng(test):
    lines = []
    lines.append("@Test")
    lines.append(f"public void {test['name']}() " + "{")
    for step in test["steps"]:
        if step["action"] == "open":
            lines.append(f'    driver.get("{step["target"]}");')
        elif step["action"] == "input":
            lines.append(f'    driver.findElement(By.cssSelector("{step["target"]}")).sendKeys("{step["value"]}");')
        elif step["action"] == "click":
            lines.append(f'    driver.findElement(By.cssSelector("{step["target"]}")).click();')
        elif step["action"] == "assert_text":
            lines.append(f'    Assert.assertTrue(driver.getPageSource().contains("{step["value"]}"));')
    lines.append("}")
    return "\n".join(lines)

java_code = []
java_code.append("import org.testng.annotations.Test;")
java_code.append("import org.testng.Assert;")
java_code.append("import org.openqa.selenium.*;")
java_code.append("public class GeneratedTest {")
for t in ir:
    java_code.append(gen_testng(t))
java_code.append("}")

with open("testng/GeneratedTest.java", "w", encoding="utf-8") as f:
    f.write("\n".join(java_code))

print("✅ 已生成 GeneratedTest.java")
