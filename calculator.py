DEBUG = True
def calculate_progress_dynamic(
    data_levels,
    data_dailys,
    current_level,
    current_exp,
    burning=False,
    target_level=260,
    recommendations=None,
    include_mp=True,
    debug=False
):
    total_exp_needed = 0
    total_days = 0
    current_exp_at_level = current_exp

    if debug:
        print(f"DEBUG: Starting Calculation - Current Level: {current_level}, Current EXP: {current_exp}, Burning: {burning}, Include MP: {include_mp}")

    while current_level < target_level:
        if burning:
            block_exp_needed = 0
            block_daily_exp = 0
            for i in range(3):
                next_level = current_level + i
                if next_level >= target_level:
                    break
                block_exp_needed += data_levels[data_levels['Level'] == next_level]['Total_EXP'].sum()
                block_daily_exp += data_dailys[data_dailys['Level_Unlocked'] <= next_level]['EXP_Reward'].sum()
                if include_mp:
                    mp_exp = data_dailys[(data_dailys['Level_Unlocked'] <= next_level) & (data_dailys['MP'].notna())]['MP'].max()
                    block_daily_exp += mp_exp if mp_exp is not None else 0

            if block_daily_exp > 0:
                days_for_block = block_exp_needed / block_daily_exp
            else:
                days_for_block = float('inf')

            if debug:
                print(f"DEBUG: Burning Mode - Level Block ({current_level}-{min(current_level+2, target_level-1)}):")
                print(f"  - Total EXP Needed: {block_exp_needed}")
                print(f"  - Total Daily EXP Gain: {block_daily_exp}")
                print(f"  - Days for Block: {days_for_block:.2f}")

            total_days += days_for_block
            total_exp_needed += block_exp_needed
            current_level += 3  # Progress by 3 levels
        else:
            level_exp = data_levels[data_levels['Level'] == current_level]['Total_EXP'].sum()
            exp_needed_for_level = level_exp - current_exp_at_level
            daily_exp_gain = data_dailys[data_dailys['Level_Unlocked'] <= current_level]['EXP_Reward'].sum()
            if include_mp:
                mp_exp = data_dailys[(data_dailys['Level_Unlocked'] <= current_level) & (data_dailys['MP'].notna())]['MP'].max()
                daily_exp_gain += mp_exp if mp_exp is not None else 0

            if daily_exp_gain > 0:
                days_for_level = exp_needed_for_level / daily_exp_gain
            else:
                days_for_level = float('inf')

            total_days += days_for_level
            total_exp_needed += exp_needed_for_level
            current_level += 1

        current_exp_at_level = 0  # Reset EXP after leveling up

    return {
        "Total_EXP_Needed": total_exp_needed,
        "Total_Days": round(total_days, 2)
    }







def optimize_potion_usage(current_level, current_exp, target_level, potions, data_levels, data_dailys, burning=False, debug=False):
    """
    Calculate the optimal levels to use growth potions for the fastest leveling.
    :param current_level: User's current level.
    :param current_exp: User's current EXP.
    :param target_level: Desired target level.
    :param potions: List of dictionaries with potion details (e.g., type, quantity, level cap, flat rate).
    :param data_levels: DataFrame with level EXP requirements.
    :param data_dailys: DataFrame with daily EXP gains.
    :param burning: Boolean flag for Burning Mode.
    :param debug: Boolean flag for debugging outputs.
    :return: Dictionary with recommended levels for each potion type.
    """
    potion_usage = {potion['type']: [] for potion in potions}  # Store optimal levels for each potion type

    if debug:
        print(f"DEBUG: Starting Optimization - Current Level: {current_level}, Current EXP: {current_exp}, Burning: {burning}")

    for potion in potions:  # Iterate over potion types
        for _ in range(potion['quantity']):  # Use each potion one at a time
            max_time_saved = 0
            optimal_level = None

            # Iterate only over levels reachable in Burning Mode
            level_range = range(current_level, target_level, 3 if burning else 1)

            for level in level_range:
                # Calculate time to complete the current level without potions
                exp_needed = data_levels[data_levels['Level'] == level]['Total_EXP'].sum()
                daily_exp_gain = data_dailys[data_dailys['Level_Unlocked'] <= level]['EXP_Reward'].sum()
                mp_exp = data_dailys[(data_dailys['Level_Unlocked'] <= level) & (data_dailys['MP'].notna())]['MP'].sum()
                daily_exp_gain += mp_exp

                if burning:
                    daily_exp_gain *= 3  # Adjust for Burning Mode

                days_without_potion = exp_needed / daily_exp_gain

                # Simulate potion use
                if level < potion['level_cap']:
                    potion_exp = exp_needed  # 100% of the level's EXP
                else:
                    potion_exp = potion['flat_rate']  # Flat rate for capped levels

                remaining_exp = max(0, exp_needed - potion_exp)
                days_with_potion = remaining_exp / daily_exp_gain

                # Calculate time saved
                time_saved = days_without_potion - days_with_potion

                if debug:
                    print(f"DEBUG: Potion {potion['type']} at Level {level} - Time Saved: {time_saved:.2f} Days")

                if time_saved > max_time_saved:
                    max_time_saved = time_saved
                    optimal_level = level

            # Apply the potion to the optimal level
            if optimal_level is not None:
                potion_usage[potion['type']].append(optimal_level)
                current_level = optimal_level + (3 if burning else 1)  # Advance level based on Burning Mode
                current_exp = 0  # Reset EXP after leveling up

    if debug:
        print(f"DEBUG: Final Potion Usage Recommendations: {potion_usage}")

    return potion_usage
