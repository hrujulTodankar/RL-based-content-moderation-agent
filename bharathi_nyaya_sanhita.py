#!/usr/bin/env python3
"""
Bharatiya Nyaya Sanhita (BNS) 2023 Database
==========================================

Comprehensive database of Bharatiya Nyaya Sanhita sections that replaced
the Indian Penal Code (IPC) in 2023. This module provides BNS sections
mapping for various legal domains and queries.

Features:
- Complete BNS sections database
- Domain-wise BNS section mapping
- Query-specific BNS section recommendations
- Comparison with old IPC sections

Author: Legal Agent Team
Version: 1.0.0 - BNS Integration
Date: 2025-01-15
"""

from typing import Dict, List, Tuple, Optional, Any
import re


class BharatiyaNyayaSanhitaDatabase:
    """Database containing Bharatiya Nyaya Sanhita (BNS) 2023 sections"""
    
    def __init__(self):
        """Initialize BNS sections database"""
        self.bns_sections = self._initialize_bns_sections()
        self.domain_mappings = self._create_domain_mappings()
        self.ipc_to_bns_mapping = self._create_ipc_to_bns_mapping()
    
    def _initialize_bns_sections(self) -> Dict[str, Dict[str, str]]:
        """Initialize comprehensive BNS sections database with all 358 sections"""
        
        # Load all 358 BNS sections from data
        sections_data = {
            "1": {"title": "Short title, commencement and application", "category": "preliminary"},
            "2": {"title": "Definitions", "category": "preliminary"},
            "3": {"title": "General explanations", "category": "preliminary"},
            "4": {"title": "Punishments", "category": "preliminary"},
            "5": {"title": "Commutation of sentence", "category": "preliminary"},
            "6": {"title": "Fractions of terms of punishment", "category": "preliminary"},
            "7": {"title": "Sentence may be wholly or partly rigorous or simple", "category": "preliminary"},
            "8": {"title": "Amount of fine, liability in default of payment of fine, etc.", "category": "preliminary"},
            "9": {"title": "Limit of punishment of offence made up of several offences", "category": "preliminary"},
            "10": {"title": "Punishment of person guilty of one of several offences", "category": "preliminary"},
            "11": {"title": "Solitary confinement", "category": "preliminary"},
            "12": {"title": "Limit of solitary confinement", "category": "preliminary"},
            "13": {"title": "Enhanced punishment for certain offences after previous conviction", "category": "preliminary"},
            "14": {"title": "Act done by a person bound, or by mistake of fact believing himself bound, by law", "category": "general_exceptions"},
            "15": {"title": "Act of Judge when acting judicially", "category": "general_exceptions"},
            "16": {"title": "Act done pursuant to judgment or order of Court", "category": "general_exceptions"},
            "17": {"title": "Act done by a person justified, or by mistake of fact believing himself justified, by law", "category": "general_exceptions"},
            "18": {"title": "Accident in doing a lawful act", "category": "general_exceptions"},
            "19": {"title": "Act likely to cause harm, but done without criminal intent, and to prevent other harm", "category": "general_exceptions"},
            "20": {"title": "Act of a child under seven years of age", "category": "general_exceptions"},
            "21": {"title": "Act of a child above seven and under twelve years of age of immature understanding", "category": "general_exceptions"},
            "22": {"title": "Act of a person of unsound mind", "category": "general_exceptions"},
            "23": {"title": "Act of a person incapable of judgment by reason of intoxication caused against his will", "category": "general_exceptions"},
            "24": {"title": "Offence requiring a particular intent or knowledge committed by one who is intoxicated", "category": "general_exceptions"},
            "25": {"title": "Act not intended and not known to be likely to cause death or grievous hurt, done by consent", "category": "general_exceptions"},
            "26": {"title": "Act not intended to cause death, done by consent in good faith for person's benefit", "category": "general_exceptions"},
            "27": {"title": "Act done in good faith for benefit of child or person of unsound mind, by, or by consent of guardian", "category": "general_exceptions"},
            "28": {"title": "Consent known to be given under fear or misconception", "category": "general_exceptions"},
            "29": {"title": "Exclusion of acts which are offences independently of harm caused", "category": "general_exceptions"},
            "30": {"title": "Act done in good faith for benefit of a person without consent", "category": "general_exceptions"},
            "31": {"title": "Communication made in good faith", "category": "general_exceptions"},
            "32": {"title": "Act to which a person is compelled by threats", "category": "general_exceptions"},
            "33": {"title": "Act causing slight harm", "category": "general_exceptions"},
            "34": {"title": "Things done in private defence", "category": "private_defence"},
            "35": {"title": "Right of private defence of body and of property", "category": "private_defence"},
            "36": {"title": "Right of private defence against act of a person of unsound mind, etc.", "category": "private_defence"},
            "37": {"title": "Acts against which there is no right of private defence", "category": "private_defence"},
            "38": {"title": "When right of private defence of body extends to causing death", "category": "private_defence"},
            "39": {"title": "When such right extends to causing any harm other than death", "category": "private_defence"},
            "40": {"title": "Commencement and continuance of right of private defence of body", "category": "private_defence"},
            "41": {"title": "When right of private defence of property extends to causing death", "category": "private_defence"},
            "42": {"title": "When such right extends to causing any harm other than death", "category": "private_defence"},
            "43": {"title": "Commencement and continuance of right of private defence of property", "category": "private_defence"},
            "44": {"title": "Right of private defence against deadly assault when there is risk of harm to innocent person", "category": "private_defence"},
            "45": {"title": "Abetment of a thing", "category": "abetment"},
            "46": {"title": "Abettor", "category": "abetment"},
            "47": {"title": "Abetment in India of offences outside India", "category": "abetment"},
            "48": {"title": "Abetment outside India for offence in India", "category": "abetment"},
            "49": {"title": "Punishment of abetment if act abetted is committed in consequence and where no express provision is made for its punishment", "category": "abetment"},
            "50": {"title": "Punishment of abetment if person abetted does act with different intention from that of abettor", "category": "abetment"},
            "51": {"title": "Liability of abettor when one act abetted and different act done", "category": "abetment"},
            "52": {"title": "Abettor when liable to cumulative punishment for act abetted and for act done", "category": "abetment"},
            "53": {"title": "Liability of abettor for an effect caused by act abetted different from that intended by abettor", "category": "abetment"},
            "54": {"title": "Abettor present when offence is committed", "category": "abetment"},
            "55": {"title": "Abetment of offence punishable with death or imprisonment for life", "category": "abetment"},
            "56": {"title": "Abetment of offence punishable with imprisonment", "category": "abetment"},
            "57": {"title": "Abetting commission of offence by public or by more than ten persons", "category": "abetment"},
            "58": {"title": "Concealing design to commit offence punishable with death or imprisonment for life", "category": "abetment"},
            "59": {"title": "Public servant concealing design to commit offence which it is his duty to prevent", "category": "abetment"},
            "60": {"title": "Concealing design to commit offence punishable with imprisonment", "category": "abetment"},
            "61": {"title": "Criminal conspiracy", "category": "conspiracy"},
            "62": {"title": "Punishment for attempting to commit offences punishable with imprisonment for life or other imprisonment", "category": "attempt"},
            "63": {"title": "Rape", "category": "sexual_offences"},
            "64": {"title": "Punishment for rape", "category": "sexual_offences"},
            "65": {"title": "Punishment for rape in certain cases", "category": "sexual_offences"},
            "66": {"title": "Punishment for causing death or resulting in persistent vegetative state of victim", "category": "sexual_offences"},
            "67": {"title": "Sexual intercourse by husband upon his wife during separation", "category": "sexual_offences"},
            "68": {"title": "Sexual intercourse by a person in authority", "category": "sexual_offences"},
            "69": {"title": "Sexual intercourse by employing deceitful means, etc.", "category": "sexual_offences"},
            "70": {"title": "Gang rape", "category": "sexual_offences"},
            "71": {"title": "Punishment for repeat offenders", "category": "sexual_offences"},
            "72": {"title": "Disclosure of identity of victim of certain offences, etc.", "category": "sexual_offences"},
            "73": {"title": "Printing or publishing any matter relating to Court proceedings without permission", "category": "court_offences"},
            "74": {"title": "Assault or use of criminal force to woman with intent to outrage her modesty", "category": "sexual_offences"},
            "75": {"title": "Sexual harassment", "category": "sexual_offences"},
            "76": {"title": "Assault or use of criminal force to woman with intent to disrobe", "category": "sexual_offences"},
            "77": {"title": "Voyeurism", "category": "sexual_offences"},
            "78": {"title": "Stalking", "category": "sexual_offences"},
            "79": {"title": "Word, gesture or act intended to insult modesty of a woman", "category": "sexual_offences"},
            "80": {"title": "Dowry death", "category": "marriage_offences"},
            "81": {"title": "Cohabitation caused by man deceitfully inducing belief of lawful marriage", "category": "marriage_offences"},
            "82": {"title": "Marrying again during lifetime of husband or wife", "category": "marriage_offences"},
            "83": {"title": "Marriage ceremony fraudulently gone through without lawful marriage", "category": "marriage_offences"},
            "84": {"title": "Enticing or taking away or detaining with criminal intent a married woman", "category": "marriage_offences"},
            "85": {"title": "Husband or relative of husband of a woman subjecting her to cruelty", "category": "marriage_offences"},
            "86": {"title": "Cruelty defined", "category": "marriage_offences"},
            "87": {"title": "Kidnapping, abducting or inducing woman to compel her marriage, etc.", "category": "kidnapping_abduction"},
            "88": {"title": "Causing miscarriage", "category": "offences_human_body"},
            "89": {"title": "Causing miscarriage without woman's consent", "category": "offences_human_body"},
            "90": {"title": "Death caused by act done with intent to cause miscarriage", "category": "offences_human_body"},
            "91": {"title": "Act done with intent to prevent child being born alive or to cause to die after birth", "category": "offences_human_body"},
            "92": {"title": "Causing death of quick unborn child by act amounting to culpable homicide", "category": "offences_human_body"},
            "93": {"title": "Exposure and abandonment of child under twelve years of age, by parent or person having care of it", "category": "child_offences"},
            "94": {"title": "Concealment of birth by secret disposal of dead body", "category": "child_offences"},
            "95": {"title": "Hiring, employing or engaging a child to commit an offence", "category": "child_offences"},
            "96": {"title": "Procuration of child", "category": "child_offences"},
            "97": {"title": "Kidnapping or abducting child under ten years of age with intent to steal from its person", "category": "child_offences"},
            "98": {"title": "Selling child for purposes of prostitution, etc.", "category": "child_offences"},
            "99": {"title": "Buying child for purposes of prostitution, etc.", "category": "child_offences"},
            "100": {"title": "Culpable homicide", "category": "offences_human_body"},
            "101": {"title": "Murder", "category": "offences_human_body"},
            "102": {"title": "Culpable homicide by causing death of person other than person whose death was intended", "category": "offences_human_body"},
            "103": {"title": "Punishment for murder", "category": "offences_human_body"},
            "104": {"title": "Punishment for murder by life-convict", "category": "offences_human_body"},
            "105": {"title": "Punishment for culpable homicide not amounting to murder", "category": "offences_human_body"},
            "106": {"title": "Causing death by negligence", "category": "offences_human_body"},
            "107": {"title": "Abetment of suicide of child or person of unsound mind", "category": "suicide_related"},
            "108": {"title": "Abetment of suicide", "category": "suicide_related"},
            "109": {"title": "Attempt to murder", "category": "offences_human_body"},
            "110": {"title": "Attempt to commit culpable homicide", "category": "offences_human_body"},
            "111": {"title": "Organised crime", "category": "organised_crime"},
            "112": {"title": "Petty organised crime", "category": "organised_crime"},
            "113": {"title": "Terrorist act", "category": "terrorism"},
            "114": {"title": "Hurt", "category": "offences_human_body"},
            "115": {"title": "Voluntarily causing hurt", "category": "offences_human_body"},
            "116": {"title": "Grievous hurt", "category": "offences_human_body"},
            "117": {"title": "Voluntarily causing grievous hurt", "category": "offences_human_body"},
            "118": {"title": "Voluntarily causing hurt or grievous hurt by dangerous weapons or means", "category": "offences_human_body"},
            "119": {"title": "Voluntarily causing hurt or grievous hurt to extort property, or to constrain to an illegal act", "category": "offences_human_body"},
            "120": {"title": "Voluntarily causing hurt or grievous hurt to extort confession, or to compel restoration of property", "category": "offences_human_body"},
            "121": {"title": "Voluntarily causing hurt or grievous hurt to deter public servant from his duty", "category": "offences_human_body"},
            "122": {"title": "Voluntarily causing hurt or grievous hurt on provocation", "category": "offences_human_body"},
            "123": {"title": "Causing hurt by means of poison, etc., with intent to commit an offence", "category": "offences_human_body"},
            "124": {"title": "Voluntarily causing grievous hurt by use of acid, etc.", "category": "offences_human_body"},
            "125": {"title": "Act endangering life or personal safety of others", "category": "offences_human_body"},
            "126": {"title": "Wrongful restraint", "category": "restraint_confinement"},
            "127": {"title": "Wrongful confinement", "category": "restraint_confinement"},
            "128": {"title": "Force", "category": "force_assault"},
            "129": {"title": "Criminal force", "category": "force_assault"},
            "130": {"title": "Assault", "category": "force_assault"},
            "131": {"title": "Punishment for assault or criminal force otherwise than on grave provocation", "category": "force_assault"},
            "132": {"title": "Assault or criminal force to deter public servant from discharge of his duty", "category": "force_assault"},
            "133": {"title": "Assault or criminal force with intent to dishonour person, otherwise than on grave provocation", "category": "force_assault"},
            "134": {"title": "Assault or criminal force in attempt to commit theft of property carried by a person", "category": "force_assault"},
            "135": {"title": "Assault or criminal force in attempt to wrongfully confine a person", "category": "force_assault"},
            "136": {"title": "Assault or criminal force on grave provocation", "category": "force_assault"},
            "137": {"title": "Kidnapping", "category": "kidnapping_abduction"},
            "138": {"title": "Abduction", "category": "kidnapping_abduction"},
            "139": {"title": "Kidnapping or maiming a child for purposes of begging", "category": "kidnapping_abduction"},
            "140": {"title": "Kidnapping or abducting in order to murder or for ransom, etc.", "category": "kidnapping_abduction"},
            "141": {"title": "Importation of girl or boy from foreign country", "category": "kidnapping_abduction"},
            "142": {"title": "Wrongfully concealing or keeping in confinement, kidnapped or abducted person", "category": "kidnapping_abduction"},
            "143": {"title": "Trafficking of person", "category": "trafficking"},
            "144": {"title": "Exploitation of a trafficked person", "category": "trafficking"},
            "145": {"title": "Habitual dealing in slaves", "category": "trafficking"},
            "146": {"title": "Unlawful compulsory labour", "category": "trafficking"},
            "147": {"title": "Waging, or attempting to wage war, or abetting waging of war, against Government of India", "category": "offences_against_state"},
            "148": {"title": "Conspiracy to commit offences punishable by section 147", "category": "offences_against_state"},
            "149": {"title": "Collecting arms, etc., with intention of waging war against Government of India", "category": "offences_against_state"},
            "150": {"title": "Concealing with intent to facilitate design to wage war", "category": "offences_against_state"},
            "151": {"title": "Assaulting President, Governor, etc., with intent to compel or restrain exercise of any lawful power", "category": "offences_against_state"},
            "152": {"title": "Act endangering sovereignty, unity and integrity of India", "category": "offences_against_state"},
            "153": {"title": "Waging war against Government of any foreign State at peace with Government of India", "category": "offences_against_state"},
            "154": {"title": "Committing depredation on territories of foreign State at peace with Government of India", "category": "offences_against_state"},
            "155": {"title": "Receiving property taken by war or depredation mentioned in sections 153 and 154", "category": "offences_against_state"},
            "156": {"title": "Public servant voluntarily allowing prisoner of State or war to escape", "category": "offences_against_state"},
            "157": {"title": "Public servant negligently suffering such prisoner to escape", "category": "offences_against_state"},
            "158": {"title": "Aiding escape of, rescuing or harbouring such prisoner", "category": "offences_against_state"},
            "159": {"title": "Abetting mutiny, or attempting to seduce a soldier, sailor or airman from his duty", "category": "military_offences"},
            "160": {"title": "Abetment of mutiny, if mutiny is committed in consequence thereof", "category": "military_offences"},
            "161": {"title": "Abetment of assault by soldier, sailor or airman on his superior officer, when in execution of his office", "category": "military_offences"},
            "162": {"title": "Abetment of such assault, if assault committed", "category": "military_offences"},
            "163": {"title": "Abetment of desertion of soldier, sailor or airman", "category": "military_offences"},
            "164": {"title": "Harbouring deserter", "category": "military_offences"},
            "165": {"title": "Deserter concealed on board merchant vessel through negligence of master", "category": "military_offences"},
            "166": {"title": "Abetment of act of insubordination by soldier, sailor or airman", "category": "military_offences"},
            "167": {"title": "Persons subject to certain Acts", "category": "military_offences"},
            "168": {"title": "Wearing garb or carrying token used by soldier, sailor or airman", "category": "military_offences"},
            "169": {"title": "Candidate, electoral right defined", "category": "election_offences"},
            "170": {"title": "Bribery", "category": "election_offences"},
            "171": {"title": "Undue influence at elections", "category": "election_offences"},
            "172": {"title": "Personation at elections", "category": "election_offences"},
            "173": {"title": "Punishment for bribery", "category": "election_offences"},
            "174": {"title": "Punishment for undue influence or personation at an election", "category": "election_offences"},
            "175": {"title": "False statement in connection with an election", "category": "election_offences"},
            "176": {"title": "Illegal payments in connection with an election", "category": "election_offences"},
            "177": {"title": "Failure to keep election accounts", "category": "election_offences"},
            "178": {"title": "Counterfeiting coin, Government stamps, currency-notes or bank-notes", "category": "currency_offences"},
            "179": {"title": "Using as genuine, forged or counterfeit coin, Government stamp, currency-notes or bank-notes", "category": "currency_offences"},
            "180": {"title": "Possession of forged or counterfeit coin, Government stamp, currency-notes or bank-notes", "category": "currency_offences"},
            "181": {"title": "Making or possessing instruments or materials for forging or counterfeiting coin, Government stamp, currency-notes or bank-notes", "category": "currency_offences"},
            "182": {"title": "Making or using documents resembling currency-notes or bank-notes", "category": "currency_offences"},
            "183": {"title": "Effacing writing from substance bearing Government stamp, or removing from document a stamp used for it, with intent to cause loss to Government", "category": "currency_offences"},
            "184": {"title": "Using Government stamp known to have been before used", "category": "currency_offences"},
            "185": {"title": "Erasure of mark denoting that stamp has been used", "category": "currency_offences"},
            "186": {"title": "Prohibition of fictitious stamps", "category": "currency_offences"},
            "187": {"title": "Person employed in mint causing coin to be of different weight or composition from that fixed by law", "category": "currency_offences"},
            "188": {"title": "Unlawfully taking coining instrument from mint", "category": "currency_offences"},
            "189": {"title": "Unlawful assembly", "category": "public_order"},
            "190": {"title": "Every member of unlawful assembly guilty of offence committed in prosecution of common object", "category": "public_order"},
            "191": {"title": "Rioting", "category": "public_order"},
            "192": {"title": "Wantonly giving provocation with intent to cause riot-if rioting be committed; if not committed", "category": "public_order"},
            "193": {"title": "Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes place", "category": "public_order"},
            "194": {"title": "Affray", "category": "public_order"},
            "195": {"title": "Assaulting or obstructing public servant when suppressing riot, etc.", "category": "public_order"},
            "196": {"title": "Promoting enmity between different groups on grounds of religion, race, place of birth, residence, language, etc., and doing acts prejudicial to maintenance of harmony", "category": "public_order"},
            "197": {"title": "Imputations, assertions prejudicial to national integration", "category": "public_order"},
            "198": {"title": "Public servant disobeying law, with intent to cause injury to any person", "category": "public_servants"},
            "199": {"title": "Public servant disobeying direction under law", "category": "public_servants"},
            "200": {"title": "Punishment for non-treatment of victim", "category": "public_servants"},
            "201": {"title": "Public servant framing an incorrect document with intent to cause injury", "category": "public_servants"},
            "202": {"title": "Public servant unlawfully engaging in trade", "category": "public_servants"},
            "203": {"title": "Public servant unlawfully buying or bidding for property", "category": "public_servants"},
            "204": {"title": "Personating a public servant", "category": "public_servants"},
            "205": {"title": "Wearing garb or carrying token used by public servant with fraudulent intent", "category": "public_servants"},
            "206": {"title": "Absconding to avoid service of summons or other proceeding", "category": "contempt_court"},
            "207": {"title": "Preventing service of summons or other proceeding, or preventing publication thereof", "category": "contempt_court"},
            "208": {"title": "Non-attendance in obedience to an order from public servant", "category": "contempt_court"},
            "209": {"title": "Non-appearance in response to a proclamation under section 84 of Bharatiya Nagarik Suraksha Sanhita, 2023", "category": "contempt_court"},
            "210": {"title": "Omission to produce document or electronic record to public servant by person legally bound to produce it", "category": "contempt_court"},
            "211": {"title": "Omission to give notice or information to public servant by person legally bound to give it", "category": "contempt_court"},
            "212": {"title": "Furnishing false information", "category": "false_information"},
            "213": {"title": "Refusing oath or affirmation when duly required by public servant to make it", "category": "contempt_court"},
            "214": {"title": "Refusing to answer public servant authorised to question", "category": "contempt_court"},
            "215": {"title": "Refusing to sign statement", "category": "contempt_court"},
            "216": {"title": "False statement on oath or affirmation to public servant or person authorised to administer an oath or affirmation", "category": "false_evidence"},
            "217": {"title": "False information, with intent to cause public servant to use his lawful power to injury of another person", "category": "false_information"},
            "218": {"title": "Resistance to taking of property by lawful authority of a public servant", "category": "obstruction_justice"},
            "219": {"title": "Obstructing sale of property offered for sale by authority of public servant", "category": "obstruction_justice"},
            "220": {"title": "Illegal purchase or bid for property offered for sale by authority of public servant", "category": "obstruction_justice"},
            "221": {"title": "Obstructing public servant in discharge of public functions", "category": "obstruction_justice"},
            "222": {"title": "Omission to assist public servant when bound by law to give assistance", "category": "obstruction_justice"},
            "223": {"title": "Disobedience to order duly promulgated by public servant", "category": "obstruction_justice"},
            "224": {"title": "Threat of injury to public servant", "category": "intimidation"},
            "225": {"title": "Threat of injury to induce person to refrain from applying for protection to public servant", "category": "intimidation"},
            "226": {"title": "Attempt to commit suicide to compel or restrain exercise of lawful power", "category": "suicide_related"},
            "227": {"title": "Giving false evidence", "category": "false_evidence"},
            "228": {"title": "Fabricating false evidence", "category": "false_evidence"},
            "229": {"title": "Punishment for false evidence", "category": "false_evidence"},
            "230": {"title": "Giving or fabricating false evidence with intent to procure conviction of capital offence", "category": "false_evidence"},
            "231": {"title": "Giving or fabricating false evidence with intent to procure conviction of offence punishable with imprisonment for life or imprisonment", "category": "false_evidence"},
            "232": {"title": "Threatening any person to give false evidence", "category": "false_evidence"},
            "233": {"title": "Using evidence known to be false", "category": "false_evidence"},
            "234": {"title": "Issuing or signing false certificate", "category": "false_evidence"},
            "235": {"title": "Using as true a certificate known to be false", "category": "false_evidence"},
            "236": {"title": "False statement made in declaration which is by law receivable as evidence", "category": "false_evidence"},
            "237": {"title": "Using as true such declaration knowing it to be false", "category": "false_evidence"},
            "238": {"title": "Causing disappearance of evidence of offence, or giving false information to screen offender", "category": "false_evidence"},
            "239": {"title": "Intentional omission to give information of offence by person bound to inform", "category": "false_evidence"},
            "240": {"title": "Giving false information respecting an offence committed", "category": "false_information"},
            "241": {"title": "Destruction of document or electronic record to prevent its production as evidence", "category": "false_evidence"},
            "242": {"title": "False personation for purpose of act or proceeding in suit or prosecution", "category": "false_evidence"},
            "243": {"title": "Fraudulent removal or concealment of property to prevent its seizure as forfeited or in execution", "category": "property_offences"},
            "244": {"title": "Fraudulent claim to property to prevent its seizure as forfeited or in execution", "category": "property_offences"},
            "245": {"title": "Fraudulently suffering decree for sum not due", "category": "property_offences"},
            "246": {"title": "Dishonestly making false claim in Court", "category": "property_offences"},
            "247": {"title": "Fraudulently obtaining decree for sum not due", "category": "property_offences"},
            "248": {"title": "False charge of offence made with intent to injure", "category": "false_information"},
            "249": {"title": "Harbouring offender", "category": "harbouring_offenders"},
            "250": {"title": "Taking gift, etc., to screen an offender from punishment", "category": "harbouring_offenders"},
            "251": {"title": "Offering gift or restoration of property in consideration of screening offender", "category": "harbouring_offenders"},
            "252": {"title": "Taking gift to help to recover stolen property, etc.", "category": "harbouring_offenders"},
            "253": {"title": "Harbouring offender who has escaped from custody or whose apprehension has been ordered", "category": "harbouring_offenders"},
            "254": {"title": "Penalty for harbouring robbers or dacoits", "category": "harbouring_offenders"},
            "255": {"title": "Public servant disobeying direction of law with intent to save person from punishment or property from forfeiture", "category": "public_servants"},
            "256": {"title": "Public servant framing incorrect record or writing with intent to save person from punishment or property from forfeiture", "category": "public_servants"},
            "257": {"title": "Public servant in judicial proceeding corruptly making report, etc., contrary to law", "category": "public_servants"},
            "258": {"title": "Commitment for trial or confinement by person having authority who knows that he is acting contrary to law", "category": "public_servants"},
            "259": {"title": "Intentional omission to apprehend on part of public servant bound to apprehend", "category": "public_servants"},
            "260": {"title": "Intentional omission to apprehend on part of public servant bound to apprehend person under sentence or lawfully committed", "category": "public_servants"},
            "261": {"title": "Escape from confinement or custody negligently suffered by public servant", "category": "escape_custody"},
            "262": {"title": "Resistance or obstruction by a person to his lawful apprehension", "category": "escape_custody"},
            "263": {"title": "Resistance or obstruction to lawful apprehension of another person", "category": "escape_custody"},
            "264": {"title": "Omission to apprehend, or sufferance of escape, on part of public servant, in cases not otherwise provided for", "category": "escape_custody"},
            "265": {"title": "Resistance or obstruction to lawful apprehension or escape or rescue in cases not otherwise provided for", "category": "escape_custody"},
            "266": {"title": "Violation of condition of remission of punishment", "category": "escape_custody"},
            "267": {"title": "Intentional insult or interruption to public servant sitting in judicial proceeding", "category": "contempt_court"},
            "268": {"title": "Personation of assessor", "category": "contempt_court"},
            "269": {"title": "Failure by person released on bail bond or bond to appear in Court", "category": "contempt_court"},
            "270": {"title": "Public nuisance", "category": "public_nuisance"},
            "271": {"title": "Negligent act likely to spread infection of disease dangerous to life", "category": "public_health"},
            "272": {"title": "Malignant act likely to spread infection of disease dangerous to life", "category": "public_health"},
            "273": {"title": "Disobedience to quarantine rule", "category": "public_health"},
            "274": {"title": "Adulteration of food or drink intended for sale", "category": "public_health"},
            "275": {"title": "Sale of noxious food or drink", "category": "public_health"},
            "276": {"title": "Adulteration of drugs", "category": "public_health"},
            "277": {"title": "Sale of adulterated drugs", "category": "public_health"},
            "278": {"title": "Sale of drug as a different drug or preparation", "category": "public_health"},
            "279": {"title": "Fouling water of public spring or reservoir", "category": "public_health"},
            "280": {"title": "Making atmosphere noxious to health", "category": "public_health"},
            "281": {"title": "Rash driving or riding on a public way", "category": "public_safety"},
            "282": {"title": "Rash navigation of vessel", "category": "public_safety"},
            "283": {"title": "Exhibition of false light, mark or buoy", "category": "public_safety"},
            "284": {"title": "Conveying person by water for hire in unsafe or overloaded vessel", "category": "public_safety"},
            "285": {"title": "Danger or obstruction in public way or line of navigation", "category": "public_safety"},
            "286": {"title": "Negligent conduct with respect to poisonous substance", "category": "public_safety"},
            "287": {"title": "Negligent conduct with respect to fire or combustible matter", "category": "public_safety"},
            "288": {"title": "Negligent conduct with respect to explosive substance", "category": "public_safety"},
            "289": {"title": "Negligent conduct with respect to machinery", "category": "public_safety"},
            "290": {"title": "Negligent conduct with respect to pulling down, repairing or constructing buildings, etc.", "category": "public_safety"},
            "291": {"title": "Negligent conduct with respect to animal", "category": "public_safety"},
            "292": {"title": "Punishment for public nuisance in cases not otherwise provided for", "category": "public_nuisance"},
            "293": {"title": "Continuance of nuisance after injunction to discontinue", "category": "public_nuisance"},
            "294": {"title": "Sale, etc., of obscene books, etc.", "category": "obscenity"},
            "295": {"title": "Sale, etc., of obscene objects to child", "category": "obscenity"},
            "296": {"title": "Obscene acts and songs", "category": "obscenity"},
            "297": {"title": "Keeping lottery office", "category": "gambling"},
            "298": {"title": "Injuring or defiling place of worship with intent to insult religion of any class", "category": "religious_offences"},
            "299": {"title": "Deliberate and malicious acts, intended to outrage religious feelings of any class by insulting its religion or religious beliefs", "category": "religious_offences"},
            "300": {"title": "Disturbing religious assembly", "category": "religious_offences"},
            "301": {"title": "Trespassing on burial places, etc.", "category": "religious_offences"},
            "302": {"title": "Uttering words, etc., with deliberate intent to wound religious feelings of any person", "category": "religious_offences"},
            "303": {"title": "Theft", "category": "property_offences"},
            "304": {"title": "Snatching", "category": "property_offences"},
            "305": {"title": "Theft in a dwelling house, or means of transportation or place of worship, etc.", "category": "property_offences"},
            "306": {"title": "Theft by clerk or servant of property in possession of master", "category": "property_offences"},
            "307": {"title": "Theft after preparation made for causing death, hurt or restraint in order to committing of theft", "category": "property_offences"},
            "308": {"title": "Extortion", "category": "property_offences"},
            "309": {"title": "Robbery", "category": "property_offences"},
            "310": {"title": "Dacoity", "category": "property_offences"},
            "311": {"title": "Robbery, or dacoity, with attempt to cause death or grievous hurt", "category": "property_offences"},
            "312": {"title": "Attempt to commit robbery or dacoity when armed with deadly weapon", "category": "property_offences"},
            "313": {"title": "Punishment for belonging to gang of robbers, etc.", "category": "property_offences"},
            "314": {"title": "Dishonest misappropriation of property", "category": "property_offences"},
            "315": {"title": "Dishonest misappropriation of property possessed by deceased person at the time of his death", "category": "property_offences"},
            "316": {"title": "Criminal breach of trust", "category": "property_offences"},
            "317": {"title": "Stolen property", "category": "property_offences"},
            "318": {"title": "Cheating", "category": "property_offences"},
            "319": {"title": "Cheating by personation", "category": "property_offences"},
            "320": {"title": "Dishonest or fraudulent removal or concealment of property to prevent distribution among creditors", "category": "property_offences"},
            "321": {"title": "Dishonestly or fraudulently preventing debt being available for creditors", "category": "property_offences"},
            "322": {"title": "Dishonest or fraudulent execution of deed of transfer containing false statement of consideration", "category": "property_offences"},
            "323": {"title": "Dishonest or fraudulent removal or concealment of property", "category": "property_offences"},
            "324": {"title": "Mischief", "category": "mischief"},
            "325": {"title": "Mischief by killing or maiming animal", "category": "mischief"},
            "326": {"title": "Mischief by injury, inundation, fire or explosive substance, etc.", "category": "mischief"},
            "327": {"title": "Mischief with intent to destroy or make unsafe a rail, aircraft, decked vessel or one of twenty tons burden", "category": "mischief"},
            "328": {"title": "Punishment for intentionally running vessel aground or ashore with intent to commit theft, etc.", "category": "mischief"},
            "329": {"title": "Criminal trespass and house-trespass", "category": "trespass"},
            "330": {"title": "House-trespass and housebreaking", "category": "trespass"},
            "331": {"title": "Punishment for house-trespass or house-breaking", "category": "trespass"},
            "332": {"title": "House-trespass in order to commit offence", "category": "trespass"},
            "333": {"title": "House-trespass after preparation for hurt, assault or wrongful restraint", "category": "trespass"},
            "334": {"title": "Dishonestly breaking open receptacle containing property", "category": "trespass"},
            "335": {"title": "Making a false document", "category": "document_offences"},
            "336": {"title": "Forgery", "category": "document_offences"},
            "337": {"title": "Forgery of record of Court or of public register, etc.", "category": "document_offences"},
            "338": {"title": "Forgery of valuable security, will, etc.", "category": "document_offences"},
            "339": {"title": "Having possession of document described in section 337 or section 338, knowing it to be forged and intending to use it as genuine", "category": "document_offences"},
            "340": {"title": "Forged document or electronic record and using it as genuine", "category": "document_offences"},
            "341": {"title": "Making or possessing counterfeit seal, etc., with intent to commit forgery punishable under section 338", "category": "document_offences"},
            "342": {"title": "Counterfeiting device or mark used for authenticating documents described in section 338, or possessing counterfeit marked material", "category": "document_offences"},
            "343": {"title": "Fraudulent cancellation, destruction, etc., of will, authority to adopt, or valuable security", "category": "document_offences"},
            "344": {"title": "Falsification of accounts", "category": "document_offences"},
            "345": {"title": "Property mark", "category": "property_marks"},
            "346": {"title": "Tampering with property mark with intent to cause injury", "category": "property_marks"},
            "347": {"title": "Counterfeiting a property mark", "category": "property_marks"},
            "348": {"title": "Making or possession of any instrument for counterfeiting a property mark", "category": "property_marks"},
            "349": {"title": "Selling goods marked with a counterfeit property mark", "category": "property_marks"},
            "350": {"title": "Making a false mark upon any receptacle containing goods", "category": "property_marks"},
            "351": {"title": "Criminal intimidation", "category": "intimidation"},
            "352": {"title": "Intentional insult with intent to provoke breach of peace", "category": "insulting_behaviour"},
            "353": {"title": "Statements conducing to public mischief", "category": "public_mischief"},
            "354": {"title": "Act caused by inducing person to believe that he will be rendered an object of Divine displeasure", "category": "superstition"},
            "355": {"title": "Misconduct in public by a drunken person", "category": "public_misconduct"},
            "356": {"title": "Defamation", "category": "defamation"},
            "357": {"title": "Breach of contract to attend on and supply wants of helpless person", "category": "negligence"},
            "358": {"title": "Repeal and savings", "category": "miscellaneous"}
        }
        
        # Add descriptions for all sections
        for section_num, data in sections_data.items():
            if "description" not in data:
                data["description"] = f"BNS Section {section_num}: {data['title']}"
        
        return sections_data
    
    def _create_domain_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Create mappings between legal domains and relevant BNS sections"""
        return {
            "criminal_law": {
                "general": ["101", "103", "109", "115", "116", "117", "118"],
                "theft": ["303", "304", "305"],
                "cyber_crime": ["318", "319", "320", "336", "337"],
                "assault": ["115", "116", "117", "118"],
                "fraud": ["318", "319", "320"],
                "robbery": ["316", "317"],
                "extortion": ["309", "310"],
                "criminal_breach_trust": ["329", "330"],
                "forgery": ["336", "337"]
            },
            "employment_law": {
                "general": ["85", "351", "352"],
                "workplace_harassment": ["74", "75", "76", "79"],
                "discrimination": ["74", "75", "76"],
                "confidentiality_breach": ["329", "330"],
                "criminal_intimidation": ["351", "352"]
            },
            "family_law": {
                "general": ["82", "85"],
                "domestic_violence": ["85", "115", "116", "117", "118"],
                "bigamy": ["82"],
                "cruelty": ["85"],
                "criminal_intimidation": ["351", "352"]
            },
            "cyber_crime": {
                "general": ["318", "319", "320", "336", "337"],
                "identity_theft": ["318", "319", "320"],
                "online_fraud": ["318", "319", "320"],
                "cyberbullying": ["351", "352", "356", "357"],
                "forgery": ["336", "337"]
            },
            "tenant_rights": {
                "general": ["322", "329", "330", "351", "352"],
                "criminal_breach_trust": ["329", "330"],
                "criminal_intimidation": ["351", "352"],
                "cheating": ["318", "319", "320"]
            },
            "consumer_complaint": {
                "general": ["318", "319", "320", "322"],
                "cheating": ["318", "319", "320"],
                "criminal_breach_trust": ["329", "330"],
                "defective_products": ["318", "319", "320"]
            },
            "elder_abuse": {
                "general": ["85", "115", "116", "322", "329", "330", "351", "352"],
                "financial_abuse": ["318", "319", "320", "322", "329", "330"],
                "physical_abuse": ["115", "116", "117", "118"],
                "criminal_intimidation": ["351", "352"]
            }
        }
    
    def _create_ipc_to_bns_mapping(self) -> Dict[str, str]:
        """Create mapping from old IPC sections to new BNS sections"""
        return {
            "302": "103",  # Murder
            "307": "109",  # Attempt to murder
            "323": "116",  # Voluntarily causing hurt
            "324": "118",  # Voluntarily causing grievous hurt
            "354": "74",   # Assault on woman with intent to outrage modesty
            "354A": "75",  # Sexual harassment
            "375": "63",   # Rape
            "376": "64",   # Punishment for rape
            "509": "79",   # Word, gesture or act intended to insult modesty of woman
            "378": "303",  # Theft
            "379": "304",  # Punishment for theft
            "380": "305",  # Theft in dwelling house
            "392": "317",  # Punishment for robbery
            "403": "322",  # Dishonest misappropriation of property
            "406": "330",  # Criminal breach of trust
            "420": "320",  # Cheating and dishonestly inducing delivery of property
            "415": "318",  # Cheating
            "384": "310",  # Punishment for extortion
            "463": "336",  # Forgery
            "494": "82",   # Bigamy
            "498A": "85",  # Husband or relative of husband subjecting woman to cruelty
            "503": "351",  # Criminal intimidation
            "506": "352",  # Punishment for criminal intimidation
            "499": "356",  # Defamation
            "500": "357",  # Punishment for defamation
            "191": "238",  # Giving false evidence
            "193": "239",  # Punishment for false evidence
            "161": "197",  # Public servant taking gratification
            "124A": "147"  # Sedition
        }
    
    def get_bns_sections_for_domain(self, domain: str, subdomain: str = None, query: str = "") -> List[Dict[str, Any]]:
        """Get relevant BNS sections for a domain and subdomain"""
        
        domain = domain.lower().replace(' ', '_')
        
        # Get domain mapping
        domain_mapping = self.domain_mappings.get(domain, {})
        
        # Get sections based on subdomain or general domain
        if subdomain and subdomain in domain_mapping:
            section_numbers = domain_mapping[subdomain]
        else:
            section_numbers = domain_mapping.get("general", [])
        
        # Add query-specific sections
        query_sections = self._get_query_specific_sections(query)
        section_numbers.extend(query_sections)
        
        # Remove duplicates and get section details
        section_numbers = list(set(section_numbers))
        
        bns_sections = []
        for section_num in section_numbers[:6]:  # Limit to 6 most relevant sections
            if section_num in self.bns_sections:
                section = self.bns_sections[section_num]
                bns_sections.append({
                    "section_number": section_num,
                    "title": section["title"],
                    "description": section["description"],
                    "category": section["category"]
                })
        
        return bns_sections
    
    def _get_query_specific_sections(self, query: str) -> List[str]:
        """Get BNS sections based on specific query keywords"""
        
        query_lower = query.lower()
        specific_sections = []
        
        # Keyword-based section mapping
        keyword_mappings = {
            "murder": ["101", "103"],
            "kill": ["101", "103"],
            "death": ["101", "103"],
            "attempt murder": ["109"],
            "hurt": ["115", "116"],
            "injury": ["115", "116", "117", "118"],
            "assault": ["115", "116", "117", "118"],
            "beat": ["115", "116"],
            "attack": ["115", "116", "117", "118"],
            "rape": ["63", "64"],
            "sexual": ["63", "64", "74", "75", "76"],
            "harassment": ["75", "76", "351", "352"],
            "modesty": ["74", "79"],
            "theft": ["303", "304", "305"],
            "steal": ["303", "304", "305"],
            "stolen": ["303", "304", "305"],
            "rob": ["316", "317"],
            "robbery": ["316", "317"],
            "cheat": ["318", "319", "320"],
            "fraud": ["318", "319", "320"],
            "deceive": ["318", "319", "320"],
            "breach of trust": ["329", "330"],
            "misappropriation": ["322"],
            "extortion": ["309", "310"],
            "blackmail": ["309", "310"],
            "intimidation": ["351", "352"],
            "threat": ["351", "352"],
            "defamation": ["356", "357"],
            "insult": ["356", "357", "79"],
            "forgery": ["336", "337"],
            "fake document": ["336", "337"],
            "bigamy": ["82"],
            "cruelty": ["85"],
            "domestic violence": ["85", "115", "116"],
            "cyberbullying": ["351", "352", "356", "357"],
            "online harassment": ["351", "352", "356", "357"],
            "identity theft": ["318", "319", "320"],
            "phone": ["303", "304", "318", "319", "320"],
            "mobile": ["303", "304", "318", "319", "320"],
            "hacking": ["318", "319", "320"],
            "computer": ["318", "319", "320"],
            "internet": ["318", "319", "320"],
            "online": ["318", "319", "320"],
            "digital": ["318", "319", "320"]
        }
        
        # Find matching keywords
        for keyword, sections in keyword_mappings.items():
            if keyword in query_lower:
                specific_sections.extend(sections)
        
        return list(set(specific_sections))
    
    def get_ipc_to_bns_conversion(self, ipc_section: str) -> Optional[Dict[str, Any]]:
        """Convert IPC section to corresponding BNS section"""
        
        bns_section_num = self.ipc_to_bns_mapping.get(ipc_section)
        
        if bns_section_num and bns_section_num in self.bns_sections:
            bns_section = self.bns_sections[bns_section_num]
            return {
                "ipc_section": ipc_section,
                "bns_section": bns_section_num,
                "title": bns_section["title"],
                "description": bns_section["description"],
                "category": bns_section["category"],
                "conversion_note": f"IPC Section {ipc_section} is now BNS Section {bns_section_num}"
            }
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get BNS database statistics"""
        
        total_sections = len(self.bns_sections)
        domains_covered = len(self.domain_mappings)
        ipc_mappings = len(self.ipc_to_bns_mapping)
        
        return {
            "total_bns_sections": total_sections,
            "domains_covered": domains_covered,
            "ipc_to_bns_mappings": ipc_mappings,
            "domain_list": list(self.domain_mappings.keys())
        }


def create_bns_database() -> BharatiyaNyayaSanhitaDatabase:
    """Factory function to create BNS database"""
    return BharatiyaNyayaSanhitaDatabase()


if __name__ == "__main__":
    print("📚 BHARATIYA NYAYA SANHITA (BNS) 2023 DATABASE")
    print("=" * 60)
    
    bns_db = create_bns_database()
    
    # Show database stats
    stats = bns_db.get_stats()
    print(f"📊 Database Statistics:")
    print(f"   Total BNS Sections: {stats['total_bns_sections']}")
    print(f"   Domains Covered: {stats['domains_covered']}")
    print(f"   IPC to BNS Mappings: {stats['ipc_to_bns_mappings']}")
    print()
    
    # Test domain-based section retrieval
    print("🧪 Testing Domain-Based Section Retrieval:")
    print("-" * 50)
    
    test_cases = [
        ("criminal_law", "theft", "my phone is stolen"),
        ("employment_law", "workplace_harassment", "sexual harassment at work"),
        ("family_law", "domestic_violence", "husband beating wife"),
        ("cyber_crime", "identity_theft", "someone hacked my account")
    ]
    
    for domain, subdomain, query in test_cases:
        print(f"\n🎯 Domain: {domain} | Subdomain: {subdomain}")
        print(f"   Query: \"{query}\"")
        
        sections = bns_db.get_bns_sections_for_domain(domain, subdomain, query)
        
        if sections:
            print(f"   Relevant BNS Sections:")
            for section in sections[:3]:  # Show top 3
                print(f"     • Section {section['section_number']}: {section['title']}")
        else:
            print("   No relevant sections found")
    
    print(f"\n✅ BNS Database ready for integration!")