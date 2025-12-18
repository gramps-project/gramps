# Using `select_from_*` Functions

This guide explains how to use the `select_from_person()`, `select_from_family()`, and other `select_from_*` functions to query the database using Python string expressions.

## Basic Usage

The `select_from_*` functions accept three main parameters:

- **`what`**: What data to extract (defaults to the entire object)
- **`where`**: Filter conditions (optional)
- **`order_by`**: Sorting order (optional)

### Simple Examples

```python
# Get all person handles
handles = list(db.select_from_person(what="person.handle"))

# Get handles of all males
male_handles = list(
    db.select_from_person(
        what="person.handle",
        where="person.gender == Person.MALE"
    )
)

# Get handles sorted by surname
sorted_handles = list(
    db.select_from_person(
        what="person.handle",
        order_by="person.primary_name.surname_list[0].surname"
    )
)
```

## The `what` Parameter

The `what` parameter specifies what data to extract from each matching record.

### Extracting Attributes

You can access nested attributes using dot notation:

```python
# Get surnames
surnames = list(db.select_from_person(what="person.primary_name.surname_list[0].surname"))

# Get birth dates
birth_dates = list(db.select_from_person(what="person.birth_ref.ref"))

# Get primary names
names = list(db.select_from_person(what="person.primary_name.first_name"))
```

### Extracting from Arrays (List Comprehensions)

You can extract values from arrays using list comprehensions:

```python
# Extract all role values from event_ref_list
role_values = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list]"
    )
)

# Extract role values with a condition
primary_roles = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]"
    )
)

# Extract multiple fields
event_data = list(
    db.select_from_person(
        what="[eref.ref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]"
    )
)
```

**Note**: List comprehensions in `what` return one row per matching array element. If a person has 3 matching event_refs, you'll get 3 rows.

### Array Expansion Pattern

For simpler cases, you can use the array expansion pattern:

```python
# Extract role.value from all event_refs
role_values = list(
    db.select_from_person(
        what="item.role.value",
        where="item in person.event_ref_list"
    )
)
```

You can also include person-level fields along with array element fields:

```python
# Get both person.handle and role.value for each event_ref
# Use a list for multiple fields
results = list(
    db.select_from_person(
        what=["person.handle", "item.role.value"],
        where="item in person.event_ref_list"
    )
)
# Returns tuples: (handle, role_value)
```

This is equivalent to the list comprehension but uses a different syntax. When you include `person.handle`, each row will show which person the array element belongs to.

## The `where` Parameter

The `where` parameter filters which records to include.

### Basic Filtering

```python
# Filter by gender
males = list(
    db.select_from_person(
        what="person.handle",
        where="person.gender == Person.FEMALE"
    )
)

# Filter by multiple conditions
married_males = list(
    db.select_from_person(
        what="person.handle",
        where="person.gender == Person.UNKNOWN and len(person.family_list) > 0"
    )
)

# String operations
smiths = list(
    db.select_from_person(
        what="person.handle",
        where="person.primary_name.surname_list[0].surname.startswith('Smith')"
    )
)
```

### Filtering with `any()` and List Comprehensions

Check if any element in an array matches a condition:

```python
# Find persons with any event_ref
persons_with_events = list(
    db.select_from_person(
        what="person.handle",
        where="any([eref for eref in person.event_ref_list])"
    )
)

# Find persons with any PRIMARY event_ref
persons_with_primary = list(
    db.select_from_person(
        what="person.handle",
        where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])"
    )
)

# Negation: find persons with no event_refs
persons_without_events = list(
    db.select_from_person(
        what="person.handle",
        where="not any([eref for eref in person.event_ref_list])"
    )
)
```

### Combining Filters

You can combine `any()` filters with other conditions:

```python
# Find male persons with any event_ref
male_with_events = list(
    db.select_from_person(
        what="person.handle",
        where="person.gender == Person.MALE and any([eref for eref in person.event_ref_list])"
    )
)
```

### Array Expansion in `where`

You can also use array expansion for filtering:

```python
# Get role values from event_refs where role.value == 1
primary_roles = list(
    db.select_from_person(
        what="item.role.value",
        where="item in person.event_ref_list and item.role.value == 1"
    )
)

# Include person.handle to see which person each event_ref belongs to
results = list(
    db.select_from_person(
        what=["person.handle", "item.role.value"],
        where="item in person.event_ref_list and item.role.value == 1"
    )
)
```

## Combining `what` and `where` with List Comprehensions

You can combine list comprehensions in both `what` and `where` for powerful filtering and extraction:

```python
# Filter persons with any PRIMARY event_ref, then extract role values from PRIMARY event_refs
primary_roles = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
        where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])"
    )
)

# Different conditions: filter persons with any event_ref, extract only PRIMARY roles
mixed = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
        where="any([eref for eref in person.event_ref_list])"
    )
)

# Combine with person-level filtering
female_primary = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
        where="person.gender == Person.FEMALE and any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])"
    )
)
```

## The `order_by` Parameter

Sort results using the `order_by` parameter:

```python
# Sort by surname
sorted_persons = list(
    db.select_from_person(
        what="person.handle",
        order_by="person.primary_name.surname_list[0].surname"
    )
)

# Sort by multiple fields (use a list)
sorted_persons = list(
    db.select_from_person(
        what="person.handle",
        order_by=["person.primary_name.surname_list[0].surname", "person.primary_name.first_name"]
    )
)
```

## Common Patterns

### Getting All Handles

```python
all_handles = list(db.select_from_person(what="person.handle"))
```

### Filtering by Array Length

```python
# Persons with events
with_events = list(
    db.select_from_person(
        what="person.handle",
        where="len(person.event_ref_list) > 0"
    )
)

# Persons without events
without_events = list(
    db.select_from_person(
        what="person.handle",
        where="len(person.event_ref_list) == 0"
    )
)
```

### Extracting from Nested Structures

```python
# Get all citation handles from persons
citation_handles = list(
    db.select_from_person(
        what="[cit.handle for cit in person.citation_list]"
    )
)

# Get note handles
note_handles = list(
    db.select_from_person(
        what="[note.handle for note in person.note_list]"
    )
)
```

### Working with Event References

```python
# Get all event reference handles
event_ref_handles = list(
    db.select_from_person(
        what="[eref.ref for eref in person.event_ref_list]"
    )
)

# Get PRIMARY event reference handles only
primary_event_refs = list(
    db.select_from_person(
        what="[eref.ref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]"
    )
)
```

## Limitations

1. **List Comprehensions in `what`**: When using list comprehensions in `what`, you get one row per matching array element. If a person has 5 matching event_refs, you'll get 5 rows.

2. **Array Expansion vs List Comprehension**: 
   - Array expansion (`item in person.array_path`) works in `where` and expands the result set
   - List comprehensions in `what` extract values from arrays
   - You cannot combine array expansion in `where` with list comprehensions in `what` effectively

3. **Complex Boolean Logic**: You can use `and` and `or` in `where` clauses with full structure preservation. Most combinations are supported:
   
   **All cases work correctly:**
   - Simple combinations: `condition1 and condition2` or `condition1 or condition2`
   - Same operator throughout: `A and B and C` or `A or B or C`
   - Mixed operators: `A and B or C and D`
   - Nested expressions: `(A and B) or (C and D)`
   - Deeply nested structures: `(A and (B or C)) and D`
   - `any()` with any boolean structure: `(A and B) or any([...])` or `(A or any([...])) and B`
   - Array expansion with AND: `(A and B) and (item in person.array)` ✅
   - Array expansion with OR: `(A and B) or (item in person.array)` ⚠️ (see limitation below)
   
   **Limitation with Array Expansion in OR Expressions:**
   
   When array expansion is used in an OR expression, there is a known limitation:
   
   ```python
   # This works, but has a limitation:
   db.select_from_person(
       what="person.handle",
       where="(person.gender == Person.MALE and len(person.family_list) > 0) or (item in person.event_ref_list)"
   )
   ```
   
   **What works:**
   - Returns all persons who have array elements (right side of OR)
   - Returns persons matching the left side AND who have array elements
   - Boolean structure is preserved correctly
   
   **What doesn't work:**
   - Persons matching the left side but with **empty arrays** are not included
   - This is because `json_each()` on an empty array returns no rows
   - Example: A person who is male with families but has no `event_ref_list` items will not appear in results
   
   **Workaround:**
   If you need to include persons with empty arrays, use `any()` instead of array expansion:
   
   ```python
   # This works correctly for all cases:
   db.select_from_person(
       what="person.handle",
       where="(person.gender == Person.MALE and len(person.family_list) > 0) or any([item for item in person.event_ref_list])"
   )
   ```
   
   Note: `any()` returns one row per person (not per array element), while array expansion returns one row per array element.
   

4. **Single Condition in List Comprehensions**: List comprehensions support only one `if` condition. Multiple conditions should be combined with `and`:
   ```python
   # This works:
   what="[item.field for item in person.array if item.field1 == 1 and item.field2 == 2]"
   
   # Multiple if clauses are not supported:
   # what="[item.field for item in person.array if item.field1 == 1 if item.field2 == 2]"  # Not supported
   ```

5. **Nested Arrays**: Nested array access (arrays within arrays) is **not supported**. 
   
   **What works:**
   - Single-level arrays: `person.event_ref_list`, `person.citation_list`
   - Accessing attributes of array elements: `item.role.value` where `item` is from `person.event_ref_list`
   
   **What doesn't work:**
   - Nested arrays: Accessing arrays that are properties of array elements
     - Example: If an event_ref had a `sub_items` array, `item.sub_items` would not work
     - The code does not support `json_each` within `json_each` (nested array iteration)
   - Arrays within nested objects: `person.some_object.array_field` where `some_object` itself contains arrays

6. **Lambda Functions**: You can pass lambda functions instead of strings, but they will be converted to strings internally. Using strings directly is recommended for clarity.

## Hints and Best Practices

1. **Use Constants**: All of the Gramps objects and types are available in the environment

   ```python
    # Good:
   where="eref.role.value == EventRoleType.PRIMARY"
   where="person.gender == Person.MALE"
   
   # Avoid:
   where="eref.role.value == 1"  # What does 1 mean?
   ```

2. **Empty Arrays**: To check for empty arrays, use `len()` or `not any()`:
   ```python
   # Both work:
   where="len(person.event_ref_list) == 0"
   where="not any([eref for eref in person.event_ref_list])"
   ```

3. **Performance**: 
   - List comprehensions in `what` can return many rows if arrays are large
   - `any()` in `where` is efficient for filtering
   - Consider filtering in `where` before extracting in `what` to reduce result set size

4. **Testing for Existence**: Use `any()` to test if any element exists:
   ```python
   # Check if person has any event_refs
   where="any([eref for eref in person.event_ref_list])"
   ```

5. **Extracting Multiple Fields**: 
   - For array expansion, you can include both person-level and array element fields:
     ```python
     # Get person.handle along with array element fields
     results = list(
         db.select_from_person(
             what=["person.handle", "item.role.value", "item.ref"],
             where="item in person.event_ref_list"
         )
     )
     ```
   - For list comprehensions, you extract one expression at a time, but you can combine with person fields if needed:
     ```python
     # Extract one field at a time from list comprehensions
     refs = list(db.select_from_person(what="[eref.ref for eref in person.event_ref_list]"))
     roles = list(db.select_from_person(what="[eref.role.value for eref in person.event_ref_list]"))
     ```

6. **Order of Operations**: 
   - `where` filters which records (persons) to include
   - `what` determines what data to extract from those records
   - When both use list comprehensions, `where` filters persons first, then `what` extracts from matching array elements

7. **Debugging**: If a query doesn't work as expected:
   - Check that attribute paths are correct (use dot notation)
   - Verify array names (e.g., `event_ref_list`, not `event_refs`)
   - Ensure constants are imported and used correctly
   - Test with simpler queries first, then add complexity

## Examples by Use Case

### Find All Persons with Birth Events

```python
birth_handles = list(
    db.select_from_person(
        what="person.handle",
        where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])"
    )
)
```

### Extract All Event Reference Handles

```python
# Just the handles
all_event_refs = list(
    db.select_from_person(
        what="[eref.ref for eref in person.event_ref_list]"
    )
)

# With person.handle to see which person each belongs to (using array expansion)
all_event_refs_with_person = list(
    db.select_from_person(
        what=["person.handle", "item.ref"],
        where="item in person.event_ref_list"
    )
)
```

### Find People with Families

```python
have_family =
    db.select_from_person(
        what="person.handle",
        where="len(person.family_list) > 0"
    )
)
```

### Get Surnames of All Males, Sorted

```python
male_surnames = list(
    db.select_from_person(
        what="person.primary_name.surname_list[0].surname",
        where="person.gender == Person.MALE",
        order_by="person.primary_name.surname_list[0].surname"
    )
)
```

### Extract Role Values from Event References with Conditions

```python
# Get PRIMARY role values from persons who have PRIMARY events
primary_roles = list(
    db.select_from_person(
        what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
        where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])"
    )
)
```