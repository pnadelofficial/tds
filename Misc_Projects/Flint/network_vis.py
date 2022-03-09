import networkx as nx
import plotly.graph_objects as go
import dateutil
import pandas as pd
pd.set_option('display.max_rows', 500)
import re
import pytz
import numpy as np
from text_to_df import createDF

## This function should clean all From and To cells to: Last name, First name.
## There are A LOT of inconsistencies in this format.
def cleanEntry(entry):
  if '\n' in entry:
  ### For any name cell that has a new line we can just take the first line, which should just have the name.  
    entry = entry.split('\n')[0]
    entry = re.sub(r'(?<=\<)(.*)(?=\>)', '' ,entry).replace("<", '').replace(">", '').replace('"', '').replace('|', '').replace("'", '').strip()
    ### Removing anything in between < >, usually emails 
    entry = re.sub(r'(?<=\()(.*)(?=\))', '', entry).replace("(", '').replace(")", '')
    ### Removing anything in between ( ), usually emails 
    entry = re.sub(r'(?<=\[)(.*)(?=\])', '', entry).replace("[", '').replace("]", '')
    ### Removing anything in between [ ], usually emails 
    if (',' not in entry) and (len(entry.split(' ')) > 1):
      entry = f"{entry.split(' ')[1]}" + ', ' + f"{entry.split(' ')[0]}"
    if (',' in entry) and (len(entry.split(' ')) > 2):
      entry = re.sub(r'(?!(.*)\s).', '', entry)
    return entry
  else:
    entry = re.sub(r'(?<=\<)(.*)(?=\>)', '' ,entry).replace("<", '').replace(">", '').replace('"', '').replace('|', '').replace("'", '').strip()
    entry = re.sub(r'(?<=\()(.*)(?=\))', '', entry).replace("(", '').replace(")", '')
    entry = re.sub(r'(?<=\[)(.*)(?=\])', '', entry).replace("[", '').replace("]", '')
    if (',' not in entry) and (len(entry.split(' ')) > 1):
      entry = f"{entry.split(' ')[1]}" + ', ' + f"{entry.split(' ')[0]}"
    if (',' in entry) and (len(entry.split(' ')) > 2):
      entry = re.sub(r'(?!(.*)\s).', '', entry)
    return entry

def formatDates(entry):
  ### Trying to turn Sent strings into datetime objects
  ### Doesn't work for poorly formatted strings, so much use try/except
  try: 
    if '\n' in entry:
      entry = entry.split('\n')[0]
      entry = dateutil.parser.parse(entry)
      return entry.replace(tzinfo=pytz.UTC)
    else:
      entry = dateutil.parser.parse(entry)
      return entry.replace(tzinfo=pytz.UTC)
  except dateutil.parser.ParserError:
    return entry

## Create email_df from text_to_df.py
file_path = 'data/Staff_*_djvu.txt'
email_df = createDF(file_path)

## More cleaning
from_to = email_df[['From', 'To', 'Sent']].replace('', np.nan).replace(' ', np.nan).dropna()
### Dropping empty cells
from_to['To'] = from_to['To'].str.split(';')
### Splitting To lines
from_to = from_to.explode(['To']).reset_index(drop=True)
### Exploding the DF for the split lines

## Applying function from above
from_to['From'] = from_to['From'].apply(cleanEntry)
from_to['To'] = from_to['To'].apply(cleanEntry)
from_to['Sent'] = from_to['Sent'].apply(formatDates)

## Creating weight with size()
from_to = from_to.groupby(["From", "To", "Sent"]).size().reset_index(name="Weight")
from_to

## Creating network
G = nx.from_pandas_edgelist(from_to, 'From', 'To', edge_attr=True)
pos = nx.drawing.layout.spring_layout(G)
nx.set_node_attributes(G, pos, 'pos')

## Plotly for network visualization.
## Much of this is taken from: https://plotly.com/python/network-graphs/.
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='Electric',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append(f'{str(adjacencies[0])} has '+str(len(adjacencies[1]))+' connection(s)')

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
fig.show()