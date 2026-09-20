"""
Exacte, samenstelling-afhankelijke kansberekening voor blackjack.

Dit is GEEN puntensysteem (zoals Hi-Lo) en GEEN simulatie/Monte Carlo-gok.
Het is een recursieve, uitputtende kansboom: voor elke mogelijke volgende
kaart wordt de exacte hypergeometrische kans berekend (aantal resterend van
die rang / totaal resterend), en wordt recursief verder gerekend tot elke hand
klaar is (bust, 21, of gestopt). Dat geeft de wiskundig exacte win/push/lose-
kans en verwachte waarde (EV) per actie, gegeven precies wat er nog in het
schoen zit.

Belangrijk over de dealer's verdekte kaart: die wordt NIET uit het schoen
gehaald totdat hij daadwerkelijk zichtbaar wordt (herkend door de camera).
Zolang hij onbekend is, wordt hij in de berekening terecht behandeld als een
willekeurige kaart uit het resterende schoen - precies zoals de werkelijkheid,
want dat IS wat hij is totdat je hem ziet.

Vereenvoudigingen (zie README voor detail):
- Blackjack-uitbetaling van 3:2 wordt niet apart verrekend (natural blackjack
  gevallen zijn al vóór dit beslismoment afgehandeld).
- Split-EV is een benadering: elke split-hand wordt onafhankelijk doorgerekend
  vanaf de resterende schoen-samenstelling na het splitsen; de (kleine)
  correlatie tussen de twee split-handen door onderlinge kaartverwijdering
  wordt genegeerd - dit is de gangbare aanpak, ook in professionele tools.
"""
from shoe import GROUP_ORDER, RANK_VALUES

HIT_SOFT_17 = False  # False = dealer STAAT op soft 17 (meest gangbare regel online)


def hand_total(ranks):
    """(total, is_soft) - is_soft = er telt nog een aas mee als 11 zonder bust."""
    total = 0
    aces_as_eleven = 0
    for r in ranks:
        v = 11 if r == "A" else RANK_VALUES.get(r, int(r) if r.isdigit() else 10)
        total += v
        if r == "A":
            aces_as_eleven += 1
    while total > 21 and aces_as_eleven > 0:
        total -= 10
        aces_as_eleven -= 1
    return total, aces_as_eleven > 0


def _counts_after_removal(counts_tuple, group_idx):
    c = list(counts_tuple)
    c[group_idx] -= 1
    return tuple(c)


def dealer_outcome_distribution(counts_tuple, dealer_hand, memo=None, peek=True):
    """
    Wrapper die de 'peek'-regel toepast: bij een 10- of Aas-upcard heeft de
    dealer al gecontroleerd of hij blackjack heeft. Heeft hij die, dan is de
    hand al voorbij en bereikt de speler dit beslismoment nooit. Die gevallen
    moeten dus uit de kansverdeling worden geconditioneerd, anders wordt elke
    EV tegen een 10 of Aas te pessimistisch.
    """
    if not peek or len(dealer_hand) != 1:
        return _dealer_dist_raw(counts_tuple, dealer_hand, memo)

    up = dealer_hand[0]
    if up not in ("10", "A"):
        return _dealer_dist_raw(counts_tuple, dealer_hand, memo)

    # De hole card die blackjack zou geven:
    bj_partner = "A" if up == "10" else "10"
    idx = GROUP_ORDER.index(bj_partner)
    total_remaining = sum(counts_tuple)
    if total_remaining == 0:
        return _dealer_dist_raw(counts_tuple, dealer_hand, memo)

    p_bj = counts_tuple[idx] / total_remaining
    if p_bj >= 1.0:
        return _dealer_dist_raw(counts_tuple, dealer_hand, memo)

    # Conditioneer op "geen blackjack": sommeer over alle NIET-blackjack hole cards,
    # elk met kans herschaald naar 1/(1 - p_bj).
    dist = {}
    for i, rank in enumerate(GROUP_ORDER):
        c = counts_tuple[i]
        if c == 0 or i == idx:
            continue
        p = (c / total_remaining) / (1.0 - p_bj)
        new_counts = _counts_after_removal(counts_tuple, i)
        sub = _dealer_dist_raw(new_counts, dealer_hand + (rank,), memo)
        for outcome, prob in sub.items():
            dist[outcome] = dist.get(outcome, 0.0) + p * prob
    return dist


def _dealer_dist_raw(counts_tuple, dealer_hand, memo=None):
    """
    Retourneert een kansverdeling over dealer-eindresultaten:
    {17:.., 18:.., 19:.., 20:.., 21:.., 'bust':..} (kansen sommeren tot 1.0)
    Exact berekend door recursief elke mogelijke volgende kaart te wegen met
    zijn werkelijke (hypergeometrische) kans in de huidige schoen-samenstelling.
    """
    if memo is None:
        memo = {}
    total, soft = hand_total(list(dealer_hand))

    if total > 21:
        return {"bust": 1.0}
    must_hit = total < 17 or (total == 17 and soft and HIT_SOFT_17)
    if not must_hit:
        return {total: 1.0}

    key = (counts_tuple, tuple(sorted(dealer_hand)))
    if key in memo:
        return memo[key]

    total_remaining = sum(counts_tuple)
    if total_remaining == 0:
        result = {total: 1.0}
        memo[key] = result
        return result

    dist = {}
    for idx, rank in enumerate(GROUP_ORDER):
        c = counts_tuple[idx]
        if c == 0:
            continue
        p = c / total_remaining
        new_counts = _counts_after_removal(counts_tuple, idx)
        new_hand = dealer_hand + (rank,)
        sub = _dealer_dist_raw(new_counts, new_hand, memo)
        for outcome, prob in sub.items():
            dist[outcome] = dist.get(outcome, 0.0) + p * prob

    memo[key] = dist
    return dist


def stand_ev_and_probs(player_total, dealer_dist):
    """EV bij STAND (uitbetaling +1 winst / -1 verlies / 0 push) + expliciete
    win/push/lose-kansen, gegeven een dealer-uitkomstverdeling."""
    win = push = lose = 0.0
    for outcome, prob in dealer_dist.items():
        if outcome == "bust":
            win += prob
        elif outcome > player_total:
            lose += prob
        elif outcome < player_total:
            win += prob
        else:
            push += prob
    ev = win * 1.0 + lose * -1.0 + push * 0.0
    return ev, win, push, lose


def best_hit_or_stand_ev(player_hand, dealer_up, counts_tuple, memo, dealer_memo):
    """Optimale EV vanaf deze hand, gegeven dat de speler nog vrij mag
    hitten of stoppen (gebruikt voor de recursieve 'wat als ik nu hit'-tak)."""
    total, soft = hand_total(list(player_hand))
    if total > 21:
        return -1.0

    dealer_dist = dealer_outcome_distribution(counts_tuple, (dealer_up,), dealer_memo)
    ev_stand, *_ = stand_ev_and_probs(total, dealer_dist)

    if total >= 21:
        return ev_stand

    key = (tuple(sorted(player_hand)), dealer_up, counts_tuple)
    if key in memo:
        return memo[key]

    total_remaining = sum(counts_tuple)
    if total_remaining == 0:
        memo[key] = ev_stand
        return ev_stand

    ev_hit = 0.0
    for idx, rank in enumerate(GROUP_ORDER):
        c = counts_tuple[idx]
        if c == 0:
            continue
        p = c / total_remaining
        new_counts = _counts_after_removal(counts_tuple, idx)
        new_hand = player_hand + (rank,)
        new_total, _ = hand_total(list(new_hand))
        if new_total > 21:
            sub = -1.0
        else:
            sub = best_hit_or_stand_ev(new_hand, dealer_up, new_counts, memo, dealer_memo)
        ev_hit += p * sub

    best = max(ev_stand, ev_hit)
    memo[key] = best
    return best


def _evaluate_one_split_hand(pair_rank, dealer_up, counts_tuple, dealer_memo, max_resplits):
    """
    EV van precies 1 van de twee (of meer) handen die ontstaan na het splitsen
    van `pair_rank`. Deze hand begint met 1 kaart van het paar en krijgt er
    direct 1 nieuwe kaart bij. Vanaf daar wordt de beste van STAND / HIT /
    DOUBLE gekozen - en als de nieuwe kaart toevallig opnieuw `pair_rank` is
    en er nog re-splits over zijn, wordt ook RE-SPLIT als optie meegenomen.
    """
    total_remaining = sum(counts_tuple)
    if total_remaining == 0:
        # geen kaarten meer - degenereert naar de huidige (1-kaarts) situatie; edge case
        return 0.0

    acc = 0.0
    for idx, rank in enumerate(GROUP_ORDER):
        c = counts_tuple[idx]
        if c == 0:
            continue
        p = c / total_remaining
        new_counts = _counts_after_removal(counts_tuple, idx)
        sub_hand = (pair_rank, rank)
        sub_total, _ = hand_total(list(sub_hand))

        dd = dealer_outcome_distribution(new_counts, (dealer_up,), dealer_memo)
        sub_stand, *_ = stand_ev_and_probs(sub_total, dd)

        is_ace_split = (pair_rank == "A")

        sub_hit = sub_stand
        if not is_ace_split and sub_total < 21:
            sub_hit_memo = {}
            sub_hit = best_hit_or_stand_ev(sub_hand, dealer_up, new_counts, sub_hit_memo, dealer_memo)

        # Double-na-split (DAS): exact 1 kaart erbij, dan verplicht stand, 2x inzet.
        sub_double = float("-inf")
        rem_for_double = sum(new_counts)
        if not is_ace_split and rem_for_double > 0:
            dacc = 0.0
            for idx2, rank2 in enumerate(GROUP_ORDER):
                c2 = new_counts[idx2]
                if c2 == 0:
                    continue
                p2 = c2 / rem_for_double
                counts3 = _counts_after_removal(new_counts, idx2)
                hand3 = sub_hand + (rank2,)
                total3, _ = hand_total(list(hand3))
                if total3 > 21:
                    dacc += p2 * -1.0
                else:
                    dd3 = dealer_outcome_distribution(counts3, (dealer_up,), dealer_memo)
                    s3, *_ = stand_ev_and_probs(total3, dd3)
                    dacc += p2 * s3
            sub_double = 2 * dacc

        if is_ace_split:
            # Standaardregel: gesplitste azen krijgen exact 1 kaart, geen hit/double daarna.
            best_this_hand = sub_stand
        else:
            best_this_hand = max(sub_stand, sub_hit, sub_double)

        # Opnieuw splitsen: als de nieuwe kaart weer `pair_rank` is en er nog
        # re-splits over zijn, mag de speler ook kiezen om WÉÉR te splitsen.
        if rank == pair_rank and max_resplits > 0:
            resplit_ev = 2 * _evaluate_one_split_hand(pair_rank, dealer_up, new_counts, dealer_memo,
                                                        max_resplits - 1)
            best_this_hand = max(best_this_hand, resplit_ev)

        acc += p * best_this_hand

    return acc


def evaluate_hand(player_ranks, dealer_up, group_counts_tuple, can_split=True, can_double=True):
    """
    Hoofdfunctie: berekent de exacte EV (en voor STAND ook win/push/lose-kans)
    van STAND, HIT, DOUBLE en (indien van toepassing) SPLIT, gegeven de
    werkelijke resterende schoen-samenstelling. Retourneert een dict met alle
    EV's plus de aanbevolen actie (hoogste EV).
    """
    player_hand = tuple(player_ranks)
    total, soft = hand_total(list(player_hand))

    dealer_memo = {}
    dealer_dist = dealer_outcome_distribution(group_counts_tuple, (dealer_up,), dealer_memo)
    ev_stand, win_p, push_p, lose_p = stand_ev_and_probs(total, dealer_dist)

    total_remaining = sum(group_counts_tuple)

    # ---- HIT: optimaal doorspelen na de eerste hit-kaart ----
    hit_memo = {}
    ev_hit = 0.0
    if total < 21 and total_remaining > 0:
        for idx, rank in enumerate(GROUP_ORDER):
            c = group_counts_tuple[idx]
            if c == 0:
                continue
            p = c / total_remaining
            new_counts = _counts_after_removal(group_counts_tuple, idx)
            new_hand = player_hand + (rank,)
            new_total, _ = hand_total(list(new_hand))
            if new_total > 21:
                sub = -1.0
            else:
                sub = best_hit_or_stand_ev(new_hand, dealer_up, new_counts, hit_memo, dealer_memo)
            ev_hit += p * sub
    else:
        ev_hit = ev_stand  # kan niet meer hitten (21) -> gelijk aan stand

    # ---- DOUBLE: exact 1 kaart erbij, dan verplicht stand, dubbele inzet ----
    ev_double = None
    if can_double and total_remaining > 0:
        acc = 0.0
        for idx, rank in enumerate(GROUP_ORDER):
            c = group_counts_tuple[idx]
            if c == 0:
                continue
            p = c / total_remaining
            new_counts = _counts_after_removal(group_counts_tuple, idx)
            new_hand = player_hand + (rank,)
            new_total, _ = hand_total(list(new_hand))
            if new_total > 21:
                sub = -1.0
            else:
                dd = dealer_outcome_distribution(new_counts, (dealer_up,), dealer_memo)
                sub, *_ = stand_ev_and_probs(new_total, dd)
            acc += p * sub
        ev_double = 2 * acc

    # ---- SPLIT (zie moduledocstring voor de resterende benadering rond
    # correlatie tussen split-handen) ----
    # Let op conventie: group_counts_tuple bevat AL NIET meer de kaarten die de
    # speler/dealer al open op tafel hebben liggen (die zijn er door de aanroeper
    # al uitgehaald). Bij een pair zijn dus beide paar-kaarten al verwijderd -
    # er hoeft hier dus GEEN extra kaart afgetrokken te worden.
    ev_split = None
    if can_split and len(player_hand) == 2 and player_hand[0] == player_hand[1] and total_remaining > 0:
        pair_rank = player_hand[0]
        # max_resplits=3 -> tot 4 handen totaal, de gangbare limiet op vrijwel elke site
        ev_split = 2 * _evaluate_one_split_hand(pair_rank, dealer_up, group_counts_tuple, dealer_memo,
                                                 max_resplits=3)

    candidates = {"STAND": ev_stand, "HIT": ev_hit}
    if ev_double is not None:
        candidates["DOUBLE"] = ev_double
    if ev_split is not None:
        candidates["SPLIT"] = ev_split

    best_action = max(candidates, key=candidates.get)

    return {
        "action": best_action,
        "evs": candidates,
        "win": win_p,
        "push": push_p,
        "lose": lose_p,
        "player_total": total,
        "is_soft": soft,
    }
