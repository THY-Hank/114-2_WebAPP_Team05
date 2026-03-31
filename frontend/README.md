# Frontend for ChatDev Project

This folder contains the frontend code for the ChatDev project, a GitHub-like website with an integrated chat room. It is built with Vue.js, Vue Router, and Pinia, using Vite for the development environment.

## Project Goal

The objective is to build a collaborative coding platform where users can manage projects, upload and review code, and communicate with team members in real-time chat rooms. This frontend is developed as a Single Page Application (SPA) using Vue 3 and connects to a full Django backend via REST APIs and WebSockets.

## Getting Started

To run the project locally, follow these steps:

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173` (or another port if 5173 is in use).

## Project Structure

The source code is organized into several key directories within `src/`:

-   `assets/`: Contains global and component-specific CSS files.
    -   `main.css`: Global styles and CSS variables.
    -   `layout.css`: Styles for the main application layout.
    -   Other `.css` files are specific to certain views.
-   `components/`: Contains reusable Vue components that are used across different views (e.g., `ShareModal.vue`).
-   `layouts/`: Contains layout components that define the page structure.
    -   `MainLayout.vue`: The main layout for the application after logging in, featuring a persistent sidebar for navigation.
-   `router/`: Contains the Vue Router configuration (`index.ts`). It defines all application routes, including the nested structure for the main layout.
-   `stores/`: Contains the Pinia state management store.
    -   `main.ts`: This is the core store of the application. It holds the active local state, authenticates users, and communicates with the real Django backend via REST Api (`src/api/`) and WebSockets.
-   `views/`: Contains the main page components for each route.
    -   `LoginView.vue` & `RegisterView.vue`: Authentication pages.
    -   `CodeView.vue`: The main page for browsing files, viewing code, and leaving comments.
    -   `ChatView.vue`: The page for real-time chat between users.

## Key Features & Implementation

-   **State & API Management**: The entire application state is managed by a Pinia store located at `src/stores/main.ts`. This acts as the single source of truth and coordinates with the database backend through native `fetch` wrappers in `src/api` and direct WebSocket connections for real-time messaging.
-   **Routing**: Navigation is handled by Vue Router. A key feature is the nested routing configured in `src/router/index.ts`, which uses `MainLayout.vue` to provide a consistent navigation experience for the `Code` and `Chat` views.
-   **Authentication**: The login and registration flow is handled by the `LoginView` and `RegisterView` components. They interact with the Pinia store to find or create a user.
-   **Code & Chat Integration**:
    -   Users can share code snippets from the chat. This opens a modal (`ShareModal.vue`) to select a file.
    -   When a code snippet is clicked in the chat, the application navigates to the `CodeView` and automatically selects the correct file by reading the query parameters from the URL.

## For Future AI Agent Work

To continue development, please adhere to the established structure:

-   For new pages, create a component in the `views/` directory and add a corresponding route in `src/router/index.ts`.
-   For new state or data, add it to the `state` in `src/stores/main.ts`. For new data operations, add an `action`.
-   Reusable UI elements should be created in the `components/` directory.
-   Global styles should be added to `src/assets/main.css`.
-   Always check the Pinia store (`src/stores/main.ts`) first to understand the data structure before making changes.
