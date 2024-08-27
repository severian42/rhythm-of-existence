# Life Tracking System: Rhythm of Existence

## Overview

The Life Tracking System is a comprehensive application inspired by Rob Dyrdek's "Rhythm of Existence" philosophy. It helps users monitor and optimize various aspects of their lives, including work, health, personal life, and sleep. This system allows for daily activity logging, tracking of qualitative and quantitative metrics, goal setting, and progress analysis over time.

## Rob Dyrdek's Rhythm of Existence

Rob Dyrdek's Rhythm of Existence philosophy emphasizes:

1. **Balance**: Maintaining equilibrium between work, life, and health.
2. **Intentionality**: Being purposeful in how you spend your time.
3. **Consistency**: Establishing and maintaining routines.
4. **Self-reflection**: Regular evaluation of progress and adjustments.
5. **Goal-setting**: Setting and working towards clear objectives.

This application embodies these principles by:

- Categorizing activities into Work, Life, Health, and Sleep.
- Providing daily checklists for consistent routines.
- Offering weekly and monthly analyses for self-reflection.
- Incorporating a goal-setting and tracking system.
- Allowing customization to fit individual lifestyles and priorities.

## Features

- Daily activity logging with customizable categories
- Qualitative and quantitative metric tracking
- Weekly and monthly analysis with visualizations
- Goal setting and progress monitoring
- Customizable user settings
- Interactive dashboards for data visualization
- Daily checklists for routine management

## Live Demo

You can try out the Life Tracking System without installation through our Hugging Face Space demo:

[Life Tracking System Demo](https://severian-rhythm-of-existence.hf.space)

This demo allows you to explore the features and functionality of the application in a web browser. Keep in mind that data in the demo is not persistent and is reset periodically.


## Installation

1. Clone the repository:
   ```
   git clone https://github.com/severian42/rhythm-of-existence 
   cd rhythm-of-existence 
   ```

2. Create a virtual environment (optional but recommended):
   ```
   conda create -n roe
   conda activate roe
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://localhost:7860`.

3. Use the different tabs to:
   - Log daily activities
   - Track metrics
   - View weekly and monthly analyses
   - Set and manage goals
   - Customize your settings
   - Manage your daily checklist

## Customization

### User Profiles

- Add new user profiles through the UI.
- Delete existing profiles as needed.

### Categories and Subcategories

1. Navigate to the Settings tab.
2. Choose a preset template or create a custom one.
3. Add, remove, or modify categories and subcategories.

### Metrics

To add or modify metrics:

1. Open `app.py`.
2. Locate the `create_tables()` function.
3. Modify the SQL statements for `qualitative_metrics` or `quantitative_metrics` tables.
4. Update the corresponding UI elements in the Gradio interface.

### Daily Checklist

Customize the daily checklist items:

1. Find the `checklist_items` list in the "Daily Checklist" tab section.
2. Add, remove, or modify the `gr.Checkbox()` items.

### Analysis and Visualizations

Modify analysis functions in `app.py`:

- `analyze_weekly_data()`
- `analyze_monthly_data()`
- `update_analysis()`

Adjust the Plotly charts to change visualization styles or add new charts.

### Goal Setting

Customize goal categories:

1. Locate the `goal_category` dropdown in the Goals tab section.
2. Modify the `choices` parameter to add or remove categories.

## Advanced Customization

### Database Schema

The SQLite database schema is defined in the `create_tables()` function. Modify this function to add new tables or alter existing ones.

### UI Layout

The Gradio interface is built using nested `gr.Row()` and `gr.Column()` components. Adjust these to modify the layout.

### Styling

Custom CSS is applied through the `custom_css` variable. Modify this to change the application's appearance.

## Contributing

Contributions to improve the Life Tracking System are welcome. Please submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Rob Dyrdek's "Rhythm of Existence" philosophy
- Built with [Gradio](https://www.gradio.app/), [Plotly](https://plotly.com/), and [Pandas](https://pandas.pydata.org/)
