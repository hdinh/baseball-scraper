import sys
from common.domain import *

def _detail_keyword(keyword, detail):
    return keyword in detail

keywords = [
    ['Strikeout', {'ab_type': STRIKEOUT}],
    ['Walk', {'ab_type': WALK}],
    ['Wild Pitch', {'ab_type': WILD_PITCH}],
    ['Hit By Pitch', {'ab_type': HIT_BY_PITCH}],
    ['Groundout', {'ab_type': CONTACT, 'contact_type': GROUND_BALL}],
    ['Ground Ball', {'ab_type': CONTACT, 'contact_type': GROUND_BALL}],
    ['Line Drive', {'ab_type': CONTACT, 'contact_type': LINE_DRIVE}],
    ['Popfly', {'ab_type': CONTACT, 'contact_type': POP_FLY}],
    ['Pop Fly', {'ab_type': CONTACT, 'contact_type': POP_FLY}],
    ['Flyball', {'ab_type': CONTACT, 'contact_type': FLY_BALL}],
    ['Fly Ball', {'ab_type': CONTACT, 'contact_type': FLY_BALL}],
    ['Lineout', {'ab_type': CONTACT, 'contact_type': LINE_OUT}],
    ['Ground-rule Double', {'ab_type': CONTACT, 'contact_type': LINE_DRIVE}],
    ['Bunt to', {'ab_type': BUNT}],
    ['Bunt Popup', {'ab_type': BUNT}],
    ['(Bunt)', {'ab_type': BUNT}],
    ['Defensive Indifference', {'ab_type': DEF_INDIFFERENCE}],
    ['Caught Stealing 2B', {'ab_type': CAUGHT_STEALING, 'sb_attempt_1': 1}],
    ['Caught Stealing 3B', {'ab_type': CAUGHT_STEALING, 'sb_attempt_2': 1}],
    ['Caught Stealing Hm', {'ab_type': CAUGHT_STEALING, 'sb_attempt_3': 1}],
    ['Caught Stealing (PO) 2B', {'ab_type': CAUGHT_STEALING, 'sb_attempt_1': 1}],
    ['Caught Stealing (PO) 3B', {'ab_type': CAUGHT_STEALING, 'sb_attempt_2': 1}],
    ['Caught Stealing (PO) Hm', {'ab_type': CAUGHT_STEALING, 'sb_attempt_3': 1}],
    ['Steals 2B', {'ab_type': STOLE_BASE, 'sb_attempt_1': 1, 'sb_success_1': 1}],
    ['Steals 3B', {'ab_type': STOLE_BASE, 'sb_attempt_1': 2, 'sb_success_2': 1}],
    ['Steals Hm', {'ab_type': STOLE_BASE, 'sb_attempt_1': 3, 'sb_success_3': 1}],
    ['Passed Ball', {'ab_type': PASSED_BALL}],
    ['Baserunner Out Advancing', {'ab_type': BR_OUT_ADVANCING}],
    ['Picked off 1B', {'ab_type': BR_PICKED_OFF}],
    ['Picked off 2B', {'ab_type': BR_PICKED_OFF}],
    ['Picked off 3B', {'ab_type': BR_PICKED_OFF}],
    ["Fielder's Choice", {'ab_type': CONTACT, 'contact_type': GROUND_BALL}],
    ['Reached on Interference', {'ab_type': REACH_ON_INTERFERENCE}],
    ['Balk', {'ab_type': BALK}],
    ['Scores/unER', {'ab_type': UNKNOWN_ERROR}],
    ['/Sacrifice Bunt', {'ab_type': BUNT}],
    ['/Bunt', {'ab_type': BUNT}],
    ['Single to ', {'ab_type': CONTACT, 'contact_type': UNKNOWN_CONTACT_TYPE}],
    ['Triple to ', {'ab_type': CONTACT, 'contact_type': UNKNOWN_CONTACT_TYPE}],
    ['Double', {'ab_type': CONTACT, 'contact_type': UNKNOWN_CONTACT_TYPE}],
    ['Inside-the-park Home Run', {'ab_type': CONTACT}],
]

keywords += [['E%d on Foul Ball' % p, {'ab_type': FOUL_BALL_ERROR}] for p in range(1, 10)]
keywords += [['Adv on E%d' % p, {'ab_type': UNKNOWN_ERROR}] for p in range(1, 10)]
keywords += [['Reached on E%d' % p, {'ab_type': UNKNOWN_ERROR}] for p in range(1, 10)]
keywords += [['Adv on throw to ', {'ab_type': UNKNOWN_ERROR}]]
keywords += [['Safe on E%d' % p, {'ab_type': UNKNOWN_ERROR}] for p in range(1, 10)]

ab_type_extensions = {}
ab_type_extensions[STRIKEOUT] = [
    ['Swinging', {'strikeout_swinging': 1}],
]
ab_type_extensions[WALK] = []
ab_type_extensions[WILD_PITCH] = []
ab_type_extensions[HIT_BY_PITCH] = []
ab_type_extensions[CONTACT] = [['Home Run', {'num_bases_hit': 4, 'hr': 1}]]
ab_type_extensions[CONTACT] += [
    ['%s %s' % (hit_str, pos_str), {'num_bases_hit': hit_bases + 1, 'contact_to_position': pos_num + 1}]
    for hit_bases, hit_str in enumerate(['Single to', 'Double to', 'Triple to'])
    for pos_num, pos_str in enumerate(POSITIONS)
]
ab_type_extensions[BUNT] = []
ab_type_extensions[CAUGHT_STEALING] = []
ab_type_extensions[STOLE_BASE] = []
ab_type_extensions[PASSED_BALL] = []
ab_type_extensions[DEF_INDIFFERENCE] = []
ab_type_extensions[BR_OUT_ADVANCING] = []
ab_type_extensions[BR_PICKED_OFF] = []
ab_type_extensions[REACH_ON_INTERFERENCE] = []
ab_type_extensions[BALK] = []
ab_type_extensions[FOUL_BALL_ERROR] = []
ab_type_extensions[UNKNOWN_ERROR] = []

def _part_to_map(detail):
    for kw, kw_result in keywords:
        if _detail_keyword(kw, detail):
            return kw_result
    return None

def parse(detail):
    part_map = {}

    # get ab_type
    try:
        for part in detail.split(';'):
            for ppart in part.split(','):
                m = _part_to_map(ppart)
                if m:
                    part_map.update(m)
                    break

        # extend
        for part in detail.split(';'):
            for ppart in part.split(','):
                for ppart_extension in ab_type_extensions[part_map['ab_type']]:
                    m = _part_to_map(ppart_extension)
                    if m:
                        part_map.update(m)
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
        pass

    return part_map

if __name__ == '__main__':
    _, detail = sys.argv
    print(parse(detail))
