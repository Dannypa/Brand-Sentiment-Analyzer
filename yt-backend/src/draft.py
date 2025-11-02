import plotly.express as px
import datetime as dt
import pandas as pd

# dates = [dt.datetime(year=2025, month=1, day=1), dt.datetime(year=2025, month=2, day=1)]
# vals1 = [-0.75, 0.25]
# vals2 = [0.75, -0.25]

# df = pd.DataFrame(
#     {"dates": dates, "vals1": vals1, "vals2": vals2}
# )

# fig = px.line(df, x="dates", y=["vals1", "vals2"])
# fig.show()

from charts.time_series import get_timerange
from dateutil.relativedelta import relativedelta
import datetime as dt

def test():
    a = dt.datetime(year=1, month=1, day=1)
    while a < dt.datetime.now():
        print(a)
        # yield a
        a += relativedelta(year=1) 

# for p in test():
    # print(p)

for d in get_timerange():
    print(d + relativedelta(months=12))
    print(d)
