import sqlparse
from sql_metadata import Parser as metaparse
import graphviz, colorcet
import random, itertools, argparse

def parse_sql_file(filename, drop_unknown=False, drop_delete=False, drop_drop=False):
    with open(filename, 'r') as sql_file:
        sql = sql_file.read()

    # Split SQL statements by semicolon delimiter
    statements = sqlparse.parse(sql)
    parsed_statements = []
    for statement in statements:
        statement_str = str(statement).strip()
        keep = True
        if statement_str:
            try:
                # Attempt to parse statement with metaparse
                parsed = metaparse(statement_str)
                statement_type = parsed.query_type.lower()
                table_names = parsed.tables
            except Exception:
                # Use sqlparse as fallback if metaparse fails
                parsed_tokens = sqlparse.parse(statement_str)
                if parsed_tokens and parsed_tokens[0].tokens:
                    try:
                        parsed_token_list = sqlparse.sql.TokenList(parsed_tokens[0].tokens)
                        statement_type = sqlparse.sql.Statement(parsed_token_list).get_type().lower()
                        table_names = sqlparse.sql.Statement(parsed_token_list).get_name()

                        # Identify tables referenced in JOIN clauses
                        join_tables = []
                        for token in parsed_token_list.tokens:
                            if isinstance(token, sqlparse.sql.IdentifierList):
                                for identifier in token.get_identifiers():
                                    if identifier.value.upper() == 'JOIN':
                                        # Add tables referenced in JOIN clauses to join_tables
                                        for subtoken in identifier.parent.tokens:
                                            if isinstance(subtoken, sqlparse.sql.Identifier):
                                                join_tables.append(subtoken.value)
                        if join_tables:
                            table_names.extend(join_tables)

                        # Identify target table
                        target_table = None
                        for token in parsed_token_list.tokens:
                            if isinstance(token, sqlparse.sql.Identifier):
                                if token.value.upper() in ['INTO', 'UPDATE']:
                                    target_table = token.get_parent_name()
                                    break
                        if target_table is None and table_names:
                            target_table = table_names[0]
                    except Exception:
                        statement_type = 'UNKNOWN'
                        table_names = []
                        target_table = None
                else:
                    statement_type = 'UNKNOWN'
                    table_names = []
                    target_table = None
            if (drop_unknown and statement_type.lower() == 'unknown'):
                keep = False 
            elif (drop_delete and statement_type.lower() == 'delete'):
                keep = False 
            elif (drop_drop and statement_type.lower() == 'drop table'):
                keep = False 
            if keep: 
                if target_table is None and len(table_names) > 0 : 
                    target_table = table_names[0]
                    # also, delete from table_names 
                    table_names = table_names[1:]
                parsed_statements.append({'type': statement_type, 'tables': [t.lower() for t in table_names], 'target_table': target_table.lower()})

    return parsed_statements

def create_data_transformation_graph(data):
    """
    Creates a visualization of the data transformation steps using graphviz.

    Args:
        data (list): A list of dictionaries representing data transformation steps, where each
                     dictionary contains a 'type' key indicating the transformation type, a 'tables'
                     key containing a list of input tables for the transformation, and a 'target_table'
                     key containing the output table for the transformation.

    Returns:
        graph (graphviz.Digraph): A graphviz object representing the data transformation steps.
    """

    # Create a new graph
    graph = graphviz.Digraph(graph_attr={'rankdir': 'LR'})
    all_tables = []
    # Add nodes for the input tables
    for step in data:
        for table in step['tables']:
            all_tables.append(table)
    for t in sorted(all_tables):
        graph.node(table)

    # Add nodes and edges for the transformation steps
    for i, step in enumerate(data):
        # Add a node for the transformation step
        this_node = step['target_table'] #'{} {}'.format(step['type'], step['target_table'])
        graph.node(this_node, shape='rect', style='filled', fillcolor='lightgray')
        # Add edges from input tables to this node
        for table in step['tables']:
            graph.edge(table, this_node)
        # Add an edge from the previous transformation node (if any)
        if i > 0:
            prev_node = '{} {}'.format(data[i-1]['type'], data[i-1]['target_table'])
            graph.edge(prev_node, this_node)

    return graph



def create_data_transformation_graph_v2(data):
    """
    Creates a visualization of the data transformation steps using graphviz.

    Args:
        data (list): A list of dictionaries representing data transformation steps, where each
                     dictionary contains a 'type' key indicating the transformation type, a 'tables'
                     key containing a list of input tables for the transformation, and a 'target_table'
                     key containing the output table for the transformation.

    Returns:
        graph (graphviz.Digraph): A graphviz object representing the data transformation steps.
    """

    # Create a new graph
    graph = graphviz.Digraph(graph_attr={'rankdir': 'LR', 'splines': 'polyline'})

    # Add clusters for each step
    clusters = {}
    for i, step in enumerate(data):
        cluster_name = '{}_{}'.format(step['type'], step['target_table'])
        if cluster_name not in clusters:
            clusters[cluster_name] = graphviz.Digraph(name=cluster_name, graph_attr={'label': cluster_name})
        # Add nodes and edges for the input tables
        for table in step['tables']:
            clusters[cluster_name].node(table)
            if i > 0:
                prev_cluster_name = '{}_{}'.format(data[i-1]['type'], data[i-1]['target_table'])
                if cluster_name != prev_cluster_name:
                    graph.edge('{}:out'.format(prev_cluster_name), '{}:in'.format(cluster_name))
        # Add a node for the transformation step
        this_node = step['target_table'] #'{} {}'.format(step['type'], step['target_table'])
        clusters[cluster_name].node(this_node, shape='rect', style='filled', fillcolor='lightgray')
        # Add edges from input tables to the transformation node
        for table in step['tables']:
            clusters[cluster_name].edge(table, this_node)
        # Add an edge from the previous transformation node (if any)
        if i > 0:
            prev_cluster_name = '{}_{}'.format(data[i-1]['type'], data[i-1]['target_table'])
            if cluster_name == prev_cluster_name:
                clusters[cluster_name].edge('{}:last'.format(prev_node), '{}:first'.format(this_node))
            else:
                graph.edge('{}:out'.format(prev_cluster_name), '{}:in'.format(cluster_name))
        prev_node = this_node

    # Add the clusters to the graph
    for cluster in clusters.values():
        graph.subgraph(cluster)

    return graph

def create_data_transformation_graph_v3(data):
    """
    Creates a visualization of the data transformation steps using graphviz.

    Args:
        data (list): A list of dictionaries representing data transformation steps, where each
                     dictionary contains a 'type' key indicating the transformation type, a 'tables'
                     key containing a list of input tables for the transformation, and a 'target_table'
                     key containing the output table for the transformation.

    Returns:
        graph (graphviz.Digraph): A graphviz object representing the data transformation steps.
    """

    # Create a new graph
    graph = graphviz.Digraph(graph_attr={'rankdir': 'LR'})
    all_tables = []
    # Add nodes for the input tables
    for step in data:
        for table in step['tables']:
            all_tables.append(table.split()[-1])
    schemas = list(set([table.split('.')[0] if '.' in table else '' for table in all_tables]))
    colors = ['lightblue', 'lightgreen', 'pink', 'yellow', 'lightgray', 'cyan']
    color_map = {schemas[i]: colors[i % len(colors)] for i in range(len(schemas))}
    for t in sorted(all_tables):
        tnode = t
        if t.startswith("create table "):
            tnode = t.replace("create table ","")
        schema = tnode.split('.')[0] if '.' in t else ''
        color = color_map.get(schema, 'white')
        graph.node(tnode, style='filled', fillcolor=color)

    # Add nodes and edges for the transformation steps
    for i, step in enumerate(data):
        # Add a node for the transformation step
        this_node = step['target_table']
        graph.node(this_node, shape='rect', style='filled', fillcolor='lightgray')
        # Add edges from input tables to this node
        for table in step['tables']:
            graph.edge(table, this_node)
        # Add an edge from the previous transformation node (if any)
        if i > 0:
            prev_node = '{} {}'.format(data[i-1]['type'], data[i-1]['target_table'])
            graph.edge(prev_node, this_node)

    return graph

def create_data_transformation_graph_v4(data):
    graph = graphviz.Digraph(graph_attr={'rankdir': 'LR'})
    schema_colors = {}
    node_labels = {}
    
    # loop through each step in the data transformation pipeline
    for step in data:
        target_table = step['target_table']
        tables = step['tables']
        
        # add target table node to the graph
        graph.node(target_table, target_table, color='grey', style='filled')
        node_labels[target_table] = target_table
        # loop through each source table and add it to the graph
        for table in tables:
            try:
                schema, table_name = table.split('.', 1)
            except ValueError:
                schema = None
                table_name = table 
            node_label = f"{schema}.{table_name}" if schema is not None else table_name
            
            # determine the background color for the node based on schema
            if schema in schema_colors:
                node_color = schema_colors[schema]
            else:
                if len(schema_colors) < len(colorcet.glasbey_light):
                    schema_colors[schema] = colorcet.glasbey_light[len(schema_colors)]+"33"
                else:
                    schema_colors[schema] = '#FFFFFF' # white as backup color
                node_color = schema_colors[schema]
                
            if table not in node_labels:
                graph.node(table, node_label, color=node_color, style='filled')
                node_labels[table] = node_label
            
            # add an edge from the source table to the target table
            graph.edge(table, target_table)
    
    return graph


def main():
    parser = argparse.ArgumentParser(description='Visualize SQL data transformations')
    parser.add_argument('input_file', type=str, help='Input SQL file')
    parser.add_argument('--method', type=str, default='v4', help='Version of visualization method to use')
    parser.add_argument('--drop-unknown', action='store_true', default=True, help='Drop unknown statements')
    parser.add_argument('--drop-delete', action='store_true', default=True, help='Drop DELETE statements')
    parser.add_argument('--drop-drop', action='store_true', default=True, help='Drop DROP statements')

    args = parser.parse_args()
    statements = parse_sql_file(args.input_file, drop_unknown=args.drop_unknown, drop_delete=args.drop_delete, drop_drop=args.drop_drop)
    
    if args.method == 'v1':
        graph = create_data_transformation_graph(statements)
    elif args.method == 'v2':
        graph = create_data_transformation_graph_v2(statements)
    elif args.method == 'v3':
        graph = create_data_transformation_graph_v3(statements)
    elif args.method == 'v4':
        graph = create_data_transformation_graph_v4(statements)
    else:
        print('Error: Invalid method')
        return
    
    graph.render('output', view=True)

if __name__ == '__main__':
    main()