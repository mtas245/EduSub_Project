# 🎒 EduSub – Teacher Substitute Management System

> 🚧 Replace the screenshot with one that shows your main screen.

![UI Showcase](docs/ui-images/ui_showcase.png)

EduSub is a browser-based application developed for the course Advanced Programming (BSc BIT, FHNW). The system supports school management in coordinating teacher substitute assignments in case of absence.
---

This project is intended to:

- Practice the complete process from **application requirements analysis to implementation**
- Apply advanced **Python** concepts in a browser-based application (NiceGUI)
- Demonstrate **data validation**, a clean architecture (presentation / application logic / persistence), and **database access via ORM**
- Produce clean, well-structured, and documented code (incl. tests)
- Prepare students for **teamwork and professional documentation**
- Use this repository as a starting point by importing it into your own GitHub account  
- Work only within your own copy — do not push to the original template  
- Commit regularly to track your progress

---

# 🎒 TEMPLATE for documentation

> 🚧 Please remove the paragraphs marked with "🚧". These are comments for preparing the documentation.

---

## 📝 Application Requirements

---

### Problem
In schools, when a teacher becomes ill or unavailable, the school management must quickly find a substitute teacher. This process is often handled through phone calls, emails, or spreadsheets, which can lead to delays and miscommunication. As a result, it becomes difficult to efficiently coordinate substitute assignments, track request statuses, and ensure that all classes are covered in time. EduSub addresses this problem by providing a centralized web-based platform that streamlines the creation, management, and assignment of substitute requests, improving efficiency, transparency, and reliability in the process.

---

### Scenario

When a teacher is absent:

1. The school manager logs into the system.
2. The school manager creates a substitute request including subject and date.
3. The request is stored in the system and marked as "open".
4. Substitute teachers log into the system and view all open requests.
5. A substitute teacher selects and accepts a suitable request.
6. The system assigns the request to the teacher and updates the status to "accepted".
7. The school manager can view the updated request status.
8. The system prevents multiple teachers from accepting the same request.
9. All assignments are stored and can be reviewed later by the admin.
10. Unauthorized users are prevented from accessing restricted features.

The platform ensures transparency, prevents double bookings, and maintains historical records.

In rare exceptional cases, if a substitute teacher cancels or rejects the assignment shortly before the lesson begins and no replacement can be found in time, the school manager temporarily takes over the class until a new substitute teacher is assigned.

---

### User stories

### 1. Login
**User Story:**  
As a user, I want to log into the system so that I can access my personal dashboard.

**Description:**  
The user enters their email and password on the login page. The system verifies the credentials and redirects the user to the appropriate dashboard based on their role.

**Inputs:**
- email  
- password  

**Outputs:**
- successful login confirmation  
- redirect to personal dashboard  
- error message if login fails  

---

### 2. Create Substitute Request
**User Story:**  
As a school manager, I want to create a substitute request so that I can quickly find a replacement teacher.

**Description:**  
The school manager creates a new request by entering the required details. The system stores the request and makes it available to substitute teachers.

**Inputs:**
- school name  
- subject
- date and time
- notes (optional)  

**Outputs:**
- confirmation that the request was created  
- request appears in the list  
- status set to "open"  

---

### 3. View Open Requests
**User Story:**  
As a substitute teacher, I want to see all open substitute requests so that I can choose suitable assignments.

**Description:**  
The substitute teacher views a list of all currently open requests in the system.

**Inputs:**
- logged-in session  

**Outputs:**
- list of open requests  
- request details (school, subject, date / time, etc.)  

---

### 4. Accept Substitute Request
**User Story:**  
As a substitute teacher, I want to accept a request so that the school knows I will take the assignment.

**Description:**  
The substitute teacher selects an open request and accepts it. The system assigns the request and updates its status.

**Inputs:**
- request_id  
- logged-in session  

**Outputs:**
- confirmation of acceptance  
- request status updated to "accepted"

---

### 5. View Accepted Assignments
**User Story:**  
As a substitute teacher, I want to view my accepted assignments so that I can manage my schedule.

**Description:**  
The teacher views all assignments that have been accepted.

**Inputs:**
- logged-in session  

**Outputs:**
- list of accepted assignments  
- assignment details

---

### 6. View Request Status
**User Story:**  
As a school manager, I want to see who accepted a request so that planning is reliable.

**Description:**  
The manager views the status of each request and sees which teacher has accepted it.

**Inputs:**
- request_id  
- logged-in session  

**Outputs:**
- request status  
- assigned teacher information

---

### 7. Cancel Substitute Request
**User Story:**  
As a school manager, I want to cancel a request so that outdated or unnecessary requests are removed.

**Description:**  
The manager cancels an existing request. The system updates the status and removes it from open requests.

**Inputs:**
- request_id  

**Outputs:**
- cancellation confirmation  
- status updated to "cancelled"  

---

### 8. Manage Users and Roles
**User Story:**  
As an admin, I want to add users and roles so that only authorized users can access the system.

**Description:**  
The admin creates and assigns roles.

**Inputs:**
- user_id  
- name  
- email  
- role  

**Outputs:**
- updated user list  
- confirmation of changes  

---

### 9. View Assignment History
**User Story:**  
As an admin, I want to view past assignments so that I can monitor system activity.

**Description:**  
The admin reviews historical assignment data.

**Inputs:**
- logged-in admin session  
- optional filters  

**Outputs:**
- list of past assignments  
- status and activity overview

---

### 10. Prevent Double Booking / Secure Assignment
**User Story:**  
As the system, I want to prevent multiple teachers from accepting the same request so that scheduling conflicts are avoided.

**Description:**  
When a substitute teacher tries to accept a request, the system checks whether the request has already been accepted by another teacher. If so, the system blocks the action and informs the user.

**Inputs:**
- request_id   
- logged-in session

**Outputs:**
- success confirmation if request is still available
- error message if request is already assigned
- request status remains consistent
---

### Use cases

> 🚧 Name actors and briefly describe each use case. Ideally, a UML use case diagram specifies use cases and relationships.

![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png)

<img width="480" height="813" alt="Bildschirmfoto 2026-03-23 um 13 17 25" src="https://github.com/user-attachments/assets/fcddd356-3ff6-4493-b692-5ee5b583e53c" />   


**Actors**

– **School Manager**  
Creates substitute requests, manages and confirms assignments.

– **Substitute Teacher**  
Views open requests, accepts assignments, and manages own schedule.

– **Admin**  
Manages users, roles, schools, and monitors system activity.

**Use cases**

1. **Login (All Users)**  
   Users log into the system using email and password.  
   → System authenticates user and redirects to the correct dashboard.

2. **Register Account (Visitor)**  
   A new user creates an account by entering personal details and selecting a role.  
   → Account is stored in the system.

3. **Create Substitute Request (School Manager)**  
   School Manager creates a request for a substitute teacher.  
   → Request becomes visible to substitute teachers.

4. **View Open Requests (Substitute Teacher)**  
   Substitute Teacher views available substitute requests.  
   → List of open requests is displayed.

5. **Accept Substitute Request (Substitute Teacher)**  
   Substitute Teacher accepts a request.  
   → Request is assigned to the teacher.

6. **View Accepted Assignments (Substitute Teacher)**  
   Substitute Teacher views all accepted assignments.  
   → Personal assignment list is shown.

7. **View Request Status (School Manager)**  
   School Manager checks the status of requests.  
   → Status (open, accepted, completed) is displayed.

8. **Cancel Substitute Request (School Manager)**  
   School Manager cancels an existing request.  
   → Request is removed or marked as cancelled.

9. **Manage Users and Roles (Admin)**  
   Admin creates, updates, or deletes users and roles.  
   → System user data is updated.

10. **View Assignment History (Admin)**  
    Admin reviews past assignments and system activity.  
    → Historical data is displayed.

---

### Wireframes / Mockups

> 🚧 Add screenshots of the wireframe mockups you chose to implement.

![Wireframe – Home](docs/ui-images/wireframe_home.png)
![Wireframe – Checkout](docs/ui-images/wireframe_checkout.png)

---

## 🏛️ Architecture

> 🚧 Document the architecture components, relationships, and key design decisions.

### Software Architecture

> 🚧 Insert your UML class diagram(s). Split into multiple diagrams if needed.

![UML Class Diagram](docs/architecture-diagrams/uml_class_architecture.png)

**Layers / components:**
- UI (NiceGUI pages/components, browser as thin client)
- Application logic (controllers + domain/services)
- Persistence (SQLite + ORM entities + repositories/queries)

**Design decisions (examples):**
- Organize code using **MVC**:
   - **Model:** domain + ORM entities (e.g. `models.py`)
   - **View:** NiceGUI UI components/pages
   - **Controller:** event handlers and coordination logic between UI, services, and persistence
- Separate UI (`app/main.py`) from domain logic (e.g. `pricing.py`) and persistence (e.g. `models.py`, `db.py`)
- Use and interaction of modules to minimize dependencies, by minimizing cohesion and maximizing coupling
- Keep business rules testable without starting the UI

**Design patterns used (examples):**
- MVC (Model–View–Controller)
- Repository/DAO for database access (e.g. `queries.py`)
- Strategy for business rules (e.g. discount calculation)
- Adapter for external services (e.g. invoice generation backend)

---

### 🗄️ Database and ORM

> 🚧 Describe the database and your ORM entities. Ideally, a diagram documents the database and it is described together with the ORM entities.

![ER Diagram](docs/architecture-diagrams/er_diagram.png)

**ORM and Entities (example):** In the database, order are stored in ... that are mapped an `Order` entity. The `Order` ↔ `OrderItem` relationship ... ensures that an `Order` has at least one `OrderItem` and an `OrderItem` always relates to an `Order`.

---

## ✅ Project Requirements

---

> 🚧 Requirements act as a contract: implement and demonstrate each point below.

Each app must meet the following criteria in order to be accepted (see also the official project guidelines PDF on Moodle):

1. Using NiceGUI for building an interactive web app
2. Data validation in the app
3. Using an ORM for database management

---

### 1. Browser-based App (NiceGUI)

> 🚧 In this section, document how your project fulfills each criterion.

The system is fully browser-based and built using NiceGUI.
The browser acts as a thin client while business logic and state management are handled server-side.

Users can:
– Log in
– Create and manage substitute requests
– Accept assignments
– View assignment history

**Architecture note (per SS26 guidelines):** the browser is a thin client; UI state + business logic live on the server-side NiceGUI app.

---

### 2. Data Validation

The application validates all user input to ensure data integrity, consistency, and a reliable coordination process.
Validation includes required fields when creating substitute requests (date, time range, school, subject), logical checks for valid time intervals, and role-based permission checks to ensure that only authorized users can perform specific actions.
Additionally, the system prevents double bookings by checking for overlapping assignments before allowing a substitute teacher to accept a request.
These checks prevent inconsistent data, system errors, and scheduling conflicts, while guiding users to provide correct and complete information.

---

### 3. Database Management

All data is managed via an ORM (SQLAlchemy or SQLModel).
The SQLite database persists:
– Users
– Schools
– Subjects
– Requests
– Assignments

---

## ⚙️ Implementation

---

### Technology

– Python 3.x
– NiceGUI
– SQLite
– SQLAlchemy / SQLModel
– Pydantic (optional validation)

---

### 📂 Repository Structure

```text
pizza-nicegui/
├─ README.md
├─ pyproject.toml                 # or requirements.txt
├─ .env.example                   # DATABASE_URL=sqlite:///data/pizza.db
├─ .gitignore
│
├─ docs/                          # screenshots, diagrams, additional documentation if needed
│  ├─ ui-images/
│  │  ├─ ui_showcase.png
│  │  ├─ ui_menu.png
│  │  ├─ ui_checkout.png
│  │  ├─ wireframe_home.png
│  │  └─ wireframe_checkout.png
│  └─ architecture-diagrams/
│     ├─ uml_use_case_diagram.png
│     ├─ uml_class_architecture.png
│     ├─ uml_class_domain.png
│     ├─ uml_class_persistence.png
│     └─ er_diagram.png
│
├─ app/
│  ├─ main.py                        # entrypoint, starts the main module(s)
|  └─ pizzarp/                       # main module
│     ├─ __main__.py                 # entrypoint of the module, starts NiceGui
|     ├─ persistence/                # example of a module; organize in modules according to the architecture
│     |  ├─ __main.py__              # initializes data access
│     |  ├─ models.py                # ORM models (User, Pizza, Order, OrderItem)
│     |  ├─ queries.py               # query helpers (menu, orders)
|     |  └─ db.py                    # create_engine + session factory + init_db()
│     ├─ pricing.py                  # subtotal/discount/total logic
│     ├─ invoice.py                  # generate invoice file
│     └─ seed.py                     # seed pizzas/users
│
├─ data/                          # sqlite database (gitignored)
├─ invoices/                      # generated invoices (gitignored)
└─ tests/
   ├─ test_pricing.py
   └─ test_invoice.py
```

---

### How to Run

> 🚧 Adjust to your project.

### 1. Project Setup
- Python 3.13 (or the course version) is required
- Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration
- E.g., setup of parameters or environment variables

### 3. Launch
- Start the NiceGUI app (example):
   ```bash
   python app/main.py
   ```
- Open the URL printed in the console.

### 4. Usage (document as steps)

> 🚧 Describe the usage of the main functions

Order Pizza:
1. Open the menu page and browse pizzas.
2. Add items (with quantities) to the current order.
3. Review total (incl. discounts) and validate inputs.
4. Checkout to persist the order and generate the invoice.

> 🚧 Add UI screenshots of the main screens (or a short video link):

![UI – Menu](docs/ui-images/ui_menu.png)
![UI – Checkout](docs/ui-images/ui_checkout.png)

---

## 🧪 Testing

> 🚧 Explain what you test and how to run tests.

**Types (examples):**
- Unit tests: pricing/discount rules, validators
- Integration tests: ORM mappings + queries against a test SQLite DB

**Run:**
```bash
pytest
```

> 🚧 If you provide separate commands, document them here (e.g. `pytest -m integration`).

---

### Libraries Used

- nicegui
- sqlalchemy / sqlmodel
- pydantic
- ...

## 👥 Team & Contributions

---

> 🚧 Fill in the names of all team members and describe their individual contributions below.

| Name      | Contribution |
|-----------|--------------|
| Ata Erduran | Teacher Dashboard, Application model, ApplicationService (apply, list, validation) |
| Ahmet Iyidogan | Authentication, User model, Login/Register views, database setup, route guard, and main application routing |
| Mert Kirtas | Admin Dashboard, SubstituteRequest model, RequestService (create, list, approve, reject), and request management logic |

---

## 🤝 Contributing

---

> 🚧 This is a template repository for student projects.  
> 🚧 Do not change this section in your final submission.

- Use this repository as a starting point by importing it into your own GitHub account
- Work only within your own copy — do not push to the original template
- Commit regularly to track your progress

---

## 📝 License

---

This project is provided for **educational use only** as part of the Advanced Programming module.

[MIT License](LICENSE)

