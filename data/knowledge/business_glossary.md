# Business Analytics Knowledge Base

## Order Definitions
An order is a customer purchase recorded in the orders table.
Each order has an order ID, customer ID, product ID, quantity, order date, and status.

## Order Statuses
- Delivered: The order was successfully delivered to the customer.
- Cancelled: The order was cancelled and should not count as completed sales.
- Returned: The order was returned after purchase and should be tracked separately.

## Revenue Definitions
- Order revenue is calculated as product price multiplied by order quantity.
- Delivered revenue includes only orders whose status is delivered.
- Cancelled orders should be excluded from delivered revenue calculations.
- Returned orders should be reported separately unless the business defines another accounting rule.

## Product Categories
- Electronics: Electronic products and accessories.
- Fashion: Clothing, footwear, and wearable accessories.
- Home: Products used for household needs.
- Books: Printed or educational reading materials.

## Reporting Guidelines
- When reporting delivered revenue, filter orders to delivered status.
- When comparing product categories, group results by product category.
- When reporting order counts, clarify whether the count includes all orders or only orders with a specific status.
- If a business definition is not available in this knowledge base, state that the information is unavailable rather than inventing an answer.