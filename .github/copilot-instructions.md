When solving problems, keep your solutions small and simple. Prioritize feedback over implementation by asking clarifying questions and seeking clarification on things prior to implementing.

When implementing code avoid adding comments. Prioritize naming your variables, functions, classes, etc. such that they document themselves. In principle, comments should be redundant.

Verify that your code works by running the following commands:
In `script`, `service`, or `speech` directory run `make lint`.
In `client` directory run `npm run build`.

## Client Instructions

- Avoid keeping track of server side data in state. Data should be passed down as props. State should be preserved for client side functionality (i.e. form inputs, etc.) not server side data.

## Data Flow Patterns

- **Server-First Architecture**: Fetch data in server components at the top level and pass down to children. Use Next.js `force-cache` with `revalidateTag()` for cache management.
- **Promise Passing**: Pass promises down the component tree and resolve them with `use()` in client components where the data is actually needed.
- **Single API Calls**: Avoid duplicate API calls by combining related data into single objects/promises. If multiple components need different parts of the same data, fetch once and destructure at consumption.
- **Typed Data Structures**: Create proper TypeScript interfaces for data that flows through multiple components. Define types in `app/types.ts` for reusability.
- **Client-Side Loading**: Only use client-side data loading (like `useAudioLoader`) for user-initiated, interactive features (e.g., voice previews, on-demand content).
- **Cache Strategy**: Use cache tags that align with the actual completion of background processes (e.g., speech generation) rather than request initiation.
