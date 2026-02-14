# Part 8: Homework - Add Priority Feature

Congratulations on making it to the final part!

This is your hands-on assignment to practice everything you've learned. You will add a **priority feature** (Low, Medium, High) to todos — working across the entire stack from database to frontend.

The code has been prepared with commented sections for you to uncomment and complete. Follow the 7 steps below, and your app will have a fully working priority system!

---

## What You Will Practice

By completing this homework, you will reinforce:

- Adding new columns to database models
- Extending API endpoints to handle new data
- Updating frontend forms to collect new input
- Displaying dynamic data with styled badges
- Full-stack development workflow

---

## Why This Homework Matters

Real-world development often involves:

1. **Receiving a feature request** — "We need priorities on todos"
2. **Planning the changes** — What needs to change? (DB, API, Frontend)
3. **Implementing incrementally** — One layer at a time
4. **Testing the feature** — Does it work end-to-end?

This homework simulates that entire workflow.

---

## Project Structure

```
part-8-homework/
├── app.py              # Flask app (has commented priority code)
├── models.py           # Database models (has commented priority column)
├── auth.py             # Authentication helpers
├── requirements.txt    # Python dependencies
├── templates/
│   ├── dashboard.html  # Todo list (has commented dropdown & badge)
│   └── ...
└── solution/           # Reference solution
    ├── app.py
    ├── models.py
    └── dashboard.html
```

---

## The Feature You're Building

### Before (Current State)
- Todos have: task content, completion status
- No way to indicate urgency

### After (Your Implementation)
- Todos have: task content, completion status, **priority**
- Priority dropdown when creating todos
- Colored badges showing priority level

```
┌─────────────────────────────────────────────────────────┐
│  [HIGH]    Buy groceries                        [Delete]│
│  [MEDIUM]  Review pull request                  [Delete]│
│  [LOW]     Organize desk                        [Delete]│
└─────────────────────────────────────────────────────────┘
```

Priority colors:
- **HIGH** = Red badge (urgent!)
- **MEDIUM** = Yellow badge (normal)
- **LOW** = Green badge (can wait)

---

## 7 Steps to Complete

Each step is marked in the code with comments like `# STEP 1`, `// STEP 4`, etc.

| Step | File | What to Do |
|------|------|------------|
| 1 | models.py | Uncomment priority column |
| 2 | models.py | Uncomment priority in to_dict() |
| 3 | app.py | Uncomment priority parameter |
| 4 | dashboard.html | Uncomment priority dropdown |
| 5 | dashboard.html | Add priority to API call |
| 6 | dashboard.html | Uncomment getPriorityBadge() |
| 7 | dashboard.html | Add badge to todo display |

---

## Detailed Instructions

### Step 1: Add Priority Column (models.py, line ~38)

Find this commented line and remove the `#`:

```python
# STEP 1: Uncomment this line
# priority = db.Column(db.String(10), default='medium')
```

**After:**
```python
# STEP 1: Uncomment this line
priority = db.Column(db.String(10), default='medium')
```

**What this does:**
- Adds a `priority` column to the Todo table
- Stores values: 'low', 'medium', or 'high'
- Defaults to 'medium' if not specified

---

### Step 2: Include Priority in API Response (models.py, line ~51)

Find this in the `to_dict()` method and uncomment:

```python
# STEP 2: Uncomment this line
# 'priority': self.priority
```

**After:**
```python
# STEP 2: Uncomment this line
'priority': self.priority
```

**What this does:**
- Includes priority when todo is converted to JSON
- Frontend will receive priority in API responses

---

### Step 3: Accept Priority in Create Endpoint (app.py, line ~106)

Find this in the `create_todo()` function:

```python
todo = Todo(
    task_content=data['task_content'],
    user_id=current_user.id,
    # STEP 3: Uncomment the line below
    # priority=data.get('priority', 'medium')
)
```

**After:**
```python
todo = Todo(
    task_content=data['task_content'],
    user_id=current_user.id,
    # STEP 3: Uncomment the line below
    priority=data.get('priority', 'medium')
)
```

**What this does:**
- Reads priority from the request body
- Uses 'medium' as default if not provided
- `data.get('priority', 'medium')` is safe — won't crash if missing

---

### Step 4: Add Priority Dropdown (dashboard.html, lines ~40-46)

Find the commented HTML and remove `<!--` and `-->`:

```html
<!-- STEP 4: Uncomment this dropdown
<select class="form-select" id="priority-input" style="width: 130px;">
    <option value="low">Low</option>
    <option value="medium" selected>Medium</option>
    <option value="high">High</option>
</select>
-->
```

**After:**
```html
<!-- STEP 4: Uncomment this dropdown -->
<select class="form-select" id="priority-input" style="width: 130px;">
    <option value="low">Low</option>
    <option value="medium" selected>Medium</option>
    <option value="high">High</option>
</select>
```

**What this does:**
- Adds a dropdown selector next to the task input
- Default selection is "Medium"
- Values match what the backend expects

---

### Step 5: Send Priority to API (dashboard.html, line ~115)

Find the form submit handler and update the API call:

**Before:**
```javascript
await api('/api/todos', 'POST', { task_content: taskContent });
```

**After:**
```javascript
await api('/api/todos', 'POST', {
    task_content: taskContent,
    priority: document.getElementById('priority-input').value
});
```

**What this does:**
- Reads the selected priority from the dropdown
- Sends it along with the task content
- Backend will store it in the database

---

### Step 6: Uncomment Badge Function (dashboard.html, lines ~123-129)

Find and uncomment the `getPriorityBadge` function:

```javascript
/* STEP 6: Uncomment this function
function getPriorityBadge(priority) {
    const colors = { high: 'danger', medium: 'warning', low: 'success' };
    const textClass = priority === 'medium' ? 'text-dark' : '';
    return `<span class="badge bg-${colors[priority]} ${textClass} priority-badge">${priority.toUpperCase()}</span>`;
}
*/
```

**After:**
```javascript
// STEP 6: Uncomment this function
function getPriorityBadge(priority) {
    const colors = { high: 'danger', medium: 'warning', low: 'success' };
    const textClass = priority === 'medium' ? 'text-dark' : '';
    return `<span class="badge bg-${colors[priority]} ${textClass} priority-badge">${priority.toUpperCase()}</span>`;
}
```

**What this does:**
- Creates an HTML badge based on priority
- Maps priorities to Bootstrap colors:
  - `high` → `bg-danger` (red)
  - `medium` → `bg-warning` (yellow) + `text-dark` for readability
  - `low` → `bg-success` (green)
- Returns HTML like `<span class="badge bg-danger">HIGH</span>`

---

### Step 7: Display Badge in Todo List (dashboard.html, line ~150)

Find where todos are rendered and add the badge:

**Before:**
```javascript
todoList.innerHTML = data.todos.map(todo => `
    <div class="todo-item ${todo.is_completed ? 'completed' : ''}">
        <input type="checkbox" ...>
        <span class="todo-text">${escapeHtml(todo.task_content)}</span>
        <button ...>Delete</button>
    </div>
`).join('');
```

**After:**
```javascript
todoList.innerHTML = data.todos.map(todo => `
    <div class="todo-item ${todo.is_completed ? 'completed' : ''}">
        <input type="checkbox" ...>
        ${getPriorityBadge(todo.priority)}
        <span class="todo-text">${escapeHtml(todo.task_content)}</span>
        <button ...>Delete</button>
    </div>
`).join('');
```

**What this does:**
- Calls `getPriorityBadge()` for each todo
- Inserts the colored badge HTML
- Badge appears between checkbox and task text

---

## How to Test Your Implementation

### 1. Delete the Old Database

**Important:** The database schema changed (new column), so you must delete the old database:

```bash
# Delete the database file
rm instance/todo.db      # Mac/Linux
del instance\todo.db     # Windows
```

Or manually delete the `instance/todo.db` file.

### 2. Run the Application

```bash
cd part-8-homework
pip install -r requirements.txt
python app.py
```

### 3. Test the Feature

1. Open http://127.0.0.1:5000
2. Register a new account
3. Go to the dashboard
4. **Check:** Do you see a priority dropdown next to the input?
5. Add a todo with "High" priority
6. Add a todo with "Low" priority
7. Add a todo with "Medium" priority
8. **Check:** Do you see colored badges?
   - HIGH = Red
   - MEDIUM = Yellow
   - LOW = Green

### 4. Verify Data Persistence

1. Refresh the page
2. Todos should still show their priorities
3. This confirms the database is storing priorities correctly

---

## Troubleshooting

### "Badges don't appear"
- Did you complete Step 6 (uncomment `getPriorityBadge`)?
- Did you complete Step 7 (add badge to template)?
- Check browser console (F12) for JavaScript errors

### "Priority dropdown doesn't appear"
- Did you complete Step 4 (uncomment the `<select>`)?
- Check for HTML syntax errors

### "Todos don't save priority"
- Did you delete the old database?
- Did you complete Steps 1-3?
- Check if `priority` appears in network requests (F12 → Network)

### "Database error on startup"
- Delete `instance/todo.db` and restart
- The old database doesn't have the priority column

### "getPriorityBadge is not defined"
- Step 6 wasn't completed correctly
- Make sure you removed both `/*` and `*/`

---

## Understanding the Code

### Why use data.get('priority', 'medium')?

```python
priority = data.get('priority', 'medium')
```

This is a safe way to get optional data:
- If `priority` exists in `data`, use it
- If `priority` is missing, use `'medium'` as default
- Prevents crashes if frontend doesn't send priority

### Why the text-dark class for medium?

```javascript
const textClass = priority === 'medium' ? 'text-dark' : '';
```

- Yellow background (`bg-warning`) needs dark text for readability
- Red and green backgrounds work fine with white text
- Bootstrap's default badge text is white

### Why delete the database?

SQLite doesn't easily support adding columns to existing tables. The simplest approach for development is:
1. Delete the database
2. Restart the app (creates new database with new schema)
3. Re-register users

In production, you'd use **database migrations** (like Flask-Migrate).

---

## Full-Stack Data Flow

Here's how priority flows through the entire application:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CREATING A TODO                          │
└─────────────────────────────────────────────────────────────────┘

1. User selects "High" from dropdown
   └── <select id="priority-input">
            <option value="high" selected>High</option>
       </select>

2. JavaScript reads the value
   └── priority: document.getElementById('priority-input').value
       // Returns: "high"

3. Frontend sends POST request
   └── POST /api/todos
       Body: { "task_content": "Buy milk", "priority": "high" }

4. Backend receives and parses
   └── data = request.get_json()
       priority = data.get('priority', 'medium')  # Gets "high"

5. Database stores the todo
   └── INSERT INTO todos (task_content, priority, ...)
       VALUES ('Buy milk', 'high', ...)

┌─────────────────────────────────────────────────────────────────┐
│                        DISPLAYING TODOS                          │
└─────────────────────────────────────────────────────────────────┘

1. Frontend requests todos
   └── GET /api/todos

2. Backend queries database
   └── SELECT * FROM todos WHERE user_id = ?

3. Backend returns JSON (via to_dict)
   └── { "todos": [{ "task_content": "Buy milk", "priority": "high", ... }] }

4. JavaScript creates badge HTML
   └── getPriorityBadge("high")
       // Returns: '<span class="badge bg-danger">HIGH</span>'

5. Browser renders the badge
   └── User sees: [HIGH] Buy milk
```

---

## Check Your Answer

After completing all 7 steps, compare your code with the solution:

```
part-8-homework/solution/
├── models.py       # Complete model with priority
├── app.py          # Complete app with priority handling
└── dashboard.html  # Complete frontend with dropdown and badges
```

Your code should match the solution (except for minor formatting differences).

---

## Bonus Challenges

If you finish early, try these extensions:

### Challenge 1: Sort by Priority
Modify the backend to return todos sorted by priority (high first):
```python
todos = Todo.query.filter_by(user_id=current_user.id)\
    .order_by(Todo.priority.desc()).all()
```

### Challenge 2: Filter by Priority
Add buttons to show only high/medium/low todos:
```javascript
async function loadTodos(priorityFilter = null) {
    let url = '/api/todos';
    if (priorityFilter) url += `?priority=${priorityFilter}`;
    // ...
}
```

### Challenge 3: Edit Priority
Add the ability to change a todo's priority after creation:
- Add an "Edit" button
- Show a dropdown to change priority
- Call PUT `/api/todos/:id` with new priority

### Challenge 4: Priority Statistics
Show a count of todos by priority in the dashboard:
```
High: 3 | Medium: 5 | Low: 2
```

---

## What You've Learned

By completing this homework, you've practiced:

| Skill | How You Used It |
|-------|-----------------|
| Database design | Added a column with default value |
| API development | Extended endpoint to accept new data |
| Data serialization | Added field to to_dict() |
| Form handling | Created dropdown, read its value |
| Dynamic HTML | Generated badges with JavaScript |
| CSS styling | Used Bootstrap badge classes |
| Testing | Verified full-stack data flow |
| Debugging | Used browser DevTools |

---

## Congratulations!

You've completed the entire Todo App tutorial series!

### What You've Built
A full-featured todo application with:
- User registration and login
- Secure password hashing
- JWT authentication
- Protected API routes
- User ownership verification
- Admin panel with user management
- Priority feature for todos

### Skills You've Gained
- Flask backend development
- SQLAlchemy database operations
- RESTful API design
- JavaScript frontend development
- Authentication & authorization
- Full-stack debugging

### What's Next?
- Deploy your app (Heroku, Railway, Render)
- Add more features (due dates, categories, sharing)
- Learn a frontend framework (React, Vue)
- Explore Flask extensions (Flask-Login, Flask-JWT-Extended)
- Build your own project!

---

Happy Coding!
