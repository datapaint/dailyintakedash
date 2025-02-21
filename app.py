import dash, os, datetime
import sqlalchemy
from dash import Dash, dcc, html, Input, Output, State, callback
from dash_auth import BasicAuth
from sqlalchemy import create_engine, text, values, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, registry, declarative_base
from sqlalchemy.exc import OperationalError

# Initialize the Dash app
app = dash.Dash(__name__)

# Get the auth environment variables
username = os.environ.get("DASH_AUTH_USER")
password = os.environ.get("DASH_AUTH_PASSWORD")

# Add authentication
auth = BasicAuth(app, {username: password})

# Database connection details from environment variables
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

# Create the database engine and Base
engine = sqlalchemy.create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
Base = declarative_base()
metadata = MetaData()

fiber_table_name = "fiber_intake"

# Intantiate the primary Fiber Class
class Fiber(Base):
    __tablename__ = fiber_table_name

    timestamp = Column(DateTime, primary_key=True)
    fiber = Column(Integer)

    def __init__(self, timestamp, fiber):
        self.timestamp = timestamp
        self.fiber = fiber

# Create a Database and Fiber table if it doesn't exist yet
try:
    engine.begin()
except OperationalErrior as e:
    if "database" + fiber_table_name + "does not exist" in str(e):
        engine.execute(f"CREATE DATABASE {fiber_table_name}")
        firstdbsession.close()
        print(f"Table "{fiber_table_name}" created successfully.")
    else:
        raise e

Base.metadata.create_all(engine)

# Create dashboard layout
app.layout = html.Div([
    html.H1("My Nutrition Dashboard"),

    html.H2("Submit daily estimated grams of fiber intake:"),

    html.Div([
        dcc.Input(id="fiber-input", type="text", placeholder="38..."),
        html.Button("Submit", id="submit-button", n_clicks=0),
        html.Div(id="output-message")
    ])
])

# Create a form submission action
@app.callback(
    Output("output-message", "children"),
    Input("submit-button", "n_clicks"),
    State("fiber-input", "value"),
)
def submit_data(n_clicks, fibertoday):
    if n_clicks > 0:
        if fibertoday:
            try:
                Session = sessionmaker(bind=engine)
                with Session.begin() as connection:
                    newrow = Fiber(datetime.datetime.now(), fibertoday)
                    connection.add(newrow)
                    connection.commit()
                    connection.close()
                    return "Data submitted successfully!"
            except Exception as e:
                return f"Error submitting data: {str(e)}"
        else:
            return "Please fill in how much fiber you ate today."
    return ""

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
