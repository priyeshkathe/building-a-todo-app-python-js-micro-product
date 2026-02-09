# Part 5: Todo CRUD Operations

In this chapter, we build the core functionality of our Todo application.

Up until now, users could register and log in, but they couldn't actually **do** anything with their account.
In this part, we add the ability to create, read, update, and delete todos — the fundamental operations of any data-driven application.

However, this chapter also introduces a **security vulnerability** that we will fix in Part 6.

---

## What You Will Learn

By the end of this chapter, you will understand:

- What CRUD operations are (Create, Read, Update, Delete)
- How to build RESTful API endpoints in Flask
- How to connect frontend JavaScript to backend APIs
- How HTTP methods (GET, POST, PUT, DELETE) map to operations
- Why sending `user_id` from the frontend is a security risk

---

## Why This Chapter Matters

CRUD is the foundation of almost every web application:

| Application | Create | Read | Update | Delete |
|-------------|--------|------|--------|--------|
| Todo App | Add task | View tasks | Mark complete | Remove task |
| Social Media | Post content | View feed | Edit post | Delete post |
| E-commerce | Add to cart | View orders | Update quantity | Remove item |

Understanding CRUD patterns gives you the building blocks for any application you want to create.

---

## Project Structure

```
part-5-todo-crud/
├── app.py              # Flask app with CRUD endpoints
├── models.py           # Database models (User, Todo)
├── auth.py             # Authentication helpers
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   ├── register.html   # Registration form
│   ├── login.html      # Login form
│   └── dashboard.html  # Todo list with CRUD operations
```

---

## How to Run

```bash
cd part-5-todo-crud
pip install -r requirements.txt
python app.py
```

Open in browser: http://127.0.0.1:5000

---

## Key Concepts

### 1. CRUD = Create, Read, Update, Delete

CRUD operations map directly to HTTP methods:

| Operation | HTTP Method | Endpoint | Description |
|-----------|-------------|----------|-------------|
| **C**reate | POST | `/api/todos` | Add a new todo |
| **R**ead | GET | `/api/todos` | Get all todos |
| **U**pdate | PUT | `/api/todos/:id` | Modify a todo |
| **D**elete | DELETE | `/api/todos/:id` | Remove a todo |

---

### 2. How user_id is Sent (The Insecure Way)

In this part, the frontend **explicitly sends the user_id** with every request.

**Frontend sends user_id in the request:**

```javascript
// CREATE - user_id in request body
await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        task_content: taskContent,
        user_id: user.id  // Frontend sends user_id
    })
});

// READ - user_id in query parameter
const res = await fetch(`/api/todos?user_id=${user.id}`);
```

**Backend reads user_id from the request:**

```python
# GET - reads user_id from query parameter
@app.route('/api/todos', methods=['GET'])
def get_todos():
    user_id = request.args.get('user_id')  # From URL: ?user_id=1
    todos = Todo.query.filter_by(user_id=user_id).all()
    return jsonify({'todos': [...]})

# POST - reads user_id from request body
@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    user_id = data.get('user_id')  # From request body

    todo = Todo(
        task_content=data['task_content'],
        user_id=user_id
    )
    db.session.add(todo)
    db.session.commit()
```

---

### 3. CRUD API Endpoints

#### CREATE (POST /api/todos)

```python
@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    task_content = data.get('task_content')
    user_id = data.get('user_id')

    if not task_content or not user_id:
        return jsonify({'error': 'task_content and user_id required'}), 400

    todo = Todo(
        task_content=task_content,
        is_completed=False,
        user_id=user_id
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify({
        'message': 'Todo created!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    }), 201
```

#### READ (GET /api/todos)

```python
@app.route('/api/todos', methods=['GET'])
def get_todos():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    todos = Todo.query.filter_by(user_id=user_id).all()

    return jsonify({
        'todos': [{
            'id': t.id,
            'task_content': t.task_content,
            'is_completed': t.is_completed
        } for t in todos]
    })
```

#### UPDATE (PUT /api/todos/:id)

```python
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.get_json()

    if 'task_content' in data:
        todo.task_content = data['task_content']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()

    return jsonify({
        'message': 'Todo updated!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    })
```

#### DELETE (DELETE /api/todos/:id)

```python
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted!'})
```

---

### 4. Frontend JavaScript for CRUD

The dashboard uses JavaScript to call these APIs:

```javascript
// Load todos on page load
async function loadTodos() {
    const res = await fetch(`/api/todos?user_id=${user.id}`);
    const data = await res.json();

    // Render todos to the page
    todoList.innerHTML = data.todos.map(todo => `
        <li>
            <input type="checkbox"
                   ${todo.is_completed ? 'checked' : ''}
                   onchange="toggleTodo(${todo.id}, this.checked)">
            ${todo.task_content}
            <button onclick="deleteTodo(${todo.id})">Delete</button>
        </li>
    `).join('');
}

// Toggle completion status
async function toggleTodo(id, isCompleted) {
    await fetch(`/api/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_completed: isCompleted })
    });
    loadTodos();  // Refresh the list
}

// Delete a todo
async function deleteTodo(id) {
    if (!confirm('Delete this task?')) return;

    await fetch(`/api/todos/${id}`, { method: 'DELETE' });
    loadTodos();  // Refresh the list
}
```

---

## Security Warning: Why This Approach is Dangerous

This chapter **intentionally** introduces a security vulnerability to help you understand the problem.

### The Problem

The backend **trusts** whatever `user_id` the frontend sends:

```javascript
// Frontend code - user could modify this!
body: JSON.stringify({
    task_content: 'Buy milk',
    user_id: 1  // What if user changes this to 2?
})
```

### What Could Go Wrong

1. **A user opens browser DevTools (F12)**
2. **They modify the JavaScript or intercept the request**
3. **They change `user_id` to another user's ID**
4. **They can now see, create, or delete other users' todos!**

```
User A (id=1) ─── modifies request ─── user_id=2 ─── Sees User B's todos!
```

### Visual: The Attack

```
Normal Flow:
User A ── user_id=1 ──> Backend ──> Returns User A's todos ✓

Attack Flow:
User A ── user_id=2 ──> Backend ──> Returns User B's todos! ✗
```

### Why This Happens

- The JWT token is stored but **not validated** on each request
- The backend doesn't verify if the `user_id` matches the logged-in user
- Anyone can send any `user_id` they want

### The Lesson

**Never trust data from the frontend.**

The user ID should come from the **validated JWT token**, not the request body or query parameters.

---

## What Changes in Part 6

In Part 6, we fix this vulnerability by:

1. **Validating the JWT token on every request**
2. **Extracting user_id from the token** (not the request)
3. **Adding ownership verification** before update/delete

```
Part 5 (Insecure):
Frontend ── user_id in body ──> Backend trusts it

Part 6 (Secure):
Frontend ── JWT in header ──> Backend validates token ──> Extracts user_id
```

---

## HTTP Response Codes Used

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 400 | Bad Request | Missing required fields |
| 404 | Not Found | Todo doesn't exist |

---

## Try It Yourself

### Activity 1: Test the Vulnerability
1. Log in as User A
2. Open browser DevTools (F12) → Network tab
3. Add a todo and observe the request
4. Notice `user_id` is sent in the request body
5. Think: What would happen if you changed it?

### Activity 2: Add a Feature
Try adding an "Edit" button to change the task content:
- Add an edit button to each todo
- When clicked, show an input field
- Call PUT `/api/todos/:id` with new content

---

## Self-Study Questions

1. Why do we use PUT for updates instead of POST?
2. What's the difference between `request.args` and `request.get_json()`?
3. Why does the DELETE endpoint return 404 if the todo doesn't exist?
4. How could a malicious user exploit the current implementation?

---

## Next Part

In **Part 6: Protected Routes**, we will:
- Validate JWT tokens on every API request
- Extract user_id from the token (not the request)
- Add ownership verification
- Properly secure our API endpoints
