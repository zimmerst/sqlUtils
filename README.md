# sqlUtils

`sqlUtils` is a Python package for analyzing and visualizing data transformation steps in SQL scripts. 

## Installation

You can install `sqlUtils` via pip:

```pip install sqlUtils```


## Usage

To use `sqlUtils`, you need to import the `parse_sql_file` function and one of the `create_data_transformation_graph` functions, depending on the visualization method you want to use.

```python
from sqlUtils import parse_sql_file, create_data_transformation_graph_v4

statements = parse_sql_file('input.sql')
graph = create_data_transformation_graph_v4(statements)
graph.render('output', view=True)
```


