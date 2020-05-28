import argparse
import json
import os

from rosette.api import API, DocumentParameters, RosetteException


def run(key, alt_url='https://api.rosette.com/rest/v1/'):
    """ Run the example """
    # Create an API instance
    api = API(user_key=key, service_url=alt_url)

    # Set selected API options.
    # For more information on the functionality of these
    # and other available options, see Rosette Features & Functions
    # https://developer.rosette.com/features-and-functions#entity-extraction-and-linking

    # api.set_option('calculateSalience','true')
    # api.set_option('linkEntities','false')

    entities_text_data = ("Charlene and Bruce Olson\nolson9family@yahoo.com\nbruce@truestonecoffee.com\n11004 Territorial Dr, Burnsville, MN 55337, "
        "USA\n612-501-6937\n\n8-10 am arrival time\n\n$160 plus tax for the interior and exterior panes of glass as well as the "
        "screens and sills\n\n------\n$160 plus tax = $172.44\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nWindow Cleaning\nFri, "
        "Mar 10 at 09:00 AM (4 hours)\n<A href='http://maps.google.com/?q=11004%20Territorial%20Drive%0ABurnsville,mn%2055337' "
        "target='_blank'>Appointment will be held at: 11004 Territorial Drive\nBurnsville,mn 55337</A>\nNotes\t\t\t\tYou did a "
        "fantastic job last time!  We are putting our house on the market on Monday the 13th so would really appreciate clean "
        "windows!\n\n\nTo make changes to the appointment, please follow this link: "
        "https://www.vcita.com/engagements/haq8bbncx10tsxr8?meeting_action=view&meeting_id=4029aac71f39f3ab&email_token"
        "=37348fc469f7a82fe17b&from_email=true&owner=true&flow=Email_Action&flow_origin=accepted_notification&flow_action"
        "=view_appointment\n\n\nFull details on Charlene Olson, Click Here: https://www.vcita.com/clients/?client=o2pun84hy2c31eb8&flow"
        "=Email_Action&flow_origin=accepted_notification&flow_action=view_contact_details#/o2pun84hy2c31eb8\nEmail\t"
        "\t\t\tolson9family@yahoo.com, Click Here: mailto:olson9family@yahoo.com\nPhone\t\t\t\t612-501-6937\nAddress\t\t\t\t<A "
        "href='http://maps.google.com/?q=11004%20Territorial%20Drive%0ABurnsville,mn%2055337' target='_blank'>"
        "11004 Territorial Drive\nBurnsville,mn 55337</A>\nGender\t\t\t\tFemale\nSource\t\t\t\tLiveSite Widget\n"
        "Facebook Profile, Click Here: https://www.facebook.com/charlene.olson.35\n|")
    params = DocumentParameters()
    params["content"] = entities_text_data
    params["genre"] = "social-media"
    try:
        return api.entities(params)
    except RosetteException as exception:
        print(exception)

PARSER = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Calls the ' +
                                 os.path.splitext(os.path.basename(__file__))[0] + ' endpoint')
PARSER.add_argument('-k', '--key', help='Rosette API Key', required=True)
PARSER.add_argument('-u', '--url', help="Alternative API URL",
                    default='https://api.rosette.com/rest/v1/')

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    RESULT = run('8ef3dd8a2669509d1165bcf5e21596e7', ARGS.url)
    print(json.dumps(RESULT, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8"))