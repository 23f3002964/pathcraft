# PathCraft Backend API Reference

This document provides a quick reference for the PathCraft Backend API endpoints. For interactive documentation and detailed schema definitions, please refer to the automatically generated Swagger UI at `/docs` or ReDoc at `/redoc` when the server is running.

**Base URL:** `http://127.0.0.1:8000/api` (during development)

---

## Authentication (`/api/users`, `/api/token`)

### `POST /api/users/`
- **Description:** Register a new user.
- **Request Body:** `UserCreate` schema (email, password, daily_start_hour, daily_end_hour)
- **Response:** `User` schema (id, email, is_active, daily_start_hour, daily_end_hour)

### `POST /api/token`
- **Description:** Authenticate user and get an access token.
- **Request Body:** Form data (username, password)
- **Response:** JSON object with `access_token` and `token_type`

### `GET /api/users/me`
- **Description:** Get current authenticated user's profile.
- **Authentication:** Bearer Token
- **Response:** `User` schema

### `PUT /api/users/{user_id}`
- **Description:** Update user profile.
- **Authentication:** Bearer Token (user_id must match authenticated user)
- **Request Body:** `UserCreate` schema (email, password, daily_start_hour, daily_end_hour)
- **Response:** `User` schema

---

## Goals (`/api/goals`)

### `POST /api/goals/`
- **Description:** Create a new goal.
- **Authentication:** Bearer Token
- **Request Body:** `GoalCreate` schema (title, target_date, methodology)
- **Response:** `Goal` schema

### `GET /api/goals/`
- **Description:** Retrieve a list of all goals for the authenticated user.
- **Authentication:** Bearer Token
- **Response:** Array of `Goal` schemas

### `GET /api/goals/{goal_id}`
- **Description:** Retrieve a specific goal by ID.
- **Authentication:** Bearer Token
- **Response:** `Goal` schema

### `PUT /api/goals/{goal_id}`
- **Description:** Update an existing goal.
- **Authentication:** Bearer Token
- **Request Body:** `GoalCreate` schema
- **Response:** `Goal` schema

### `DELETE /api/goals/{goal_id}`
- **Description:** Delete a goal.
- **Authentication:** Bearer Token
- **Response:** Success message

### `POST /api/goals/{goal_id}/decompose/`
- **Description:** Decompose a goal into sub-goals using AI/rule-based logic.
- **Authentication:** Bearer Token
- **Response:** Array of `SubGoal` schemas

---

## Sub-Goals (`/api/sub_goals`)

### `POST /api/sub_goals/`
- **Description:** Create a new sub-goal.
- **Authentication:** Bearer Token
- **Request Body:** `SubGoalCreate` schema (parent_goal_id, description, estimated_effort_minutes)
- **Response:** `SubGoal` schema

### `GET /api/goals/{goal_id}/sub_goals/`
- **Description:** Retrieve all sub-goals for a specific goal.
- **Authentication:** Bearer Token
- **Response:** Array of `SubGoal` schemas

### `GET /api/sub_goals/{sub_goal_id}`
- **Description:** Retrieve a specific sub-goal by ID.
- **Authentication:** Bearer Token
- **Response:** `SubGoal` schema

### `PUT /api/sub_goals/{sub_goal_id}`
- **Description:** Update an existing sub-goal.
- **Authentication:** Bearer Token
- **Request Body:** `SubGoalCreate` schema
- **Response:** `SubGoal` schema

### `DELETE /api/sub_goals/{sub_goal_id}`
- **Description:** Delete a sub-goal.
- **Authentication:** Bearer Token
- **Response:** Success message

### `POST /api/sub_goals/{sub_goal_id}/schedule/`
- **Description:** Schedule tasks for a sub-goal using AI/rule-based logic.
- **Authentication:** Bearer Token
- **Response:** Array of `Task` schemas

---

## Tasks (`/api/tasks`)

### `POST /api/tasks/`
- **Description:** Create a new task.
- **Authentication:** Bearer Token
- **Request Body:** `TaskCreate` schema (sub_goal_id, planned_start, planned_end, status, priority, dependencies)
- **Response:** `Task` schema

### `GET /api/sub_goals/{sub_goal_id}/tasks/`
- **Description:** Retrieve all tasks for a specific sub-goal.
- **Authentication:** Bearer Token
- **Response:** Array of `Task` schemas

### `GET /api/tasks/{task_id}`
- **Description:** Retrieve a specific task by ID.
- **Authentication:** Bearer Token
- **Response:** `Task` schema

### `PUT /api/tasks/{task_id}`
- **Description:** Update an existing task.
- **Authentication:** Bearer Token
- **Request Body:** `TaskCreate` schema
- **Response:** `Task` schema

### `DELETE /api/tasks/{task_id}`
- **Description:** Delete a task.
- **Authentication:** Bearer Token
- **Response:** Success message

---

## Notifications (`/api/notifications`)

### `POST /api/notifications/`
- **Description:** Create a new notification.
- **Authentication:** Bearer Token
- **Request Body:** `NotificationCreate` schema (user_id, message, notification_time, method, task_id)
- **Response:** `Notification` schema

### `GET /api/notifications/me`
- **Description:** Retrieve all notifications for the authenticated user.
- **Authentication:** Bearer Token
- **Response:** Array of `Notification` schemas

### `PUT /api/notifications/{notification_id}/mark_sent`
- **Description:** Mark a notification as sent.
- **Authentication:** Bearer Token
- **Response:** `Notification` schema

---

## Recurring Tasks (`/api/recurring_tasks`)

### `POST /api/recurring_tasks/`
- **Description:** Create a new recurring task.
- **Authentication:** Bearer Token
- **Request Body:** `RecurringTaskCreate` schema (user_id, title, description, rrule, start_date, end_date)
- **Response:** `RecurringTask` schema

### `GET /api/recurring_tasks/me`
- **Description:** Retrieve all recurring tasks for the authenticated user.
- **Authentication:** Bearer Token
- **Response:** Array of `RecurringTask` schemas

### `POST /api/recurring_tasks/{recurring_task_id}/generate_tasks`
- **Description:** Generate concrete tasks from a recurring task based on its RRULE.
- **Authentication:** Bearer Token
- **Response:** Array of `Task` schemas

---

## Calendar Integrations (`/api/calendar_integrations`)

### `POST /api/calendar_integrations/`
- **Description:** Create a new calendar integration.
- **Authentication:** Bearer Token
- **Request Body:** `CalendarIntegrationCreate` schema (user_id, provider, access_token, refresh_token, expires_at)
- **Response:** `CalendarIntegration` schema

### `GET /api/calendar_integrations/me`
- **Description:** Retrieve all calendar integrations for the authenticated user.
- **Authentication:** Bearer Token
- **Response:** Array of `CalendarIntegration` schemas

### `DELETE /api/calendar_integrations/{integration_id}`
- **Description:** Delete a calendar integration.
- **Authentication:** Bearer Token
- **Response:** Success message
