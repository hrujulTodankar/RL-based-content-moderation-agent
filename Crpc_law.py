"""
Code of Criminal Procedure (CrPC) 1973 Database
==============================================

This file contains structured data for the Code of Criminal Procedure, 1973.
Each section includes title, content, and category for legal content moderation.

Author: Legal Content Moderation System
Version: 1.0.0
"""

class CrpcDatabase:
    """Database class for Code of Criminal Procedure sections"""

    def __init__(self):
        self.sections = {
            "1": {
                "title": "Short title, extent and commencement",
                "content": "This Act may be called the Code of Criminal Procedure, 1973. It extends to the whole of India except the State of Jammu and Kashmir: Provided that the provisions of this Code, other than those relating to Chapters VIII, X and XI thereof, shall not apply to the State of Nagaland, tribal areas, etc.",
                "category": "Preliminary"
            },
            "2": {
                "title": "Definitions",
                "content": "In this Code, unless the context otherwise requires, the definitions given in this section shall apply to the expressions used in the Code.",
                "category": "Preliminary"
            },
            "4": {
                "title": "Trial of offences under the Indian Penal Code and other laws",
                "content": "All offences under the Indian Penal Code shall be investigated, inquired into, tried, and otherwise dealt with according to the provisions of this Code.",
                "category": "Preliminary"
            },
            "5": {
                "title": "Saving",
                "content": "Nothing contained in this Code shall, in the absence of a specific provision to the contrary, affect any special or local law now in force, or any special jurisdiction or power conferred, or any special form of procedure prescribed, by any other law for the time being in force.",
                "category": "Preliminary"
            },
            "6": {
                "title": "Classes of Criminal Courts",
                "content": "Besides the High Courts and the Courts constituted under any law, other than this Code, there shall be, in every State, the following classes of Criminal Courts, namely: (i) Courts of Session; (ii) Judicial Magistrates of the first class and, in any metropolitan area, Metropolitan Magistrates; (iii) Judicial Magistrates of the second class; and (iv) Executive Magistrates.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "7": {
                "title": "Territorial divisions",
                "content": "Every State shall be a sessions division or shall consist of sessions divisions; and every sessions division shall, for the purposes of this Code, be a district or consist of districts.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "8": {
                "title": "Metropolitan areas",
                "content": "The State Government may, by notification, declare that, as from such date as may be specified in the notification, any area in the State comprising a city or town whose population exceeds one million shall be a metropolitan area for the purposes of this Code.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "9": {
                "title": "Court of Session",
                "content": "The State Government shall establish a Court of Session for every sessions division; and the Court of Session shall consist of a Judge appointed by the High Court for such division.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "10": {
                "title": "Subordination of Judicial Magistrates",
                "content": "All Judicial Magistrates appointed under this Chapter shall be subordinate to the Sessions Judge; and he may, from time to time, make rules consistent with this Code as to the distribution of business among such Magistrates.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "11": {
                "title": "Chief Judicial Magistrate and Additional Chief Judicial Magistrate, etc.",
                "content": "In every district (not being a metropolitan area), the High Court shall appoint a Judicial Magistrate of the first class to be the Chief Judicial Magistrate.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "12": {
                "title": "Special Judicial Magistrates",
                "content": "The State Government may, if requested by the Central Government, confer upon any person who holds or has held any office under the Government all or any of the powers conferred or conferrable by or under this Code on a Judicial Magistrate of the first class or of the second class.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "13": {
                "title": "Local Jurisdiction of Judicial Magistrates",
                "content": "Subject to the control of the High Court, every Judicial Magistrate may exercise his powers within the local limits of his jurisdiction.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "14": {
                "title": "Place of sitting",
                "content": "Subject to the provisions of this Code, every Judge or Magistrate shall hold his Court in some building provided for the purpose by the State Government.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "15": {
                "title": "Courts open to public",
                "content": "The place in which any Criminal Court is held for the purpose of inquiring into or trying any offence shall be deemed to be an open Court, to which the public generally may have access, so far as the same can conveniently contain them.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "16": {
                "title": "Court to be open from day to day",
                "content": "Every Criminal Court shall sit on all days in the week except such days as the State Government may, by notification, appoint to be holidays.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "17": {
                "title": "Language of Courts",
                "content": "The State Government may determine what shall be, for purposes of this Code, the language of each Court within the State other than the High Court.",
                "category": "Constitution of Criminal Courts and Offices"
            },
            "18": {
                "title": "Persons who may be arrested without warrant",
                "content": "Any police officer may, without an order from a Magistrate and without a warrant, arrest any person who commits, in the presence of a police officer, a cognizable offence.",
                "category": "Arrest of Persons"
            },
            "19": {
                "title": "Arrest how made",
                "content": "Every police officer or other person arresting any person under the previous section shall actually touch or confine the body of the person to be arrested, unless there be a submission to the custody by word or action.",
                "category": "Arrest of Persons"
            },
            "20": {
                "title": "Search of place entered by person sought to be arrested",
                "content": "If any person acting under a warrant of arrest, or any police officer having authority to arrest, has reason to believe that the person to be arrested has entered into or is within any place, the person residing in or being in charge of such place shall, on demand of such person acting as aforesaid or such police officer, allow him free ingress thereto, and afford all reasonable facilities for a search therein.",
                "category": "Arrest of Persons"
            },
            "21": {
                "title": "Search of arrested person",
                "content": "Whenever a person is arrested by a police officer under a warrant which does not provide for the taking of bail, or under a warrant which provides for the taking of bail but the person arrested cannot furnish bail, the officer shall search such person.",
                "category": "Arrest of Persons"
            },
            "22": {
                "title": "Power to seize offensive weapons",
                "content": "The police officer or other person making any arrest under this Code may take from the person arrested any offensive weapons which he may have about his person, and shall deliver all weapons so taken to the Court or officer before which or whom the officer or person making the arrest is required by this Code to produce the person arrested.",
                "category": "Arrest of Persons"
            },
            "23": {
                "title": "Examination of arrested person by medical officer",
                "content": "When any person is arrested, he shall be examined by a medical officer in the service of the Central or State Government, and in case the medical officer is not available, by a registered medical practitioner appointed by the State Government for that purpose.",
                "category": "Arrest of Persons"
            },
            "24": {
                "title": "No unnecessary restraint",
                "content": "The person arrested shall not be subjected to more restraint than is necessary to prevent his escape.",
                "category": "Arrest of Persons"
            },
            "25": {
                "title": "Search of place suspected to contain stolen property, etc.",
                "content": "Any police officer, making an investigation, may search any place in which he suspects any articles or things used or likely to be used in the commission of an offence may be, or that any person so concerned in the commission of an offence may be found.",
                "category": "Arrest of Persons"
            },
            "26": {
                "title": "Power to require attendance of prisoners",
                "content": "Whenever, in the course of an inquiry, trial or other proceeding under this Code, it appears to a Criminal Court that a person confined or detained in a prison should be brought before the Court for answering to a charge of an offence, or for any other purpose, the Court may make an order requiring the officer in charge of the prison to bring such person before it.",
                "category": "Arrest of Persons"
            },
            "27": {
                "title": "Search of persons in prison",
                "content": "Whenever any person is sent to any prison under a warrant of commitment, the officer in charge of the prison shall search such person, and any article or thing found upon his person shall be taken from him, and shall be placed in the custody of the officer in charge of the prison.",
                "category": "Arrest of Persons"
            },
            "28": {
                "title": "Examination of witnesses by police",
                "content": "Any police officer making an investigation under this Chapter, or any police officer not below such rank as the State Government may, by general or special order, prescribe in this behalf, acting on the requisition of such officer, may examine orally any person supposed to be acquainted with the facts and circumstances of the case.",
                "category": "Processes to Compel Appearance"
            },
            "29": {
                "title": "Police officer's power to require attendance of witnesses",
                "content": "Any police officer making an investigation under this Chapter may, by order in writing, require the attendance before himself of any person being within the limits of his own or any adjoining station who, from the information given or otherwise, appears to be acquainted with the circumstances of the case.",
                "category": "Processes to Compel Appearance"
            },
            "30": {
                "title": "Power of police to seize property associated with offence",
                "content": "Any police officer may seize any property which may be alleged or suspected to have been stolen or which may be found under circumstances which create suspicion of the commission of any offence.",
                "category": "Processes to Compel Appearance"
            },
            "31": {
                "title": "Summons how served",
                "content": "Every summons issued by a Court under this Code shall be in writing, in duplicate, and shall bear the seal of the Court.",
                "category": "Processes to Compel Appearance"
            },
            "32": {
                "title": "Summons to produce document or other thing",
                "content": "Whenever any Court or any officer in charge of a police station considers that the production of any document or other thing is necessary or desirable for the purposes of any investigation, inquiry, trial or other proceeding under this Code by or before such Court or officer, such Court may issue a summons, or such officer a written order, to the person in whose possession or power such document or thing is believed to be, requiring him to attend and produce it, or to produce it, at the time and place stated in the summons or order.",
                "category": "Processes to Compel Appearance"
            },
            "33": {
                "title": "Warrant of arrest",
                "content": "Every warrant of arrest issued by a Court under this Code shall be in writing, signed by the presiding officer of such Court, and shall bear the seal of the Court.",
                "category": "Processes to Compel Appearance"
            },
            "34": {
                "title": "Warrant of arrest to whom directed",
                "content": "A warrant of arrest shall ordinarily be directed to one or more police officers; but the Court issuing such a warrant may, if its immediate execution is necessary and no police officer is immediately available, direct it to any other person or persons, and such person or persons shall execute the same.",
                "category": "Processes to Compel Appearance"
            },
            "35": {
                "title": "Warrant may be directed to landholders, etc.",
                "content": "When a warrant is directed to a landholder, farmer or cultivator, it may require him to use due diligence in preventing the escape of the person to be arrested.",
                "category": "Processes to Compel Appearance"
            },
            "36": {
                "title": "Warrant directed to police officer",
                "content": "A warrant directed to any police officer may also be executed by any other police officer whose name is endorsed upon the warrant by the officer to whom it is directed or endorsed.",
                "category": "Processes to Compel Appearance"
            },
            "37": {
                "title": "Warrant how endorsed",
                "content": "When a warrant directed to a police officer is to be executed outside the local limits of his jurisdiction, he shall take it for endorsement to a Magistrate within the local limits of whose jurisdiction it is to be executed.",
                "category": "Processes to Compel Appearance"
            },
            "38": {
                "title": "Warrant on endorsement, executable anywhere",
                "content": "Any warrant endorsed in accordance with the foregoing provisions may be executed by the police officer to whom it is endorsed anywhere within the local limits of the jurisdiction of the Court which issued the warrant.",
                "category": "Processes to Compel Appearance"
            },
            "39": {
                "title": "Warrant forwarded for execution outside jurisdiction",
                "content": "When a warrant is to be executed outside the local limits of the jurisdiction of the Court issuing the same, such Court may, instead of directing the warrant to a police officer within those limits, forward it by post or otherwise to any Executive Magistrate or District Superintendent of Police within the local limits of whose jurisdiction it is to be executed.",
                "category": "Processes to Compel Appearance"
            },
            "40": {
                "title": "Warrant addressed to police officer for execution outside jurisdiction",
                "content": "When a warrant addressed to a police officer is received by him for execution outside the local limits of his jurisdiction, he shall endorse his name thereon and cause it to be executed.",
                "category": "Processes to Compel Appearance"
            },
            "41": {
                "title": "When police may arrest without warrant",
                "content": "Any police officer may without an order from a Magistrate and without a warrant, arrest any person who commits, in the presence of a police officer, a cognizable offence, or against whom a reasonable complaint has been made, or credible information has been received, or a reasonable suspicion exists that he has committed a cognizable offence punishable with imprisonment for a term which may be less than seven years or which may extend to seven years whether with or without fine.",
                "category": "Arrest of Persons"
            },
            "41A": {
                "title": "Notice of appearance before police officer",
                "content": "Where any person, against whom a reasonable complaint has been made or credible information has been received, or a reasonable suspicion exists that he has committed a cognizable offence punishable with imprisonment for a term which may be less than seven years or which may extend to seven years whether with or without fine, the officer in charge of a police station shall issue a notice directing such person to appear before him or at such other place as may be specified in the notice.",
                "category": "Arrest of Persons"
            },
            "41B": {
                "title": "Procedure of arrest and duties of officer making arrest",
                "content": "Every police officer while making an arrest shall bear an accurate, visible and clear identification of his name which will facilitate easy identification, an undertaking shall be signed by the police officer to that effect, and he shall prepare a memorandum of arrest which shall be attested by at least one witness who is a member of the family of the person arrested or a respectable member of the locality where the arrest is made.",
                "category": "Arrest of Persons"
            },
            "41C": {
                "title": "Control room at districts",
                "content": "The State Government shall establish a police control room in every district and at State level to monitor and prevent illegal detention and torture of persons in custody.",
                "category": "Arrest of Persons"
            },
            "41D": {
                "title": "Right of arrested person to meet an advocate of his choice during interrogation",
                "content": "When any person is arrested and interrogated by the police, he shall be entitled to meet an advocate of his choice during interrogation, though not throughout interrogation.",
                "category": "Arrest of Persons"
            },
            "42": {
                "title": "Arrest on refusal to give name and residence",
                "content": "When any person who, in the presence of a police officer, has committed or has been accused of committing a non-cognizable offence refuses, on demand of such officer, to give his name and residence, or gives a name or residence which such officer has reason to believe to be false, he may be arrested by such officer in order that his name or residence may be ascertained.",
                "category": "Arrest of Persons"
            },
            "43": {
                "title": "Arrest by private person and procedure on such arrest",
                "content": "Any private person may arrest or cause to be arrested any person who, in his presence, commits a non-bailable and cognizable offence, or any proclaimed offender, and, without unnecessary delay, shall make over or cause to be made over any person so arrested to a police officer, or, in the absence of a police officer, take such person or cause him to be taken in custody to the nearest police station.",
                "category": "Arrest of Persons"
            },
            "44": {
                "title": "Arrest by Magistrate",
                "content": "When any offence is committed in the presence of a Magistrate, whether Executive or Judicial, within his local jurisdiction, he may himself arrest or order any person to arrest the offender, and may thereupon, subject to the provisions herein contained as to bail, commit the offender to custody.",
                "category": "Arrest of Persons"
            },
            "45": {
                "title": "Protection of members of the Armed Forces from arrest",
                "content": "Notwithstanding anything contained in sections 41 to 44 (both inclusive), no member of the Armed Forces of the Union shall be arrested for anything done or purported to be done by him in the discharge of his official duties except after obtaining the consent of the Central Government.",
                "category": "Arrest of Persons"
            },
            "46": {
                "title": "Arrest how made",
                "content": "In making an arrest the police officer or other person making the same shall actually touch or confine the body of the person to be arrested, unless there be a submission to the custody by word or action: Provided that where a woman is to be arrested, unless the circumstances indicate to the contrary, her submission to custody on an oral intimation of arrest shall be presumed and, unless the circumstances otherwise require or unless the police officer is a female, the police officer shall not touch the person of the woman for making her arrest.",
                "category": "Arrest of Persons"
            },
            "47": {
                "title": "Search of place entered by person sought to be arrested",
                "content": "If any person acting under a warrant of arrest, or any police officer having authority to arrest, has reason to believe that the person to be arrested has entered into or is within any place, the person residing in or being in charge of such place shall, on demand of such person acting as aforesaid or such police officer, allow him free ingress thereto, and afford all reasonable facilities for a search therein.",
                "category": "Arrest of Persons"
            },
            "48": {
                "title": "Pursuit of offenders into other jurisdictions",
                "content": "A police officer may, for the purpose of arresting without warrant any person whom he is authorized to arrest, pursue such person into any place in India.",
                "category": "Arrest of Persons"
            },
            "49": {
                "title": "No unnecessary restraint",
                "content": "The person arrested shall not be subjected to more restraint than is necessary to prevent his escape.",
                "category": "Arrest of Persons"
            },
            "50": {
                "title": "Person arrested to be informed of grounds of arrest and of right to bail",
                "content": "Every police officer or other person arresting any person without warrant shall forthwith communicate to him full particulars of the offence for which he is arrested or other grounds for such arrest.",
                "category": "Arrest of Persons"
            },
            "50A": {
                "title": "Obligation of person making arrest to inform about the arrest, etc., to a nominated person",
                "content": "Every police officer or other person making arrest shall forthwith give the information regarding such arrest and place where the arrested person is being held to any of his friends, family members or any other person as may be nominated by the arrested person for the purpose of giving such information.",
                "category": "Arrest of Persons"
            },
            "51": {
                "title": "Search of arrested person",
                "content": "Whenever a person is arrested by a police officer under a warrant which does not provide for the taking of bail, or under a warrant which provides for the taking of bail but the person arrested cannot furnish bail, the officer shall search such person, and shall place in safe custody all articles, except necessary wearing apparel, found upon him and where any article is seized from the arrested person, a receipt showing the articles taken in possession shall be given to such person.",
                "category": "Arrest of Persons"
            },
            "52": {
                "title": "Power to seize offensive weapons",
                "content": "The police officer or other person making any arrest under this Code may take from the person arrested any offensive weapons which he may have about his person, and shall deliver all weapons so taken to the Court or officer before which or whom the officer or person making the arrest is required by this Code to produce the person arrested.",
                "category": "Arrest of Persons"
            },
            "53": {
                "title": "Examination of arrested person by medical officer",
                "content": "When any person is arrested, he shall be examined by a medical officer in the service of the Central or State Government, and in case the medical officer is not available, by a registered medical practitioner appointed by the State Government for that purpose, and in either case, the medical officer or registered medical practitioner shall report to the Magistrate, without delay, the result of his examination.",
                "category": "Arrest of Persons"
            },
            "53A": {
                "title": "Examination of person accused of rape by medical practitioner",
                "content": "When a person is arrested on a charge of committing an offence of rape or an attempt to commit rape and there are reasonable grounds for believing that an examination of his person will afford evidence as to the commission of such offence, it shall be lawful for a registered medical practitioner employed in a hospital run by the Government or by a local authority and in the absence of such a practitioner within the radius of sixteen kilometers from the place where the offence has been committed, by any other registered medical practitioner acting at the request of a police officer not below the rank of sub-inspector, and for any person acting in good faith in his aid and under his direction, to make such an examination of the arrested person and to use such force as is reasonably necessary for that purpose.",
                "category": "Arrest of Persons"
            },
            "54": {
                "title": "Examination of arrested person by medical officer at the request of the arrested person",
                "content": "When a person who is arrested, whether on a charge or otherwise, alleges that he has been subjected to physical or mental torture during arrest or during custody, he shall be entitled to be examined by a medical officer.",
                "category": "Arrest of Persons"
            },
            "55": {
                "title": "Procedure when police officer deputes subordinate to arrest without warrant",
                "content": "When any officer in charge of a police station or any police officer making an investigation under Chapter XII requires any officer subordinate to him to arrest without a warrant (otherwise than in his presence) any person who may lawfully be arrested without a warrant, he shall deliver to the officer required to make the arrest an order in writing, specifying the person to be arrested and the offence or other cause for which the arrest is to be made and the officer so required shall, before making the arrest, notify to the person to be arrested the substance of the order and, if so required by such person, shall show him the order.",
                "category": "Arrest of Persons"
            },
            "56": {
                "title": "Person arrested to be taken before Magistrate or officer in charge of police station",
                "content": "A police officer making an arrest without warrant shall, without unnecessary delay and subject to the provisions herein contained as to bail, take or send the person arrested before a Magistrate having jurisdiction in the case, or before the officer in charge of a police station.",
                "category": "Arrest of Persons"
            },
            "57": {
                "title": "Person arrested not to be detained more than twenty-four hours",
                "content": "No police officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not, in the absence of a special order of a Magistrate under section 167, exceed twenty-four hours exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court.",
                "category": "Arrest of Persons"
            },
            "58": {
                "title": "Police to report apprehensions",
                "content": "Officers in charge of police stations shall report to the District Magistrate, or, if he so directs, to the Sub-divisional Magistrate, the cases of all persons arrested without warrant, within the limits of their respective stations, whether such persons have been admitted to bail or otherwise.",
                "category": "Arrest of Persons"
            },
            "59": {
                "title": "Release on bail",
                "content": "When any person accused of or suspected of the commission of any non-bailable offence is arrested or detained without warrant by an officer in charge of a police station, or appears or is brought before a Court, and is prepared to give bail, he may be released on bail.",
                "category": "Arrest of Persons"
            },
            "60": {
                "title": "Bond of person released on bail",
                "content": "Before any person is released on bail or released on his own bond, a bond for such sum of money as the police officer or Court, as the case may be, thinks sufficient shall be executed by such person, and when he is released on bail by a police officer it shall be countersigned by a Magistrate.",
                "category": "Arrest of Persons"
            },
            "61": {
                "title": "Cancellation of bond and bail-bond",
                "content": "Any Court may cancel any bond for appearance or bail-bond on the application of the person who has executed such bond or bail-bond, or without such application in the following circumstances: (a) if it is proved to the satisfaction of the Court that the person who has executed the bond has absconded, or is about to abscond; (b) if the address of the person who has executed the bond is not known to the Court; (c) if the person who has executed the bond is of such character that his appearance at the hearing is unlikely; (d) if the bond has been executed by a person who has no means to pay the amount mentioned in the bond; (e) if the bond is for an amount which is excessive.",
                "category": "Arrest of Persons"
            }
        }

def create_crpc_database():
    """Create and return CrPC database instance"""
    return CrpcDatabase()

# Example usage
if __name__ == "__main__":
    crpc_db = create_crpc_database()
    print(f"Loaded {len(crpc_db.sections)} CrPC sections")

    # Print sample sections
    for section_num in ["1", "41", "41A", "46"]:
        if section_num in crpc_db.sections:
            section = crpc_db.sections[section_num]
            print(f"\nSection {section_num}: {section['title']}")
            print(f"Category: {section['category']}")
            print(f"Content: {section['content'][:100]}...")