
import pandas as pd 
import os
import duckdb


# Get the directory containing this Python file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the SQL script and DuckDB database
sql_file = os.path.join(BASE_DIR, "northwinddw.sql")
database_file = os.path.join(BASE_DIR, "northwind.duckdb")

# Create a connection to the DuckDB database
con = duckdb.connect(database_file)

# Read and execute the SQL script
with open(sql_file, "r", encoding="utf-8") as file:
    sql_script = file.read()

con.execute(sql_script)

First_query = con.execute("""
SELECT
    Customer.CompanyName,
    Product.ProductName,
    Employee.LastName,
    SUM(Sales.Quantity * Sales.UnitPrice) AS total

FROM Sales
JOIN Customer
    ON Sales.CustomerKey = Customer.CustomerKey

JOIN Product
    ON Sales.ProductKey = Product.ProductKey

JOIN Employee
    ON Sales.EmployeeKey = Employee.EmployeeKey

GROUP BY CUBE (
    Customer.CompanyName,
    Product.ProductName,
    Employee.LastName
)
Having total > 10000
ORDER BY total DESC
""").df().head()

print('Query in SQL with an extended group-by clause (CUBE) to include all combinations of the three columns:')
print(First_query)


Second_query = con.execute("""
SELECT
    Customer.CompanyName,
    Product.ProductName,
    Employee.LastName,
    SUM(Sales.Quantity * Sales.UnitPrice) AS total
FROM Sales
JOIN Customer ON Sales.CustomerKey = Customer.CustomerKey
JOIN Product ON Sales.ProductKey = Product.ProductKey
JOIN Employee ON Sales.EmployeeKey = Employee.EmployeeKey

GROUP BY GROUPING SETS (
    (Customer.CompanyName, Product.ProductName, Employee.LastName),
    (Customer.CompanyName, Product.ProductName),
    (Customer.CompanyName, Employee.LastName),
    (Product.ProductName, Employee.LastName),
    (Customer.CompanyName),
    (Product.ProductName),
    (Employee.LastName),
    ()
)

HAVING SUM(Sales.Quantity * Sales.UnitPrice) > 10000
ORDER BY total DESC
""").df()
print('Query in SQL with an extended group-by clause (Sets) to include all combinations of the three columns:')
print(Second_query)

Third_query = con.execute("""
SELECT
    Customer.CompanyName,
    Product.ProductName,
    Employee.LastName,
    SUM(Sales.Quantity * Sales.UnitPrice) AS total
FROM Sales
JOIN Customer
    ON Sales.CustomerKey = Customer.CustomerKey
JOIN Product
    ON Sales.ProductKey = Product.ProductKey
JOIN Employee
    ON Sales.EmployeeKey = Employee.EmployeeKey

GROUP BY ROLLUP (
    Customer.CompanyName,
    Product.ProductName,
    Employee.LastName
)
HAVING SUM(Sales.Quantity * Sales.UnitPrice) > 10000
ORDER BY total DESC
""").df()

print("Query in SQL with an extended GROUP BY clause (ROLLUP):")
print(Third_query.to_string(index=False))




Fourth_query = con.execute("""
SELECT
    Customer.CompanyName,
    City.CityName,
    State.StateName,
    Country.CountryName,
    SUM(Sales.Quantity) AS total

FROM Sales

JOIN Customer
    ON Sales.CustomerKey = Customer.CustomerKey

JOIN City
    ON Customer.CityKey = City.CityKey

JOIN State
    ON City.StateKey = State.StateKey

JOIN Country
    ON State.CountryKey = Country.CountryKey

GROUP BY ROLLUP (
    Customer.CompanyName,
    City.CityName,
    State.StateName,
    Country.CountryName
)

HAVING SUM(Sales.Quantity) > 100

ORDER BY total DESC
""").df()

print("Question (b): Compute the sum of quantity (under the new name total) rolled up along the geographical customer hierarchy formed by Customer.CompanyName, City.CityName, State.StateName, Country.CountryName, and All.")
print("Only include rows where the sum is larger than 100, and order rows by decreasing total.")
print("\nSQL Query using ROLLUP:")
print(Fourth_query.to_string(index=False))
