
# API Documentation

## Endpoints

### 1. GET `/nodes/`

- **Description**: Fetches a list of all nodes with their IDs and names.
- **Response**: 
  - **Status Code**: `200 OK`
  - **Example**:
    ```js
    [
      {id: "123abc", name: "Node1"},
      {id: "456def", name: "Node2"}
    ]
    ```

### 2. GET `/nodes/<string:node_id>` or `/nodes/root`

Retrieves a node's details and its linked network.

- **Response Keys**:
  - `nodes`: Array of node details.
  - `links`: Array of connections between nodes.

**Note**: `links.source` and `links.target` refer to node `id`s in `nodes`.

```js
{
  nodes: [
    {id: "123abc", name: "Node1"},
    {
      id: "456def",
      name: "Bullock, George",
      "bgcolor": null,
      "birth": {
        "date": "+1916-01-02T00:00:00Z",
        "place": {
          "coordinates": [52.584167, -2.125278],
          "country": "United Kingdom",
          "name": "Wolverhampton"
        }
      },
      "color": null,
      "death": {
        "date": "+1943-05-31T00:00:00Z",
        "place": {

        }
      },
      "label": "Victorian sculptor furniture maker",
      "places": [],
      "typeId": "f710f257-cd80-5fca-83bd-4a90e5427805",
      "wikidataId": "Q62995264",
      "wikilink": "https://en.wikipedia.org/wiki/Sculptor"}
  ],
  links: [
    {source: "123abc", target: "456def", name: "friend of", color: "rgb(255,0,0)"},
    {source: "456def", target: "123abc", name: "worked with", color: null}
  ]
}
```

Use `links.source` and `links.target` to map connections to `nodes.id`.