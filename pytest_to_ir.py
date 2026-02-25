import ast, json

class PyTestParser(ast.NodeVisitor):
    def __init__(self):
        self.tests = []

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            test = {"name": node.name, "steps": []}
            for stmt in node.body:
                # driver.get("/login")
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    call = stmt.value
                    if isinstance(call.func, ast.Attribute):
                        # driver.get
                        if call.func.attr == "get":
                            url = call.args[0].value
                            test["steps"].append({"action": "open", "target": url})

                        # driver.find(...).send_keys(...)
                        if call.func.attr == "send_keys":
                            sel = call.func.value.args[0].value
                            val = call.args[0].value
                            test["steps"].append({"action": "input", "target": sel, "value": val})

                        # driver.find(...).click()
                        if call.func.attr == "click":
                            sel = call.func.value.args[0].value
                            test["steps"].append({"action": "click", "target": sel})

                # assert "成功" in driver.page_source
                if isinstance(stmt, ast.Assert):
                    val = stmt.test.left.value
                    test["steps"].append({"action": "assert_text", "target": "page", "value": val})

            self.tests.append(test)

with open("pytest/test_selenium_demo.py") as f:
    tree = ast.parse(f.read())

parser = PyTestParser()
parser.visit(tree)

with open("ir.json", "w", encoding="utf-8") as f:
    json.dump(parser.tests, f, ensure_ascii=False, indent=2)

print("✅ 已生成 ir.json")
