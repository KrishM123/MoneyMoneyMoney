# Market Making Project

## Setup Instructions

1. Create and activate a new conda environment with Python 3.10:
```bash
conda create -n market-making python=3.10
conda activate market-making
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create necessary directories:
```bash
mkdir -p outlook/models outlook/eval_data
```

## Running the Project

1. Activate the conda environment if not already activated:
```bash
conda activate market-making
```

2. Run the main script:
```bash
python outlook/main.py
```

### Command Line Arguments
- `--no-train`: Skip training new models
- `--no-chart`: Skip displaying charts

Example with arguments:
```bash
python outlook/main.py --no-train --no-chart
```

## Project Structure
- `outlook/`: Main project directory
  - `main.py`: Entry point of the application
  - `src/`: Source code for training, inference, and trading
  - `models/`: Trained model files (created during runtime)
  - `eval_data/`: Evaluation data (created during runtime)
- `utils/`: Utility functions for ML and trading operations
