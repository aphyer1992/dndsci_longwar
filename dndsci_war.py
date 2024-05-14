import math
import random
global_aliens = [
    {'Name' : 'Arachnoid Abomination', 'Health' : 9, 'Threat' : 4},
    {'Name' : 'Chitinous Crawler', 'Health' : 3, 'Threat' : 2},
    {'Name' : 'Swarming Scarab', 'Health' : 1, 'Threat' : 1},
    {'Name' : 'Towering Tyrant', 'Health' : 15, 'Threat' : 5},
    {'Name' : 'Voracious Venompede', 'Health' : 5, 'Threat' : 3},
    ]

global_weapons = [
    {'Name' : 'Antimatter Artillery', 'Shots' : [1,2], 'Damage' : 20},
    {'Name' : 'Fusion Flamethrower', 'Shots' : [3,12], 'Damage' : 1} ,
    {'Name' : 'Gluon Grenades', 'Shots' : [2,3], 'Damage' : 7},
    {'Name' : 'Laser Lance', 'Shots' : [2,5], 'Damage' : 5},
    {'Name' : 'Macross Minigun', 'Shots' : [5,8], 'Damage' : 1} ,
    {'Name' : 'Pulse Phaser', 'Shots' : [4,6], 'Damage' : 2},
    {'Name' : 'Rail Rifle', 'Shots' : [3,5], 'Damage' : 3},
    {'Name' : 'Thermo-Torpedos', 'Shots' : [1,3], 'Damage' : 13},
]


global_threat_weight = 4
global_alien_strength = 0
max_num = 20


def vals_to_structure(vals):
    vals.sort()
    vals_dict = {}
    for i in range(1, max_num + 1):
        vals_dict[i] = 0
    for v in vals:
        vals_dict[v] = vals_dict[v] + 1
    vals_dict['max'] = max(vals)
    vals_dict['min'] = min(vals)
    vals_dict['count'] = len(vals)
    vals_dict['sum'] = sum(vals)
    return(vals_dict)

def shots_from_weapon(weapon_name, pessimize=False, optimize=False):
    weapon_details = [w for w in global_weapons if w['Name'] == weapon_name][0]
    [min_shots, max_shots] = weapon_details['Shots']
    if pessimize:
        return(min_shots)
    elif optimize:
        return(max_shots)
    else:
        return(random.choice(range(min_shots, max_shots + 1 )))

def shots_from_weapons(weapon_names, pessimize=False, optimize=False):
    shots = []
    for weapon_name in weapon_names:
        weapon_details = [w for w in global_weapons if w['Name'] == weapon_name][0]
        shots = shots + [ weapon_details['Damage'] ] * shots_from_weapon(weapon_name, pessimize, optimize)

    return(shots)

def struct_from_weapons(weapon_names, pessimize=False, optimize=False):
    shots = shots_from_weapons(weapon_names, pessimize, optimize)
    struct = vals_to_structure(shots)
    return(struct)

def healths_from_aliens(alien_list):
    healths = []
    for alien in alien_list:
        alien_details = [a for a in global_aliens if a['Name'] == alien][0]
        healths.append(alien_details['Health'])
    return(healths)

def struct_from_aliens(alien_list):
    healths = healths_from_aliens(alien_list)
    struct = vals_to_structure(healths)
    return(struct)


def gen_alien_wave():
    aliens = []
    for a in global_aliens:
        temp = (random.random() * 100) - 50 + global_alien_strength
        if temp > 0:
            to_add = math.ceil(pow((temp / a['Health']), 0.5))
            for i in range(to_add):
                aliens.append(a['Name'])

    return(aliens)

def alien_wave_threat(alien_list):
    threat = 0
    for alien in alien_list:
        alien_details = [a for a in global_aliens if a['Name'] == alien][0]
        threat = threat + alien_details['Threat']
    return(threat)

def gen_squad(threat):
    threat_weight = global_threat_weight - (2 * random.random()) + (2 * random.random())
    soldiers_base = (threat / threat_weight)
    soldiers = math.floor(soldiers_base)
    if random.random() < (soldiers_base - soldiers):
        soldiers = soldiers + 1
    if soldiers == 0:
        soldiers = soldiers + 1
    weapons = []
    while soldiers >= 2:
        soldiers = soldiers - 2
        squad_weapons = random.sample(global_weapons, 2)
        for w in squad_weapons:
            weapons.append(w['Name'])

    remaining_weapons = random.sample(global_weapons, soldiers)
    for w in remaining_weapons:
        weapons.append(w['Name'])

    return(weapons)

def struct_remove(struct, value):
    struct[value] = struct[value] - 1
    struct['count'] = struct['count'] - 1
    struct['sum'] = struct['sum'] - value
    if struct[value] == 0 and struct['count'] > 0:
        if value == struct['max']:
            while struct[struct['max']] == 0:
                struct['max'] = struct['max'] - 1
        if value == struct['min']:
            while struct[struct['min']] == 0:
                struct['min'] = struct['min'] + 1
    return(struct)

def struct_add(struct, value):
    struct[value] = struct[value] + 1
    struct['count'] = struct['count'] + 1
    struct['sum'] = struct['sum'] - value
    struct['max'] = max(struct['max'], value)
    struct['min'] = min(struct['min'], value)
    return(struct)

def easy_decisions(shots_struct, healths_struct):
    # exact kills are always good
    for k in range(1, max_num + 1):
        while shots_struct[k] > 0 and healths_struct[k] > 0:
            shots_struct = struct_remove(shots_struct, k)
            healths_struct = struct_remove(healths_struct, k)

    # one-shotting the strongest alien is good
    while (healths_struct['max'] <= shots_struct['max']) and healths_struct['count'] > 0 and shots_struct['count'] > 0:
        healths_struct = struct_remove(healths_struct, healths_struct['max'])
        shots_struct = struct_remove(shots_struct, shots_struct['max'])

    # one-shotting with our weakest weapon is good
    while (healths_struct['min'] <= shots_struct['min']) and healths_struct['count'] > 0 and shots_struct['count'] > 0:
        healths_struct = struct_remove(healths_struct, healths_struct['min'])
        shots_struct = struct_remove(shots_struct, shots_struct['min'])

    return((shots_struct, healths_struct))

def eval_win(shots_struct, healths_struct, depth=1):
    #print('Comparing at depth {}'.format(depth))
    #print(shots_struct)
    #print(healths_struct)
    #Taking easy shots
    (shots_struct, healths_struct) = easy_decisions(shots_struct, healths_struct)
    #print('After easy decisions...')
    #print(shots_struct)
    #print(healths_struct)
    #Checking for clear resolutions
    if healths_struct['count'] == 0:
        #print('Found win at depth {}'.format(depth))
        return depth
    if shots_struct['count'] < healths_struct['count']:
        return -1
    if shots_struct['sum'] < healths_struct['sum']:
        return -1

    # things we could do with the strongest weapon:
    strongest_weapon = shots_struct['max']
    highest_oneshot = None
    partial_damage = []
    for k in range(1, max_num + 1):
        if healths_struct[k] > 0:
            if k > strongest_weapon:
                partial_damage.append(k)
            else:
                highest_oneshot = k
    possible_targets = partial_damage
    if highest_oneshot is not None:
        possible_targets.append(highest_oneshot)

    shots_struct = struct_remove(shots_struct, strongest_weapon)

    for p in possible_targets:
        healths_temp = healths_struct.copy()
        healths_temp = struct_remove(healths_temp, p)
        if p > strongest_weapon:
            healths_temp = struct_add(healths_temp, p - strongest_weapon)
        result = eval_win(shots_struct, healths_temp, depth + 1)
        if result > 0:
            return result
    return -1

def write_log_row(log_row, mode='a'):
        log_string = ','.join([str(e) for e in log_row])+"\n"
        f = open('war_output.csv', mode)
        f.write(log_string)

def setup_logs():
    
    row = []
    for a in global_aliens:
        row.append(a['Name'])
    for w in global_weapons:
        row.append(w['Name'])
    row.append('Soldiers')
    row.append("Glorious Victory for Freedom and Democracy?")
    row.append('Threat')
    row.append('Ratio')
    write_log_row(row, mode='w')

def squad_vs_wave(squad, alien_wave, pessimize=False, optimize=False):
    healths_struct = struct_from_aliens(alien_wave)
    shots_struct = struct_from_weapons(squad, pessimize, optimize)

    result = eval_win(shots_struct, healths_struct)
    return(result)

def eval_wave():
    alien_wave = gen_alien_wave()
    threat = alien_wave_threat(alien_wave)
    if len(alien_wave) == 0:
        return()

    squad = gen_squad(threat)
    result = squad_vs_wave(squad, alien_wave)

    row = []
    for a in global_aliens:
        row.append(len([s for s in alien_wave if s==a['Name']]))

    for w in global_weapons:
        row.append(len([s for s in squad if s==w['Name']]))
    row.append(len(squad))
    if result > 0:
        row.append('Yes')
    else:
        row.append('No')
    row.append(threat)
    row.append(threat/len(squad))
    write_log_row(row)
    return(result)

def get_possible_squads(num_soldiers, possible_weapons=None):
    if possible_weapons is None:
        possible_weapons = [w['Name'] for w in global_weapons]
    #print(num_soldiers)
    #print(possible_weapons)

    if num_soldiers == 0:
        return([[]])

    if len(possible_weapons) == 1:
        return([[possible_weapons[0]]*num_soldiers])

    squads = []
    focus_weapon = possible_weapons[0]
    other_weapons = possible_weapons[1:]
    for i in range(num_soldiers + 1):
        focus_array = [focus_weapon]*i
        remain_poss = get_possible_squads(num_soldiers-i, other_weapons)
        for r in remain_poss:
            squads.append(focus_array + r)
    return(squads)

def consider_wave_vs_number(alien_wave, number, verbose=False):
    squads = get_possible_squads(number)
    auto_win = 0
    avg_win = 0
    runs_per_squad = min(math.ceil(1e6 / pow(2,number)), 5000)
    best_rate = 0
    best_rate_squad = None
    for squad in squads:
        squad_rate = 0
        for i in range(runs_per_squad):
            result = squad_vs_wave(squad, alien_wave)
            if result > 0:
                squad_rate = squad_rate + (1/runs_per_squad)
        avg_win = avg_win + squad_rate
        if squad_rate > best_rate:
            best_rate = squad_rate
            best_rate_squad = squad
        result2 = squad_vs_wave(squad, alien_wave, pessimize=True)
        if result2 > 0:
            auto_win = auto_win + 1
            #print(squad)
            winner = squad

    win_rate = avg_win / len(squads)
    if auto_win >= 1:
        best_rate_squad = winner
    if auto_win == 1:
        champ = winner
    else:
        champ = None
    if verbose:
        print('Of {} squads with size {}, {:.2f}% average winrate and {} auto wins.  Best squad found won {:.2f}%:'.format(len(squads), number, 100*win_rate, auto_win, best_rate * 100))
        print(best_rate_squad)
    return(win_rate, champ, auto_win)

def consider_wave(alien_wave):
    if len(alien_wave) == 0:
        return()
    threat = alien_wave_threat(alien_wave)
    #print('Considering alien wave:')
    #print(alien_wave)
    verbose = False
    for i in range(1, 11):
        #print("Considering squads of {}".format(i))
        (win_rate, champ, auto_win) = consider_wave_vs_number(alien_wave, i)
        if verbose == True:
            print('Average win rate with {} soldiers is {:.2f}%'.format(i, 100* win_rate))

        if champ is not None:
            print('POTENTIAL HIT!\n')
            print(alien_wave)
            print('With {} soldiers there is one winning team:'.format(i))
            print(champ)
            break
        if champ is None and auto_win > 0 and (verbose == False or win_rate > 0.95):
            break


def expand_weapon_names(weapons):
    output = []
    for w in weapons:
        matches = [g for g in global_weapons if g['Name'][0] == w]
        output.append(matches[0]['Name'])
    return(output)


def expand_alien_names(aliens):
    output = []
    for a in aliens:
        matches = [g for g in global_aliens if g['Name'][0] == a]
        output.append(matches[0]['Name'])
    return(output)

def all_possible_shots_of_squad(squad):
    squad_shot_possibilities = [{'probability' : 1}]
    for w in global_weapons:
        num_weapon = len([s for s in squad if s == w["Name"]])
        shots_range = w["Shots"]
        num_shot_possibilities = shots_range[1] - shots_range[0] + 1
        shot_chances = { 0 : 1 }
        for i in range(num_weapon):
            new_shot_chances = {}
            for shots_before in shot_chances.keys():
                for shots_now in range(shots_range[0], shots_range[1] + 1):
                    shots_after = shots_before + shots_now
                    if shots_after not in new_shot_chances.keys():
                        new_shot_chances[shots_after] = 0
                    new_shot_chances[shots_after] = new_shot_chances[shots_after] + (shot_chances[shots_before] / num_shot_possibilities)
            shot_chances = new_shot_chances
        new_squad_shot_possibilities = []
        for p in squad_shot_possibilities:
            for w_shots in shot_chances.keys():
                p_new= p.copy()
                p_new[w["Name"][0]] = w_shots
                p_new['probability'] = p_new['probability'] * shot_chances[w_shots]
                new_squad_shot_possibilities.append(p_new)
        squad_shot_possibilities = new_squad_shot_possibilities
    return(squad_shot_possibilities)
            
def full_eval_squad_vs_wave(squad, wave, expand=True):
    if expand:
       squad = expand_weapon_names(squad)
       wave = expand_alien_names(wave)
    shot_possibilities = all_possible_shots_of_squad(squad)
    win = 0
    loss= 0
    for p in shot_possibilities:
        shots = []
        for w in global_weapons:
            for i in range(p[w['Name'][0]]):
                shots.append(w['Damage'])   
        shots_struct = vals_to_structure(shots)
        healths_struct = struct_from_aliens(wave)
        result = eval_win(shots_struct, healths_struct)
        if result > 0:
            win = win + p['probability']
        else:
            loss = loss + p['probability']
    return(win)


def full_eval_wave_vs_number(alien_wave, number, verbose=False):
    squads = get_possible_squads(number)
    output = []
    for squad in squads:
        win_rate = full_eval_squad_vs_wave(squad, alien_wave, expand=False)
        output.append({'squad' : squad, 'win_rate' : win_rate})
    output.sort(key=lambda x: x['win_rate'], reverse=True)
    avg = sum([x['win_rate'] for x in output])/len(output)
    print('Average winrate is {:.2f}%'.format(avg*100))
    print('Top Three:')
    print(output[0])
    print(output[1])
    print(output[2])
          
    return(output)

    
random.seed('XCOM Long War')

focus_scores = True
if focus_scores:
    wave = [ 'Swarming Scarab' ] * 7 + ['Chitinous Crawler' ] * 2 + [ "Voracious Venompede" ] + [ "Arachnoid Abomination" ] * 3 + [ "Towering Tyrant" ] * 3
    out_file = open('alien_winrates_2.txt', 'w')
    for i in range(1,11):
        print('Doing size {}...'.format(i))
        squads = get_possible_squads(i)
        for squad in squads:
            win_rate = full_eval_squad_vs_wave(squad, wave, expand=False)
            squad_string = ''.join([w[0] for w in squad])
            out_file.write("'{}' : {:.4f}\n".format(squad_string, win_rate))
    out_file.close()
    print('Done')
            
    
focus_wave = False
if focus_wave:
    wave = [ 'Swarming Scarab' ] * 7 + ['Chitinous Crawler' ] * 2 + [ "Voracious Venompede" ] + [ "Arachnoid Abomination" ] * 3 + [ "Towering Tyrant" ] * 3

    
    players = [
        { 'name' : 'oneofeach', 'squad' : "MFPRLGTA"},
        { 'name' : 'abstractapplic8', 'squad' : "AAALLMTT"},
        { 'name' : 'abstractapplic7', 'squad' : "AAALLMT"},
        { 'name' : 'abstractapplic6', 'squad' : "AALLMT"},
        { 'name' : 'abstractapplic5', 'squad' : "AALMT"},
        { 'name' : 'abstractapplic4', 'squad' : "ALMT"},
    ]
    for p in players:
        p_name = p['name']
        p_squad = expand_weapon_names(p['squad'])
        print('Evaluatin {}'.format(p_name))
        wins = 0
        tries = 1e5
        for i in range(int(tries)):
            result = squad_vs_wave(p_squad, wave)
            if result > 0:
                wins = wins + 1
        print('Winrate is {:.2f}% with squad size {} ({})'.format(wins * 100 / tries, len(p_squad), p['squad']))

    sizes = [len(p['squad']) for p in players]
    for i in range(4,8):
        consider_wave_vs_number(wave, i, verbose=True)
            


find_interest = False
if find_interest:
    for i in range(100000):
        alien_wave = gen_alien_wave()
        consider_wave(alien_wave)

gen_dataset = False
if gen_dataset:
    setup_logs()
    global_threat_weight = 4
    global_alien_strength = 0
    month = 0
    timeout = 999999
    while timeout > 0:
        baseline = 4 + (month * 0.002)
        global_alien_strength = global_alien_strength + 0.02
        global_threat_weight = global_threat_weight + (random.random() * 0.03) #the war gets worse
        if global_threat_weight > (baseline + 1 + random.random() * 10):            #if it is going sufficiently badly we hold a new mobilization
            print('Month {}, threat has risen to {}, remobilizing...'.format(month, global_threat_weight))
            global_threat_weight = baseline # but that resets to a steadily-worse baseline.
            if month > 1000: # the mobilization you arrive in.
                timeout = 6
        encounters_in_month = (100 + global_alien_strength) * (1+random.random())
        for i in range(int(encounters_in_month)):
            eval_wave()
        month = month + 1
        timeout = timeout - 1
