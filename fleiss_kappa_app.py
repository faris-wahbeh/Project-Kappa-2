import numpy as np
from typing import List, Tuple
import streamlit as st
import numpy as np
from typing import List, Tuple

def fleiss_kappa_binary(ratings: List[List[int]]) -> Tuple[float, float]:
    """
    Calculate Fleiss' Kappa for multiple raters with binary ratings.

    Parameters:
    ratings (list of lists): Each inner list represents a reviewer's ratings.
                             The length of the inner lists should be equal (number of items being rated).
                             The ratings should be binary (0 or 1).

    Returns:
    kappa (float): Fleiss' Kappa score
    po (float): Proportion of times the raters agree

    Raises:
    ValueError: If the input data is not valid.
    """
    # Input validation
    if not ratings:
        raise ValueError("The ratings list is empty.")
    if len(ratings) < 2:
        raise ValueError("There should be at least two raters.")
    if len(set(map(len, ratings))) != 1:
        raise ValueError("All inner lists should have the same length.")
    if any(rating not in [0, 1] for sublist in ratings for rating in sublist):
        raise ValueError("All ratings should be binary (0 or 1).")
    if len(ratings[0]) < 2:
        raise ValueError("There should be at least two items being rated.")

    # Number of reviewers and items being rated
    n_raters = len(ratings)
    n_items = len(ratings[0])

    # Initialize agreement counts
    agreements = 0
    total_pairs = 0

    # Calculate the number of times the raters agree and total pairs
    for i in range(n_items):
        for j in range(n_raters):
            for k in range(j + 1, n_raters):
                total_pairs += 1
                if ratings[j][i] == ratings[k][i]:
                    agreements += 1

    # Calculate the proportion of times the raters agree (Po or Pā¯)
    po = agreements / total_pairs

    # Calculate P_e (expected agreement)
    p_pos = np.mean([sum(item) / n_raters for item in zip(*ratings)])
    p_neg = 1 - p_pos
    p_e = p_pos**2 + p_neg**2

    # Calculate Fleiss' Kappa
    kappa = (po - p_e) / (1 - p_e)

    return kappa, po


def reviewer_contribution_analysis(ratings: List[List[int]]) -> Tuple[int, float, List[float]]:
    """
    Analyze which reviewer contributes most to a lower Fleiss' Kappa score by excluding each reviewer one at a time.

    Parameters:
    ratings (list of lists): Each inner list represents a reviewer's ratings.
                             The length of the inner lists should be equal (number of items being rated).
                             The ratings should be binary (0 or 1).

    Returns:
    Tuple[int, float, List[float]]: The index of the reviewer contributing most to the lower Kappa score,
                                    the highest Kappa score obtained by excluding a reviewer,
                                    and the list of Kappa scores excluding each reviewer.
    """
    n_raters = len(ratings)
    kappa_scores = []

    # Calculate Kappa scores by excluding each reviewer
    for i in range(n_raters):
        reduced_ratings = [ratings[j] for j in range(n_raters) if j != i]
        kappa, _ = fleiss_kappa_binary(reduced_ratings)
        kappa_scores.append(kappa)

    # Find the reviewer whose exclusion leads to the highest Kappa score
    highest_kappa = max(kappa_scores)
    most_contributory_reviewer = kappa_scores.index(highest_kappa)

    return most_contributory_reviewer, highest_kappa, kappa_scores

# Example usage
ratings = [
    [1, 0, 1, 1, 0],  # Reviewer 1
    [1, 0, 1, 1, 0],  # Reviewer 2
    [1, 1, 1, 0, 0]   # Reviewer 3
]

most_contributory_reviewer, highest_kappa, kappa_scores = reviewer_contribution_analysis(ratings)
print("Most contributory reviewer to lower Kappa score:", most_contributory_reviewer + 1)
print("Highest Kappa score obtained by excluding a reviewer:", highest_kappa)
print("Kappa scores excluding each reviewer:", kappa_scores)


# Streamlit UI
st.title("Rayyan Fleiss' Kappa Testing")



# Input number of reviewers and items
num_reviewers = st.number_input("Number of reviewers:", min_value=2, value=3)
num_items = st.number_input("Number of items:", min_value=2, value=5)

# Input the ratings
ratings = []
for i in range(num_reviewers):
    rating = st.text_input(f"Ratings for Reviewer {i + 1} (comma-separated, e.g., 1,0,1,1,0):")
    if rating:
        ratings.append(list(map(int, rating.split(','))))

# Calculate Fleiss' Kappa and contribution analysis
if st.button("Calculate Fleiss' Kappa"):
    try:
        if len(ratings) != num_reviewers or any(len(r) != num_items for r in ratings):
            st.error("Please ensure all reviewers have rated all items.")
        else:
            kappa, po = fleiss_kappa_binary(ratings)
            st.write(f"Fleiss' Kappa: {kappa}")
   

            most_contributory_reviewer, highest_kappa, kappa_scores = reviewer_contribution_analysis(ratings)
            st.write(f"Most contributory reviewer to lower Kappa score: Reviewer {most_contributory_reviewer + 1}")
            st.write(f"Highest Kappa score obtained by excluding a reviewer: {highest_kappa}")

    except ValueError as e:
        st.error(f"Error: {e}")
