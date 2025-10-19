import plotly.express as px


# x and y given as array_like objects
fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
print(fig.to_json())

# import plotly.io as pio
# print(pio.renderers)
