"""Static educational content: question bank, study resources, offline knowledge base."""

TOPICS = ["Python", "Data Structures", "DBMS", "Machine Learning"]

QUESTION_BANK = {
    "Python": [
        {"q": "Which keyword defines a function in Python?", "options": ["func", "def", "function", "lambda only"], "answer": 1,
         "explain": "Functions are defined with the `def` keyword."},
        {"q": "What is the output of len([1, 2, [3, 4]])?", "options": ["2", "3", "4", "Error"], "answer": 1,
         "explain": "The list has three elements; the nested list counts as one."},
        {"q": "Which data type is immutable?", "options": ["list", "dict", "set", "tuple"], "answer": 3,
         "explain": "Tuples cannot be modified after creation."},
        {"q": "What does `//` do?", "options": ["Float division", "Floor division", "Modulus", "Power"], "answer": 1,
         "explain": "`//` divides and rounds down to the nearest integer."},
        {"q": "Which statement handles exceptions?", "options": ["try/except", "catch/throw", "if/else", "do/while"], "answer": 0,
         "explain": "Python uses try/except blocks."},
    ],
    "Data Structures": [
        {"q": "Which structure follows LIFO?", "options": ["Queue", "Stack", "Heap", "Graph"], "answer": 1,
         "explain": "A stack removes the most recently added item first."},
        {"q": "Average time complexity of binary search?", "options": ["O(n)", "O(n log n)", "O(log n)", "O(1)"], "answer": 2,
         "explain": "Each step halves the search space."},
        {"q": "Which traversal of a BST gives sorted output?", "options": ["Preorder", "Inorder", "Postorder", "Level order"], "answer": 1,
         "explain": "Inorder visits left, root, right, giving ascending order."},
        {"q": "A hash table's ideal lookup time is:", "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"], "answer": 0,
         "explain": "With a good hash function and few collisions, lookups are constant time."},
        {"q": "Which structure is best for BFS?", "options": ["Stack", "Queue", "Tree", "Array only"], "answer": 1,
         "explain": "BFS visits nodes level by level using a queue."},
    ],
    "DBMS": [
        {"q": "Which SQL command removes all rows but keeps the table?", "options": ["DROP", "DELETE FROM t WHERE 1=0", "TRUNCATE", "REMOVE"], "answer": 2,
         "explain": "TRUNCATE empties the table; DROP removes the table itself."},
        {"q": "A primary key must be:", "options": ["Unique and not null", "Unique only", "Numeric", "Repeated"], "answer": 0,
         "explain": "Primary keys uniquely identify rows and cannot be NULL."},
        {"q": "Which normal form removes partial dependency?", "options": ["1NF", "2NF", "3NF", "BCNF"], "answer": 1,
         "explain": "2NF removes partial dependencies on part of a composite key."},
        {"q": "ACID's 'I' stands for:", "options": ["Integrity", "Isolation", "Indexing", "Inheritance"], "answer": 1,
         "explain": "Isolation: concurrent transactions do not interfere."},
        {"q": "Which JOIN returns only matching rows from both tables?", "options": ["LEFT", "RIGHT", "INNER", "FULL"], "answer": 2,
         "explain": "INNER JOIN keeps rows with matches in both tables."},
    ],
    "Machine Learning": [
        {"q": "Which is a supervised learning task?", "options": ["Clustering", "Classification", "Dimensionality reduction", "Association rules"], "answer": 1,
         "explain": "Classification learns from labelled examples."},
        {"q": "Overfitting means the model:", "options": ["Is too simple", "Performs well on training data but poorly on new data", "Has no parameters", "Trains too fast"], "answer": 1,
         "explain": "It memorises training data instead of generalising."},
        {"q": "Which metric suits imbalanced classification better than accuracy?", "options": ["F1-score", "Mean", "Variance", "Epoch"], "answer": 0,
         "explain": "F1 balances precision and recall."},
        {"q": "Gradient descent is used to:", "options": ["Clean data", "Minimise a loss function", "Split datasets", "Plot graphs"], "answer": 1,
         "explain": "It iteratively updates parameters to reduce the loss."},
        {"q": "k-means is a(n):", "options": ["Supervised algorithm", "Unsupervised clustering algorithm", "Reinforcement algorithm", "Regression algorithm"], "answer": 1,
         "explain": "k-means groups unlabelled data into k clusters."},
    ],
}

RESOURCES = {
    "Python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "why": "Authoritative introduction to the language."},
        {"title": "Python Standard Library Reference", "url": "https://docs.python.org/3/library/", "why": "Look up built-in types and modules."},
    ],
    "Data Structures": [
        {"title": "VisuAlgo", "url": "https://visualgo.net/", "why": "Animated visualisations of data structures and algorithms."},
        {"title": "GeeksforGeeks DSA", "url": "https://www.geeksforgeeks.org/data-structures/", "why": "Worked examples and practice problems."},
    ],
    "DBMS": [
        {"title": "SQLite Tutorial", "url": "https://www.sqlitetutorial.net/", "why": "Practise SQL queries with a lightweight database."},
        {"title": "W3Schools SQL", "url": "https://www.w3schools.com/sql/", "why": "Quick reference with try-it examples."},
    ],
    "Machine Learning": [
        {"title": "scikit-learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "why": "Official documentation for classic ML algorithms."},
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "why": "Beginner-friendly structured course."},
    ],
}

# Offline fallback knowledge base used when no AI API key is configured.
KNOWLEDGE_BASE = {
    "stack": "A stack is a LIFO (last-in, first-out) structure. Operations: push, pop, peek. Used in function calls, undo features and expression evaluation.",
    "queue": "A queue is FIFO (first-in, first-out). Operations: enqueue and dequeue. Used in scheduling and breadth-first search.",
    "binary search": "Binary search finds an item in a sorted array by repeatedly halving the search range. Time complexity is O(log n).",
    "normalization": "Normalization organises tables to reduce redundancy: 1NF (atomic values), 2NF (no partial dependency), 3NF (no transitive dependency).",
    "primary key": "A primary key uniquely identifies each row in a table and cannot be NULL.",
    "join": "A SQL JOIN combines rows from two tables. INNER keeps matches only; LEFT keeps all left rows; RIGHT keeps all right rows; FULL keeps all.",
    "overfitting": "Overfitting happens when a model memorises training data and fails on new data. Fixes: more data, regularisation, simpler models, cross-validation.",
    "gradient descent": "Gradient descent minimises a loss function by repeatedly moving parameters opposite to the gradient, scaled by a learning rate.",
    "supervised": "Supervised learning trains on labelled data (classification, regression). Unsupervised learning finds structure in unlabelled data (clustering).",
    "list": "A Python list is an ordered, mutable sequence. Tuples are ordered but immutable. Dicts map keys to values; sets hold unique items.",
    "function": "In Python, functions are defined with `def name(params):` and return values with `return`.",
    "exception": "Python handles errors with try/except/finally blocks so a program can recover instead of crashing.",
}
