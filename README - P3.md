# Vehicle Database Project part 3
Group 106 : 
Hongwei Zha (hz2816@columbia.edu)
Wei Zhang (wz2580@co1umbia.edu)

## PostgreSQL Account
hz2816

## URL
http://34.74.203.207:8111

## Descriptions

1. Browsering: The Applications allow the user to browser through vehicle, dearlership, and manufacturer informations with search option and constraints.
2. Order check: The user can check his or her order by enter CID and phone number. 
3. Place order: user can place order by entering vehicle id, manufacuter id, and insurance id.
4. Admin interface: Admin can check all the table in database, and run sql commands.
5. Recommendation: Choose a vehicle, and return recommendation based on vehicle and car prices.

## 2 Most interesting database operation

1. Recommendation page: Based on the chosen vehicle, sql query will return the one with the same manufacturer, and similar price cars.

2. Checkout webpage will auto insert the new transaction into car_sale_transaction.