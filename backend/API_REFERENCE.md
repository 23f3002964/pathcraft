# PathCraft API Reference

This document provides a comprehensive reference for all API endpoints in the PathCraft application.

## Authentication

All endpoints require Bearer Token authentication unless otherwise specified. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

---

## Users (`/api/users`)

### `POST /api/users/`
- **Description:** Create a new user account.
- **Request Body:** `UserCreate` schema (email, password)
- **Response:** `User` schema

### `POST /api/token`
- **Description:** Generate access token (login).
- **Request Body:** Form data (username, password)
- **Response:** Access token

### `GET /api/users/me`
- **Description:** Get current user details.
- **Authentication:** Bearer Token
- **Response:** `User` schema

### `PUT /api/users/me`
- **Description:** Update current user profile.
- **Authentication:** Bearer Token
- **Request Body:** `UserUpdate` schema
- **Response:** `User` schema

---

## Goals (`/api/goals`)

### `POST /api/goals/`
- **Description:** Create a new goal.
- **Authentication:** Bearer Token
- **Request Body:** `GoalCreate` schema (title, target_date, methodology)
- **Response:** `Goal` schema

### `GET /api/goals/`
- **Description:** Retrieve all goals for the authenticated user.
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

### `POST /api/goals/{goal_id}/decompose`
- **Description:** Decompose a goal into sub-goals using AI/rule-based logic.
- **Authentication:** Bearer Token
- **Response:** Array of `SubGoal` schemas

---

## Sub-Goals (`/api/sub_goals`)

### `POST /api/sub_goals/`
- **Description:** Create a new sub-goal.
- **Authentication:** Bearer Token
- **Request Body:** `SubGoalCreate` schema (goal_id, title, description, target_date)
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

### `PUT /api/tasks/{task_id}/reschedule`
- **Description:** Reschedule an existing task by providing new planned start and end times.
- **Authentication:** Bearer Token
- **Request Body:** `RescheduleTask` schema (planned_start, planned_end)
- **Response:** `Task` schema

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

---

## Teams (`/api/teams`)

### `POST /api/teams/`
- **Description:** Create a new team.
- **Authentication:** Bearer Token
- **Request Body:** `TeamCreate` schema (name, description)
- **Response:** `Team` schema

### `GET /api/teams/me`
- **Description:** Get all teams the current user is a member of.
- **Authentication:** Bearer Token
- **Response:** Array of `Team` schemas

### `GET /api/teams/{team_id}`
- **Description:** Get a specific team by ID.
- **Authentication:** Bearer Token
- **Response:** `Team` schema

### `GET /api/teams/{team_id}/members`
- **Description:** Get all members of a team.
- **Authentication:** Bearer Token
- **Response:** Array of `TeamMember` schemas

### `PUT /api/teams/{team_id}`
- **Description:** Update team information (only team owner can do this).
- **Authentication:** Bearer Token
- **Request Body:** `TeamCreate` schema
- **Response:** `Team` schema

### `DELETE /api/teams/{team_id}`
- **Description:** Delete a team (only team owner can do this).
- **Authentication:** Bearer Token
- **Response:** Success message

### `POST /api/teams/{team_id}/members/`
- **Description:** Add a new member to the team.
- **Authentication:** Bearer Token
- **Request Body:** `TeamMemberCreate` schema (user_id, role)
- **Response:** `TeamMember` schema

### `DELETE /api/teams/{team_id}/members/{user_id}`
- **Description:** Remove a member from the team (only team admins can do this).
- **Authentication:** Bearer Token
- **Response:** Success message

---

## Team OKRs (`/api/team_okrs`)

### `POST /api/teams/{team_id}/okrs/`
- **Description:** Create a new OKR for a team.
- **Authentication:** Bearer Token
- **Request Body:** `TeamOKRCreate` schema (title, description, objective, quarter, year, key_results)
- **Response:** `TeamOKR` schema

### `GET /api/teams/{team_id}/okrs/`
- **Description:** Get all OKRs for a team.
- **Authentication:** Bearer Token
- **Response:** Array of `TeamOKR` schemas

### `GET /api/teams/{team_id}/okrs/{okr_id}`
- **Description:** Get a specific OKR by ID.
- **Authentication:** Bearer Token
- **Response:** `TeamOKR` schema

### `PUT /api/teams/{team_id}/okrs/{okr_id}`
- **Description:** Update an OKR (only team admins can do this).
- **Authentication:** Bearer Token
- **Request Body:** `TeamOKRCreate` schema
- **Response:** `TeamOKR` schema

### `DELETE /api/teams/{team_id}/okrs/{okr_id}`
- **Description:** Delete an OKR (only team admins can do this).
- **Authentication:** Bearer Token
- **Response:** Success message

### `POST /api/okrs/{okr_id}/key-results/`
- **Description:** Add a key result to an OKR.
- **Authentication:** Bearer Token
- **Request Body:** `TeamOKRKeyResultCreate` schema (title, description, target_value, unit)
- **Response:** `TeamOKRKeyResult` schema

### `PUT /api/okrs/{okr_id}/key-results/{kr_id}`
- **Description:** Update a key result.
- **Authentication:** Bearer Token
- **Request Body:** `TeamOKRKeyResultCreate` schema
- **Response:** `TeamOKRKeyResult` schema

### `DELETE /api/okrs/{okr_id}/key-results/{kr_id}`
- **Description:** Delete a key result.
- **Authentication:** Bearer Token
- **Response:** Success message

---

## User Preferences (`/api/user_preferences`)

### `POST /api/preferences/`
- **Description:** Create a new user preference.
- **Authentication:** Bearer Token
- **Request Body:** `UserPreferenceCreate` schema (user_id, preference_key, preference_value)
- **Response:** `UserPreference` schema

### `GET /api/preferences/`
- **Description:** Get all preferences for the current user.
- **Authentication:** Bearer Token
- **Response:** Array of `UserPreference` schemas

### `GET /api/preferences/{preference_key}`
- **Description:** Get a specific preference by key.
- **Authentication:** Bearer Token
- **Response:** `UserPreference` schema

### `PUT /api/preferences/{preference_key}`
- **Description:** Update a user preference.
- **Authentication:** Bearer Token
- **Request Body:** `UserPreferenceCreate` schema
- **Response:** `UserPreference` schema

### `DELETE /api/preferences/{preference_key}`
- **Description:** Delete a user preference.
- **Authentication:** Bearer Token
- **Response:** Success message

---

## User Analytics (`/api/user_preferences`)

### `POST /api/analytics/`
- **Description:** Create a new analytics entry for the current user.
- **Authentication:** Bearer Token
- **Request Body:** `UserAnalyticsCreate` schema (user_id, date, tasks_completed, goals_achieved, productivity_score, focus_time_minutes)
- **Response:** `UserAnalytics` schema

### `GET /api/analytics/`
- **Description:** Get analytics for the current user with optional date range.
- **Authentication:** Bearer Token
- **Query Parameters:** start_date (optional), end_date (optional)
- **Response:** Array of `UserAnalytics` schemas

### `GET /api/analytics/{analytics_date}`
- **Description:** Get analytics for a specific date.
- **Authentication:** Bearer Token
- **Response:** `UserAnalytics` schema

### `PUT /api/analytics/{analytics_date}`
- **Description:** Update analytics for a specific date.
- **Authentication:** Bearer Token
- **Request Body:** `UserAnalyticsCreate` schema
- **Response:** `UserAnalytics` schema

### `GET /api/analytics/summary/`
- **Description:** Get analytics summary for the last N days.
- **Authentication:** Bearer Token
- **Query Parameters:** days (default: 30)
- **Response:** Summary object with totals and averages

---

## Learning Platforms (`/api/learning_platforms`)

### `POST /api/learning-platforms/`
- **Description:** Create a new learning platform integration.
- **Authentication:** Bearer Token
- **Request Body:** `LearningPlatformCreate` schema (user_id, platform_name, api_key, api_secret, access_token, refresh_token, expires_at)
- **Response:** `LearningPlatform` schema

### `GET /api/learning-platforms/`
- **Description:** Get all learning platforms for the current user.
- **Authentication:** Bearer Token
- **Response:** Array of `LearningPlatform` schemas

### `GET /api/learning-platforms/{platform_id}`
- **Description:** Get a specific learning platform by ID.
- **Authentication:** Bearer Token
- **Response:** `LearningPlatform` schema

### `PUT /api/learning-platforms/{platform_id}`
- **Description:** Update a learning platform integration.
- **Authentication:** Bearer Token
- **Request Body:** `LearningPlatformCreate` schema
- **Response:** `LearningPlatform` schema

### `DELETE /api/learning-platforms/{platform_id}`
- **Description:** Delete a learning platform integration.
- **Authentication:** Bearer Token
- **Response:** Success message

### `POST /api/learning-platforms/{platform_id}/courses/`
- **Description:** Create a new learning course.
- **Authentication:** Bearer Token
- **Request Body:** `LearningCourseCreate` schema (platform_id, course_id, title, description, duration_minutes, progress_percentage, status)
- **Response:** `LearningCourse` schema

### `GET /api/learning-platforms/{platform_id}/courses/`
- **Description:** Get all courses for a learning platform.
- **Authentication:** Bearer Token
- **Response:** Array of `LearningCourse` schemas

### `GET /api/learning-courses/{course_id}`
- **Description:** Get a specific learning course by ID.
- **Authentication:** Bearer Token
- **Response:** `LearningCourse` schema

### `PUT /api/learning-courses/{course_id}`
- **Description:** Update a learning course.
- **Authentication:** Bearer Token
- **Request Body:** `LearningCourseCreate` schema
- **Response:** `LearningCourse` schema

### `DELETE /api/learning-courses/{course_id}`
- **Description:** Delete a learning course.
- **Authentication:** Bearer Token
- **Response:** Success message

### `GET /api/learning-courses/summary/`
- **Description:** Get learning summary for the current user.
- **Authentication:** Bearer Token
- **Response:** Summary object with platform and course statistics

---

## WebSocket Endpoints

### `GET /ws/{user_id}`
- **Description:** WebSocket connection for real-time notifications.
- **Authentication:** User ID in path
- **Protocol:** WebSocket
- **Usage:** Connect to receive real-time updates and notifications

---

## Health Check

### `GET /health`
- **Description:** Health check endpoint.
- **Authentication:** None required
- **Response:** Status object

---

## Data Models

### User
- `id`: String (UUID)
- `email`: String
- `is_active`: Boolean
- `daily_start_hour`: Integer
- `daily_end_hour`: Integer
- `tier`: String (free, pro, enterprise)
- `goal_limit`: Integer

### Goal
- `id`: String (UUID)
- `title`: String
- `target_date`: DateTime
- `methodology`: String
- `owner_id`: String (User ID)
- `team_id`: String (Team ID, optional)

### SubGoal
- `id`: String (UUID)
- `title`: String
- `description`: String
- `target_date`: DateTime
- `goal_id`: String (Goal ID)

### Task
- `id`: String (UUID)
- `sub_goal_id`: String (SubGoal ID)
- `planned_start`: DateTime
- `planned_end`: DateTime
- `status`: String (todo, in_progress, done)
- `priority`: Integer (0=high, 1=medium, 2=low)
- `dependencies`: String (JSON array)

### Team
- `id`: String (UUID)
- `name`: String
- `description`: String
- `owner_id`: String (User ID)

### TeamMember
- `id`: String (UUID)
- `team_id`: String (Team ID)
- `user_id`: String (User ID)
- `role`: String (admin, member)

### TeamOKR
- `id`: String (UUID)
- `team_id`: String (Team ID)
- `title`: String
- `description`: String
- `objective`: String
- `quarter`: String
- `year`: Integer
- `status`: String (active, completed, archived)

### TeamOKRKeyResult
- `id`: String (UUID)
- `okr_id`: String (OKR ID)
- `title`: String
- `description`: String
- `target_value`: Float
- `current_value`: Float
- `unit`: String
- `status`: String (in_progress, completed, at_risk)

### UserPreference
- `id`: String (UUID)
- `user_id`: String (User ID)
- `preference_key`: String
- `preference_value`: String

### UserAnalytics
- `id`: String (UUID)
- `user_id`: String (User ID)
- `date`: Date
- `tasks_completed`: Integer
- `goals_achieved`: Integer
- `productivity_score`: Float
- `focus_time_minutes`: Integer

### LearningPlatform
- `id`: String (UUID)
- `user_id`: String (User ID)
- `platform_name`: String
- `api_key`: String
- `api_secret`: String
- `access_token`: String
- `refresh_token`: String
- `expires_at`: DateTime
- `is_active`: Boolean

### LearningCourse
- `id`: String (UUID)
- `platform_id`: String (Platform ID)
- `course_id`: String
- `title`: String
- `description`: String
- `duration_minutes`: Integer
- `progress_percentage`: Float
- `status`: String (enrolled, in_progress, completed, dropped)
- `enrollment_date`: DateTime
- `completion_date`: DateTime
