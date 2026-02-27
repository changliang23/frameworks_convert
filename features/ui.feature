Feature: Flask UI Test

Scenario: UI login success
  Given browser is open
  When I open login page
  And I login via ui with username "admin" and password "123456"
  Then I should see dashboard

Scenario: UI register user
  Given browser is open
  When I open register page
  And I register random user via ui
  Then I should go to login page

Scenario: UI delete user
  Given browser is open
  When I login as admin via ui
  And I delete user via ui
  Then I should see delete success