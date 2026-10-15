# Extra GROUP BY explanation slides inserted into Part 2.
GB_BEFORE = [
dict(kind="code", title="What GROUP BY actually does", code="""-- Employee table (sorted by DeptID so you can see the piles)
-- EmpName  DeptID  Salary
-- Ravi       1     45000    <- pile for Dept 1  (1 person)
-- ------------------------
-- Meena      2     75000    \\
-- Suresh     2     52000     > pile for Dept 2  (3 people)
-- Kavya      2     61000    /
-- ------------------------
-- Anil       3     35000    <- pile for Dept 3  (1 person)

SELECT DeptID, COUNT(*), MAX(Salary), SUM(Salary)
FROM Employee
GROUP BY DeptID;
-- DeptID | COUNT(*) | MAX(Salary) | SUM(Salary)
--    1   |    1     |   45000     |   45000
--    2   |    3     |   75000     |  188000
--    3   |    1     |   35000     |   35000""",
 steps=["Rows with the SAME value go into one pile", "COUNT / SUM / MAX / AVG run on EACH pile", "Output = ONE row per pile"],
 say="Let's understand what group by really does. Look at the employee table. Group by dept I D takes all the rows and puts rows with the same dept I D into one pile. Ravi is alone in department one. Meena, Suresh and Kavya go into the pile for department two. Anil is alone in department three. So we get three piles. Then the aggregate functions run separately on each pile. Count star counts the people in each pile: one, three, one. Max salary finds the highest in each pile. Sum adds up each pile, so department two is seventy five thousand plus fifty two thousand plus sixty one thousand, which is one lakh eighty eight thousand. And the output has exactly one row per pile. Five employees in, three rows out, because there are three departments. That's all group by is: make piles, then calculate per pile."),
dict(kind="code", title="Without GROUP BY vs with GROUP BY", code="""-- WITHOUT GROUP BY: the whole table is ONE pile
SELECT COUNT(*), MAX(Salary) FROM Employee;
-- COUNT(*) | MAX(Salary)
--    5     |   75000          <- one answer for everyone

-- WITH GROUP BY: one pile per department
SELECT DeptID, COUNT(*), MAX(Salary) FROM Employee GROUP BY DeptID;
-- DeptID | COUNT(*) | MAX(Salary)
--    1   |    1     |   45000
--    2   |    3     |   75000
--    3   |    1     |   35000   <- one answer per department""",
 steps=["No GROUP BY → 1 answer for the whole table", "GROUP BY col → 1 answer for each value of col", "\"highest salary\" vs \"highest salary in EACH dept\""],
 say="Compare the two. Without group by, the whole table is treated as one big pile, so count star gives five and max salary gives seventy five thousand, one answer for everyone. With group by dept I D, you get one answer per department. So, if the question says highest salary, you don't need group by. If it says highest salary in each department, you need group by dept I D. The word each is your signal."),
dict(kind="code", title="The GROUP BY rule: what can go in SELECT?", code="""-- CORRECT: grouped column + aggregates
SELECT DeptID, COUNT(*), AVG(Salary)
FROM Employee
GROUP BY DeptID;

-- WRONG: EmpName is not grouped
SELECT DeptID, EmpName, COUNT(*)
FROM Employee
GROUP BY DeptID;
-- Dept 2 has Meena, Suresh AND Kavya... which ONE name
-- should go in Dept 2's single row?
-- → ERROR 1055: EmpName isn't in GROUP BY

-- Group by MORE than one column = smaller piles
SELECT DeptID, YEAR(HireDate), COUNT(*)
FROM Employee
GROUP BY DeptID, YEAR(HireDate);""",
 steps=["SELECT only: the GROUP BY column(s) + aggregates", "Every other column → error (ONLY_FULL_GROUP_BY)", "Same column in SELECT and GROUP BY"],
 say="One rule you must follow. When you use group by, the select list can only contain the column you grouped by, plus aggregate functions like count, sum and average. Why? Department two's pile has three people, Meena, Suresh and Kavya, but the output has only one row for department two. So which name would MySQL print? It can't decide, so MySQL eight gives an error. The easy way to remember: whatever column is in group by, put the same column in select, and everything else must be inside count, sum, average, max or min. You can also group by two columns, which simply makes smaller piles."),
]

GB_AFTER_HAVING = [
dict(kind="code", title="WHERE vs HAVING: the order MySQL runs it", code="""SELECT DeptID, COUNT(*) AS EmpCount
FROM Employee            -- 1. take the table
WHERE Salary > 40000     -- 2. remove ROWS: Anil (35000) goes
GROUP BY DeptID          -- 3. make piles: D1 = Ravi
                         --    D2 = Meena, Suresh, Kavya
HAVING COUNT(*) > 1      -- 4. remove PILES: D1 has 1 → goes
ORDER BY DeptID;         -- 5. sort

-- Result:   DeptID | EmpCount
--              2   |    3

-- WHERE COUNT(*) > 1  → ERROR (no piles yet at step 2)""",
 steps=["WHERE filters ROWS (before piles)", "HAVING filters PILES (after GROUP BY)", "COUNT/SUM/AVG in a condition → HAVING"],
 say="Here's the order MySQL actually runs a grouped query, and it makes where versus having very clear. Step one, from: pick the employee table. Step two, where salary greater than forty thousand removes individual rows, so Anil with thirty five thousand is gone before any grouping. Step three, group by makes the piles: department one has only Ravi, department two has Meena, Suresh and Kavya. Step four, having count star greater than one removes whole piles, so department one is removed because it has only one person. Step five, select and order by. The result is department two with three employees. And notice: you cannot write where count star greater than one, because at the where step the piles don't exist yet. That's why conditions with count, sum or average always go in having."),
]
