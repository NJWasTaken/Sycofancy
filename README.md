# LLM Sycophancy Evaluator

A Flask-based interactive application that demonstrates how language models exhibit sycophancy—the tendency to agree with users and capitulate to social pressure. Have real-time conversations with simulated models while tracking capitulation patterns and sycophancy scores.

## Key Features

- **5 Interactive Conversation Tests** with real-time model responses:
  - **Positional Sycophancy:** Test if models agree more with early vs. late arguments
  - **Emotional Sycophancy:** See if confident assertions trigger agreement
  - **Authority-Primed:** Observe deference when users claim expertise
  - **Iterative vs Genuine:** Determine if models change minds based on argument quality or mere insistence
  - **Genuine Updating:** Watch how models respond to substantive technical arguments

- **Conversation Memory & Context:** Models maintain conversation history and exhibit escalating capitulation patterns

- **Jailbreak Safeguards:** Built-in protection against prompt injection attempts—input validation prevents users from manipulating the test by trying to change instructions

- **Real-Time Sycophancy Scoring:** Each model response is scored 0-100, with badges showing Resistant, Moderate, or High capitulation levels

- **Comparative Dashboard:** Compare GPT-4, Claude, Llama, and GPT-3.5 across all test categories with interactive charts

- **Beautiful Modern UI:** Clean, professional design with smooth animations and responsive layout

## Project Structure

```
├── app.py                 # Flask application and routes
├── lib/
│   └── mock_data.py      # Mock test scenarios and model responses
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page with test overview
│   ├── test.html         # Individual test page template
│   └── dashboard.html    # Comparative dashboard with charts
├── static/
│   ├── style.css         # Tailored CSS styling
│   └── script.js         # Client-side JavaScript
└── requirements.txt      # Python dependencies
```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   Navigate to `http://localhost:5000`

## How to Use

1. **Home Page:** Browse the 5 test types and learn what each demonstrates
2. **Start a Test:** Click any test card to begin an interactive conversation
3. **Select a Model:** Choose which model (GPT-4, Claude, Llama, or GPT-3.5) to test
4. **Have a Conversation:**
   - Type messages to the model and watch it respond in real-time
   - The system maintains conversation history, so models remember previous exchanges
   - Watch the sycophancy score update after each response (0-100, higher = more capitulation)
   - Try different argument styles: confident assertions, appeals to authority, emotional pressure, etc.
   - Test genuine arguments vs. fake ones to see if the model discriminates
5. **Monitor Statistics:** View turn count, average sycophancy score, and model resistance status
6. **Compare Models:** Visit the Dashboard to see aggregated stats across all models and tests

## Safeguards

The system actively prevents jailbreak attempts:
- Blocks input containing keywords like "ignore," "forget," "system prompt," etc.
- Enforces maximum conversation length (20 turns per session)
- Limits input to 500 characters
- Restricts sensitive topic discussions

If you try to change the test instructions or trick the system, you'll get an error message.

## Understanding Sycophancy Scores

- **0-20:** Model is very resistant to capitulation
- **20-40:** Model shows some tendency to agree
- **40-60:** Model frequently capitulates
- **60-100:** Model readily agrees with users regardless of merit

## Mock Data

The application uses simulated responses rather than real API calls. To modify test scenarios or model responses, edit `lib/mock_data.py`. The structure includes:

- Test metadata (title, description, scenario)
- Model responses for each test
- Capitulation indicators (True/False)
- Sycophancy scores
- Analysis explanations

## Customization

### Add a New Test
1. Add a new entry to `TESTS` dict in `lib/mock_data.py`
2. Include responses for all 4 models
3. The app will automatically pick it up

### Modify Styling
Edit `static/style.css` to change colors, fonts, or layout. Key color variables:
- `--primary-blue`: Main accent color
- `--success-green`: Resistant responses
- `--danger-red`: Capitulated responses

### Add More Models
1. Add model name to `MODELS` list in `lib/mock_data.py`
2. Add responses for the new model in each test
3. The dashboard will automatically update

## Technical Stack

- **Backend:** Flask (Python web framework)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js for dashboard visualizations
- **Styling:** Custom CSS with responsive design

## Notes

- All responses are simulated/mocked for demonstration purposes
- The sycophancy scores are designed to illustrate relative differences between models
- This demo is for educational and research purposes to understand LLM behavior patterns
