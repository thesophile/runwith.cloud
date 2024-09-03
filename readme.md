# CloudPy

Run Python libraries online with ease
 
> ## Key Features
> 
> - No need to install libraries or manage dependencies.
> - Continue your work seamlessly across different devices.
> - Run in mobile phones and tablets with ease.
>   
> Visit [cloudpy.online](https://cloudpy.online) to use the website.
 


## Getting Started

### Prerequisites

- **Python:** 3.11 (tested), but other versions may work.
- **Virtualenv** (optional but recommended)
- **Git**
- **pip**: For installing Python packages.

 

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/thesophile/CloudPy.git 
   cd CloudPy
   ```
2. **Create a Virtual Environment:**

    ```
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```
    pip install -r requirements.txt
    ```
    
4. **Run Migrations:**

    ```
    python manage.py migrate
    ```
    
5. **Start the Development Server:**

    ```
    python manage.py runserver
    ```


