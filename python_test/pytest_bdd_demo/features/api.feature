Feature: Flask API Test

Scenario: Register user
    Given API server is running
    When I register a new user
    Then register response should be success

Scenario: Login success
    Given API server is running
    When I login with username "admin" and password "123456"
    Then login response should be "login success"

Scenario: Get user list
    Given API server is running
    When I get user list
    Then user list should not be empty