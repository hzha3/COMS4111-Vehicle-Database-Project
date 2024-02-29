# Vehicle Database Project part 4
Group 106 : 
Hongwei Zha (hz2816@columbia.edu)
Wei Zhang (wz2580@co1umbia.edu)

## PostgreSQL Account
hz2816


## Item 1 (text attribute - Customer Review)
We create a new table (reviews). Within the review, we add the column review, which is text attribute containing long text review for the particular vehicle. Customer want to find the reviews related to vehicle they want to buy.

Example Query:
(select reviews contain the word 'nightmare')
        SELECT *
        FROM reviews
        WHERE to_tsvector(review) @@ to_tsquery( 'nightmare');

This query returns a series of review, and no surprise that these reviews are rated very low.

    
## Item 2 (Array attribute - tags list)
With in the table (reviews), it also contained column tags, which is text array attribute. It contains a list of tag assoicates with the review. It accomdates the customers to find the review to look at.

Example Query:
(for each review, show the first 3 tags associated with review)
        select review_title, review, tags[1],tags[2],tags[3]
        from reviews

Example Query 2:
(show reviews contain tag 'child')
        select review_title, review, rating, tags
        from reviews
        where tags @> '{"child"}'

## Item 3 (Create Type)

Skip


## Item 4 (Trigger - check if car price < anuall income)
We create trigger to check if customer income is higher than car price before buying the car.

### Function
```

        CREATE OR REPLACE FUNCTION income_check() RETURNS TRIGGER AS $$
        DECLARE
            c_income integer;
            v_price integer;
        BEGIN
            IF NEW.v_id IS NOT NULL AND NEW.c_id IS NOT NULL THEN
                SELECT customer.annual_income INTO STRICT c_income
                FROM customer
                WHERE c_id = NEW.c_id;

                SELECT vehicle.price_in_thousands INTO STRICT v_price
                FROM vehicle
                WHERE v_id = NEW.v_id;

                IF c_income < v_price * 1000 THEN
                    RAISE EXCEPTION 'Customer income is lower than car price';
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;    
```
###Trigger

```
        CREATE TRIGGER check_customer_income_trigger
        BEFORE INSERT ON car_sale_transaction
        FOR EACH ROW
        EXECUTE FUNCTION income_check();
```


###Testing

Case with income lower than vehicle car:
vehicle V_84: Mercedes-B	S-Class	39k
customer C_1: Geraldine     13,500 (income)
```
        INSERT INTO car_sale_transaction (t_id , transaction_date ,v_id , c_id , s_id , d_id,i_id,manufacturer_name)
        VALUES ('T_35000', '04/17/2023', 'V_84','C_1','S_316','D7_S2','I_9','Mercedes-B');
        ; 
```
result:
ERROR:  Customer income is lower than car price
CONTEXT:  PL/pgSQL function income_check() line 16 at RAISE


Case with income higher than vehicle car:
vehicle V_39: Dodge  Intrepid	11k
customer C_1: Geraldine     13,500 (income)
```
        INSERT INTO car_sale_transaction (t_id , transaction_date ,v_id , c_id , s_id , d_id,i_id,manufacturer_name)
        VALUES ('T_34740', '04/17/2023', 'V_39','C_1','S_316','D7_S2','I_9','Mercedes-B');
        ; 
```
