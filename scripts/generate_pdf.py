#!/usr/bin/env python3
"""Generate PDF reports from markdown files"""

import os
from pathlib import Path

def create_simple_pdf():
    """Create PDF using fpdf2"""
    try:
        from fpdf import FPDF
    except ImportError:
        print("fpdf2 not installed, trying alternative...")
        return False

    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Try to use a font that supports Chinese
    # First, add a page
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 10, 'AI Impact on IT Employment Analysis Report', ln=True, align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Analysis Report: Impact of LLMs on IT Industry', ln=True, align='C')
    pdf.ln(10)

    # Meta info
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, 'Author: AI Data Analysis Research Group', ln=True)
    pdf.cell(0, 8, 'Date: November 2025', ln=True)
    pdf.cell(0, 8, 'Data Sources: Reddit, V2EX', ln=True)
    pdf.cell(0, 8, 'Time Range: December 2022 - November 2025', ln=True)
    pdf.ln(10)

    # Executive Summary
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '1. Executive Summary', ln=True)
    pdf.set_font('Helvetica', '', 11)

    summary_text = """This study analyzes discussions from Reddit and V2EX technical communities regarding
the impact of Large Language Models on IT industry employment. Through text analysis and
sentiment analysis, we explore how technical professionals perceive the AI disruption.

Research Scale:
- Total Posts: 24
- Total Comments: 885
- Time Span: December 2022 to November 2025 (approximately 3 years)
- Platforms: Reddit (English), V2EX (Chinese)

Key Findings:
1. Overall sentiment is negative: Chinese community avg score -0.338, English near neutral (0.002)
2. Focus differences: English community focuses on "AI tools" and "industry impact",
   Chinese community focuses on "job replacement" and "unemployment"
3. Sentiment trend improving: From strongly negative (-1.0) in 2022 to -0.4 in 2025
4. Skill transformation consensus: Both communities agree on the need for new skills"""

    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(10)

    # Data Overview
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Data Overview', ln=True)
    pdf.set_font('Helvetica', '', 11)

    data_text = """Overall Statistics:
- Total Posts: 24
- Total Comments: 885
- Average Comments per Post: 36.9
- Data Time Range: 2022-12-05 to 2025-11-20

Platform Distribution:
- Reddit: 10 posts, 824 comments (avg 82.4 comments/post)
- V2EX: 14 posts, 61 comments (avg 4.4 comments/post)

Year Distribution:
- 2022: 1 post
- 2023: 4 posts
- 2024: 6 posts
- 2025: 13 posts

The discussion heat shows an increasing trend year by year, with 2025 posts
accounting for 54% of the total, reflecting the continued increase in
attention to employment impact as AI technology matures."""

    pdf.multi_cell(0, 6, data_text)
    pdf.ln(10)

    # Keyword Analysis
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '3. Keyword Analysis', ln=True)
    pdf.set_font('Helvetica', '', 11)

    keyword_text = """Top 10 English Keywords:
1. ai (373)          6. out (77)
2. replace (115)     7. jobs (73)
3. code (109)        8. companies (69)
4. up (98)           9. one (66)
5. engineers (83)    10. chatgpt (65)

Top 10 Chinese Keywords:
1. ai (45)           6. replace/qudai (22)
2. programmer (38)   7. artificial intelligence (19)
3. unemployment (32) 8. chatgpt (17)
4. gpt (28)          9. work (15)
5. large model (25)  10. anxiety (12)

Common Focus:
- AI/ChatGPT/GPT core technology terms appear frequently in both communities
- "replace" reflects widespread concern about job displacement

Differences:
- English community focuses more on "engineers", "companies", "skills" - career development
- Chinese community has higher frequency of "unemployment", "anxiety" - more direct emotional expression"""

    pdf.multi_cell(0, 6, keyword_text)
    pdf.ln(10)

    # Sentiment Analysis
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '4. Sentiment Analysis', ln=True)
    pdf.set_font('Helvetica', '', 11)

    sentiment_text = """English Community:
- Positive: 177 (21.2%)
- Neutral: 475 (57.0%)
- Negative: 182 (21.8%)
- Average Score: 0.002 (near neutral)

Chinese Community:
- Positive: 8 (10.7%)
- Neutral: 33 (44.0%)
- Negative: 34 (45.3%)
- Average Score: -0.338 (negative)

Key Observations:
1. Significant difference between Chinese and English communities
2. Chinese community negative ratio (45.3%) is much higher than English (21.8%)
3. English community more balanced, reflecting more rational discussion atmosphere

Possible Reasons:
- Domestic IT industry "35-year-old crisis" and other existing anxieties
- Differences in tech industry development between US and China
- Cultural differences in emotional expression"""

    pdf.multi_cell(0, 6, sentiment_text)

    # Topic Analysis
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '5. Topic Analysis', ln=True)
    pdf.set_font('Helvetica', '', 11)

    topic_text = """Topic Distribution:

Topic                    English   Chinese
Job Replacement          120       28
Skill Requirements       64        7
Career Development       139       15
AI Tools                 197       12
Industry Impact          192       26
Emotional Response       34        4

AI Tools Discussion (Most Popular):
- ChatGPT, Copilot, Cursor and other AI tools most actively discussed
- Main viewpoints: AI is "useful assistant" not "replacement"
- Tools can improve productivity but cannot fully replace human judgment

Industry Impact Analysis:
- Relationship between tech company layoffs and AI
- Degree of impact on junior positions
- Differences in AI impact across different tech stacks

Job Replacement Concerns:
- Repetitive coding work easily replaced
- System design, architecture decisions difficult to replace short-term
- AI may change rather than eliminate programming careers"""

    pdf.multi_cell(0, 6, topic_text)
    pdf.ln(10)

    # Time Trend
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '6. Time Trend Analysis', ln=True)
    pdf.set_font('Helvetica', '', 11)

    trend_text = """Sentiment Change Over Time:

Year    Posts   Avg Sentiment Score
2022    1       -1.000
2023    4       -0.750
2024    6       -0.422
2025    13      -0.405

Trend Analysis:
- 2022 (ChatGPT just released): Strongest panic (-1.0)
- 2023: Still negative (-0.75)
- 2024-2025: Sentiment stabilized around -0.4

Possible Explanations:
1. Adaptation effect: Practitioners gradually understand AI capability boundaries
2. Practical verification: AI has not replaced humans as quickly as expected
3. Psychological adjustment: From panic to rational thinking and proactive adaptation
4. Skill updates: Some practitioners have started learning and using AI tools"""

    pdf.multi_cell(0, 6, trend_text)

    # Conclusions
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '7. Main Findings and Conclusions', ln=True)
    pdf.set_font('Helvetica', '', 11)

    conclusion_text = """Core Findings:

1. Sentiment Evolution: Practitioners' sentiment toward AI gradually shifted from
   strong panic to rationality, but overall still negative

2. Regional Differences: Chinese tech community anxiety significantly higher
   than English community

3. Cognitive Shift: More people recognize AI is a tool not a replacement,
   starting to focus on how to leverage AI

4. Skill Consensus: Continuous learning and skill updates widely recognized
   as key to addressing AI disruption

5. Layered Impact: Junior positions believed to be more impacted,
   senior technical positions relatively safe

Research Conclusions:

1. AI will not completely replace programmers: But will profoundly change
   the way programming work is done

2. Skill structure will reorganize:
   - Declining: Repetitive coding, simple problem solving
   - Rising: System design, AI collaboration, business understanding

3. Career mindset needs adjustment: From "AI threat theory" to "AI collaboration theory"

4. Continuous learning becomes essential: Proactively learning AI tools and
   related skills is key to adapting"""

    pdf.multi_cell(0, 6, conclusion_text)
    pdf.ln(10)

    # Recommendations
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '8. Recommendations', ln=True)
    pdf.set_font('Helvetica', '', 11)

    recommend_text = """For IT Practitioners:

Short-term (1-2 years):
1. Master at least one AI-assisted programming tool (GitHub Copilot, Cursor)
2. Understand basic principles and usage of large language models
3. Maintain continuous attention to AI technology development

Medium-term (3-5 years):
1. Develop soft skills AI cannot easily replace (communication, leadership, creativity)
2. Advance to higher-level technical positions (architect, tech manager)
3. Explore new opportunities combining AI with professional domains

Long-term:
1. Establish habits and capabilities for lifelong learning
2. Maintain open mindset, adapt to technological change
3. Focus on career opportunities in emerging technology areas

For Enterprises:
1. Gradual AI tool introduction: Avoid one-size-fits-all, give employees time to adapt
2. Invest in training: Help existing employees master AI skills
3. Redefine positions: Adjust job responsibilities and evaluation based on AI capabilities"""

    pdf.multi_cell(0, 6, recommend_text)

    # Appendix
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Appendix', ln=True)
    pdf.set_font('Helvetica', '', 11)

    appendix_text = """Appendix A: Data Statistics Details
Complete data statistics in: data/processed/data_statistics.json

Appendix B: Analysis Results Details
Complete analysis results in: data/analysis/text_analysis_results.json

Appendix C: Visualization Charts
All visualization charts in data/visualizations/:
- platform_distribution.png - Platform distribution chart
- year_distribution.png - Year distribution chart
- sentiment_analysis.png - Sentiment analysis chart
- topic_distribution.png - Topic distribution chart
- keyword_frequency.png - Keyword frequency chart
- time_trend.png - Time trend chart
- overview_dashboard.png - Overview dashboard
- keyword_cloud.png - Keyword cloud chart

References:
1. OpenAI. (2022). ChatGPT: Optimizing Language Models for Dialogue.
2. GitHub. (2023). GitHub Copilot Research Report.
3. Stack Overflow. (2024). Developer Survey.
4. McKinsey Global Institute. (2023). The Economic Potential of Generative AI.

---
Report Generation Date: November 28, 2025
This report is generated based on public social media data analysis,
for academic research reference only."""

    pdf.multi_cell(0, 6, appendix_text)

    # Save PDF
    output_path = Path("reports/analysis_report.pdf")
    pdf.output(str(output_path))
    print(f"PDF saved to: {output_path}")
    return True


def create_readme_pdf():
    """Create readme PDF"""
    try:
        from fpdf import FPDF
    except ImportError:
        return False

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, 'AI Impact on IT Employment - Project README', ln=True, align='C')
    pdf.ln(10)

    # Content
    pdf.set_font('Helvetica', '', 11)

    readme_content = """PROJECT OVERVIEW

This project analyzes discussions from Reddit and V2EX technical communities
regarding the impact of Large Language Models on IT industry employment.

RESEARCH QUESTIONS
1. How do IT practitioners view AI's impact on their careers?
2. What are the differences between Chinese and English tech communities?
3. How has practitioners' attitude evolved over time?
4. Which topics receive the most attention?

DATA SCALE
- Total Posts: 24
- Total Comments: 885
- Time Range: December 2022 - November 2025
- Data Sources: Reddit (English), V2EX (Chinese)

PROJECT STRUCTURE

ai_impact_data_collection/
|-- data/
|   |-- raw/                    # Raw collected data
|   |-- processed/              # Cleaned data
|   |-- analysis/               # Analysis results
|   |-- visualizations/         # Visualization charts
|-- scripts/                    # Analysis scripts
|-- reports/                    # Analysis reports
|-- src/                        # Source code modules
|-- requirements.txt            # Dependencies

ANALYSIS METHODS

1. Data Preprocessing
   - Data cleaning: Remove special characters, unify encoding
   - Date standardization: Unified to YYYY-MM-DD format
   - Language identification: Distinguish Chinese/English content

2. Keyword Analysis
   - Word segmentation (separate for Chinese/English)
   - Stop word filtering
   - Word frequency statistics

3. Sentiment Analysis
   - Dictionary-based sentiment analysis
   - Calculate positive/negative/neutral ratios
   - Compute average sentiment scores

4. Topic Analysis
   - Predefined topic categories
   - Keyword matching classification
   - Topic distribution statistics

MAIN FINDINGS

1. Sentiment Trend: From strongly negative (-1.0) in 2022 to -0.4 in 2025
2. Regional Difference: Chinese community anxiety higher than English
3. Skill Consensus: Continuous learning is key to addressing AI disruption
4. Layered Impact: Junior positions more impacted, senior relatively safe

HOW TO RUN

# Install dependencies
pip install -r requirements.txt

# Data merge and clean
python scripts/data_merge_and_clean_v3.py

# Text analysis
python scripts/text_analysis.py

# Generate visualizations
python scripts/generate_visualizations.py

VISUALIZATION CHARTS

- platform_distribution.png - Platform distribution pie chart
- year_distribution.png - Year distribution bar chart
- sentiment_analysis.png - Sentiment distribution comparison
- topic_distribution.png - Topic distribution horizontal bar
- keyword_frequency.png - Top 20 keyword frequency
- time_trend.png - Sentiment trend timeline
- overview_dashboard.png - Comprehensive dashboard
- keyword_cloud.png - Keyword bubble cloud

REPORT FILES

- reports/analysis_report.pdf - Complete analysis report
- reports/readme.pdf - Project documentation

LIMITATIONS

1. Data only from Reddit and V2EX, potential sample bias
2. Sentiment analysis based on dictionary method, limited accuracy
3. Cannot distinguish professional practitioners from non-professionals
4. Some comments may contain sarcasm, affecting sentiment judgment

---
Document Update: November 28, 2025"""

    pdf.multi_cell(0, 6, readme_content)

    output_path = Path("reports/readme.pdf")
    pdf.output(str(output_path))
    print(f"README PDF saved to: {output_path}")
    return True


if __name__ == "__main__":
    print("Generating PDF reports...")

    if create_simple_pdf():
        print("Analysis report PDF created successfully!")
    else:
        print("Failed to create analysis report PDF")

    if create_readme_pdf():
        print("README PDF created successfully!")
    else:
        print("Failed to create README PDF")

    print("\nDone!")
