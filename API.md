# API Documentation

The Simulyn Enterprise Backend provides asynchronous REST endpoints orchestrated by FastAPI.

## Base URL
`http://localhost:8000/api`

## Endpoints

### 1. `POST /extract_scenario`
Extracts structured market parameters from raw user text using Fireworks AI.
- **Request Body:**
  ```json
  { "text": "Launch a new luxury gaming laptop" }
  ```
- **Response (200 OK):**
  ```json
  {
    "product_name": { "value": "Luxury Gaming Laptop", "confidence": "95%" },
    "price": { "value": 2500, "confidence": "90%" },
    "id": "uuid-string"
  }
  ```

### 2. `POST /generate_population`
Generates the SKPI agent network based on the extracted scenario.
- **Request Body:**
  ```json
  {
    "scenario": { ... },
    "num_nodes": 500
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "simulation_id": "uuid-string",
    "agents": [ ... ],
    "links": [ ... ]
  }
  ```

### 3. `POST /simulate`
Executes the PyTorch diffusion matrix across the generated population.
- **Request Body:**
  ```json
  { "simulation_id": "uuid-string" }
  ```
- **Response (200 OK):**
  ```json
  {
    "history": [ ... ],
    "reasoning_traces": { ... }
  }
  ```
- **Error (422 Unprocessable Entity):** Triggered if `simulation_id` is not a strict `UUID4`.

### 4. `GET /health`
Returns the operational state of the API and PyTorch bindings.
- **Response (200 OK):**
  ```json
  { "status": "online", "pytorch_installed": true }
  ```
