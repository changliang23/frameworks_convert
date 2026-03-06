Feature: Flask UI Test

Scenario: Login success
    Given browser is open
    When I open login page
    And I login with username "admin" and password "123456"
    Then I should see dashboard