# frameworks_convert
This is a demo project for those familiar with learning Python and Java frameworks (currently including Python's PyTest[selenium, playwright],, Behave, and Java's TestNG, JUnit, RestAssured, Cucumber). It also includes a mock server (currently featuring Flask and TypeScript) and a project for converting scripts between frameworks (currently including conversion from Pytest to TestNG).

The project directory structure is as follows:  
frameworks_convert/  
│  
├── framework_convert/  
│   ├── pytest_to_testng  
│  
├── mock_server/  
│   ├── flask_demo  
│   ├── ts_demo  
│  
├── python_tests/  
│   ├── behave_demo  
│   ├── pytest_demo  
│  
├── src/test/java/com/convert/    
│   ├── cucumber  
│   ├── junit  
│   ├── restassured    
│   └── testng  
│  
├── src/resources/  
│   ├── features    
│   └── testdata     
│  
├── Jenkinsfile  
│  
└── README.md

TypeScript demo dependency installation and startup steps:
npm init -y
npm install express
npm install -D typescript ts-node-dev @types/express
Start: npx ts-node-dev src/app.ts

Flask demo dependency installation and startup steps:
pip install flask
Start: python app.py

Running Cucumber/JUnit/RestAssured/TestNG scripts:
mvn clean test

Running Pytest scripts:
pytest -v

Running Behave scripts:
behave  

Playwright dependency installation:  
pip install playwright pytest  
playwright install  
playwright install chromium  