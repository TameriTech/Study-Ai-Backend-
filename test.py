import json
from utils.open_router import ask_openrouter

# Sample quiz configuration
quiz_data = {
    "level_of_difficulty": "beginner",
    "quiz_type": "multiple choice",
    "number_of_questions": 3,
    "quiz_instruction": "Include only questions based on reporting requirements and deadlines."
}

# Full original text
course = {
    "original_text": """
Beneficial Ownership Information Report
Filing Instructions
Financial Crimes Enforcement Network
U.S. Department of the Treasury
Version 1.0 January 2024
Beneficial Ownership Information Reporting Filing Instructions 
January 2024 - Version 1.0

Table of Contents
I. Who, What, When of Beneficial Ownership Information Reporting Requirements
II. Where to Report Beneficial Ownership Information
III. How to Report Beneficial Ownership Information
a. Recommendations for Successful Filings
b. Item Instructions

Disclaimer: These filing instructions are explanatory only and do not supplement or modify any 
obligations imposed by statute or regulation. FinCEN may also revise these filing instructions to 
clarify or update content. For additional and latest information, consult www.fincen.gov/boi.

I. Who, What, When of Beneficial Ownership Information Reporting Requirements
The Corporate Transparency Act requires certain types of U.S. and foreign entities to report 
beneficial ownership information to the Financial Crimes Enforcement Network (FinCEN), a 
bureau of the U.S. Department of the Treasury. Beneficial ownership information is information 
about the entity, its beneficial owners, and in certain cases its company applicants. Beneficial 
ownership information is reported to FinCEN through Beneficial Ownership Information Reports 
(BOIRs).

FinCEN’s website includes guidance about the beneficial ownership information reporting 
requirements on its beneficial ownership information webpage. FinCEN’s Small Entity 
Compliance Guide explains who must report, what they must report, and when they must 
report. The Guide includes interactive flowcharts, checklists, and other aids to help determine 
whether an entity needs to file a BOIR with FinCEN, and if so, how to comply with the reporting 
requirements. More information on where to look in the Small Entity Compliance Guide is 
provided below.

WHO
An entity is required to report beneficial ownership information if it is a “reporting 
company” and does not qualify for an exemption. Chapter 1 of FinCEN’s Small Entity 
Compliance Guide may assist in determining whether an entity qualifies for an exemption.

WHAT
Beneficial ownership information is information about an entity, its beneficial owners, 
and, in certain cases, its company applicants. The person submitting beneficial 
ownership information to FinCEN must certify that the information is true, correct, and 
complete. The specific information required is described in these instructions and 
in Chapter 4 of FinCEN’s Small Entity Compliance Guide. To learn more about how 
to identify beneficial owners, review Chapter 2 of FinCEN’s Small Entity Compliance 
Guide.

WHEN
FinCEN will begin accepting BOIRs electronically through its secure filing system January 
1, 2024. FinCEN will not accept BOIRs prior to January 1, 2024.  

If a reporting company already exists as of January 1, 2024, it must file its initial BOIR by 
January 1, 2025. If a reporting company is created or registered to do business in the 
United States on or after January 1, 2024 and before January 1, 2025, it must file its initial 
BOIR within 90 days after receiving actual or public notice that its creation or registration 
is effective. If a reporting company is created or registered to do business in the United 
States after January 1, 2025, then it must file its initial BOIR within 30 days after receiving 
actual or public notice that its creation or registration is effective.  

If there is any change to the required information about a reporting company or its 
beneficial owners in a BOIR that a reporting company filed, the reporting company must 
file an updated BOIR no later than 30 days after the date on which the change occurred.

If the reporting company identifies an inaccuracy in a BOIR that the reporting company 
filed, the reporting company must correct it no later than 30 days after the date the 
reporting company became aware of the inaccuracy or had reason to know of it.

More information about reporting timelines may be found in Chapter 5 and Chapter 6 of 
FinCEN’s Small Entity Compliance Guide.

II. Where to Report Beneficial Ownership Information 
Reporting companies may complete BOIRs electronically by accessing the BOI E-Filing portal at 
https://boiefiling.fincen.gov (accessible beginning on January 1, 2024).

The E-Filing portal permits a reporting company to choose one of the following filing methods to 
submit a BOIR:
— Upload finalized PDF version of BOIR and submit online.
— Fill out Web-based version of BOIR and submit online.

A reporting company may submit its BOIR through either of these methods, both of which require 
the filing to be done online as BOIRs cannot be mailed or faxed to FinCEN. In each case, the 
person who submits a BOIR will need to provide their name and email address to FinCEN.

The person who submits a BOIR will receive confirmation of submission when a BOIR is accepted 
by FinCEN.

The E-Filing submission guides for both PDF and web-based versions of the BOIR may
assist in submitting completed BOIRs to FinCEN. To access these guides, go to
https://boifiling.fincen.gov and select Help.

FinCEN also offers system-to-system BOIR transmission via secure Application Programming 
Interface (API) for those, including third-party service providers, who are interested in 
automating the BOIR filing process.
"""
}

# System prompt: JSON-only response enforcement
system_prompt = """
You are a JSON-only assistant.

You must return all answers strictly as valid JSON, based on the exact structure provided in the prompt.

NEVER include markdown, extra text, or explanations. Only raw JSON is allowed in your output.

If anything is unclear, guess but keep the format. Never break JSON structure.
"""

# User prompt: instruct the model to generate a quiz
user_prompt = f"""
from this text I quiz with this criteria:
level of difficulty: {quiz_data["level_of_difficulty"]}
quiz type: {quiz_data["quiz_type"]}, 
Number of questions: {quiz_data["number_of_questions"]}
additiomal instruction: {quiz_data["quiz_instruction"]}
---
{course["original_text"]}
---
Make sure the correct answer matches the right option 
because it will be use to rate the quiz.
Return ONLY a JSON array formatted like this:
Questions: [
  {{
    "question": "questions",
    "choices": {{"A": "answer A", "B": "answer B", "C": "answer C", "D": "answer D"}},
    "correct_answer": "correct letter from choices e.g C"
  }}
]
Remember "choice is a dictionary".
"""
response = ask_openrouter(user_prompt, model="nousresearch/deephermes-3-mistral-24b-preview:free", system_prompt=system_prompt)
# Extract the content from the message
message_content = response['choices'][0]['message']['content']

print(message_content)