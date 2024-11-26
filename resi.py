import json
    
residency_programs = {}
master_score_list = json.load(open("global_scores.txt", "r"))
dimension_weights = {"prestige": 0.5, "vibes": 0.3, "location": 0.2}

# Save master_score_list to file
def save_global_scores(master_score_list):
    """
    Save the locally updated Elo rankings as the global rankings. 
    """
    with open("global_scores.txt", "w") as file:
        json.dump(master_score_list, file, indent=4)

def update_scores_by_dimension(program1, program2, winner, dimension, k_factor=32, use_global_scores):
    """
    Updates scores for a specific dimension (e.g., prestige, vibes, location).
    If use_global_scores is True, updates global scores in master_score_list as well.
    """
    score1 = residency_programs[program1][dimension]
    score2 = residency_programs[program2][dimension]

    # Calculate expected scores using an Elo formula
    expected1 = 1 / (1 + 10 ** ((score2 - score1) / 400))
    expected2 = 1 - expected1

    # Update scores based on the winner
    if winner == program1:
        residency_programs[program1][dimension] += k_factor * (1 - expected1)
        residency_programs[program2][dimension] += k_factor * (0 - expected2)
    elif winner == program2:
        residency_programs[program1][dimension] += k_factor * (0 - expected1)
        residency_programs[program2][dimension] += k_factor * (1 - expected2)

    # Update global scores if applicable
    if use_global_scores:
        master_score_list[program1][dimension] = residency_programs[program1][dimension]
        master_score_list[program2][dimension] = residency_programs[program2][dimension]
        save_global_scores(master_score_list)


# Calculate Overall Score
def calculate_overall_score(program_name, dimension_weights):
    """
    Computes the overall weighted score for a program based on current weights.
    """
    scores = master_score_list[program_name]
    overall_score = sum(scores[dimension] * weight for dimension, weight in dimension_weights.items())
    return overall_score


# Generate Rank List
def generate_rank_list(dimension_weights):
    """
    Ranks programs based on their overall weighted scores.
    """
    overall_scores = {
        program: calculate_overall_score(program, dimension_weights)
        for program in master_score_list
    }
    sorted_programs = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_programs


# Add New Residency Program
def add_new_program(program_name, starting_scores=None, use_global_scores=False):
    """
    Adds a new program with default scores for each dimension.
    Adds the program to the global master_score_list only if use_global_scores is True.
    """
    if program_name not in residency_programs:
        if starting_scores is None:
            starting_scores = {"prestige": 1000, "vibes": 1000, "location": 1000}
        residency_programs[program_name] = starting_scores

        if use_global_scores and program_name not in master_score_list:
            master_score_list[program_name] = starting_scores.copy()
            save_global_scores(master_score_list)  # Save changes to file


# Compare New Program
def compare_new_program(program_name, use_global_scores=False):
    """
    Prompts the user to compare the new program with existing ones.
    """
    for existing_program in residency_programs:
        if existing_program != program_name:
            for dimension in ["prestige", "vibes", "location"]:
                print(f"Which program has better {dimension}? {program_name} or {existing_program}")
                user_input = input(f"Enter your choice ('{program_name}' or '{existing_program}'): ")
                if user_input in [program_name, existing_program]:
                    update_scores_by_dimension(program_name, existing_program, user_input, dimension, use_global_scores)


def get_curr_scores(program_name):
    """
    Get the current global Elo scores of a given program.

    Parameters:
    - program_name (str): The name of the program whose scores are to be retrieved.

    Returns:
    - dict: The current global Elo scores for each dimension of the program if it exists.
    - None: If the program does not exist in the master_score_list.
    """
    global master_score_list
    if program_name in master_score_list:
        return master_score_list[program_name]
    else:
        print(f"Error: {program_name} not found in the master_score_list.")
        return None


if __name__ == "__main__":
    use_global_scores = input("Would you like to use global default scores (enter yes or no)? ").strip().lower() == "yes"

    while True:
        new_program = input("Enter the name of a new program (or 'done' to finish adding programs): ")
        if new_program.lower() == "done":
            break

        if use_global_scores:
            starting_scores = get_curr_scores(new_program) or {"prestige": 1000, "vibes": 1000, "location": 1000}
        else:
            starting_scores = {"prestige": 1000, "vibes": 1000, "location": 1000}

        add_new_program(new_program, starting_scores, use_global_scores)
        compare_new_program(new_program, use_global_scores)

    # Generate and display the final rank list with initial weights
    rank_list = generate_rank_list(dimension_weights)
    print("\nFinal Residency Program Rankings (using initial weights):")
    for rank, (program, score) in enumerate(rank_list, start=1):
        print(f"{rank}. {program} - {score:.2f}")

    # Allow user to adjust weights dynamically
    print("\nYou can now adjust the weights for final ranking:")
    for dimension in dimension_weights:
        new_weight = float(input(f"Enter new weight for {dimension} (current: {dimension_weights[dimension]}): "))
        dimension_weights[dimension] = new_weight

    # Recalculate rankings with updated weights
    rank_list = generate_rank_list(dimension_weights)
    print("\nFinal Residency Program Rankings (using updated weights):")
    for rank, (program, score) in enumerate(rank_list, start=1):
        print(f"{rank}. {program} - {score:.2f}")
