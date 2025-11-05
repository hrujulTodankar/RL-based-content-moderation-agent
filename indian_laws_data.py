"""
Indian Laws Data Repository
This file contains Indian legal content for moderation testing.
Add your Indian laws data here for testing with the moderation API.
"""

INDIAN_LAWS_DATA = [
    {
        "id": "ipc_302",
        "category": "criminal_law",
        "subcategory": "murder",
        "content": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "section": "Section 302",
        "act": "Indian Penal Code, 1860"
    },
    {
        "id": "ipc_376",
        "category": "criminal_law",
        "subcategory": "rape",
        "content": "Whoever, except in the cases provided for by sub-section (2), commits rape shall be punished with imprisonment of either description for a term which shall not be less than seven years but which may be for life or for a term which may extend to imprisonment for life and shall also be liable to fine.",
        "section": "Section 376",
        "act": "Indian Penal Code, 1860"
    },
    {
        "id": "ipc_420",
        "category": "criminal_law",
        "subcategory": "cheating",
        "content": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "section": "Section 420",
        "act": "Indian Penal Code, 1860"
    },
    {
        "id": "employment_law_1",
        "category": "employment_law",
        "subcategory": "workplace_harassment",
        "content": "No woman shall be subjected to sexual harassment at any workplace. The following circumstances, among other circumstances, if it occurs or is present in relation to or connected with any act or behavior of sexual harassment may amount to sexual harassment.",
        "section": "Section 2(n)",
        "act": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013"
    },
    {
        "id": "family_law_1",
        "category": "family_law",
        "subcategory": "domestic_violence",
        "content": "Any act, omission or commission or conduct of the respondent shall constitute domestic violence in case it harms or injures or endangers the health, safety, life, limb or well-being, whether mental or physical, of the aggrieved person or tends to do so and includes causing physical abuse, sexual abuse, verbal and emotional abuse and economic abuse.",
        "section": "Section 3",
        "act": "Protection of Women from Domestic Violence Act, 2005"
    },
    {
        "id": "cyber_law_1",
        "category": "cyber_crime",
        "subcategory": "identity_theft",
        "content": "Whoever, with the intent to cause or knowing that he is likely to cause wrongful loss or damage to the public or any person, destroys or deletes or alters any information residing in a computer resource or diminishes its value or utility or affects it injuriously by any means, commits hacking.",
        "section": "Section 66",
        "act": "Information Technology Act, 2000"
    },
    {
        "id": "constitution_1",
        "category": "constitutional_law",
        "subcategory": "fundamental_rights",
        "content": "All persons are equally entitled to freedom of speech and expression, freedom of assembly, freedom of association or union, freedom of movement, freedom of residence and freedom to practice any profession or occupation, subject to reasonable restrictions.",
        "section": "Article 19",
        "act": "Constitution of India"
    }
]

def get_all_laws():
    """Get all Indian laws data"""
    return INDIAN_LAWS_DATA

def get_laws_by_category(category):
    """Get laws by category (criminal_law, employment_law, etc.)"""
    return [law for law in INDIAN_LAWS_DATA if law["category"] == category]

def get_law_by_id(law_id):
    """Get a specific law by ID"""
    for law in INDIAN_LAWS_DATA:
        if law["id"] == law_id:
            return law
    return None

def get_sample_content_for_testing():
    """Get sample content for API testing"""
    return [
        ("criminal_law", "murder", "Whoever commits murder shall be punished with death"),
        ("employment_law", "workplace_harassment", "sexual harassment at work"),
        ("family_law", "domestic_violence", "husband beating wife"),
        ("cyber_crime", "identity_theft", "someone hacked my account"),
        ("constitutional_law", "fundamental_rights", "freedom of speech and expression")
    ]

# Add your Indian laws data here
# Example format:
# {
#     "id": "unique_id",
#     "category": "category_name",
#     "subcategory": "subcategory_name",
#     "content": "The actual legal text content",
#     "section": "Section/Article number",
#     "act": "Name of the Act"
# }