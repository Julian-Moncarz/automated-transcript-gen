"""Bank of 60 diverse, realistic coding task descriptions."""

import random

import dspy

TASK_DESCRIPTIONS: list[str] = [
    # --- Auth / Security (8) ---
    "Fix the authentication bug in the login endpoint that allows users to bypass password validation when the email contains a plus sign.",
    "Add OAuth2 integration with Google for the user registration flow, including token refresh handling.",
    "Implement role-based access control (RBAC) for the admin dashboard API endpoints.",
    "Patch the session management code to invalidate tokens on password change.",
    "Add rate limiting to the password reset endpoint to prevent brute-force attacks.",
    "Implement CSRF protection for all state-changing API endpoints.",
    "Add two-factor authentication support using TOTP with QR code generation.",
    "Fix the JWT token validation to properly check expiration and issuer claims.",

    # --- API Development (8) ---
    "Add pagination and filtering to the /api/v2/products endpoint using cursor-based pagination.",
    "Implement a webhook delivery system with retry logic and exponential backoff.",
    "Create a GraphQL resolver for the user profile query with nested address and order history.",
    "Add request validation middleware using JSON Schema for all POST/PUT endpoints.",
    "Implement API versioning using URL path prefixes and deprecation headers.",
    "Build a file upload endpoint that supports multipart uploads with virus scanning.",
    "Add OpenAPI/Swagger documentation generation for the REST API.",
    "Implement server-sent events (SSE) for real-time order status updates.",

    # --- Database (8) ---
    "Refactor the database connection pooling to use pgBouncer and handle connection timeouts.",
    "Write a migration to add a full-text search index on the products table for the search feature.",
    "Fix the N+1 query problem in the order listing endpoint by adding proper JOIN queries.",
    "Implement soft delete for user accounts with a scheduled cleanup job for GDPR compliance.",
    "Add database sharding logic for the analytics events table based on tenant ID.",
    "Create a data migration script to move user preferences from a JSON column to normalized tables.",
    "Implement optimistic locking for the inventory management system to prevent overselling.",
    "Add read replica routing for GET endpoints to reduce load on the primary database.",

    # --- DevOps / CI (8) ---
    "Update the Kubernetes deployment manifests to add health checks and resource limits.",
    "Configure the CI pipeline to run integration tests against a Dockerized PostgreSQL instance.",
    "Set up Terraform modules for provisioning the staging environment on AWS.",
    "Add a Helm chart for deploying the microservice with configurable replicas and environment variables.",
    "Fix the Docker build to use multi-stage builds and reduce the image size.",
    "Configure log aggregation using Fluentd to ship application logs to Elasticsearch.",
    "Add Prometheus metrics instrumentation to the API gateway for request latency tracking.",
    "Set up GitHub Actions workflow for automated releases with semantic versioning.",

    # --- Frontend (7) ---
    "Fix the infinite re-render loop in the React dashboard component caused by useEffect dependencies.",
    "Add client-side form validation with error messages for the checkout flow.",
    "Implement lazy loading for the product image gallery to improve page load performance.",
    "Fix the CSS grid layout breaking on mobile viewports for the settings page.",
    "Add accessibility attributes (ARIA labels, keyboard navigation) to the dropdown menu component.",
    "Implement dark mode toggle with persistent user preference stored in localStorage.",
    "Add end-to-end tests using Playwright for the user registration and login flows.",

    # --- Performance (7) ---
    "Add Redis caching for the product catalog API to reduce database load during peak traffic.",
    "Profile and optimize the report generation endpoint that times out on large datasets.",
    "Implement request deduplication for the payment processing queue to prevent double charges.",
    "Add connection pooling and keep-alive headers to the HTTP client used for third-party API calls.",
    "Optimize the image processing pipeline to use streaming instead of loading full files into memory.",
    "Fix the memory leak in the WebSocket handler caused by event listeners not being cleaned up.",
    "Add database query result caching with TTL-based invalidation for the analytics dashboard.",

    # --- Testing (7) ---
    "Write unit tests for the payment processing module covering edge cases like currency conversion.",
    "Add integration tests for the email notification service using a mock SMTP server.",
    "Set up property-based testing for the data serialization layer using Hypothesis.",
    "Write regression tests for the bug where concurrent updates to the same order caused data loss.",
    "Add load testing scripts using k6 for the checkout API under simulated Black Friday traffic.",
    "Create test fixtures and factories for the user and order models to simplify test setup.",
    "Add contract tests for the inter-service communication between the order and inventory services.",

    # --- Integrations (7) ---
    "Integrate Stripe webhooks for handling subscription lifecycle events (created, updated, cancelled).",
    "Add Slack notification integration for critical error alerts from the monitoring system.",
    "Implement an S3 backup job that archives database snapshots with lifecycle policies.",
    "Build a data sync pipeline between the CRM and the internal user database using change data capture.",
    "Add SendGrid integration for transactional emails with template management.",
    "Implement a Salesforce API connector for syncing lead data from the marketing forms.",
    "Add Datadog APM instrumentation to trace requests across the microservices.",
]

assert len(TASK_DESCRIPTIONS) == 60


def _shuffled(seed: int = 42) -> list[str]:
    """Return a deterministically shuffled copy of TASK_DESCRIPTIONS."""
    tasks = list(TASK_DESCRIPTIONS)
    random.Random(seed).shuffle(tasks)
    return tasks


def get_trainset(n: int = 40) -> list[dspy.Example]:
    """Return n training examples (shuffled, deterministic)."""
    tasks = _shuffled()
    return [
        dspy.Example(task_description=desc).with_inputs("task_description")
        for desc in tasks[:n]
    ]


def get_devset(n: int = 20) -> list[dspy.Example]:
    """Return n held-out dev examples (shuffled, deterministic)."""
    tasks = _shuffled()
    return [
        dspy.Example(task_description=desc).with_inputs("task_description")
        for desc in tasks[-n:]
    ]
