
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

Retrieves a node's details and its linked network.

- **Response Keys**:
  - `nodes`: Array of node details.
  - `links`: Array of connections between nodes.

**Note**: `links.source` and `links.target` refer to node `id`s in `nodes`.

```json
{
  "nodes": [
    {"id": "123abc", "name": "Node1"},
    {"id": "456def", "name": "Node2"}
  ],
  "links": [
    {"source": "123abc", "target": "456def"},
    {"source": "456def", "target": "123abc"}
  ]
}
```

Use `links.source` and `links.target` to map connections to `nodes.id`.