# Frontend Architecture

The AEGON frontend is built to be a robust, high-performance visualization layer. It is designed to run in modern browsers and interact strictly with the AEGON API Gateway.

## Technology Stack

- **Framework**: React 19 (TypeScript)
- **Routing**: TanStack Router (Type-safe routing)
- **Data Fetching**: TanStack Query (React Query)
- **Styling**: TailwindCSS v4
- **Animations**: Framer Motion
- **Charting**: Recharts
- **Icons**: Lucide React
- **Typography**: IBM Plex Mono (for data-dense tables), Inter (for general UI)

## Core Principles

### 1. Zero Business Logic
The frontend must not contain any calculations, predictive logic, or state optimizations that rightfully belong on the backend. Its sole purpose is to:
- Fetch and display data.
- Capture user interactions.
- Provide fluid, enterprise-grade UX/UI.

### 2. Component Hierarchy
We maintain a strict separation between Presentational components and Container components (Features).

- `components/`: Generic, reusable UI primitives (Buttons, Modals, Cards, Inputs). These components receive data via props and emit events via callbacks. They are entirely agnostic to the application state.
- `features/`: Domain-specific components (e.g., `AssetHealthDashboard`, `MaintenanceTicketList`). These components orchestrate the UI primitives and connect them to TanStack Query hooks.
- `routes/`: The page-level entry points mapped to URLs.

### 3. Server State vs. Client State
- **Server State**: Any data originating from the backend must be managed by TanStack Query. This handles caching, invalidation, background refetching, and pagination out of the box.
- **Client State**: Local UI state (e.g., modal visibility, active tab) is managed via React's `useState` or `useReducer`. Global client state should be minimal.

## Styling Guidelines

- Use Tailwind utility classes for all styling.
- Avoid inline `style={{}}` attributes unless dynamically computing highly variable properties (e.g., chart coordinates).
- Maintain the Enterprise Dark Theme across all new components. Avoid harsh primary colors; utilize muted tones, sophisticated gradients, and subtle glassmorphism effects where appropriate.

## Performance Optimization

- **Code Splitting**: Utilize React's `lazy` and `Suspense` coupled with TanStack Router's lazy loading to keep the initial JS bundle small.
- **Virtualization**: Any list or table rendering more than 100 items must be virtualized.
- **Memoization**: Use `React.memo`, `useMemo`, and `useCallback` judiciously to prevent unnecessary re-renders in complex dashboards.
