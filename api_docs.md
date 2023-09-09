
# API Documentation

## Endpoints

### 1. GET `/nodes/`

- **Description**: Fetches a list of all nodes with their IDs and names.
- **Response**: 
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    [
      {"id": "123abc", "name": "Node1"},
      {"id": "456def", "name": "Node2"}
    ]
    ```

### 2. GET `/nodes/<string:node_id>` or `/nodes/root`

- **Description**: Retrieves a node by its ID or the root node, along with its neighbors and connected links.
- **Response**: 
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    {
      "nodes": [
        {"id": "123abc", "name": "Node1", "content": "Markdown content"},
        {"id": "456def", "name": "Node2", "content": null}
      ],
      "links": [
        {"source": "123abc", "target": "456def", "secundary": true},
        {"source": "456def", "target": "123abc", "secundary": false}
      ]
    }
    ```
