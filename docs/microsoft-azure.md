# Microsoft and Azure deployment notes

Local development uses FastAPI and Vite with no cloud credentials. The backend Docker image can be deployed to Azure Container Apps as an HTTP ingress service on port 8000; configure health probing at `/health`. The current compose setup is for local demonstration, not a production cloud topology.

An Azure AI / Microsoft Foundry narrative provider is intentionally not wired into this initial prototype. A future adapter can be configured using environment variables and must receive only the approved evidence-derived narrative contract. Keep deterministic local fallback enabled for offline demos. Never place secrets in source control; use managed identity or the platform's secret store when adding a cloud provider. PostgreSQL and AKS are unnecessary for this filesystem-backed MVP.
