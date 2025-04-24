# Data Analyst Agent

An AI-powered assistant that interprets natural language queries to analyze CSV datasets, providing insights through SQL queries and visualizations.

## Features

- **Natural Language Processing**: Understand and process user queries in plain English.
- **SQL Query Generation**: Automatically convert natural language into SQL queries.
- **Data Visualization**: Generate plots and charts to visualize data insights.
- **Interactive Interface**: User-friendly interface for seamless interaction.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kaushik-holla/Data-Analyst_agent.git
   cd Data-Analyst_agent
2. **Create a Virtual Environment:**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
4. **ADD API KEY:**
    add Groq API Key in .env

## Usage

### Prepare Your Dataset
Place your CSV file in the `data/` directory. Ensure the file is clean and properly formatted.

### Run the Application
   ```bash
      streamlit run main.py
   ```

## Interact with the Agent

Upon running, you'll be prompted to enter a natural language query.

### Examples

- "What is the average age of customers?"
- "Show a bar chart of sales by region."

The agent will:
- Process your query
- Generate the corresponding SQL
- Execute it
- Display the results along with any relevant visualizations

---

## Project Structure

```graphql
Data-Analyst_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Core logic for processing queries
│   ├── data_loader.py    # Functions to load and preprocess data
│   └── visualization.py  # Functions to generate plots
├── data/
│   └── your_dataset.csv  # Place your CSV files here
├── main.py               # Entry point of the application
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
```


---

## Dependencies

Ensure the following Python packages are installed:

- pandas
- numpy
- matplotlib
- seaborn
- sqlalchemy
- langchain
- langchain_groq
- python-dotenv
- langgraph
- streamlit

These are all listed in the `requirements.txt` file.

---

## Configuration

### API Keys

Right now it runs with Opensource models loaded with Groq. 

If you are using any API and want to modify it accrodingly, Set them as environment variables or configure them securely within the application.


## Contributing

Contributions are welcome!  
Please fork the repository and submit a pull request with your enhancements.



   