Feature: Shopping catalogue
  Customers can find a product and place it in their anonymous cart.

  Scenario Outline: Search for and add a catalogue product to the cart
    Given the customer views the product catalogue
    When they search for "<query>"
    And they open a matching product
    And they add the selected product to the cart
    Then the cart shows the selected product

    Examples:
      | query  |
      | hammer |
      | pliers |
