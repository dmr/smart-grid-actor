Feature: Query simple actor server
  In order for the simulation to work
  A simple actor server
  Should return the current consumption

  Scenario: Actor returns current consumption
    Given ActorServer with vr [1,2] on port 9001
    #Given Server on port 9001 <-- just comment out the above line to start without server
    When I query 9001 "/"
    Then I receive status 200
    And I receive json "{'value':1}"

  Scenario: Actor returns value range
    Given ActorServer with vr [1,2] on port 9001
    When I query 9001 "/vr/"
    Then I receive status 200
    And I receive json "{'value_range':[1,2]}"

  Scenario: Actor allows value update
    Given ActorServer with vr [1,2] on port 9001
    When I update 9001 "/" with "2"
    Then I receive status 200
    And I receive json "{'value':2}"
    And actor 9001 value is "{'value':2}"

  Scenario: Actor denies value update out of range
    Given ActorServer with vr [1,2] on port 9001
    When I update 9001 "/" with "3"
    Then I receive status 400
    And I receive content "Input error: 3 not in value_range [1, 2]"
    And actor 9001 value is "{'value':1}"

  Scenario: Actor denies value update wrong input
    Given ActorServer with vr [1,2] on port 9001
    When I update 9001 "/" with "drei"
    Then I receive status 400
    And I receive content "Input error: Not a valid integer: 'drei'"
    And actor 9001 value is "{'value':1}"

  Scenario: Actor returns Redirect
    Given ActorServer with vr [1,2] on port 9001
    When I query 9001 "/wrong"
    Then I receive status 301
    And I receive content "Moved permanently: /"