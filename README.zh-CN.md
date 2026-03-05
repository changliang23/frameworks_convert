# frameworks_convert
这是一个供熟悉学习Python,Java各框架(目前包含Python的PyTest[selenium, playwright],Behave，Java的testng,junit,restassured,cucumber)运行的demo，另外包含mock server(目前包含flask,typescript),及各框架脚本转换的项目(目前包含pytest转testng)

项目目录结构如下：
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
│   ├── playwright_demo  
│   ├── pytest_demo  
│  
├── src/test/java/com/convert/    
│   ├── cucumber  
│   ├── junit  
│   ├── playwright  
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

typescript demo依赖安装及启动步骤：  
npm init -y  
npm install express   
npm install -D typescript ts-node-dev @types/express  
启动： npx ts-node-dev src/app.ts  

flask demo依赖安装及启动步骤：  
pip install flask  
启动： python app.py  

cucumber/junit/restassured/testng脚本运行:  
mvn clean test  

pytest脚本运行:  
pytest -v  

behave脚本运行：  
behave  

playwright依赖安装：  
pip install playwright pytest  
playwright install  
playwright install chromium  
