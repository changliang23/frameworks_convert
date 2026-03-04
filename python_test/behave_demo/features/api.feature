Feature: Flask API Test

Scenario: Register user
  Given API server is running
  When I register via api
  Then api register response should be success

Scenario: Login success
  Given API server is running
  When I login via api with username "admin" and password "123456"
  Then api login response should be "login success"

Scenario: Get users
  Given API server is running
  When I get user list via api
  Then api user list should not be empty

Scenario: Delete user
  Given API server is running
  When I create and delete user via api
  Then api delete response should be success