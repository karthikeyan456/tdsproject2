# /// script
# requires-python = ">=3.12"
# dependencies = [
# "pandas",
# "numpy",
# "seaborn",
# "httpx",
# "python-dotenv",
# "chardet"]
# ///

import csv
import sys
import chardet
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import os
import httpx

load_dotenv()
try:
    API_KEY=os.environ['AI_PROXY']
    API_URL="https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
except:
    sys.exit(0)

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read() 
    return chardet.detect(raw_data)['encoding']

def analyze_data(df):
    columns_with_datatypes=df.dtypes
    shape=df.shape
    describe=df.describe()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    numerical_columns=df.select_dtypes(include=['number']).columns.tolist()
    correlation_coeff=df[numerical_columns].corr()
    missing_values = df.isnull().sum()  # Count of missing values in each column
    unique_values = {col: df[col].nunique() for col in df.columns}  # Count of unique values per column
    outliers = {col: df[col][(df[col] > df[col].quantile(0.75) + 1.5 * (df[col].quantile(0.75) - df[col].quantile(0.25))) |
                              (df[col] < df[col].quantile(0.25) - 1.5 * (df[col].quantile(0.75) - df[col].quantile(0.25)))]
                for col in numerical_columns}  # Identify outliers in numerical columns
    # Statistical analysis techniques
    variance = df[numerical_columns].var()  # Variance of numerical columns
    skewness = df[numerical_columns].skew()  # Skewness of numerical columns
    kurtosis = df[numerical_columns].kurt()  # Kurtosis of numerical columns

    return {
        "columns_with_datatypes": columns_with_datatypes,
        "shape": shape,
        "describe": describe,
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "correlation_coeff": correlation_coeff,
        "variance": variance,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "missing_values":missing_values,
        "unique_values":unique_values,
        "outliers":outliers
    }

def generate_readme(analysis):
    """
    Generates a detailed analysis report based on the input analysis dictionary.

    This function constructs a comprehensive prompt using the input dataset analysis and sends it to an external API (e.g., a GPT model) to generate a natural language explanation of the dataset. It includes key elements such as dataset description, handling of missing values, relationships, statistical interpretations, and recommendations for further analysis.

    Args:
        analysis (dict): A dictionary containing the dataset's analysis results. It should have the following keys:
            - 'columns_with_datatypes': A dictionary mapping column names to their data types.
            - 'shape': A tuple representing the dataset's dimensions (rows, columns).
            - 'describe': A dictionary or string containing summary statistics for the dataset.
            - 'categorical_columns': A list of column names that are categorical.
            - 'numerical_columns': A list of column names that are numerical.
            - 'correlation_coeff': A dictionary or table representing correlation coefficients between numerical columns.
            - 'missing_values': A dictionary showing the number of missing values per column.
            - 'unique_values': A dictionary with the count of unique values per column.
            - 'outliers': A dictionary indicating the presence of outliers for numerical columns.
            - 'variance': A dictionary with variance values for numerical columns.
            - 'skewness': A dictionary with skewness values for numerical columns.
            - 'kurtosis': A dictionary with kurtosis values for numerical columns.

    Returns:
        str: A string containing the generated report if the API call is successful.
        str: An error message if the API call fails.

    API Interaction:
        - Sends a POST request to an external API with the generated prompt.
        - The API response is parsed to extract the generated analysis content.

    Error Handling:
        - Handles HTTP errors, request exceptions, and other unexpected errors.
        - Prints an error message for debugging purposes and returns a generic failure message.

    Example Usage:
        analysis = {
            "columns_with_datatypes": {"column1": "int", "column2": "float"},
            "shape": (100, 5),
            "describe": "Statistics summary here",
            "categorical_columns": ["column1"],
            "numerical_columns": ["column2"],
            "correlation_coeff": {"column2": 0.85},
            "missing_values": {"column1": 5, "column2": 0},
            "unique_values": {"column1": 10, "column2": 50},
            "outliers": {"column2": [1.5, 99.8]},
            "variance": {"column2": 0.25},
            "skewness": {"column2": 0.5},
            "kurtosis": {"column2": 3.1},
        }
        report = generate_readme(analysis)
    

    """


    prompt = f"""
    You are a data analysis expert. I have performed an initial analysis of a dataset and obtained the following results. Your task is to interpret this data and provide a detailed analysis. Specifically, I want you to:

    1. **Description of the dataset:** Summarize the key characteristics of the dataset, including the data types, shape, and key statistics.
    2. **Imputing Null Values:** Identify strategies to handle missing values in the dataset based on the provided missing values information.
    3. **Discussing Relationships:** Analyze the relationships between variables using the correlation coefficients and any other relevant metrics.
    4. **Interpretation of Statistical Results:** Explain the significance of the variance, skewness, and kurtosis for the numerical columns.
    5. **Recommendations:** Based on your findings, suggest next steps for data cleaning, transformation, or further analysis.

    Here is the data analysis summary:

    - **Columns and Data Types:**  
      ```
      {analysis['columns_with_datatypes']}
      ```

    - **Dataset Shape:**  
      ```
      {analysis['shape']}
      ```

    - **Summary Statistics:**  
      ```
      {analysis['describe']}
      ```

    - **Categorical Columns:**  
      ```
      {', '.join(analysis['categorical_columns'])}
      ```

    - **Numerical Columns:**  
      ```
      {', '.join(analysis['numerical_columns'])}
      ```

    - **Correlation Coefficients:**  
      ```
      {analysis['correlation_coeff']}
      ```
    
    **Missing Values (per column):**  
      ```
      {analysis['missing_values']}
      ```

    - **Unique Values (per column):**  
      ```
      {analysis['unique_values']}
      ```
   

   

    - **Outliers (numerical columns):**  
      ```
      {analysis['outliers']}
      ```

    - **Variance (numerical columns):**  
      ```
      {analysis['variance']}
      ```

    - **Skewness (numerical columns):**  
      ```
      {analysis['skewness']}
      ```

    - **Kurtosis (numerical columns):**  
      ```
      {analysis['kurtosis']}
      ```

    Please provide a comprehensive analysis addressing all the points above.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    prompt = prompt
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = httpx.post(API_URL, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return "Narrative generation failed due to an error."

def find_columns_to_plot(analysis):
    """
    Recommends columns for visualization plots based on dataset analysis.

    This function constructs a prompt using the provided dataset analysis summary and sends it to an external API (e.g., a GPT model). It requests recommendations for three specific plots from Scatter Plot, Line Plot, Bar Plot, Histogram, and Box Plot, identifying the best columns for visualization. The response is formatted as a nested Python list.

    Args:
        analysis (dict): A dictionary containing the dataset's analysis results. It should have the following keys:
            - 'columns_with_datatypes': A dictionary mapping column names to their data types.
            - 'shape': A tuple representing the dataset's dimensions (rows, columns).
            - 'describe': A dictionary or string containing summary statistics for the dataset.
            - 'categorical_columns': A list of column names that are categorical.
            - 'numerical_columns': A list of column names that are numerical.
            - 'correlation_coeff': A dictionary or table representing correlation coefficients between numerical columns.
            - 'missing_values': A dictionary showing the number of missing values per column.
            - 'outliers': A dictionary indicating the presence of outliers for numerical columns.

    Returns:
        list: A nested Python list containing recommendations for three plots in the format:
              [
                  ['Plot 1 Type', 'X Axis Column', 'Y Axis Column', 'Plot Title'],
                  ['Plot 2 Type', 'X Axis Column', 'Y Axis Column', 'Plot Title'],
                  ['Plot 3 Type', 'X Axis Column', 'Y Axis Column', 'Plot Title']
              ]
        str: An error message if the API call fails.

    API Interaction:
        - Sends a POST request to an external API with the constructed prompt.
        - Parses the response to extract the list of recommended plots.

    Error Handling:
        - Handles HTTP errors, request exceptions, and other unexpected errors.
        - Prints error messages for debugging purposes and returns a generic failure message.

    Example Usage:
        analysis = {
            "columns_with_datatypes": {"column1": "int", "column2": "float"},
            "shape": (100, 5),
            "describe": "Statistics summary here",
            "categorical_columns": ["column1"],
            "numerical_columns": ["column2"],
            "correlation_coeff": {"column2": 0.85},
            "missing_values": {"column1": 5, "column2": 0},
            "outliers": {"column2": [1.5, 99.8]},
        }
        plot_recommendations = find_columns_to_plot(analysis)
        plot_list = eval(plot_recommendations)  # Converts the string output to a Python list
    """
    prompt = f"""
    You are a data visualization expert. Based on the following dataset analysis summary, your task is to recommend configurations for six specific plot types: Scatter Plot, Line Plot, Histogram (with KDE), Box Plot, Bar Plot, and Heatmap. Provide your recommendations as a Python dictionary in the following format:


    Use the dataset analysis summary below to guide your recommendations:

    - **Columns and Data Types:**  
      ```
      {analysis['columns_with_datatypes']}
      ```

    - **Dataset Shape:**  
      ```
      {analysis['shape']}
      ```

    - **Summary Statistics:**  
      ```
      {analysis['describe']}
      ```

    - **Categorical Columns:**  
      ```
      {', '.join(analysis['categorical_columns'])}
      ```

    - **Numerical Columns:**  
      ```
      {', '.join(analysis['numerical_columns'])}
      ```

    - **Correlation Coefficients:**  
      ```
      {analysis['correlation_coeff']}
      ```

    - **Missing Values (per column):**  
      ```
      {analysis['missing_values']}
      ```

    - **Outliers (numerical columns):**  
      ```
      {analysis['outliers']}
      ```

    The plot Type Can be in ['Scatter Plot','Line Plot','Bar Plot','Histogram','Box Plot']. Give the top 3 plots suitable for this dataset. 
    The response must be a nested list [['Plot 1 Type','X Axis Column','Y Axis Column','Plot Title'],['Plot 2 Type','X Axis Column','Y Axis Column','Plot Title'], ['Plot 3 Type','X Axis Column','Y Axis Column','Plot Title']].
    Return only the list. No need to explain. Return in such a way that i have to convert into a python list using eval.
    """

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = httpx.post(API_URL, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        #print(response.json())
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return "Plot recommendation generation failed due to an error."


import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def create_and_save_plot(input_array,i):
    """
    Generate a plot based on the input array and save it as a 150x150 pixel image.

    Parameters:
        input_array (list): A list containing plot type, x-axis column, y-axis column, and title.

    Output:
        Saves a 150x150 pixel .png image of the plot.
    """
    # Extract plot parameters
    plot_type, x_col, y_col, title = input_array


    # Initialize the plot
    plt.figure(figsize=(2, 2))  # Set figure size in inches to approximately match 150x150 pixels

    # Generate the specified plot
    if plot_type.lower() == 'scatter plot':
        sns.scatterplot(data=df, x=x_col, y=y_col)
    elif plot_type.lower() == 'box plot':
        sns.boxplot(data=df, x=x_col, y=None)
    elif plot_type.lower() == 'histogram':
        sns.histplot(data=x_col, kde=True)
    elif plot_type.lower() == 'line plot':
        sns.lineplot(data=df, x=x_col, y=y_col)
    elif plot_type.lower() == 'bar plot':
        sns.barplot(data=df, x=x_col, y=y_col)
    else:
        raise ValueError("Unsupported plot type. Choose from: scatter plot, box plot, histogram, line plot, bar plot.")

    # Add title and labels
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    # Save the plot as a 150x150 pixel image
    plt.savefig('plot_'+str(i)+'.png', dpi=150 / 2, bbox_inches='tight')  # dpi is adjusted for approximate sizing
    plt.close()


    

if len(sys.argv) < 2:
    print("Usage: python script.py <path_to_csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]

try:
    # Detect encoding
    encoding = detect_encoding(csv_file)
    if not encoding:
        print("Could not detect file encoding. Using default 'utf-8'.")
        encoding = 'utf-8'
    
    
    
    
    """Reading the data into a Pandas Dataframe"""
    df=pd.read_csv(csv_file,encoding=encoding)

    """Generate the Descriptive Analysis of the data to be passed into the LLM"""
    analysis=analyze_data(df)
    """Generate the Narrative of the data to be and store it in a Readme.MD file"""
    narrative=generate_readme(analysis)
    f=open('README.md','w')
    f.write(narrative)
    f.close()

    #print(analysis)
    columns_to_plot=eval(find_columns_to_plot(analysis))
    for i in range(3):
        create_and_save_plot(columns_to_plot[i],i)


except FileNotFoundError:
    print(f"File '{csv_file}' not found.")
except UnicodeDecodeError:
    print(f"Error decoding file '{csv_file}'. Ensure the correct encoding.")
except Exception as e:
    print(f"An error occurred: {e}")
