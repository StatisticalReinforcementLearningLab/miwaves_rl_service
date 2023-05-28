# src/server/update.py

# Imports
import csv
import datetime
import src.algorithm
import requests

from src.server import app, db

from src.server.tables import (
    User,
    UserStatus,
    AlgorithmStatus,
    RLWeights,
    RLActionSelection,
    UserStudyPhaseEnum,
)

# def get_latest_data() -> None:
#     """
#     Gets the latest data from the backend api
#     and updates the database
#     """

#     try:
#         # Get the latest ema data from the backend api
#         ema_url = app.config.get('EMA_API')

#         # Iterate over all the users in userstatus tables
#         for user in UserStatus.query.all():

#             if user.user_study_phase != UserStudyPhaseEnum.STARTED:
#                 continue

#             # Get used id
#             user_id = user.id

#             # Create payload for the backend api
#             payload = {
#                 'user_id': user_id
#             }

#             # Get the latest ema data for the user from the backend api
#             data = requests.get(ema_url, params=payload).json()

#             # Get the ema data from the response
#             ema_data = data['ema_data']

#             # Check if the ema data is empty
#             if not ema_data:
#                 pass
#             else:
#                 # Iterate over all the decision points in each day of the ema data
#                 for key, value in ema_data.items():
#                     # Get the decision point
#                     decision_point_idx = key

#                     # Get the decision point data
#                     decision_point_data = value

#                     # Get the data fields from the decision point data
#                     date = decision_point_data['date']
#                     time = decision_point_data['time'] # morning or evening

#                     # TODO: Complete the rest


            
#             # Get the latest user's study phase from the backend api
#             try:
#                 study_phase = data['study_phase']

#                 if not study_phase:
#                     pass
#                 else:
#                     # Update the user's study phase in the database
#                     if study_phase == 'started':
#                         user.user_study_phase = UserStudyPhaseEnum.STARTED
#                     elif study_phase == 'ended':
#                         user.user_study_phase = UserStudyPhaseEnum.ENDED
#             except Exception as e:
#                 # If DEBUG is True, print the error
#                 if app.config.get('DEBUG'):
#                     print(e)
#                 pass
            
     

#     except Exception as e:
#         if app.config.get('DEBUG'):
#             print(e)
#         return

def update_algorithm() -> None:
    """Updates the algorithm to the latest version"""
    # Get the algorithm
    algo = app.config.get('ALGORITHM')
    
    # Get the latest data from the backend api
    # try:
    #     get_latest_data()
    # except Exception as e:
    #     print(e)
    #     return