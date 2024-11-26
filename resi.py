import json

# Load global scores from file
try:
    global_scores = json.load(open("global_scores.txt", "r"))
except FileNotFoundError:
    print("Global scores file not found. Initializing empty global scores.")
    global_scores = {}

# Load local scores from file
try:
    local_scores = json.load(open("local_scores.txt", "r"))
except FileNotFoundError:
    print("Local scores file not found. Initializing empty local scores.")
    local_scores = {}

# Global variables
update_global_scores = True
dim_weights = {"prestige": 0.5, "vibes": 0.2, "location": 0.3}
default_score = {"prestige": 1000, "vibes": 1000, "location": 1000}


# Save scores to file
def save_score(score_type=None):
    if score_type == "local":
        with open("local_scores.txt", "w") as file:
            json.dump(local_scores, file, indent=4)
    else:
        with open("global_scores.txt", "w") as file:
            json.dump(global_scores, file, indent=4)


# Add New Residency Program
def add_new_program(program_name):
    if program_name not in local_scores:
        local_scores[program_name] = default_score.copy()

        if update_global_scores and program_name not in global_scores:
            global_scores[program_name] = default_score.copy()
            save_score()  # Save any missing programs to the global scores


# Update Scores by Dimension
def update_scores_by_dimension(program1, program2, score_list, winner, dimension, k_factor=32):
    """
    Updates the score list (either global or local) for a specific dimension (e.g., prestige, vibes, location).
    """
    score1 = score_list[program1][dimension]
    score2 = score_list[program2][dimension]

    # Calculate expected scores using an Elo formula
    expected1 = 1 / (1 + 10 ** ((score2 - score1) / 400))
    expected2 = 1 - expected1

    # Update scores based on the winner
    if winner == program1:
        score_list[program1][dimension] += k_factor * (1 - expected1)
        score_list[program2][dimension] += k_factor * (0 - expected2)
    elif winner == program2:
        score_list[program1][dimension] += k_factor * (0 - expected1)
        score_list[program2][dimension] += k_factor * (1 - expected2)


# Compare New Program
def compare_new_program(program_name):
    """
    Prompts the user to compare the new program with existing ones.
    """
    for existing_program in local_scores:
        if existing_program != program_name:
            for dimension in dim_weights.keys():
                print(f"Which program has better {dimension}? {program_name} or {existing_program}")
                user_input = input(f"Enter your choice ('{program_name}' or '{existing_program}'): ")
                if user_input in [program_name, existing_program]:
                    update_scores_by_dimension(program_name, existing_program, local_scores, user_input, dimension)
                    if update_global_scores:
                        update_scores_by_dimension(program_name, existing_program, global_scores, user_input, dimension)


# Calculate Overall Score
def calculate_overall_score(program_name, dimension_weights):
    """
    Computes the overall weighted score for a program based on current weights.
    """
    scores = local_scores[program_name]
    overall_score = sum(scores[dimension] * weight for dimension, weight in dimension_weights.items())
    return overall_score


# Generate Rank List
def generate_rank_list(dimension_weights):
    """
    Ranks programs based on their overall weighted scores.
    """
    overall_scores = {
        program: calculate_overall_score(program, dimension_weights)
        for program in local_scores
    }
    sorted_programs = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_programs


if __name__ == "__main__":
    # Ask the user whether to update global scores
    update_global_scores = input("Would you like to update the current global scores (yes or no)?: ").strip().lower() == "yes"

    while True:
        new_program = input("Enter the name of a new program (or 'done' if finished adding programs): ")
        if new_program.strip().lower() == "done":
            break

        add_new_program(new_program)
        compare_new_program(new_program)

        # Display the current rankings
        rank_list = generate_rank_list(dim_weights)
        print("\nCurrent Residency Program Rankings:")
        for rank, (program, score) in enumerate(rank_list, start=1):
            print(f"{rank}. {program} - {score:.2f}")

    # Save the updated scores
    save_score(score_type="local")
    save_score()