When solving problems, keep your solutions small and simple. Prioritize feedback over implementation by asking clarifying questions and seeking clarification on things prior to implementing.

When implementing code avoid adding comments. Prioritize naming your variables, functions, classes, etc. such that they document themselves. In principle, comments should be redundant.

Verify that your code works by running the following commands:
In `script`, `service`, or `speech` directory run `make lint`.
In `client` directory run `npm run build`.

## Client Instructions

- Avoid keeping track of server side data in state. Data should be passed down as props. State should be preserved for client side functionality (i.e. form inputs, etc.) not server side data.
