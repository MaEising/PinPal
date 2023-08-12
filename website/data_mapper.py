from .data_models import PenaltyRecord, Penalty
import random

def map_penalties(all_penalties, quantity=0):
    penalties = []
    for penalty_entity in all_penalties:
        penalties.append(Penalty(penalty_entity.id,penalty_entity.title,penalty_entity.pay_amount,quantity,penalty_entity.invert))
    return penalties

def map_penalty_records(PenaltyRecord_of_player, game_id, all_penalties,participant_total_fine):
    data_penaltyrecords_list = []
    penalties = map_penalties(all_penalties, PenaltyRecord_of_player.quantity)
    data_penaltyrecords_list.append(PenaltyRecord(game_id,penalties,PenaltyRecord_of_player.participant.username, PenaltyRecord_of_player.participant_id,PenaltyRecord_of_player.participant.avatar_index, participant_total_fine))
    return data_penaltyrecords_list

def map_to_game_summary(all_penalty_records_of_player, participant_total_fine):
    list_of_final_penalties = []
    for penaltyrecord in all_penalty_records_of_player:
        penalty_with_quantities = map_penalty_record_for_game_summary(penaltyrecord)
        list_of_final_penalties.append(penalty_with_quantities)
    final_penalty_record = PenaltyRecord(all_penalty_records_of_player[0].game_id,list_of_final_penalties,all_penalty_records_of_player[0].participant.username,all_penalty_records_of_player[0].participant.id,all_penalty_records_of_player[0].participant.avatar_index,participant_total_fine)
    return final_penalty_record

def map_penalty_record_for_game_summary(penalty_record):
    penalty_summary = Penalty(penalty_record.id,penalty_record.penalty.title,penalty_record.penalty.pay_amount,penalty_record.quantity,penalty_record.penalty.invert)
    return penalty_summary